from __future__ import annotations

from pathlib import Path


def load_documents(directory: str | Path) -> list[str]:
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    docs: list[str] = []
    for p in sorted(d.glob("**/*")):
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            docs.append(p.read_text(encoding="utf-8", errors="ignore"))
    return docs
