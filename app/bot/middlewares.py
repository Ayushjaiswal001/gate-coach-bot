"""Allowlist gatekeeper and a global error boundary."""

import logging

from telegram import Update
from telegram.ext import ApplicationHandlerStop, ContextTypes

from app.config import settings

logger = logging.getLogger(__name__)


async def gatekeeper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    allowed = settings.allowed_ids
    if user is not None and (not allowed or user.id in allowed):
        return
    if update.effective_message:
        await update.effective_message.reply_text("🔒 This is a private GATE coach bot.")
    raise ApplicationHandlerStop


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("handler error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Something went wrong. Try again in a moment."
            )
        except Exception:
            pass
