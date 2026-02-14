from fastapi import FastAPI

from artiisly_automation.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Artiisly Automation Platform",
        version="0.1.0",
        description="Secure orchestration for Artisly product generation and multi-channel monetization.",
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
