"""/flag <text> — bookmark a tough topic/PYQ;  /revision — list bookmarks + short-notes plan."""

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.formatting import esc, send_html
from app.bot.users import ensure_user
from app.db.session import SessionLocal
from app.engines import bookmarks

SHORT_NOTES_PLAN = (
    "🗂 <b>Short-Notes Extraction (Month 5, Week 4)</b>\n"
    "For every flagged item below:\n"
    "  1. Write the core formula / definition on a single index card.\n"
    "  2. Note the exact edge case or trap that caught you.\n"
    "  3. Re-solve one PYQ on it from memory.\n"
    "Goal: a compact formula+trap sheet you can revise in the final week."
)


async def flag_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args).strip() if context.args else ""
    if not text:
        await update.effective_message.reply_html(
            "Usage: <code>/flag &lt;topic or PYQ description&gt;</code>\n"
            "e.g. <code>/flag GATE2019 Q35 — TLB hit ratio numerical</code>"
        )
        return
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)
        await bookmarks.add(session, user.id, text)
    await update.effective_message.reply_html(
        f"🚩 Flagged: <i>{esc(text)}</i>\nSee all with /revision."
    )


async def revision_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with SessionLocal() as session:
        user, _ = await ensure_user(session, update.effective_user)
        items = await bookmarks.list_for(session, user.id)

    if not items:
        body = (
            "📭 No bookmarks yet. Flag tough topics with <code>/flag &lt;text&gt;</code>.\n\n"
            + SHORT_NOTES_PLAN
        )
    else:
        listed = "\n".join(f"  {i + 1}. {esc(b.text)}" for i, b in enumerate(items))
        body = f"🚩 <b>Your flagged items ({len(items)})</b>\n{listed}\n\n{SHORT_NOTES_PLAN}"
    await send_html(update.effective_message, body)
