"""Telegram Application wiring: handlers, gatekeeper, error boundary, command menu, jobs."""

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    TypeHandler,
    filters,
)

from app.bot import callbacks, middlewares
from app.bot.handlers import dashboard, field, flag, start, text, today, track
from app.bot.scheduler import register_jobs
from app.config import settings

COMMANDS = [
    ("start", "6-month strategy & setup"),
    ("field", "Switch between CSE and ECE"),
    ("today", "Today's checklist & hours"),
    ("dashboard", "Progress & current target"),
    ("track", "Browse & update syllabus"),
    ("flag", "Bookmark a tough topic/PYQ"),
    ("revision", "Flagged items & notes plan"),
    ("help", "Command list"),
]


async def setup_application(app: Application) -> None:
    from app.db.session import SessionLocal, init_db
    from app.scripts.seed import load_syllabus, seed

    await init_db()
    async with SessionLocal() as session:  # idempotent — keeps the cloud DB populated on every boot
        await seed(session, load_syllabus())
    register_jobs(app)
    await app.bot.set_my_commands([BotCommand(c, d) for c, d in COMMANDS])


def build_application() -> Application:
    settings.require_bot_token()
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .get_updates_connect_timeout(30)
        .get_updates_read_timeout(40)
        .build()
    )
    app.add_handler(TypeHandler(Update, middlewares.gatekeeper), group=-1)
    app.add_handler(CommandHandler("start", start.start_cmd))
    app.add_handler(CommandHandler("field", field.field_cmd))
    app.add_handler(CommandHandler("help", start.help_cmd))
    app.add_handler(CommandHandler("today", today.today_cmd))
    app.add_handler(CommandHandler("dashboard", dashboard.dashboard_cmd))
    app.add_handler(CommandHandler("track", track.track_cmd))
    app.add_handler(CommandHandler("flag", flag.flag_cmd))
    app.add_handler(CommandHandler("revision", flag.revision_cmd))
    app.add_handler(CallbackQueryHandler(callbacks.on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text.free_text))
    app.add_error_handler(middlewares.on_error)
    return app
