# Update application — plan

1. **Edit form route (`GET /edit/<int:id>`)**
   - `SELECT` the row by id.
   - 404 if missing.
   - Render `templates/edit.html` with read-only company/role/date and a form for status and notes.

2. **Save route (`POST /edit/<int:id>`)**
   - 404 if id missing.
   - Validate status against the allowed set; trim notes.
   - On failure: re-render edit template with error; do not UPDATE.
   - On success: parameterized `UPDATE applications SET status = ?, notes = ? WHERE id = ?`, then redirect to `/` with a flash message.

3. **List link**
   - Add an Edit link on each row in `templates/index.html` pointing at `/edit/<id>`.

4. **Test**
   - Open edit for an existing id; submit a new status and notes; confirm list and SQLite.
   - POST invalid status; confirm row unchanged.
   - Request `/edit/99999` and expect 404.
