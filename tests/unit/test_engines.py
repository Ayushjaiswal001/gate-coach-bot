from datetime import date, timedelta

from sqlalchemy import select
from app.db.models import STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_NOT_STARTED, UserSyllabusProgress
from app.engines import bookmarks, logs, progress, tracker


async def test_current_week_from_start_date(env):
    env.user.start_date = date.today() - timedelta(days=0)
    assert progress.current_week(env.user) == (1, 1)
    env.user.start_date = date.today() - timedelta(days=7)
    assert progress.current_week(env.user) == (1, 2)
    env.user.start_date = date.today() - timedelta(days=7 * 5)  # into month 2 week 2
    assert progress.current_week(env.user) == (2, 2)
    env.user.start_date = date.today() - timedelta(days=7 * 100)  # clamps to last week
    assert progress.current_week(env.user) == (6, 4)


async def test_overall_and_completion(env):
    o0 = await progress.overall(env.session, env.user.id, env.user.field)
    assert o0["done"] == 0 and o0["pct"] == 0.0 and o0["total"] == 62

    # complete one high-priority sub-topic via the tracker cycle (NS -> IP -> Completed)
    rows = await tracker.sub_topics(env.session, env.user.id, env.user.field, 1, 1)
    row = rows[0]
    assert row.status == STATUS_NOT_STARTED
    await tracker.cycle_status(env.session, env.user.id, row.id)
    
    # Check status from UserSyllabusProgress table
    p_status = await env.session.scalar(
        select(UserSyllabusProgress.status).where(
            UserSyllabusProgress.user_id == env.user.id,
            UserSyllabusProgress.syllabus_tracker_id == row.id
        )
    )
    assert p_status == STATUS_IN_PROGRESS
    
    await tracker.cycle_status(env.session, env.user.id, row.id)
    p_status2 = await env.session.scalar(
        select(UserSyllabusProgress.status).where(
            UserSyllabusProgress.user_id == env.user.id,
            UserSyllabusProgress.syllabus_tracker_id == row.id
        )
    )
    assert p_status2 == STATUS_COMPLETED

    o1 = await progress.overall(env.session, env.user.id, env.user.field)
    assert o1["done"] == 1
    assert o1["hp_done"] == 1


async def test_dashboard_shape(env):
    d = await progress.dashboard(env.session, env.user)
    assert d["month"] == 1 and d["week"] == 1
    assert "C Programming" in d["current_subjects"]
    assert d["current_total"] == 3  # Pointers, Recursion, Arrays


async def test_daily_log_toggle_and_hours(env):
    log = await logs.get_or_create(env.session, env.user.id)
    assert logs.blocks_done(log) == 0
    await logs.toggle_block(env.session, log, "theory_done")
    await logs.toggle_block(env.session, log, "pyq_done")
    assert logs.blocks_done(log) == 2
    await logs.toggle_block(env.session, log, "theory_done")  # untoggle
    assert logs.blocks_done(log) == 1
    await logs.set_hours(env.session, log, 4.5)
    assert log.hours_studied == 4.5
    # get_or_create returns the same row for the same day
    again = await logs.get_or_create(env.session, env.user.id)
    assert again.id == log.id


async def test_bookmarks_add_and_list(env):
    await bookmarks.add(env.session, env.user.id, "GATE2019 Q35 TLB numerical")
    await bookmarks.add(env.session, env.user.id, "AVL rotations")
    items = await bookmarks.list_for(env.session, env.user.id)
    assert len(items) == 2
    assert items[0].text == "AVL rotations"  # newest first
