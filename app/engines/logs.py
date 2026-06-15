"""Daily Closed-Loop Study Protocol logs: get-or-create, toggle blocks, set hours."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DailyLog

BLOCKS = ("theory_done", "pyq_done", "aptitude_done")


async def get_or_create(session: AsyncSession, user_id: int, day: date | None = None) -> DailyLog:
    day = day or date.today()
    log = await session.scalar(
        select(DailyLog).where(DailyLog.user_id == user_id, DailyLog.date == day)
    )
    if log is None:
        log = DailyLog(user_id=user_id, date=day)
        session.add(log)
        await session.commit()
    return log


async def toggle_block(session: AsyncSession, log: DailyLog, field: str) -> DailyLog:
    if field not in BLOCKS:
        raise ValueError(f"unknown block: {field}")
    setattr(log, field, not getattr(log, field))
    await session.commit()
    return log


async def set_hours(session: AsyncSession, log: DailyLog, hours: float) -> DailyLog:
    log.hours_studied = max(0.0, round(hours, 2))
    await session.commit()
    return log


def blocks_done(log: DailyLog) -> int:
    return sum(1 for f in BLOCKS if getattr(log, f))
