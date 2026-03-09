from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_genomic_ai.pipeline.pipeline_orchestrator import AgenticPipelineOrchestrator


if __name__ == "__main__":
    sample = ROOT / "sample_data" / "demo_reads.fastq"
    orchestrator = AgenticPipelineOrchestrator()
    result = orchestrator.run_fastq_pipeline(sample)
    print(json.dumps(result, indent=2))
