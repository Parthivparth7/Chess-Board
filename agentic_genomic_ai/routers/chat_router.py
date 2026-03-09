from __future__ import annotations

from fastapi import APIRouter

from agentic_genomic_ai.agents.chatbot_agent import ChatbotAgent
from agentic_genomic_ai.agents.rag_retrieval_agent import RAGRetrievalAgent
from agentic_genomic_ai.schemas.request_schema import ChatQuestionRequest
from agentic_genomic_ai.schemas.response_schema import ChatAnswerResponse

router = APIRouter(prefix="/chat", tags=["chat"])
chatbot = ChatbotAgent()
rag = RAGRetrievalAgent()


@router.post("/genomics", response_model=ChatAnswerResponse)
def ask_genomics_question(payload: ChatQuestionRequest) -> ChatAnswerResponse:
    context = rag.run(payload.question)
    answer = chatbot.run(
        question=payload.question,
        analysis_summary=payload.analysis_summary or "No analysis summary provided.",
        retrieved_context=context,
    )
    return ChatAnswerResponse(answer=answer)
