import logging

from fastapi import FastAPI

from genomics_ai_system.routers.api_router import router as api_router


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    app = FastAPI(
        title="Genomics AI System",
        version="1.0.0",
        description="FastAPI backend orchestrating FASTQ preprocessing, QC, modeling, reporting, and chatbot delivery.",
    )
    app.include_router(api_router)
    return app


app = create_app()
