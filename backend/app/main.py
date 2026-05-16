from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import chat, conversations, developer, emotion, health, memory, plugins, settings_router
from .services.plugin_runtime import plugin_runtime


def create_app() -> FastAPI:
    init_db()
    plugin_runtime.scan()
    app = FastAPI(title="Aether Dev API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(conversations.router)
    app.include_router(chat.router)
    app.include_router(memory.router)
    app.include_router(emotion.router)
    app.include_router(developer.router)
    app.include_router(plugins.router)
    app.include_router(settings_router.router)
    return app


app = create_app()

