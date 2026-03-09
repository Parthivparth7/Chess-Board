from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from Bio import SeqIO  # type: ignore
except Exception:  # fallback parser keeps local pipeline runnable
    SeqIO = None


def validate_fastq_file(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"FASTQ file not found: {p}")
    if p.suffix not in {".fastq", ".fq"}:
        raise ValueError("Only .fastq/.fq supported for local parser")
    return p


def _parse_fastq_fallback(p: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        while True:
            h = f.readline().rstrip("\n")
            if not h:
                break
            s = f.readline().rstrip("\n")
            _ = f.readline().rstrip("\n")
            q = f.readline().rstrip("\n")
            if not s:
                break
            records.append(
                {
                    "id": h[1:] if h.startswith("@") else h,
                    "sequence": s,
                    "quality": [max(0, ord(ch) - 33) for ch in q[: len(s)]],
                }
            )
    return records


def parse_fastq(path: str | Path) -> list[dict[str, Any]]:
    p = validate_fastq_file(path)
    if SeqIO is None:
        return _parse_fastq_fallback(p)

    records: list[dict[str, Any]] = []
    for rec in SeqIO.parse(str(p), "fastq"):
        records.append(
            {
                "id": rec.id,
                "sequence": str(rec.seq),
                "quality": list(rec.letter_annotations.get("phred_quality", [])),
            }
        )
    return records
