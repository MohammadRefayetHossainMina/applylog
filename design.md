# Project Brainstorming

## Idea 1
- **Problem:** Job applications live in emails, browser tabs, and memory. It is easy to forget which company you applied to, when you applied, and whether the process moved to interview, offer, or rejection.
- **Who experiences this:** A job seeker (student or career changer) sending many applications by hand.
- **Why it matters:** Without a single list, follow-ups get missed and the same role gets applied to twice — or never followed up at all.

## Idea 2
- **Problem:** Groceries and leftovers sit in the fridge with no record of when they were bought or when they expire, so food is thrown away.
- **Who experiences this:** A household cook who shops weekly and loses track of what is still edible.
- **Why it matters:** A short log of items and expiry dates would cut waste and last-minute grocery runs.

## Idea 3
- **Problem:** Class assignments, due dates, and completion status are scattered across LMS pages, chat messages, and paper notes.
- **Who experiences this:** A student juggling several courses in the same week.
- **Why it matters:** One list of tasks with due dates makes it obvious what is next and what is already done.

## Selected Project
- **App Name:** ApplyLog
- **Target User:** A job seeker tracking many applications by hand
- **Core Problem:** It is hard to see what was applied to, what is still open, and what moved to interview, offer, or rejected.
- **Purpose:** Log each application once and update its status as the process changes.

## Core Requirements
1. Users can add a job application with company, role, date applied, status, and optional notes.
2. Users can view all saved applications, newest date applied first.
3. Users can update an application’s status and notes.
4. Users can delete a mistaken or duplicate application.

Status values are a fixed set: `applied`, `interview`, `offer`, `rejected`.

## Non-Goals
- No user registration or login system (single-user local application)
- No email, SMS, or push notifications
- No LinkedIn, Indeed, or other third-party API integrations
- No resume uploads or file attachments
- No calendar sync
- No React, Vue, SQLAlchemy, or cloud databases
- No PDF/CSV export
- No native mobile app

## Database Questions
1. **Add an application:** What company, role, date applied, status, and notes should be stored for a new row?
2. **View all applications:** What applications exist, ordered by date applied descending (newest first)?
3. **Update status and notes:** What is the current status and notes for application id N, and what should they become?
4. **Delete an application:** Which row (by id) should be removed so it no longer appears in the list?

## Schema

Table: applications
- id: INTEGER PRIMARY KEY AUTOINCREMENT  # unique row id
- company: TEXT NOT NULL                 # employer name
- role: TEXT NOT NULL                    # job title
- date_applied: TEXT NOT NULL            # ISO date YYYY-MM-DD
- status: TEXT NOT NULL                  # applied | interview | offer | rejected
- notes: TEXT                            # optional free-text notes
