# Hiring notes — validation

1. **Migration**
   - After startup, `PRAGMA table_info(applications)` includes `hiring_notes` and `posting_paste`.
   - A database created before this feature still opens; columns are added with `ALTER TABLE`.

2. **Add with paste**
   - Paste a sample job posting on Add → Save.
   - `SELECT hiring_notes, posting_paste FROM applications WHERE id = ?` shows non-empty paste and a bullet-style summary.
   - List Info button is enabled; modal shows the summary with left-aligned readable text.

3. **Add without paste**
   - Save with empty paste field.
   - `hiring_notes` is NULL/empty; Info is disabled or shows “No hiring info pasted yet.”

4. **Edit**
   - Change the paste on Edit → Save; `hiring_notes` updates to match the new extract.
   - Clearing the paste and saving clears stored hiring info (or leaves a clear empty state).

5. **Modal UX**
   - Close works via X, Escape, and backdrop click.
   - Company-name Wikipedia hover tooltip still works.

6. **Persistence**
   - Restart Flask; stored hiring notes remain and Info still opens them.
