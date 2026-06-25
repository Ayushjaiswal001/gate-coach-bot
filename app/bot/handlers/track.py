"""/track — drill Month → Subject(week) → Sub-topic; tap a sub-topic to cycle its status."""

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.formatting import esc, send_html
from app.bot.keyboards import months_kb, sub_topics_kb, subjects_kb
from app.bot.users import ensure_user
from app.db.session import SessionLocal
from app.engines import tracker
from app.engines.meta import month_title


async def track_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)
        months = await tracker.months(session, user.field)
    await send_html(
        update.effective_message,
        "📚 <b>Syllabus Tracker</b>\nPick a month:",
        kb=months_kb(months, user.field),
    )


async def show_month(query, session, user, month: int) -> None:
    weeks = await tracker.subjects_in_month(session, user.field, month)
    await query.edit_message_text(
        f"📚 <b>Month {month} — {esc(month_title(user.field, month))}</b>\nPick a week/subject:",
        parse_mode="HTML",
        reply_markup=subjects_kb(month, weeks),
    )


async def show_week(query, session, user, month: int, week: int) -> None:
    rows = await tracker.sub_topics(session, user.id, user.field, month, week)
    subject = rows[0].subject if rows else ""
    body = (
        f"📖 <b>M{month} · W{week}: {esc(subject)}</b>\n"
        "Tap a sub-topic to cycle: ⬜ Not Started → 🔶 In Progress → ✅ Completed"
    )
    await query.edit_message_text(
        body, parse_mode="HTML", reply_markup=sub_topics_kb(month, week, rows)
    )


async def on_root(query, session, user) -> None:
    months = await tracker.months(session, user.field)
    await query.edit_message_text(
        "📚 <b>Syllabus Tracker</b>\nPick a month:",
        parse_mode="HTML",
        reply_markup=months_kb(months, user.field),
    )


async def on_cycle(query, session, user, row_id: int, month: int, week: int) -> None:
    row = await tracker.cycle_status(session, user.id, row_id)
    if row is not None:
        await query.answer(f"{row.sub_topic} → {row.status}")
    await show_week(query, session, user, month, week)
