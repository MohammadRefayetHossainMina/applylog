# Delete application — validation

1. **Delete removes from UI**
   - Delete an existing row from the list.
   - After redirect, that company/role is no longer in the table (or the empty state appears if it was the last row).

2. **Delete removes from SQLite**
   - `SELECT * FROM applications WHERE id = ?` returns no row for the deleted id.

3. **Other rows remain**
   - A different id that was not deleted is still present.

4. **Missing id**
   - `POST /delete/99999` returns 404.

5. **Restart persistence**
   - After delete, a new SQLite connection (or server restart) still does not show the deleted row.

6. **GET does not delete**
   - `GET /delete/<id>` is not a working delete (404 or method not allowed). The row remains.
