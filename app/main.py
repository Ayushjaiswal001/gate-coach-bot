"""Entry point: python -m app.main  (bot polling + health server in one event loop)."""

import asyncio
import logging
import os
from pathlib import Path

from app.api.health import make_server, set_bot_app
from app.bot.app import build_application, setup_application
from app.config import settings

logger = logging.getLogger("app.main")


async def _bootstrap():
    app = build_application()
    try:
        await app.initialize()
        await setup_application(app)
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        return app
    except Exception:
        try:
            await app.shutdown()
        except Exception:
            pass
        raise


async def amain() -> None:
    Path("data").mkdir(exist_ok=True)
    logger.info("startup config summary: %r", settings.safe_startup_summary())
    server = make_server(int(os.environ.get("PORT", "7860")))
    server_task = asyncio.create_task(server.serve())
    app = None
    try:
        for attempt in range(1, 9):
            try:
                app = await _bootstrap()
                break
            except Exception as e:  # transient cold-start network/DB hiccups
                logger.warning("bootstrap attempt %s failed: %r", attempt, e)
                await asyncio.sleep(min(3 * attempt, 20))
        if app is None:
            raise RuntimeError("bot failed to start after retries")
        logger.info("bot polling started")
        set_bot_app(app)  # /healthz reports 503 if polling dies → host restarts the container
        await server_task
    finally:
        logger.info("shutting down")
        server.should_exit = True
        if not server_task.done():
            try:
                await asyncio.wait_for(server_task, timeout=10)
            except TimeoutError:
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass
        if app is not None:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(amain())


if __name__ == "__main__":
    main()
