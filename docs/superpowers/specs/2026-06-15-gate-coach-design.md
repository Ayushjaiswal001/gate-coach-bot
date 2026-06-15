# GATE Coach Bot — Design Spec (2026-06-15)

A personal Telegram bot that tracks a final-year CSE student's 6-month GATE preparation
against a fixed high-ROI roadmap: progress dashboard, daily study protocol, syllabus
status tracking, and a bookmark/revision system. **Deterministic — no AI/LLM.**

## Decisions (approved)
- Stack mirrors the proven `ai-mentor-bot`: python-telegram-bot v21 (async), SQLAlchemy 2
  async + Alembic, single asyncio loop running bot + FastAPI `/healthz`. Modular package.
- **DB-agnostic** (SQLAlchemy): SQLite file locally, Neon Postgres in cloud. Honors the
  `aiosqlite` intent for dev while surviving Render restarts (Render free has no persistent disk).
- Host: Render + Neon + GitHub-Actions keepalive (Hugging Face blocks Telegram — ruled out).
- Personal bot: allowlisted to owner's Telegram ID (schema is per-user, so multi-user-capable).
- Daily reminder included (core to a "daily planner"); configurable hour, off-switchable.

## Data model (SQLAlchemy)
- `user_profile`: id, tg_user_id (unique), daily_hours_goal (float, default 4.5),
  start_date (date), timezone, reminder_hour (int|null), created_at.
- `syllabus_tracker`: id, month (int), week (int), subject, sub_topic, status
  (Not Started|In Progress|Completed), is_high_priority (bool). One row per sub-topic.
- `daily_logs`: id, user_id, date, theory_done (bool), pyq_done (bool), aptitude_done (bool),
  hours_studied (float). Unique (user_id, date).
- `bookmarks`: id, user_id, text, created_at.

## Syllabus seed (`content/syllabus.yaml`)
The exact 6-month micro-timeline (Months 1–6 → weeks → subject → sub-topics, with
high-priority flags), loaded by an idempotent seeder. Each sub-topic becomes one tracker row.

## Commands & UX (inline keyboards + callback routing)
- `/start` — welcome (recognizes CSE background), init user_profile, print 6-month strategy.
- `/dashboard` — overall % complete, current week's target, high-priority topics remaining.
- `/today` — Closed-Loop Study Protocol: 3 tappable checkboxes (Morning Theory 2h /
  Afternoon PYQ 1.5h / Evening Revision-Aptitude 1h) + hours-studied input (conversation step).
- `/track` — inline drill-down Month → Subject → Sub-topic → cycle status.
- `/flag <text>` — instant bookmark of a tough concept/PYQ.
- `/revision` — list bookmarks + show Month 5 Week 4 "Short Notes Extraction" instructions.
- `/help` — command reference.

## Engines (testable, no Telegram/network)
- `progress`: overall %, current-week target (from start_date + elapsed), high-priority-left.
- `tracker`: syllabus browse + status transitions.
- `logs`: daily-log get-or-create, toggle blocks, set hours, streak.
- `bookmarks`: add/list.

## Scheduler
PTB JobQueue heartbeat (every 30 min): per-user daily reminder at reminder_hour (tz-aware),
idempotent via a daily marker; nudges with the day's `/today` summary.

## Hosting & ops
Render (Docker, polling) + Neon Postgres; GitHub-Actions keepalive ping on `/healthz` every
10 min; allowlist auth; secrets via env. Local fallback: `run_bot.bat`.

## Testing
pytest + SQLite test DB (no network): progress math, current-week computation, status
transitions, daily-log toggles + hours, bookmark add/list, seeder counts.

## Non-goals (v1)
No AI/LLM, no PYQ content/question bank, no analytics charts, no multi-user onboarding,
no payment. (Possible later: mock-score logging table, weekly review, CSV export.)
