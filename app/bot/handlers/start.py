"""/start and /help."""

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.formatting import esc, send_html
from app.bot.users import ensure_user
from app.db.session import SessionLocal
from app.engines.meta import MONTH_TITLES


def get_strategy(field: str) -> str:
    titles = MONTH_TITLES.get(field.upper(), {})
    return "\n".join(f"  <b>Month {m}</b> — {t}" for m, t in titles.items())


WELCOME = (
    "🎯 <b>Welcome, {name}!</b>\n\n"
    "As a final-year <b>{field}</b> engineer, you already have the fundamentals — now we make them "
    "<b>exam-sharp</b>. I'm your GATE coach for the next 6 months. Here's the high-ROI plan:\n\n"
    "{strategy}\n\n"
    "<b>The daily engine — Closed-Loop Study Protocol:</b>\n"
    "  🌅 Morning Theory (2h) → 📝 Afternoon PYQ (1.5h) → 🌙 Evening Revision/Aptitude (1h)\n\n"
    "<b>Commands</b>\n"
    "/today — today's checklist & log hours\n"
    "/dashboard — progress, current target, high-priority left\n"
    "/track — browse & update syllabus status\n"
    "/field — switch between CSE/ECE fields\n"
    "/flag &lt;text&gt; — bookmark a tough topic/PYQ\n"
    "/revision — your flagged items + short-notes plan\n"
    "/help — this list\n\n"
    "Start now → /today"
)

HELP = (
    "🧭 <b>GATE Coach — commands</b>\n\n"
    "/today — Closed-Loop checklist (3 blocks) + log hours\n"
    "/dashboard — overall %, current week's target, high-priority topics left\n"
    "/track — Month → Subject → Sub-topic; tap to cycle status\n"
    "/field — switch between CSE and ECE fields\n"
    "/flag &lt;text&gt; — instantly bookmark a tough concept or PYQ number\n"
    "/revision — all bookmarks + the Short-Notes Extraction plan\n"
    "/start — re-show the 6-month strategy"
)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)
        strategy = get_strategy(user.field)
        field_name = user.field
    await send_html(
        update.effective_message,
        WELCOME.format(
            name=esc(user.first_name or "engineer"),
            field=esc(field_name),
            strategy=strategy,
        ),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_html(update.effective_message, HELP)
