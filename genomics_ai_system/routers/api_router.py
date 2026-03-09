import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from genomics_ai_system.services.pipeline_service import (
    DataSourceError,
    GenomicsPipelineService,
    PipelineStageError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["genomics"])
service = GenomicsPipelineService()


class FastqUrlRequest(BaseModel):
    fastq_url: str = Field(..., description="Direct HTTP/HTTPS URL of a .fastq/.fastq.gz file")
    filename: str | None = Field(default=None, description="Optional filename hint for temp suffix")


class EnaRunRequest(BaseModel):
    run_accession: str = Field(..., description="ENA run accession, e.g., SRR390728")


@router.post("/analyze-fastq")
async def analyze_fastq(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required.")

    allowed_suffixes = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
    if not file.filename.endswith(allowed_suffixes):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a FASTQ file.")

    try:
        return await service.analyze_fastq(file)
    except PipelineStageError as exc:
        logger.exception("Pipeline stage resolution/execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unhandled pipeline error")
        raise HTTPException(status_code=500, detail="FASTQ analysis failed") from exc


@router.post("/analyze-fastq-stream")
async def analyze_fastq_stream(file: UploadFile = File(...)) -> StreamingResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required.")

    allowed_suffixes = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
    if not file.filename.endswith(allowed_suffixes):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a FASTQ file.")

    return StreamingResponse(service.analyze_fastq_stream(file), media_type="application/x-ndjson")


@router.post("/analyze-fastq-url")
async def analyze_fastq_url(payload: FastqUrlRequest) -> dict:
    try:
        return await service.analyze_fastq_from_url(payload.fastq_url, payload.filename)
    except DataSourceError as exc:
        logger.exception("FASTQ source download failed")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PipelineStageError as exc:
        logger.exception("Pipeline stage resolution/execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/analyze-fastq-ena")
async def analyze_fastq_ena(payload: EnaRunRequest) -> dict:
    try:
        return await service.analyze_fastq_from_ena(payload.run_accession)
    except DataSourceError as exc:
        logger.exception("ENA FASTQ fetch failed")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PipelineStageError as exc:
        logger.exception("Pipeline stage resolution/execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
