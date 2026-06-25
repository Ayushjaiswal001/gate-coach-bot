"""Syllabus browsing + status transitions for /track."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import STATUS_CYCLE, STATUS_NOT_STARTED, SyllabusTracker, UserSyllabusProgress


async def months(session: AsyncSession, field: str) -> list[int]:
    rows = await session.execute(
        select(SyllabusTracker.month)
        .where(SyllabusTracker.field == field.upper())
        .distinct()
        .order_by(SyllabusTracker.month)
    )
    return [m for (m,) in rows.all()]


async def subjects_in_month(session: AsyncSession, field: str, month: int) -> list[tuple[int, str]]:
    """Distinct (week, subject) within a month, in order."""
    rows = await session.execute(
        select(SyllabusTracker.week, SyllabusTracker.subject)
        .where(SyllabusTracker.field == field.upper(), SyllabusTracker.month == month)
        .distinct()
        .order_by(SyllabusTracker.week)
    )
    seen: list[tuple[int, str]] = []
    for week, subject in rows.all():
        if (week, subject) not in seen:
            seen.append((week, subject))
    return seen


async def sub_topics(session: AsyncSession, user_id: int, field: str, month: int, week: int) -> list[SyllabusTracker]:
    stmt = (
        select(SyllabusTracker, UserSyllabusProgress.status)
        .outerjoin(
            UserSyllabusProgress,
            (UserSyllabusProgress.syllabus_tracker_id == SyllabusTracker.id)
            & (UserSyllabusProgress.user_id == user_id),
        )
        .where(
            SyllabusTracker.field == field.upper(),
            SyllabusTracker.month == month,
            SyllabusTracker.week == week,
        )
        .order_by(SyllabusTracker.sort_order)
    )
    rows = await session.execute(stmt)
    result = []
    for tracker_row, status in rows.all():
        tracker_row.status = status or STATUS_NOT_STARTED
        result.append(tracker_row)
    return result


async def cycle_status(session: AsyncSession, user_id: int, row_id: int) -> SyllabusTracker | None:
    """Advance a sub-topic's status: Not Started → In Progress → Completed → (wraps)."""
    tracker_row = await session.get(SyllabusTracker, row_id)
    if tracker_row is None:
        return None

    # Get or create the progress record
    stmt = select(UserSyllabusProgress).where(
        UserSyllabusProgress.user_id == user_id,
        UserSyllabusProgress.syllabus_tracker_id == row_id
    )
    progress = await session.scalar(stmt)
    if progress is None:
        progress = UserSyllabusProgress(user_id=user_id, syllabus_tracker_id=row_id, status=STATUS_NOT_STARTED)
        session.add(progress)

    cur = progress.status if progress.status in STATUS_CYCLE else STATUS_NOT_STARTED
    next_status = STATUS_CYCLE[(STATUS_CYCLE.index(cur) + 1) % len(STATUS_CYCLE)]
    progress.status = next_status
    await session.commit()

    tracker_row.status = next_status
    return tracker_row
