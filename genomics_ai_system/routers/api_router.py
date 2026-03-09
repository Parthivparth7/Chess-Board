import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from genomics_ai_system.services.pipeline_service import GenomicsPipelineService, PipelineStageError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["genomics"])
service = GenomicsPipelineService()


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
