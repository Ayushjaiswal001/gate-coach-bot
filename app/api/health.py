"""Health/keep-alive HTTP server — runs as a coroutine in the bot's event loop."""

from fastapi import FastAPI

api = FastAPI(title="GATE Coach Bot", docs_url=None, redoc_url=None)


@api.get("/")
def root() -> dict:
    return {"status": "GATE Coach Bot is alive 🎯"}


@api.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


def make_server(port: int):
    import uvicorn

    config = uvicorn.Config(api, host="0.0.0.0", port=port, log_level="info", log_config=None)
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None
    return server
