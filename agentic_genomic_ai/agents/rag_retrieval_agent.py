from __future__ import annotations

import logging

from agentic_genomic_ai.rag.retriever import GenomicRetriever

logger = logging.getLogger(__name__)


class RAGRetrievalAgent:
    def __init__(self, knowledge_dir: str = "agentic_genomic_ai/data/knowledge_base") -> None:
        self.retriever = GenomicRetriever(knowledge_dir=knowledge_dir)

    def run(self, query: str) -> list[str]:
        context = self.retriever.retrieve(query, top_k=3)
        logger.info("RAGRetrievalAgent retrieved %d documents", len(context))
        return context
