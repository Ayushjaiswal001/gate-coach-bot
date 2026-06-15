"""Load-or-create the UserProfile for a Telegram user."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import User as TgUser

from app.config import settings
from app.db.models import UserProfile


async def ensure_user(session: AsyncSession, tg_user: TgUser) -> tuple[UserProfile, bool]:
    user = await session.scalar(select(UserProfile).where(UserProfile.tg_user_id == tg_user.id))
    if user is not None:
        return user, False
    user = UserProfile(
        tg_user_id=tg_user.id,
        first_name=tg_user.first_name,
        daily_hours_goal=settings.default_daily_hours,
        timezone=settings.default_timezone,
        reminder_hour=settings.reminder_hour,
    )
    session.add(user)
    await session.commit()
    return user, True
