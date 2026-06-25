from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers import field, today, track
from app.bot.users import ensure_user
from app.db.session import SessionLocal


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    parts = (query.data or "").split(":")

    async with SessionLocal() as session:
        user, _ = await ensure_user(session, query.from_user)
        match parts:
            case ["td", "t"]:
                await today.on_toggle(query, session, user, "theory_done")
            case ["td", "p"]:
                await today.on_toggle(query, session, user, "pyq_done")
            case ["td", "a"]:
                await today.on_toggle(query, session, user, "aptitude_done")
            case ["td", "hours"]:
                await today.on_hours_prompt(query, context)
            case ["tk", "root"]:
                await track.on_root(query, session, user)
            case ["tk", "m", month]:
                await track.show_month(query, session, user, int(month))
            case ["tk", "w", month, week]:
                await track.show_week(query, session, user, int(month), int(week))
            case ["tk", "s", row_id, month, week]:
                await track.on_cycle(query, session, user, int(row_id), int(month), int(week))
            case ["field", new_field]:
                await field.on_set_field(query, session, user, new_field)
