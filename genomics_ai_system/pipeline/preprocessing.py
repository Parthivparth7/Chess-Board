from __future__ import annotations

from pathlib import Path
from typing import Any


def run_preprocessing(input_path: str | Path) -> dict[str, Any]:
    """Basic preprocessing stage.

    Keeps orchestration lightweight: validates existence and returns normalized path payload.
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"FASTQ file not found: {path}")

    return {
        "fastq_path": str(path),
        "file_size_bytes": path.stat().st_size,
        "status": "preprocessed",
    }


def run_qc_analysis(preprocessed_output: dict[str, Any]) -> dict[str, Any]:
    """Compute simple FASTQ QC metrics from raw reads.

    FASTQ format blocks are read in groups of 4 lines.
    Quality uses Phred+33 estimation.
    """
    fastq_path = Path(preprocessed_output["fastq_path"])

    total_reads = 0
    total_bases = 0
    gc_bases = 0
    q20_bases = 0
    q30_bases = 0
    quality_bases = 0
    min_len: int | None = None
    max_len = 0

    with fastq_path.open("r", encoding="utf-8", errors="ignore") as handle:
        while True:
            header = handle.readline()
            if not header:
                break
            seq = handle.readline().strip()
            plus = handle.readline()
            qual = handle.readline().strip()

            if not seq or not plus:
                break

            total_reads += 1
            read_len = len(seq)
            total_bases += read_len
            if min_len is None or read_len < min_len:
                min_len = read_len
            if read_len > max_len:
                max_len = read_len

            seq_u = seq.upper()
            gc_bases += seq_u.count("G") + seq_u.count("C")

            for ch in qual[:read_len]:
                quality_bases += 1
                score = ord(ch) - 33
                if score >= 20:
                    q20_bases += 1
                if score >= 30:
                    q30_bases += 1

    if total_reads == 0 or total_bases == 0:
        return {
            "total_reads": 0,
            "avg_read_length": 0,
            "min_read_length": 0,
            "max_read_length": 0,
            "gc_percent": 0.0,
            "q20_percent": 0.0,
            "q30_percent": 0.0,
            "qc_flag": "failed",
            "qc_reason": "No readable FASTQ records detected.",
        }

    avg_len = total_bases / total_reads
    gc_percent = (gc_bases / total_bases) * 100
    quality_den = quality_bases if quality_bases > 0 else total_bases
    q20_percent = (q20_bases / quality_den) * 100
    q30_percent = (q30_bases / quality_den) * 100

    qc_flag = "pass" if q30_percent >= 70 and total_reads >= 100 else "warn"

    return {
        "total_reads": total_reads,
        "avg_read_length": round(avg_len, 2),
        "min_read_length": min_len or 0,
        "max_read_length": max_len,
        "gc_percent": round(gc_percent, 2),
        "q20_percent": round(q20_percent, 2),
        "q30_percent": round(q30_percent, 2),
        "qc_flag": qc_flag,
    }
