# Delete application — requirements

## Feature
Remove a mistaken or duplicate application so it no longer appears in the list or in SQLite.

## Aligns with
SPECS/MISSION.md: delete a mistaken row. ROADMAP item 3.

## User actions
1. From the list on `GET /`, choose Delete on a row.
2. Confirm the delete (browser confirm dialog is enough).
3. Submit `POST /delete/<id>`.
4. After success, return to `/`. That row is gone.

## Data constraints
- `id` must exist; unknown id returns 404.
- Delete uses POST only (not GET) so a prefetch cannot remove a row.
- Only the matching row is removed.

## Expected behavior
- **Success:** POST-redirect-GET to `/` with a confirmation message. `SELECT` by that id returns no row.
- **Missing id:** 404 and other rows unchanged.
- **Restart:** A deleted row does not reappear after the server is stopped and started.

## Out of scope
Undo/recycle bin, bulk delete, authentication.
