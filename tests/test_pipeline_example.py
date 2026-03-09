from pathlib import Path

from agentic_genomic_ai.pipeline.pipeline_orchestrator import AgenticPipelineOrchestrator


def test_pipeline_example() -> None:
    sample = Path("sample_data/demo_reads.fastq")
    orchestrator = AgenticPipelineOrchestrator()
    out = orchestrator.run_fastq_pipeline(sample)
    assert "qc_metrics" in out
    assert "model_predictions" in out
    assert "variant_risk" in out
    assert "analysis_summary" in out
    assert "chatbot_explanation" in out
    # backward compatibility key
    assert "model_prediction" in out
