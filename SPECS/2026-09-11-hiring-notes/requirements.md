# Hiring notes — requirements

## Feature
When a job seeker pastes text from a hiring or careers page into an application, ApplyLog extracts a short structured summary of important posting details, stores it on the row, and shows it from a small Info button on the applications list.

## Aligns with
Local heuristics only (no paid APIs). ROADMAP item 6.

## Entities
Table `applications` as in SPECS/TECH.md, plus:
- `hiring_notes` TEXT optional/nullable — extracted bullet summary of the job posting
- `posting_paste` TEXT optional/nullable — raw pasted hiring-page text (for re-extract on edit)

Existing `database.db` files must gain these columns via `ALTER TABLE` when missing.

## User actions
1. On Add application, optionally paste hiring-page text into “Paste hiring page text (optional)”. On `POST /add`, extract and store `hiring_notes` (and `posting_paste`). Empty paste leaves both empty/NULL.
2. On the applications list, each row has a small **Info** button. Click opens an in-page modal with the extracted summary. If none stored, the button is disabled or the modal explains there is no hiring info yet.
3. On Edit, see the current extracted summary and a textarea for paste/replace. On `POST /edit/<id>`, re-extract from the paste and update stored fields.

## Extraction rules
- Pure Python heuristics (regex / keyword lines). No OpenAI or paid APIs.
- Prefer bullets for: role/title, location/remote, employment type, salary, key requirements, responsibilities, benefits, deadline, other notable lines.
- Strip simple HTML tags if markup is pasted.
- If structure is weak, store a cleaned condensed version (~800–1200 chars of meaningful lines), not a junk dump.

## Expected behavior
- **Add + paste:** Application saved; `hiring_notes` has a readable summary; Info opens the modal with that text.
- **Add + empty paste:** `hiring_notes` empty/NULL; Info disabled or “No hiring info pasted yet.”
- **Edit + new paste:** Summary updates on save.
- **Modal:** Close via X, Escape, or backdrop. Does not break company-name Wikipedia hover.

## Out of scope
Authentication, React, SQLAlchemy, paid LLMs, job-board scrapers, email, export.
