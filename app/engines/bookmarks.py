"""Flagged topics / PYQs for revision."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Bookmark


async def add(session: AsyncSession, user_id: int, text: str) -> Bookmark:
    bm = Bookmark(user_id=user_id, text=text.strip())
    session.add(bm)
    await session.commit()
    return bm


async def list_for(session: AsyncSession, user_id: int, limit: int = 100) -> list[Bookmark]:
    rows = await session.execute(
        select(Bookmark)
        .where(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
        .limit(limit)
    )
    return list(rows.scalars())
