# Delete application — plan

1. **Delete route (`POST /delete/<int:id>`)**
   - `SELECT` the row; 404 if missing.
   - Parameterized `DELETE FROM applications WHERE id = ?`.
   - Redirect to `/` with a flash message.

2. **List control**
   - Add a POST form with a Delete button on each row.
   - `onsubmit` confirm: “Delete this application?”

3. **Test**
   - Add or pick a known id, delete it, confirm it is absent from `/` and from SQLite.
   - POST `/delete/99999` returns 404.
   - Other rows remain.
