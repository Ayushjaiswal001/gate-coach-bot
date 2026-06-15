"""Free-text router: currently only consumes an awaited hours value, else a gentle hint."""

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.today import receive_hours
from app.bot.users import ensure_user
from app.db.session import SessionLocal

HINT = (
    "I track your GATE prep — try /today, /dashboard, /track, or /flag &lt;text&gt;. "
    "Send /help for the full list."
)


async def free_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)
        if await receive_hours(update.effective_message, context, session, user):
            return
    await update.effective_message.reply_html(HINT)
