"""Inline keyboards. Callback formats (<=64 bytes):

  td:t | td:p | td:a        toggle today's blocks
  td:hours                  start hours-input
  tk:root                   track: month list
  tk:m:{month}              track: weeks/subjects in a month
  tk:w:{month}:{week}       track: sub-topics in a week
  tk:s:{row_id}:{month}:{week}   cycle a sub-topic's status (then re-render the week)
  nav:today | nav:dash      shortcuts
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import STATUS_COMPLETED, STATUS_IN_PROGRESS, SyllabusTracker
from app.engines.meta import month_title

STATUS_ICON = {
    "Not Started": "⬜",
    STATUS_IN_PROGRESS: "🔶",
    STATUS_COMPLETED: "✅",
}


def _check(done: bool) -> str:
    return "✅" if done else "⬜"


def today_kb(log) -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton
    return InlineKeyboardMarkup(
        [
            [btn(f"{_check(log.theory_done)} Morning Theory (2h)", callback_data="td:t")],
            [btn(f"{_check(log.pyq_done)} Afternoon PYQ (1.5h)", callback_data="td:p")],
            [btn(f"{_check(log.aptitude_done)} Evening Rev/Aptitude (1h)", callback_data="td:a")],
            [btn(f"✍️ Log hours (now: {log.hours_studied:g}h)", callback_data="td:hours")],
        ]
    )


def months_kb(months: list[int]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"Month {m} — {month_title(m)}", callback_data=f"tk:m:{m}")]
        for m in months
    ]
    return InlineKeyboardMarkup(rows)


def subjects_kb(month: int, weeks: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"W{week}: {subject}", callback_data=f"tk:w:{month}:{week}")]
        for week, subject in weeks
    ]
    rows.append([InlineKeyboardButton("⬅️ Months", callback_data="tk:root")])
    return InlineKeyboardMarkup(rows)


def sub_topics_kb(month: int, week: int, rows: list[SyllabusTracker]) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                f"{STATUS_ICON.get(r.status, '⬜')} {r.sub_topic}",
                callback_data=f"tk:s:{r.id}:{month}:{week}",
            )
        ]
        for r in rows
    ]
    kb.append([InlineKeyboardButton("⬅️ Back", callback_data=f"tk:m:{month}")])
    return InlineKeyboardMarkup(kb)
