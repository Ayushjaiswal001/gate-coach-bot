"""Dashboard math: overall completion, high-priority remaining, current-week target."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import STATUS_COMPLETED, STATUS_NOT_STARTED, SyllabusTracker, UserProfile, UserSyllabusProgress
from app.engines import tracker
from app.engines.meta import TOTAL_WEEKS, month_title


def current_week(profile: UserProfile, today: date | None = None) -> tuple[int, int]:
    """(month, week_in_month) the user should be on, from start_date. Clamped to the roadmap."""
    today = today or date.today()
    elapsed_days = (today - profile.start_date).days
    week_index = max(0, elapsed_days // 7)
    week_index = min(week_index, TOTAL_WEEKS - 1)
    return week_index // 4 + 1, week_index % 4 + 1


async def _count_for_user(
    session: AsyncSession, user_id: int, field: str, is_completed: bool = False, is_hp: bool = None
) -> int:
    stmt = select(func.count(SyllabusTracker.id)).where(SyllabusTracker.field == field.upper())
    if is_hp is not None:
        stmt = stmt.where(SyllabusTracker.is_high_priority == is_hp)
    if is_completed:
        stmt = stmt.join(
            UserSyllabusProgress,
            (UserSyllabusProgress.syllabus_tracker_id == SyllabusTracker.id)
            & (UserSyllabusProgress.user_id == user_id),
        ).where(UserSyllabusProgress.status == STATUS_COMPLETED)
    return (await session.scalar(stmt)) or 0


async def overall(session: AsyncSession, user_id: int, field: str) -> dict:
    total = await _count_for_user(session, user_id, field)
    done = await _count_for_user(session, user_id, field, is_completed=True)
    hp_total = await _count_for_user(session, user_id, field, is_hp=True)
    hp_done = await _count_for_user(session, user_id, field, is_completed=True, is_hp=True)
    pct = round(100 * done / total, 1) if total else 0.0
    return {
        "total": total,
        "done": done,
        "pct": pct,
        "hp_total": hp_total,
        "hp_done": hp_done,
        "hp_left": hp_total - hp_done,
    }


async def week_rows(session: AsyncSession, user_id: int, field: str, month: int, week: int) -> list[SyllabusTracker]:
    return await tracker.sub_topics(session, user_id, field, month, week)


async def dashboard(session: AsyncSession, profile: UserProfile) -> dict:
    o = await overall(session, profile.id, profile.field)
    month, week = current_week(profile)
    rows = await week_rows(session, profile.id, profile.field, month, week)
    subjects = sorted({r.subject for r in rows})
    wk_done = sum(1 for r in rows if r.status == STATUS_COMPLETED)
    return {
        **o,
        "month": month,
        "week": week,
        "month_title": month_title(profile.field, month),
        "current_subjects": subjects,
        "current_topics": [(r.sub_topic, r.status) for r in rows],
        "current_done": wk_done,
        "current_total": len(rows),
    }
