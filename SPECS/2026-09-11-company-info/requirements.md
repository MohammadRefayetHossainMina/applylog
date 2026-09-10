# Company info — requirements

## Feature
When a job seeker logs an application, ApplyLog fetches a short public summary of the company from Wikipedia and stores it on the row so they can read it before interviews.

## Aligns with
SPECS/MISSION.md company-research exception (2026-09-11). ROADMAP item 5.

## Entities
Table `applications` as in SPECS/TECH.md, plus:
- `company_info` TEXT optional/nullable — plain-text public summary

Existing `database.db` files must gain this column via `ALTER TABLE applications ADD COLUMN company_info TEXT` when it is missing. `CREATE TABLE IF NOT EXISTS` alone is not enough.

## User actions
1. Add an application as before (`POST /add`). After a valid save, the row includes `company_info` when a summary is found.
2. On `GET /`, see a short snippet of company info next to notes (full table must stay readable).
3. On `GET /edit/<id>`, read the full stored summary (left-aligned, body type) and optionally edit it in a textarea, then `POST /edit/<id>` with status, notes, and company info.
4. On the edit page, choose **Refresh company info** (`POST /edit/<id>/refresh-company-info`) to fetch again for the logged company name.

Company, role, and date applied stay as logged. Status and notes still update as in the update-application feature.

## Fetch rules
- Source: Wikipedia REST `GET https://en.wikipedia.org/api/rest_v1/page/summary/{quoted_name}` with a proper User-Agent. Use JSON field `extract`.
- Truncate huge extracts to about 600–800 characters.
- If that page is missing (404), try Wikipedia OpenSearch (`action=opensearch`) then summary for the top hit. If still nothing, store a clear “No public summary found.” message.
- Timeout about 5–8 seconds for the lookup.
- Never crash the save on network error, timeout, or unexpected Wikipedia response.
- No API key. Stdlib `urllib` only. No job-board scrapers.

## Expected behavior
- **Add + summary found:** Application is saved; `company_info` is persisted and visible after restart.
- **Add + no page:** Application is saved; `company_info` stores the not-found message.
- **Add + network failure:** Application is saved; `company_info` stays empty/NULL; flash/error explains that info could not be fetched.
- **Refresh + network failure:** Previous `company_info` is kept; flash/error explains the failure.
- **Edit save:** Status, notes, and any corrected `company_info` are written with parameterized SQL. Invalid status still must not update the row.

## Out of scope
Authentication, React, SQLAlchemy, job-board scrapers, email, notifications, export, extra tables.
