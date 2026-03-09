from __future__ import annotations

import logging
from pathlib import Path

from agentic_genomic_ai.utils.fastq_parser import parse_fastq

logger = logging.getLogger(__name__)


class DataIngestionAgent:
    def run(self, fastq_path: str | Path) -> dict:
        records = parse_fastq(fastq_path)
        logger.info("DataIngestionAgent loaded %d reads", len(records))
        return {"records": records, "source_path": str(fastq_path)}
