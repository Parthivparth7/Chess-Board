from __future__ import annotations

from fastapi import FastAPI

from agentic_genomic_ai.routers.chat_router import router as chat_router
from agentic_genomic_ai.routers.genomics_router import router as genomics_router
from agentic_genomic_ai.utils.logging_utils import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Agentic Genomic AI Platform", version="2.0.0")
    app.include_router(genomics_router)
    app.include_router(chat_router)
    return app


app = create_app()
