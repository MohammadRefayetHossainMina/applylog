import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DATABASE_PATH", APP_DIR / "database.db"))
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

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "applylog-local-single-user")


class CompanyInfoFetchError(Exception):
    """Raised when Wikipedia cannot be reached or returns an unexpected error."""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
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
            company_info TEXT
        )
        """
    )
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(applications)").fetchall()
    }
    if "company_info" not in columns:
        conn.execute("ALTER TABLE applications ADD COLUMN company_info TEXT")
    conn.commit()
    conn.close()


def fetch_applications():
    conn = get_db()
    try:
        return conn.execute(
            """
            SELECT id, company, role, date_applied, status, notes, company_info
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
            SELECT id, company, role, date_applied, status, notes, company_info
            FROM applications
            WHERE id = ?
            """,
            (application_id,),
        ).fetchone()
    finally:
        conn.close()


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
        },
        statuses=ALLOWED_STATUSES,
    )


@app.route("/add", methods=["POST"])
def add_application():
    values, errors = parse_application_form(request.form)
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
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO applications
                (company, role, date_applied, status, notes, company_info)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                values["company"],
                values["role"],
                values["date_applied"],
                values["status"],
                values["notes"],
                company_info,
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
            SET status = ?, notes = ?, company_info = ?
            WHERE id = ?
            """,
            (
                status,
                notes,
                company_info,
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
    port = int(os.environ.get("PORT", "3000"))
    app.run(host="0.0.0.0", port=port, debug=False)
