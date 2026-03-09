from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from agentic_genomic_ai.pipeline.pipeline_orchestrator import AgenticPipelineOrchestrator
from agentic_genomic_ai.schemas.response_schema import GenomicsAnalysisResponse

router = APIRouter(prefix="/genomics", tags=["genomics"])
orchestrator = AgenticPipelineOrchestrator()


@router.post("/analyze_fastq", response_model=GenomicsAnalysisResponse)
async def analyze_fastq(file: UploadFile = File(...)) -> GenomicsAnalysisResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing FASTQ file")
    if not (file.filename.endswith(".fastq") or file.filename.endswith(".fq")):
        raise HTTPException(status_code=400, detail="Only .fastq/.fq supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        path = Path(tmp.name)

    try:
        result = orchestrator.run_fastq_pipeline(path)
        return GenomicsAnalysisResponse(**result)
    finally:
        path.unlink(missing_ok=True)
