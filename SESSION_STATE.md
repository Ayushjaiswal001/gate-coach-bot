# SESSION_STATE.md — GATE Coach Bot (continuity & build tracker)

> **Resume protocol:** Read this file first. Do the next unchecked task. Update status + check
> off before ending a session. Append, don't rewrite. Design spec:
> `docs/superpowers/specs/2026-06-15-gate-coach-design.md`.

## Status
- **Phase:** `CODE COMPLETE ✅ (M0–M2) — local-verified. Awaiting Ayush: BotFather token + Neon + Render deploy.`
- **Last updated:** 2026-06-15 (full bot built: 7 commands, engines, scheduler, deploy files. 8/8 tests, ruff clean, migration cad789423a98 applied, seed=62 sub-topics. Not yet deployed — needs a NEW @BotFather bot + Neon DB.)
- **Next action (Ayush):** (1) @BotFather → /newbot → token; (2) new Neon project → connection string; (3) `.env` from `.env.example`; (4) GitHub repo + Render (render.yaml blueprint) + set TELEGRAM_BOT_TOKEN/ALLOWED_TG_USER_IDS/DATABASE_URL secrets; (5) set keepalive RENDER_URL. Then verify with 409 getUpdates probe + live test.
- **Dev:** test `.venv\Scripts\python -m pytest -q` · lint `.venv\Scripts\ruff check .` · run `run_bot.bat` · seed `.venv\Scripts\python -m app.scripts.seed`

## Key facts
- Personal GATE tracker bot for Ayush (final-year CSE, GATE in ~6 months). **No LLM** — pure tracker.
- Stack copied from `D:\ai-mentor-bot` patterns: PTB v21 async, SQLAlchemy async, single-loop
  entrypoint + FastAPI health server, Render+Neon, GitHub-Actions keepalive, allowlist.
- **HF Spaces blocks Telegram → use Render.** Render free has no persistent disk → Neon Postgres
  for cloud data; SQLite only for local dev. (Same lessons as the mentor bot.)
- Deploy = `git push origin main` → Render auto-deploy; verify with getUpdates 409 conflict probe.

## Build tracker
### M0 — scaffold ✅
- [x] pyproject, ruff, .env.example, .gitignore, git init
- [x] config.py (DB-agnostic URL normalize), app package
- [x] SQLAlchemy models (4 tables) + Alembic migration cad789423a98
- [x] content/syllabus.yaml (exact 6-month roadmap) + idempotent seeder (62 sub-topics)
- [x] pytest skeleton + CI

### M1 — commands & engines ✅
- [x] engines: progress (dashboard math, current-week from start_date), tracker (cycle status), logs (toggle/hours), bookmarks
- [x] bot bootstrap (polling, allowlist, error boundary) + formatting/keyboards/users
- [x] /start, /help
- [x] /dashboard (overall %, current-week target, HP left, progress bar)
- [x] /today (3 checkbox toggles via inline kb + hours input via free-text)
- [x] /track (Month→week/Subject→Sub-topic→cycle status, inline drill-down)
- [x] /flag, /revision (bookmarks + short-notes plan)
- [x] 8/8 tests (seeder counts/idempotency/HP flag; current-week math; overall+completion; dashboard; daily-log toggle+hours; bookmarks)

### M2 — schedule & deploy
- [x] JobQueue daily reminder (tz-aware, idempotent, configurable hour)
- [x] Dockerfile + render.yaml + health server + keepalive workflow + run_bot.bat
- [ ] deploy to Render+Neon (NEEDS Ayush: new bot token + Neon); verify polling; live test

## Decisions log
| # | Decision | Why |
|---|---|---|
| 1 | Reuse ai-mentor-bot stack/patterns | Proven, fast, Ayush knows the deploy flow |
| 2 | SQLAlchemy (not raw aiosqlite) | DB-agnostic: SQLite local + Neon cloud; survives Render restarts |
| 3 | No LLM | Spec is a deterministic tracker; keeps it free + simple |
| 4 | Daily reminder included | Core to a "daily planner"; trivial via JobQueue |
| 5 | One syllabus_tracker row per sub-topic | Granular status tracking per spec schema |

## Open questions
- Telegram bot token for THIS bot (separate @BotFather bot from @trainmemybot) — needed for deploy/test.
- Reuse same Neon project (new DB/branch) or a fresh Neon project? (default: new Neon project, clean separation)

## Notes
- (none yet)
