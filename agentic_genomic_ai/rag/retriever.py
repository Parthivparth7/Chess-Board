from __future__ import annotations

from agentic_genomic_ai.rag.document_loader import load_documents
from agentic_genomic_ai.rag.vector_store import InMemoryVectorStore


class GenomicRetriever:
    def __init__(self, knowledge_dir: str = "agentic_genomic_ai/data/knowledge_base") -> None:
        self.knowledge_dir = knowledge_dir
        self.store = InMemoryVectorStore()
        self.refresh()

    def refresh(self) -> None:
        docs = load_documents(self.knowledge_dir)
        self.store.build(docs)

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        return self.store.query(query, top_k=top_k)
