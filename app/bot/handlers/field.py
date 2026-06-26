"""/field command to switch between CSE and ECE."""

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.formatting import send_html
from app.bot.keyboards import field_kb
from app.bot.users import ensure_user
from app.db.session import SessionLocal


async def field_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)

    body = (
        "🎓 <b>GATE Field Selection</b>\n\n"
        f"Your current field: <b>{user.field}</b>\n\n"
        "Select a field to study:"
    )
    await send_html(update.effective_message, body, kb=field_kb())


async def on_set_field(query, session, user, new_field: str) -> None:
    field_upper = new_field.upper()
    user.field = field_upper
    await session.commit()

    await query.answer(f"Field updated to {field_upper}!")

    body = (
        f"✅ <b>Field updated!</b>\n\n"
        f"You are now tracking the <b>{field_upper}</b> syllabus.\n\n"
        "Use /dashboard or /track to proceed!"
    )
    await query.edit_message_text(body, parse_mode="HTML")
