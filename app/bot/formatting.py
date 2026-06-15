"""Outbound text helpers: HTML escaping, chunking, send/edit."""

import html

from telegram import InlineKeyboardMarkup, Message

CHUNK_LIMIT = 3500


def esc(text: object) -> str:
    return html.escape(str(text), quote=False)


def chunk(text: str, limit: int = CHUNK_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]
    out, cur = [], ""
    for para in text.split("\n\n"):
        candidate = f"{cur}\n\n{para}" if cur else para
        if len(candidate) > limit and cur:
            out.append(cur)
            cur = para
        else:
            cur = candidate
    if cur:
        out.append(cur)
    return out


async def send_html(message: Message, text: str, kb: InlineKeyboardMarkup | None = None) -> None:
    parts = chunk(text)
    for i, part in enumerate(parts):
        await message.reply_html(part, reply_markup=kb if i == len(parts) - 1 else None)
