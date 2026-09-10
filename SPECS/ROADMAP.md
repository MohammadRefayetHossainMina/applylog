# ApplyLog Roadmap

Implement one item at a time. Specify, implement, and verify before starting the next item.

1. **Initial build** — Create the `applications` table, add an application, list all applications newest `date_applied` first, and persist rows across a server restart.
2. **Update application** — Change status and notes on an existing row.
3. **Delete application** — Remove a mistaken or duplicate row.
4. **UI polish** — CSS and layout only. No new data fields or routes that change behavior beyond clearer labels and messages.
5. **Company info** — Fetch a short public Wikipedia summary for the company name, store it on the row, and show it on the list and edit page. Exception to the original “no third-party APIs” non-goal; job-board scrapers and other APIs stay out of scope.
6. **Hiring notes** — Paste hiring-page text on add/edit, extract a local heuristic summary into `hiring_notes` (raw paste in `posting_paste`), and open it from an Info button modal on each list row.
