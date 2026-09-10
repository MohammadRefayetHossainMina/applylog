# Initial build — requirements

## Feature
Create the SQLite table, let the user add one application, and show every saved application on the home page. Data must still be there after the Flask process is stopped and started again.

## Aligns with
SPECS/MISSION.md: log each application once and see the list. ROADMAP item 1. Does not include update or delete.

## Entities
Table `applications` as defined in SPECS/TECH.md:
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `company` TEXT NOT NULL
- `role` TEXT NOT NULL
- `date_applied` TEXT NOT NULL (`YYYY-MM-DD`)
- `status` TEXT NOT NULL (`applied` | `interview` | `offer` | `rejected`)
- `notes` TEXT optional

## User actions
1. Open `GET /` and see an add form plus a list of existing applications (empty state if none).
2. Submit the form with company, role, date applied, status, and optional notes.
3. After a valid submit, the new row appears in the list without needing a manual refresh beyond the redirect.

## Data constraints
- `company` and `role` required; reject if blank or only whitespace.
- `date_applied` required; must match `YYYY-MM-DD`.
- `status` required; must be one of the four allowed values.
- `notes` optional; store empty string if omitted.
- Invalid submits must not insert a row.

## Expected behavior
- **Success:** POST-redirect-GET to `/`. The list is ordered by `date_applied` descending, then `id` descending. A short confirmation message is shown.
- **Error:** Re-render `/` with an error message. Previously valid rows remain. Form fields can be re-shown with the attempted values.
- **Empty list:** Visible message such as “No applications yet.”
- **Restart:** Rows written to `database.db` remain after stop/start.

## Out of scope
Update, delete, filter, authentication, styling polish.
