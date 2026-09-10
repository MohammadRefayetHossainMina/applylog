# Initial build — plan

Implement and test in this order. Do not add update or delete routes in this slice.

1. **Database init**
   - On Flask startup, connect to `database.db` and `CREATE TABLE IF NOT EXISTS applications (...)` with the TECH.md columns.
   - Confirm with a one-off sqlite3 `.tables` / `PRAGMA table_info` check after first run.

2. **App shell**
   - `app.py` with Flask, `host='0.0.0.0'`, `port=3000`.
   - Helper to get a connection (`row_factory = sqlite3.Row`).

3. **List + form route (`GET /`)**
   - `SELECT` all rows `ORDER BY date_applied DESC, id DESC`.
   - Render `templates/index.html` with the form and the table (or empty state).
   - Minimal CSS file can exist but does not need polish yet.

4. **Add route (`POST /add`)**
   - Read form fields, trim strings, validate constraints from requirements.md.
   - On failure: render index with `error` and submitted values; HTTP 400 is acceptable if the list still loads.
   - On success: `INSERT` parameterized row, then `redirect` to `/` with a flash or query-flag success message.

5. **Manual test**
   - Start `python app.py` (or `python3 app.py`).
   - Add one valid application; confirm it appears.
   - Submit empty company; confirm error and no extra row.
   - Stop the server, start it again, reload `/`; the row is still listed.
