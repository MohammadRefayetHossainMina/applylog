# Initial build — UI polish

Layout and CSS only. No new tables, columns, or routes.

## Requirements
- Home and edit pages share a readable layout: header, cards, spaced form fields, and a clear table.
- Status values are visually distinct (applied, interview, offer, rejected) without changing stored values.
- Labels and empty-state copy stay specific: “No applications yet.”
- Delete remains a POST with confirm; Edit remains a link.

## Validation
- All previous feature validation still passes.
- `/` and `/edit/<id>` load with the stylesheet applied.
