"""Entry point: python -m app.main  (bot polling + health server in one event loop)."""

import asyncio
import logging
import os
from pathlib import Path

from app.api.health import make_server
from app.bot.app import build_application, setup_application

logger = logging.getLogger("app.main")


async def _bootstrap():
    app = build_application()
    await app.initialize()
    await setup_application(app)
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    return app


async def amain() -> None:
    Path("data").mkdir(exist_ok=True)
    app = None
    for attempt in range(1, 9):
        try:
            app = await _bootstrap()
            break
        except Exception as e:  # transient cold-start network/DB hiccups
            logger.warning("bootstrap attempt %s failed: %r", attempt, e)
            if app is not None:
                try:
                    await app.shutdown()
                except Exception:
                    pass
                app = None
            await asyncio.sleep(min(3 * attempt, 20))
    if app is None:
        raise RuntimeError("bot failed to start after retries")
    logger.info("bot polling started")

    server = make_server(int(os.environ.get("PORT", "7860")))
    try:
        await server.serve()
    finally:
        logger.info("shutting down")
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
