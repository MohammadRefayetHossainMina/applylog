# ApplyLog

A single-user job application tracker.

**Use the app:** https://mohammadrefayethossainmina.github.io/applylog/

That GitHub Pages site *is* ApplyLog — a static page. Add applications in the browser; they are stored in **localStorage** (GitHub Pages cannot run Flask or SQLite).

The Flask app (`python app.py`) is the course / local SQLite version on `http://127.0.0.1:3000`. Same add / list / edit / delete loop, with records in `database.db`. On first run, if `database.db` is missing, Flask copies committed `demo.db` so you see sample applications; your personal database stays local and is not committed.

## The Problem

Job applications scatter across emails, browser tabs, and memory. It is easy to forget which company you applied to, when you applied, and whether the process moved to interview, offer, or rejection.

## The Solution

Log each application once (company, role, date, status, optional notes), see the full list newest-first, update status and notes as the process changes, and delete a mistaken row. On the Pages app, a short public Wikipedia summary may be stored with the row for a hover tooltip (skipped if the request fails). The Flask version does the same lookup server-side and keeps rows in SQLite so they survive a process restart.

## Main Features

- Add an application with company, role, date applied, status, and optional notes
- View all applications, newest date applied first
- Optional company summary on hover (Wikipedia)
- Update status and notes on an existing row
- Delete a duplicate or mistaken row (with a confirm step)

## Tech Stack & Architecture

**GitHub Pages (the public app)**

- Vanilla HTML, CSS, and JavaScript in `docs/`
- Persistence: `localStorage` in the visitor’s browser

**Local / course version**

- Frontend: vanilla HTML and CSS (plus a confirm dialog for delete)
- Backend: Python and Flask in `app.py` (`0.0.0.0:3000`)
- Database: SQLite file `database.db`

There is no login layer and no ORM.

## Database Design

The Flask version uses one table, `applications`:

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | Unique row id |
| `company` | TEXT NOT NULL | Employer name |
| `role` | TEXT NOT NULL | Job title |
| `date_applied` | TEXT NOT NULL | ISO date `YYYY-MM-DD` |
| `status` | TEXT NOT NULL | `applied`, `interview`, `offer`, or `rejected` |
| `notes` | TEXT | Optional notes |
| `company_info` | TEXT | Optional public company summary |

The Pages app stores the same fields as JSON in `localStorage`.

## What I Learned

The useful work happened before `app.py` existed: picking one problem, writing non-goals, and turning each roadmap item into requirements, a plan, and pass/fail checks. A page that still shows a row after submit is not enough — persistence only counts if the data is still there after a reload (localStorage on Pages, SQLite after stopping Flask locally). Keeping auth, job-board APIs, and export out of scope is what made a complete add/list/update/delete loop possible.

## How to run locally (Flask + SQLite)

```bash
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:3000
