# ApplyLog Roadmap

Implement one item at a time. Specify, implement, and verify before starting the next item.

1. **Initial build** — Create the `applications` table, add an application, list all applications newest `date_applied` first, and persist rows across a server restart.
2. **Update application** — Change status and notes on an existing row.
3. **Delete application** — Remove a mistaken or duplicate row.
4. **UI polish** — CSS and layout only. No new data fields or routes that change behavior beyond clearer labels and messages.
5. **Company info** — Fetch a short public Wikipedia summary for the company name, store it on the row, and show it on the list and edit page. Exception to the original “no third-party APIs” non-goal; job-board scrapers and other APIs stay out of scope.

Hiring-page paste, `hiring_notes` / `posting_paste` extraction, and the list Info modal were specified and then rolled back. They are not part of the product surface.
