# Company info — plan

1. **Schema**
   - Add `company_info TEXT` to `CREATE TABLE IF NOT EXISTS applications`.
   - On startup, `PRAGMA table_info(applications)` and `ALTER TABLE ... ADD COLUMN company_info TEXT` if the column is missing.

2. **Lookup helper**
   - `urllib` GET Wikipedia REST summary with User-Agent and a ~7s overall deadline.
   - On 404, OpenSearch then summary for the top title.
   - Return extract (truncated), a not-found message, or `(None, failed)` on network error. Never raise into the request handler.

3. **Routes**
   - `POST /add`: fetch then `INSERT` including `company_info`. Always insert after validation even if fetch fails.
   - `POST /edit/<id>`: also save `company_info` from the textarea (no fetch unless refresh).
   - `POST /edit/<id>/refresh-company-info`: fetch for the stored company name; update only that column on success.

4. **UI**
   - Home table: Company info column with a truncated snippet.
   - Edit page: readable block, refresh button, optional textarea. Keep Inter / Source Serif; body 16px / 1.55 leading; charcoal; measure not full-bleed.

5. **Verify**
   - Add a well-known company; confirm UI + SQLite.
   - Add a nonsense name; confirm not-found or empty without a crash.
   - Edit still updates status and notes.
