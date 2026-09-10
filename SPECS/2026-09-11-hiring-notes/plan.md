# Hiring notes — plan

1. **Schema**
   - Add `hiring_notes TEXT` and `posting_paste TEXT` to `CREATE TABLE IF NOT EXISTS applications`.
   - On startup, `PRAGMA table_info` and `ALTER TABLE ... ADD COLUMN` for each missing column (same pattern as `company_info`).

2. **Extraction (`extract_hiring_notes`)**
   - Strip HTML tags, normalize whitespace/lines.
   - Pull lines matching keywords (salary, remote, full-time, requirements, benefits, deadline, etc.).
   - Build a short bullet list; fall back to condensed meaningful lines (~1000 chars) if few keyword hits.
   - Return `None`/empty string when input is empty.

3. **Routes**
   - `POST /add`: read `posting_paste`, extract, insert with `hiring_notes` and `posting_paste`.
   - `POST /edit/<id>`: read paste, re-extract, update alongside status/notes/company_info.
   - SELECT lists include the new columns.

4. **UI**
   - Add form: textarea for paste.
   - Edit page: show current `hiring_notes`; textarea for `posting_paste`.
   - List: Info button per row; shared modal; small JS for open/close (Escape, backdrop, X). Cache-bust CSS/JS.

5. **Docs**
   - SPECS feature folder; short notes in TECH.md and ROADMAP.md.
