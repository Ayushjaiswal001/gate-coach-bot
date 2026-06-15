"""Dashboard math: overall completion, high-priority remaining, current-week target."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import STATUS_COMPLETED, SyllabusTracker, UserProfile
from app.engines.meta import TOTAL_WEEKS, month_title


def current_week(profile: UserProfile, today: date | None = None) -> tuple[int, int]:
    """(month, week_in_month) the user should be on, from start_date. Clamped to the roadmap."""
    today = today or date.today()
    elapsed_days = (today - profile.start_date).days
    week_index = max(0, elapsed_days // 7)
    week_index = min(week_index, TOTAL_WEEKS - 1)
    return week_index // 4 + 1, week_index % 4 + 1


async def _count(session: AsyncSession, *conds) -> int:
    return (await session.scalar(select(func.count(SyllabusTracker.id)).where(*conds))) or 0


async def overall(session: AsyncSession) -> dict:
    total = await _count(session)
    done = await _count(session, SyllabusTracker.status == STATUS_COMPLETED)
    hp_total = await _count(session, SyllabusTracker.is_high_priority.is_(True))
    hp_done = await _count(
        session,
        SyllabusTracker.is_high_priority.is_(True),
        SyllabusTracker.status == STATUS_COMPLETED,
    )
    pct = round(100 * done / total, 1) if total else 0.0
    return {
        "total": total,
        "done": done,
        "pct": pct,
        "hp_total": hp_total,
        "hp_done": hp_done,
        "hp_left": hp_total - hp_done,
    }


async def week_rows(session: AsyncSession, month: int, week: int) -> list[SyllabusTracker]:
    rows = await session.execute(
        select(SyllabusTracker)
        .where(SyllabusTracker.month == month, SyllabusTracker.week == week)
        .order_by(SyllabusTracker.sort_order)
    )
    return list(rows.scalars())


async def dashboard(session: AsyncSession, profile: UserProfile) -> dict:
    o = await overall(session)
    month, week = current_week(profile)
    rows = await week_rows(session, month, week)
    subjects = sorted({r.subject for r in rows})
    wk_done = sum(1 for r in rows if r.status == STATUS_COMPLETED)
    return {
        **o,
        "month": month,
        "week": week,
        "month_title": month_title(month),
        "current_subjects": subjects,
        "current_topics": [(r.sub_topic, r.status) for r in rows],
        "current_done": wk_done,
        "current_total": len(rows),
    }
