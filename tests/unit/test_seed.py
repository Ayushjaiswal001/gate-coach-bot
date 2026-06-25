from sqlalchemy import func, select

from app.db.models import SyllabusTracker
from app.scripts.seed import load_syllabus, seed

# 6 months; sub-topic counts per month:
# CSE: 15 + 11 + 13 + 12 + 7 + 4 = 62
# ECE: 12 + 12 + 12 + 12 + 10 + 4 = 62
# Combined: 124
EXPECTED_SUBTOPICS = 124


async def test_seed_counts(session):
    n = await seed(session, load_syllabus())
    assert n == EXPECTED_SUBTOPICS
    assert (await session.scalar(select(func.count(SyllabusTracker.id)))) == EXPECTED_SUBTOPICS


async def test_seed_idempotent(session):
    data = load_syllabus()
    await seed(session, data)
    await seed(session, data)
    assert (await session.scalar(select(func.count(SyllabusTracker.id)))) == EXPECTED_SUBTOPICS


async def test_high_priority_flagged(session):
    await seed(session, load_syllabus())
    pointers = await session.scalar(
        select(SyllabusTracker).where(
            SyllabusTracker.field == "CSE",
            SyllabusTracker.sub_topic == "Pointers"
        )
    )
    assert pointers.is_high_priority is True
    assert pointers.month == 1 and pointers.week == 1
    assert pointers.field == "CSE"
