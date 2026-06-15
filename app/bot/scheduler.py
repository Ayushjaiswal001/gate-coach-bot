"""Daily reminder via PTB JobQueue. Heartbeat scans users every 30 min; tz-aware; idempotent.

Idempotency uses an in-memory per-(user, date) set — fine for a single-instance personal bot.
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes

from app.db.models import UserProfile
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)
_sent: set[tuple[int, str]] = set()

REMINDER = (
    "🌅 <b>Good morning! Time to close today's loop.</b>\n"
    "🌅 Morning Theory (2h) → 📝 Afternoon PYQ (1.5h) → 🌙 Evening Revision (1h)\n\n"
    "Open today's checklist → /today   ·   See your target → /dashboard"
)


def _tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo("Asia/Kolkata")


async def heartbeat(context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        users = list((await session.execute(select(UserProfile))).scalars())
    for user in users:
        if user.reminder_hour is None:
            continue
        now = datetime.now(_tz(user.timezone))
        key = (user.tg_user_id, now.date().isoformat())
        if now.hour == user.reminder_hour and key not in _sent:
            try:
                await context.bot.send_message(
                    chat_id=user.tg_user_id, text=REMINDER, parse_mode=ParseMode.HTML
                )
                _sent.add(key)
            except Exception:
                logger.warning("reminder failed for %s", user.tg_user_id, exc_info=True)


def register_jobs(app: Application) -> None:
    if app.job_queue is None:  # pragma: no cover
        return
    app.job_queue.run_repeating(heartbeat, interval=1800, first=20, name="heartbeat")
