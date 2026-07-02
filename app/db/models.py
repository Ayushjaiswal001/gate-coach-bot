"""SQLAlchemy 2.0 models. Schema: docs/superpowers/specs/2026-06-15-gate-coach-design.md."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

STATUS_NOT_STARTED = "Not Started"
STATUS_IN_PROGRESS = "In Progress"
STATUS_COMPLETED = "Completed"
STATUS_CYCLE = [STATUS_NOT_STARTED, STATUS_IN_PROGRESS, STATUS_COMPLETED]


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(128))
    field: Mapped[str] = mapped_column(String(16), default="CSE")  # "CSE" or "ECE"
    daily_hours_goal: Mapped[float] = mapped_column(Float, default=4.5)
    start_date: Mapped[date] = mapped_column(Date, default=lambda: utcnow().date())
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")
    reminder_hour: Mapped[int | None] = mapped_column(default=7)  # None = reminders off
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SyllabusTracker(Base):
    """Global pre-populated curriculum; one row per sub-topic."""

    __tablename__ = "syllabus_tracker"
    __table_args__ = (
        UniqueConstraint("field", "month", "week", "sub_topic", name="uq_syllabus_row"),
        Index("ix_syllabus_month_week", "month", "week"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    field: Mapped[str] = mapped_column(String(16), default="CSE", index=True)
    month: Mapped[int] = mapped_column()
    week: Mapped[int] = mapped_column()
    subject: Mapped[str] = mapped_column(String(128))
    sub_topic: Mapped[str] = mapped_column(String(160))
    is_high_priority: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(default=0)

    @property
    def status(self) -> str:
        return getattr(self, "_status", STATUS_NOT_STARTED)

    @status.setter
    def status(self, val: str) -> None:
        self._status = val


class UserSyllabusProgress(Base):
    __tablename__ = "user_syllabus_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "syllabus_tracker_id", name="uq_user_syllabus_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profile.id", ondelete="CASCADE"), index=True
    )
    syllabus_tracker_id: Mapped[int] = mapped_column(
        ForeignKey("syllabus_tracker.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(16), default=STATUS_NOT_STARTED)


class DailyLog(Base):
    __tablename__ = "daily_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_daily_log"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"))
    date: Mapped[date] = mapped_column(Date)
    theory_done: Mapped[bool] = mapped_column(Boolean, default=False)
    pyq_done: Mapped[bool] = mapped_column(Boolean, default=False)
    aptitude_done: Mapped[bool] = mapped_column(Boolean, default=False)
    hours_studied: Mapped[float] = mapped_column(Float, default=0.0)


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (Index("ix_bookmarks_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
