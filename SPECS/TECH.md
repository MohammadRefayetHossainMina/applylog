# ApplyLog Tech

## Stack
- Frontend: vanilla HTML, CSS, and a small amount of JavaScript if needed for confirm-delete
- Backend: Python and Flask
- Database: SQLite file `database.db` in the project root
- No React, Vue, SQLAlchemy, or hosted databases
- Company summaries: Python `urllib` to Wikipedia REST (no extra packages, no API key)

## Runtime
- Flask app in `app.py`
- Bind host `0.0.0.0`, port `3000`
- Templates in `templates/`
- Static files in `static/`

## Schema
Table: `applications`

| Column        | Type    | Constraints                                      | Stores                          |
|---------------|---------|--------------------------------------------------|---------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT                        | Unique row id                   |
| company       | TEXT    | NOT NULL                                         | Employer name                   |
| role          | TEXT    | NOT NULL                                         | Job title                       |
| date_applied  | TEXT    | NOT NULL                                         | ISO date `YYYY-MM-DD`           |
| status        | TEXT    | NOT NULL; one of applied, interview, offer, rejected | Pipeline stage              |
| notes         | TEXT    | optional                                         | Free-text notes                 |
| company_info  | TEXT    | optional / nullable                              | Short public company summary    |

## Constraints
- `company`, `role`, and `date_applied` are required and must be non-empty after trimming whitespace.
- `status` must be exactly one of: `applied`, `interview`, `offer`, `rejected`.
- `date_applied` must match `YYYY-MM-DD`.
- `notes` may be empty.
- `company_info` may be empty or NULL if fetch failed or the user cleared it.
- All reads and writes use parameterized SQL. No ORM.

## Company info fetch
- On add, look up a summary for the company name before insert. Insert still happens if the lookup fails.
- Preferred: `GET https://en.wikipedia.org/api/rest_v1/page/summary/{quoted_name}` with a descriptive User-Agent. Store `extract`, truncated to about 700 characters.
- If that page 404s, try Wikipedia `action=opensearch` and then the summary for the top title. If nothing useful is found, store `No public summary found.`
- Overall lookup budget is about 7 seconds. Network errors must not crash the save; keep `company_info` empty (add) or unchanged (refresh) and show a flash error.
- Edit can correct the stored text, or POST `/edit/<id>/refresh-company-info` to fetch again.

## Engineering standards
- Initialize the table with `CREATE TABLE IF NOT EXISTS` on startup.
- Existing database files: if `company_info` is missing, run `ALTER TABLE applications ADD COLUMN company_info TEXT`. `CREATE TABLE IF NOT EXISTS` does not add columns to an already-created table. Older local databases may still have unused `hiring_notes` / `posting_paste` columns; the app does not read or write them.
- Prefer POST-redirect-GET after successful writes.
- Show a clear error on the same page when validation fails; do not insert invalid rows.
- Keep styling out of the first slices; CSS polish comes after add, update, and delete work.
