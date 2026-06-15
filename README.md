---
title: GATE Coach Bot
emoji: 🎯
sdk: docker
app_port: 7860
---

# GATE Coach Bot 🎯

A personal Telegram bot that tracks a 6-month GATE CSE preparation roadmap — progress
dashboard, daily Closed-Loop Study Protocol, syllabus status tracking, and bookmarks/revision.
Deterministic (no AI), free to run.

## Resuming work (AI assistants)
Read **[SESSION_STATE.md](SESSION_STATE.md)** first — build tracker, decisions, next task.
Design: [docs/superpowers/specs/2026-06-15-gate-coach-design.md](docs/superpowers/specs/2026-06-15-gate-coach-design.md).

## Commands
`/start` · `/dashboard` · `/today` · `/track` · `/flag <text>` · `/revision` · `/help`

## Stack
Python 3.12 · python-telegram-bot v21 (async, polling) · SQLAlchemy 2 async + Alembic ·
SQLite (local) → Neon Postgres (cloud) · Render · GitHub Actions keepalive.

## Run locally
1. `python -m venv .venv && .venv\Scripts\pip install -e ".[dev]"`
2. Copy `.env.example` → `.env`, fill `TELEGRAM_BOT_TOKEN` + `ALLOWED_TG_USER_IDS`.
3. `.venv\Scripts\alembic upgrade head && .venv\Scripts\python -m app.scripts.seed`
4. `.venv\Scripts\python -m app.main`  (or double-click `run_bot.bat`)
