# ApplyLog

A single-user job application tracker.

- **Project page (GitHub Pages):** https://mohammadrefayethossainmina.github.io/applylog/
- **Live demo (Render):** https://applylog.onrender.com

> Free Render instances sleep when idle and may take a minute to wake. SQLite data on
> the free tier can reset when the service restarts or redeploys — fine for a portfolio
> demo; use local mode for lasting records.

## The Problem

Job applications scatter across emails, browser tabs, and memory. It is easy to forget which company you applied to, when you applied, and whether the process moved to interview, offer, or rejection.

## The Solution

ApplyLog is a small Flask + SQLite web app. You log each application once (company, role, date, status, optional notes), see the full list newest-first, update status as the process changes, and delete a mistaken row. On add (and on refresh from the edit page), it stores a short public company summary from Wikipedia so you can read it before interviews. Records are stored on disk, so they survive a server restart.

## Main Features

- Add an application with company, role, date applied, status, and optional notes
- Optionally paste hiring-page text; store an extracted posting summary
- View all applications, newest date applied first
- Open hiring info from an Info button on each row
- Store a short public company summary (Wikipedia) on the row
- Update status, notes, company info, and hiring paste on an existing row
- Delete a duplicate or mistaken row (with a confirm step)

## Tech Stack & Architecture

- **Frontend:** vanilla HTML and CSS (plus a confirm dialog for delete)
- **Backend:** Python and Flask in `app.py` (`0.0.0.0:3000`)
- **Database:** SQLite file `database.db`

The browser posts a form to Flask. Flask validates the input, runs a parameterized SQL statement, then renders the updated list from SQLite. There is no login layer and no ORM.

## Database Design

One table, `applications`:

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | Unique row id |
| `company` | TEXT NOT NULL | Employer name |
| `role` | TEXT NOT NULL | Job title |
| `date_applied` | TEXT NOT NULL | ISO date `YYYY-MM-DD` |
| `status` | TEXT NOT NULL | `applied`, `interview`, `offer`, or `rejected` |
| `notes` | TEXT | Optional notes |
| `company_info` | TEXT | Optional public company summary |
| `hiring_notes` | TEXT | Optional extracted job-posting summary |
| `posting_paste` | TEXT | Optional raw pasted hiring-page text |

This answers: what did I apply to and when, what is the status of application *N*, what does that company do, and which row should be updated or deleted.

## What I Learned

The useful work happened before `app.py` existed: picking one problem, writing non-goals, and turning each roadmap item into requirements, a plan, and pass/fail checks. A page that still shows a row after submit is not enough — persistence only counts if SQLite still has the row after the process is gone. Keeping auth, job-board APIs, and export out of scope is what made a complete add/list/update/delete loop possible.

## How to run

```bash
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:3000

## Deploy (Render)

The repo includes `render.yaml`, a `Procfile`, and `gunicorn` in `requirements.txt`.

1. Open [Deploy to Render](https://render.com/deploy?repo=https://github.com/MohammadRefayetHossainMina/applylog), or in the Render dashboard choose **New → Blueprint** and connect this repository.
2. Apply the Blueprint (free web service named `applylog`).
3. After the build finishes, open `https://applylog.onrender.com` (or the URL Render shows).

Production start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
