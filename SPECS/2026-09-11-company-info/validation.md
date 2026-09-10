# Company info — validation

Pass/fail checks.

1. **Column exists on new and old databases**
   - After startup, `PRAGMA table_info(applications)` includes `company_info`.
   - A database created before this feature still opens; the column is added with `ALTER TABLE`, and existing rows have NULL until add/refresh.

2. **Well-known company**
   - Add an application with company `Microsoft` or `Google`.
   - After redirect, the list shows a company-info snippet.
   - `SELECT company_info FROM applications WHERE id = ?` is non-empty public-summary text (not the not-found message).
   - Edit page shows the full stored text.

3. **Nonsense name**
   - Add an application with a nonsense company name.
   - The row is saved (status 302, then listed).
   - `company_info` is the not-found message, or empty with a fetch-error flash if the network failed. The process does not 500.

4. **Fetch failure does not block add**
   - If Wikipedia is unreachable, the application row is still inserted.
   - A flash/error says company info could not be fetched.

5. **Edit still works**
   - Change status and notes on a row; both persist.
   - Correcting the company-info textarea and saving updates SQLite without requiring a new fetch.
   - Refresh company info updates the stored summary when Wikipedia succeeds.

6. **Restart persistence**
   - Stop and start Flask. The same `company_info` values remain in SQLite and in the UI.

7. **SQL safety**
   - All application reads/writes use parameterized placeholders. Company names are only interpolated into Wikipedia URLs after `urllib.parse.quote`.
