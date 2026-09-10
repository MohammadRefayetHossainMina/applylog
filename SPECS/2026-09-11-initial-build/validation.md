# Initial build — validation

Pass/fail checks. Every item must be unambiguous.

1. **Table exists**
   - After starting the app once, `database.db` contains table `applications` with columns `id`, `company`, `role`, `date_applied`, `status`, `notes`.

2. **Add appears in UI**
   - Submit a valid form (company, role, date, status, optional notes).
   - After redirect, that company and role are visible in the list.

3. **Newest first**
   - Add two applications with different `date_applied` values.
   - The later date appears above the earlier date.

4. **Restart persistence**
   - Add a record via the form.
   - Stop the Flask process completely.
   - Start it again and reload `/`.
   - The same record is still in the UI and in `SELECT * FROM applications`.

5. **Invalid data is rejected**
   - Submit with company blank (or status missing / invalid date).
   - An error message is shown.
   - Row count in SQLite does not increase.

6. **Empty state**
   - With an empty table, `/` shows a “No applications yet” (or equivalent) message and still shows the add form.

7. **No update/delete yet**
   - There is no working edit or delete control required for this slice to pass.
