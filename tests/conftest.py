from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base, UserProfile
from app.scripts.seed import load_syllabus, seed


@pytest.fixture
async def session(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


@pytest.fixture
async def env(session):
    """Seeded syllabus + a user whose prep started today."""
    await seed(session, load_syllabus())
    user = UserProfile(tg_user_id=42, first_name="Ayush", start_date=date.today())
    session.add(user)
    await session.commit()
    return SimpleNamespace(session=session, user=user)
