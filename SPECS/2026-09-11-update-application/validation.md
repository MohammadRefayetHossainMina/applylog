# Update application — validation

1. **Edit page loads**
   - For an existing id, `GET /edit/<id>` shows that row’s company, role, date applied, status, and notes.

2. **Update appears in UI**
   - Change status (e.g. applied → interview) and notes, submit.
   - After redirect, the list shows the new status and notes for the same company/role.

3. **SQLite matches UI**
   - `SELECT status, notes FROM applications WHERE id = ?` matches the submitted values.

4. **Invalid status rejected**
   - POST a status that is not applied/interview/offer/rejected.
   - Error is shown.
   - The stored status is unchanged.

5. **Missing id**
   - `GET /edit/99999` (unused id) returns 404.

6. **Restart persistence**
   - After a successful update, stop and start the server (or open a new SQLite connection after the request finishes).
   - The updated status and notes are still stored.
