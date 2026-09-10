# ApplyLog Mission

## Purpose
ApplyLog is a single-user web app that gives a job seeker one place to log job applications and keep their status current.

## Intended user
A job seeker who applies to many roles by hand and currently tracks them in emails, tabs, or memory.

## Problem
It is hard to see what was applied to, what is still open, and what moved to interview, offer, or rejected. It is also hard to recall what a company does before an interview.

## What success looks like
The user can add an application, see every application after a server restart, change status and notes as the process moves, delete a mistaken row, and read a short public company summary stored with that row.

## Non-negotiables
- Single user, local use only — no authentication, accounts, or roles.
- Flask + SQLite + vanilla HTML/CSS/JavaScript only.
- One SQLite table (`applications`) is enough.
- Data must survive stopping and restarting the Flask process.
- No third-party job-board APIs, notifications, file uploads, calendar sync, or export.
- **Exception (2026-09-11):** Wikipedia’s public REST summary (and Wikipedia search as a fallback) may be used with no API key solely to fill `company_info`. No other third-party APIs.

## Scope
Build the four core actions: add, view (newest first), update status/notes, delete. Also store a short public company summary on add (and refresh on edit) so the seeker can read it before interviews.
