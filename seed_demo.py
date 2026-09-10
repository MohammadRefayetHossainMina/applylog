"""Write demo.db with sample applications. Does not touch database.db."""

import sqlite3
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DEMO_PATH = APP_DIR / "demo.db"

DEMO_ROWS = [
    (
        "SEEK",
        "Senior Software Engineer",
        "2026-08-20",
        "interview",
        None,
        "SEEK Limited is an Australian online employment marketplace that connects job seekers with employers.",
    ),
    (
        "Qantas",
        "Back-End Developer",
        "2026-09-04",
        "applied",
        None,
        "Qantas Airways Limited is the flag carrier of Australia and the country's largest airline.",
    ),
    (
        "Atlassian",
        "Senior Principal Software Engineer",
        "2026-09-09",
        "applied",
        None,
        "Atlassian Corporation is an Australian software company known for collaboration tools such as Jira and Confluence.",
    ),
    (
        "Dematic",
        "Software Developer",
        "2026-08-12",
        "rejected",
        None,
        "Dematic is a supplier of automated material-handling systems and software for warehouses and distribution centres.",
    ),
]


def main():
    if DEMO_PATH.exists():
        DEMO_PATH.unlink()
    conn = sqlite3.connect(DEMO_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE applications (
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
        conn.executemany(
            """
            INSERT INTO applications
                (company, role, date_applied, status, notes, company_info)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            DEMO_ROWS,
        )
        conn.commit()
    finally:
        conn.close()
    print(f"Wrote {DEMO_PATH} with {len(DEMO_ROWS)} sample applications.")


if __name__ == "__main__":
    main()
