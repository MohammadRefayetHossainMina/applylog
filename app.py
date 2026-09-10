import json
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "database.db"
ALLOWED_STATUSES = ("applied", "interview", "offer", "rejected")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

WIKI_USER_AGENT = (
    "ApplyLog/1.0 (local job-application tracker; educational project)"
)
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_OPENSEARCH_URL = "https://en.wikipedia.org/w/api.php"
FETCH_DEADLINE_SEC = 7.0
SUMMARY_MAX_CHARS = 700
NOT_FOUND_MESSAGE = "No public summary found."
SNIPPET_MAX_CHARS = 140
HIRING_FALLBACK_MAX_CHARS = 1100
HTML_TAG_RE = re.compile(r"<[^>]+>")
BULLET_PREFIX_RE = re.compile(r"^[\s]*([•*\-–—]|\d+[.)])\s+")

app = Flask(__name__)
app.secret_key = "applylog-local-single-user"


class CompanyInfoFetchError(Exception):
    """Raised when Wikipedia cannot be reached or returns an unexpected error."""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            date_applied TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            company_info TEXT,
            hiring_notes TEXT,
            posting_paste TEXT
        )
        """
    )
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(applications)").fetchall()
    }
    if "company_info" not in columns:
        conn.execute("ALTER TABLE applications ADD COLUMN company_info TEXT")
    if "hiring_notes" not in columns:
        conn.execute("ALTER TABLE applications ADD COLUMN hiring_notes TEXT")
    if "posting_paste" not in columns:
        conn.execute("ALTER TABLE applications ADD COLUMN posting_paste TEXT")
    conn.commit()
    conn.close()


def fetch_applications():
    conn = get_db()
    try:
        return conn.execute(
            """
            SELECT id, company, role, date_applied, status, notes, company_info,
                   hiring_notes, posting_paste
            FROM applications
            ORDER BY date_applied DESC, id DESC
            """
        ).fetchall()
    finally:
        conn.close()


def fetch_application(application_id):
    conn = get_db()
    try:
        return conn.execute(
            """
            SELECT id, company, role, date_applied, status, notes, company_info,
                   hiring_notes, posting_paste
            FROM applications
            WHERE id = ?
            """,
            (application_id,),
        ).fetchone()
    finally:
        conn.close()


def _strip_html(text):
    text = HTML_TAG_RE.sub(" ", text or "")
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return text


def _clean_line(line):
    line = BULLET_PREFIX_RE.sub("", (line or "").strip())
    return " ".join(line.split())


def _line_matches(line, patterns):
    lower = line.casefold()
    return any(p.search(lower) for p in patterns)


def _is_section_header(line):
    compact = line.rstrip(":").strip()
    return len(compact) <= 48 and compact.casefold() in {
        "requirements",
        "requirement",
        "qualifications",
        "qualification",
        "responsibilities",
        "responsibility",
        "duties",
        "benefits",
        "perks",
        "what you'll do",
        "what you will do",
        "about the role",
        "the role",
        "job description",
        "location",
        "compensation",
        "salary",
        "employment type",
    }


SECTION_STOP = re.compile(
    r"^(requirements?|qualifications?|responsibilit(y|ies)|duties|benefits?|"
    r"perks?|compensation|salary|location|about (the )?(role|us|company)|"
    r"what you.?ll do|employment type|how to apply|equal opportunity)\b",
    re.I,
)


def _collect_section_lines(raw_lines, start_idx, used, limit):
    """Take following lines after a section header until the next section."""
    collected = []
    for j in range(start_idx + 1, len(raw_lines)):
        if j in used:
            continue
        nxt = raw_lines[j]
        if _is_section_header(nxt) or SECTION_STOP.match(nxt):
            break
        if re.search(
            r"\b(deadline|apply by|applications? close|visa|sponsorship|"
            r"equal opportunity)\b",
            nxt,
            re.I,
        ):
            break
        if len(nxt) < 3:
            continue
        collected.append(nxt)
        used.add(j)
        if len(collected) >= limit:
            break
    return collected


def _shorten(line, limit=220):
    if len(line) <= limit:
        return line
    return line[: limit - 1].rstrip() + "…"


def _looks_like_header_only(line, label):
    compact = line.rstrip(":").strip()
    if _is_section_header(line):
        return True
    return compact.casefold() == label.casefold()


def extract_hiring_notes(paste):
    """Heuristic extract of important hiring-page info. Returns None if empty."""
    paste = _strip_html(paste or "").strip()
    if not paste:
        return None

    raw_lines = []
    for line in paste.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        cleaned = _clean_line(line)
        if cleaned and len(cleaned) > 1:
            raw_lines.append(cleaned)

    if not raw_lines:
        return None

    categories = [
        (
            "Role / title",
            [
                re.compile(r"\b(job title|position title|role title)\b"),
                re.compile(r"\b(we are hiring|now hiring|opening for)\b"),
            ],
            2,
            False,
        ),
        (
            "Location / remote",
            [
                re.compile(r"\b(location|based in|headquarters|office)\b"),
                re.compile(r"\b(remote|hybrid|on[- ]?site|work from home|wfh)\b"),
            ],
            3,
            False,
        ),
        (
            "Employment type",
            [
                re.compile(
                    r"\b(full[- ]?time|part[- ]?time|contract|temporary|"
                    r"internship|permanent|freelance|employment type)\b"
                ),
            ],
            2,
            False,
        ),
        (
            "Salary / compensation",
            [
                re.compile(
                    r"\b(salary|compensation|pay|wage|stipend|equity|"
                    r"base pay|total cash|otc)\b"
                ),
                re.compile(r"[\$£€]\s?\d"),
                re.compile(r"\b\d{2,3}[,.]?\d{3}\s*[-–—to]+\s*[\$£€]?\s?\d"),
            ],
            3,
            False,
        ),
        (
            "Requirements",
            [
                re.compile(
                    r"\b(requirements?|qualifications?|must have|you (have|bring)|"
                    r"minimum qualifications?)\b"
                ),
            ],
            5,
            True,
        ),
        (
            "Responsibilities",
            [
                re.compile(
                    r"\b(responsibilit(y|ies)|what you.?ll do|you will|"
                    r"day[- ]to[- ]day|duties|about the role)\b"
                ),
            ],
            4,
            True,
        ),
        (
            "Benefits",
            [
                re.compile(
                    r"\b(benefits?|perks?|pto|paid time off|health insurance|"
                    r"401\(?k\)?|wellness|vacation)\b"
                ),
            ],
            4,
            True,
        ),
        (
            "Deadline",
            [
                re.compile(
                    r"\b(deadline|apply by|applications? close|closing date|"
                    r"last day to apply)\b"
                ),
            ],
            2,
            False,
        ),
    ]

    used = set()
    bullets = []

    first = raw_lines[0]
    if len(first) <= 90 and re.search(
        r"\b(engineer|developer|analyst|manager|designer|scientist|"
        r"specialist|coordinator|director|intern|associate)\b",
        first,
        re.I,
    ):
        bullets.append(f"- Role / title: {first}")
        used.add(0)

    for label, patterns, limit, grab_following in categories:
        if label == "Role / title" and any(
            b.startswith("- Role / title:") for b in bullets
        ):
            continue
        hits = []
        for idx, line in enumerate(raw_lines):
            if idx in used:
                continue
            if not _line_matches(line, patterns):
                continue
            header_only = _looks_like_header_only(line, label)
            if header_only and grab_following:
                used.add(idx)
                hits.extend(_collect_section_lines(raw_lines, idx, used, limit))
            else:
                hits.append(line)
                used.add(idx)
                # Only pull siblings when the match was a bare section title.
                if grab_following and header_only:
                    hits.extend(
                        _collect_section_lines(
                            raw_lines, idx, used, max(0, limit - len(hits))
                        )
                    )
            if len(hits) >= limit:
                hits = hits[:limit]
                break
        if not hits:
            continue
        if len(hits) == 1 and len(hits[0]) < 140:
            bullets.append(f"- {label}: {hits[0]}")
        else:
            bullets.append(f"- {label}:")
            for hit in hits:
                bullets.append(f"  - {_shorten(hit)}")

    if not bullets:
        skip = re.compile(
            r"^(home|careers|jobs|menu|skip to|cookie|privacy|sign in|"
            r"log in|share|apply now)$",
            re.I,
        )
        meaningful = [
            line
            for line in raw_lines
            if len(line) >= 25 and not skip.fullmatch(line)
        ]
        if not meaningful:
            meaningful = raw_lines
        text = "\n".join(f"- {line}" for line in meaningful)
        if len(text) > HIRING_FALLBACK_MAX_CHARS:
            text = text[:HIRING_FALLBACK_MAX_CHARS].rsplit("\n", 1)[0]
            if not text.endswith("…"):
                text = text.rstrip() + "…"
        return text or None

    other = []
    notable = re.compile(
        r"\b(visa|sponsorship|clearance|security|travel|relocation|"
        r"equal opportunity|eoe|diversity)\b",
        re.I,
    )
    for idx, line in enumerate(raw_lines):
        if idx in used:
            continue
        if notable.search(line):
            other.append(line)
            used.add(idx)
            if len(other) >= 3:
                break
    if other:
        bullets.append("- Other notes:")
        for line in other:
            bullets.append(f"  - {_shorten(line)}")

    return "\n".join(bullets)


def parse_application_form(form):
    values = {
        "company": (form.get("company") or "").strip(),
        "role": (form.get("role") or "").strip(),
        "date_applied": (form.get("date_applied") or "").strip(),
        "status": (form.get("status") or "").strip(),
        "notes": (form.get("notes") or "").strip(),
    }
    errors = []
    if not values["company"]:
        errors.append("Company is required.")
    if not values["role"]:
        errors.append("Role is required.")
    if not values["date_applied"]:
        errors.append("Date applied is required.")
    elif not DATE_PATTERN.fullmatch(values["date_applied"]):
        errors.append("Date applied must be YYYY-MM-DD.")
    if values["status"] not in ALLOWED_STATUSES:
        errors.append("Status must be applied, interview, offer, or rejected.")
    return values, errors


def truncate_summary(text, limit=SUMMARY_MAX_CHARS):
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    space = cut.rfind(" ")
    if space >= int(limit * 0.7):
        cut = cut[:space]
    return cut.rstrip(" ,;:-") + "…"


@app.template_filter("snippet")
def snippet_filter(text, limit=SNIPPET_MAX_CHARS):
    text = " ".join((text or "").split())
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _remaining_timeout(deadline):
    return deadline - time.monotonic()


def _wiki_json(url, timeout):
    if timeout <= 0.2:
        raise CompanyInfoFetchError("Timed out before request.")
    request_obj = urllib.request.Request(
        url,
        headers={
            "User-Agent": WIKI_USER_AGENT,
            "Api-User-Agent": WIKI_USER_AGENT,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request_obj, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        try:
            exc.read()
        except OSError:
            pass
        if exc.code in (400, 404):
            return None
        raise CompanyInfoFetchError(f"Wikipedia HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise CompanyInfoFetchError("Wikipedia request failed") from exc
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise CompanyInfoFetchError("Wikipedia response was not JSON") from exc


def wikipedia_page_extract(title, deadline):
    timeout = _remaining_timeout(deadline)
    quoted = urllib.parse.quote(title, safe="")
    url = WIKI_SUMMARY_URL.format(title=quoted)
    data = _wiki_json(url, timeout)
    if not data:
        return None
    extract = (data.get("extract") or "").strip()
    if not extract:
        return None
    return truncate_summary(extract)


def wikipedia_search_title(company, deadline):
    timeout = _remaining_timeout(deadline)
    query = urllib.parse.urlencode(
        {
            "action": "opensearch",
            "search": company,
            "limit": "1",
            "namespace": "0",
            "format": "json",
        }
    )
    url = f"{WIKI_OPENSEARCH_URL}?{query}"
    data = _wiki_json(url, timeout)
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return None
    title = data[1][0]
    if not isinstance(title, str) or not title.strip():
        return None
    return title.strip()


def lookup_company_info(company_name):
    """Return (stored_text_or_none, fetch_failed). Never raises."""
    company_name = (company_name or "").strip()
    if not company_name:
        return None, False
    deadline = time.monotonic() + FETCH_DEADLINE_SEC
    try:
        extract = wikipedia_page_extract(company_name, deadline)
        if extract:
            return extract, False
        if _remaining_timeout(deadline) <= 0.2:
            raise CompanyInfoFetchError("Timed out before search fallback.")
        title = wikipedia_search_title(company_name, deadline)
        if title and title.casefold() != company_name.casefold():
            extract = wikipedia_page_extract(title, deadline)
            if extract:
                return extract, False
        return NOT_FOUND_MESSAGE, False
    except CompanyInfoFetchError:
        return None, True


@app.route("/")
def index():
    return render_template(
        "index.html",
        applications=fetch_applications(),
        error=None,
        form={
            "company": "",
            "role": "",
            "date_applied": "",
            "status": "applied",
            "notes": "",
            "posting_paste": "",
        },
        statuses=ALLOWED_STATUSES,
    )


@app.route("/add", methods=["POST"])
def add_application():
    values, errors = parse_application_form(request.form)
    posting_paste = (request.form.get("posting_paste") or "").strip()
    values["posting_paste"] = posting_paste
    if errors:
        return (
            render_template(
                "index.html",
                applications=fetch_applications(),
                error=" ".join(errors),
                form=values,
                statuses=ALLOWED_STATUSES,
            ),
            400,
        )
    company_info, fetch_failed = lookup_company_info(values["company"])
    hiring_notes = extract_hiring_notes(posting_paste)
    stored_paste = posting_paste or None
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO applications
                (company, role, date_applied, status, notes, company_info,
                 hiring_notes, posting_paste)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                values["company"],
                values["role"],
                values["date_applied"],
                values["status"],
                values["notes"],
                company_info,
                hiring_notes,
                stored_paste,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    flash("Application saved.", "success")
    if fetch_failed:
        flash(
            "Company info could not be fetched. The application was still saved.",
            "error",
        )
    return redirect(url_for("index"))


@app.route("/edit/<int:application_id>")
def edit_application(application_id):
    application = fetch_application(application_id)
    if application is None:
        return ("Application not found.", 404)
    return render_template(
        "edit.html",
        application=application,
        error=None,
        form={
            "status": application["status"],
            "notes": application["notes"] or "",
            "company_info": application["company_info"] or "",
            "posting_paste": application["posting_paste"] or "",
        },
        statuses=ALLOWED_STATUSES,
    )


@app.route("/edit/<int:application_id>", methods=["POST"])
def update_application(application_id):
    application = fetch_application(application_id)
    if application is None:
        return ("Application not found.", 404)
    status = (request.form.get("status") or "").strip()
    notes = (request.form.get("notes") or "").strip()
    company_info = (request.form.get("company_info") or "").strip()
    posting_paste = (request.form.get("posting_paste") or "").strip()
    hiring_notes = extract_hiring_notes(posting_paste)
    stored_paste = posting_paste or None
    if status not in ALLOWED_STATUSES:
        return (
            render_template(
                "edit.html",
                application=application,
                error="Status must be applied, interview, offer, or rejected.",
                form={
                    "status": status,
                    "notes": notes,
                    "company_info": company_info,
                    "posting_paste": posting_paste,
                },
                statuses=ALLOWED_STATUSES,
            ),
            400,
        )
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE applications
            SET status = ?, notes = ?, company_info = ?,
                hiring_notes = ?, posting_paste = ?
            WHERE id = ?
            """,
            (
                status,
                notes,
                company_info,
                hiring_notes,
                stored_paste,
                application_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    flash("Application updated.", "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:application_id>/refresh-company-info", methods=["POST"])
def refresh_company_info(application_id):
    application = fetch_application(application_id)
    if application is None:
        return ("Application not found.", 404)
    company_info, fetch_failed = lookup_company_info(application["company"])
    if fetch_failed:
        flash(
            "Company info could not be fetched. The previous summary was kept.",
            "error",
        )
        return redirect(url_for("edit_application", application_id=application_id))
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE applications
            SET company_info = ?
            WHERE id = ?
            """,
            (company_info, application_id),
        )
        conn.commit()
    finally:
        conn.close()
    flash("Company info updated.", "success")
    return redirect(url_for("edit_application", application_id=application_id))


@app.route("/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    application = fetch_application(application_id)
    if application is None:
        return ("Application not found.", 404)
    conn = get_db()
    try:
        conn.execute("DELETE FROM applications WHERE id = ?", (application_id,))
        conn.commit()
    finally:
        conn.close()
    flash("Application deleted.", "success")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
