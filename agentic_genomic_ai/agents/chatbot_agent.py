from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ChatbotAgent:
    def run(self, question: str, analysis_summary: str, retrieved_context: list[str]) -> str:
        context_text = "\n---\n".join(retrieved_context[:2]) if retrieved_context else "No external genomic context found."
        answer = (
            f"Question: {question}\n"
            f"Analysis Summary: {analysis_summary}\n"
            f"Knowledge Context: {context_text[:1200]}\n"
            "Interpretation: Based on QC + model outputs, validate with downstream domain tools before clinical decisions."
        )
        logger.info("ChatbotAgent generated answer")
        return answer
