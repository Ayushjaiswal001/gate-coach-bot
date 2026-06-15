"""/dashboard — overall progress, current-week target, high-priority remaining."""

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.formatting import esc, send_html
from app.bot.keyboards import STATUS_ICON
from app.bot.users import ensure_user
from app.db.session import SessionLocal
from app.engines import progress


def _bar(pct: float, width: int = 10) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


async def dashboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)
        d = await progress.dashboard(session, user)

    lines = [
        "📊 <b>GATE Dashboard</b>\n",
        f"Overall: <b>{d['pct']:g}%</b>  {_bar(d['pct'])}",
        f"Topics done: <b>{d['done']}/{d['total']}</b>",
        f"🔥 High-priority left: <b>{d['hp_left']}/{d['hp_total']}</b>",
        "",
        f"🎯 <b>This week</b> — M{d['month']} ({esc(d['month_title'])}) · Week {d['week']}",
        f"   {esc(', '.join(d['current_subjects']))}",
        f"   Week progress: <b>{d['current_done']}/{d['current_total']}</b>",
    ]
    for sub, status in d["current_topics"]:
        lines.append(f"   {STATUS_ICON.get(status, '⬜')} {esc(sub)}")
    lines.append("\nUpdate status → /track   ·   Log today → /today")
    await send_html(update.effective_message, "\n".join(lines))
