"""Syllabus browsing + status transitions for /track."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import STATUS_CYCLE, STATUS_NOT_STARTED, SyllabusTracker


async def months(session: AsyncSession) -> list[int]:
    rows = await session.execute(
        select(SyllabusTracker.month).distinct().order_by(SyllabusTracker.month)
    )
    return [m for (m,) in rows.all()]


async def subjects_in_month(session: AsyncSession, month: int) -> list[tuple[int, str]]:
    """Distinct (week, subject) within a month, in order."""
    rows = await session.execute(
        select(SyllabusTracker.week, SyllabusTracker.subject)
        .where(SyllabusTracker.month == month)
        .distinct()
        .order_by(SyllabusTracker.week)
    )
    seen: list[tuple[int, str]] = []
    for week, subject in rows.all():
        if (week, subject) not in seen:
            seen.append((week, subject))
    return seen


async def sub_topics(session: AsyncSession, month: int, week: int) -> list[SyllabusTracker]:
    rows = await session.execute(
        select(SyllabusTracker)
        .where(SyllabusTracker.month == month, SyllabusTracker.week == week)
        .order_by(SyllabusTracker.sort_order)
    )
    return list(rows.scalars())


async def cycle_status(session: AsyncSession, row_id: int) -> SyllabusTracker | None:
    """Advance a sub-topic's status: Not Started → In Progress → Completed → (wraps)."""
    row = await session.get(SyllabusTracker, row_id)
    if row is None:
        return None
    cur = row.status if row.status in STATUS_CYCLE else STATUS_NOT_STARTED
    row.status = STATUS_CYCLE[(STATUS_CYCLE.index(cur) + 1) % len(STATUS_CYCLE)]
    await session.commit()
    return row
