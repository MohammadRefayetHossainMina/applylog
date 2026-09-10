# Update application — requirements

## Feature
Change the status and notes of an existing application. Company, role, and date applied stay as recorded.

## Aligns with
SPECS/MISSION.md: update status as the process changes. ROADMAP item 2.

## User actions
1. From the list on `GET /`, choose Edit on a row.
2. On `GET /edit/<id>`, see company, role, and date applied (read-only) plus editable status and notes.
3. Submit `POST /edit/<id>` to save status and notes.
4. After success, return to `/` and see the updated status and notes on that row.

## Data constraints
- `id` must exist; unknown id returns 404.
- `status` must be one of: `applied`, `interview`, `offer`, `rejected`.
- `notes` optional; empty is allowed.
- Company, role, and date_applied are not changed by this feature.
- Invalid status must not update the row.

## Expected behavior
- **Success:** POST-redirect-GET to `/` with a confirmation message. The row keeps the same `id`.
- **Error:** Re-render the edit page with an error message; SQLite still has the previous status and notes.
- **Restart:** Updated values remain after the server is stopped and started.

## Out of scope
Delete, filter, authentication, new columns.
