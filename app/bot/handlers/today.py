"""/today — Closed-Loop Study Protocol checklist + hours logging."""

from telegram import Message, Update
from telegram.ext import ContextTypes

from app.bot.formatting import send_html
from app.bot.keyboards import today_kb
from app.bot.users import ensure_user
from app.db.models import DailyLog
from app.db.session import SessionLocal
from app.engines import logs

AWAIT_HOURS_KEY = "await_hours"


def _text(log: DailyLog) -> str:
    done = logs.blocks_done(log)
    return (
        "🗓 <b>Today's Closed-Loop Protocol</b>\n\n"
        "Tap to check off each block as you finish it:\n"
        "  🌅 <b>Morning Theory</b> — 2 hours\n"
        "  📝 <b>Afternoon PYQ</b> — 1.5 hours\n"
        "  🌙 <b>Evening Revision/Aptitude</b> — 1 hour\n\n"
        f"Blocks done: <b>{done}/3</b> · Hours logged: <b>{log.hours_studied:g}h</b>"
        + ("\n\n🎉 Full loop closed today — great work!" if done == 3 else "")
    )


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)
        log = await logs.get_or_create(session, user.id)
    await send_html(update.effective_message, _text(log), kb=today_kb(log))


async def on_toggle(query, session, user, field: str) -> None:
    log = await logs.get_or_create(session, user.id)
    await logs.toggle_block(session, log, field)
    await query.edit_message_text(_text(log), parse_mode="HTML", reply_markup=today_kb(log))


async def on_hours_prompt(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[AWAIT_HOURS_KEY] = True
    await query.message.reply_html(
        "✍️ How many hours did you study today? Send a number (e.g. <code>4.5</code>)."
    )


async def receive_hours(
    message: Message, context: ContextTypes.DEFAULT_TYPE, session, user
) -> bool:
    """If awaiting an hours value, parse and store it. Returns True if handled."""
    if not context.user_data.get(AWAIT_HOURS_KEY):
        return False
    raw = (message.text or "").strip().replace("h", "")
    try:
        hours = float(raw)
    except ValueError:
        await message.reply_html("That doesn't look like a number. Try e.g. <code>4.5</code>.")
        return True
    context.user_data.pop(AWAIT_HOURS_KEY, None)
    log = await logs.get_or_create(session, user.id)
    await logs.set_hours(session, log, hours)
    await send_html(
        message, f"✅ Logged <b>{log.hours_studied:g}h</b> for today.", kb=today_kb(log)
    )
    return True
