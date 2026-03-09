from __future__ import annotations


def send_to_chatbot(analysis_summary: str) -> str:
    return (
        "Genomics assistant response: "
        f"{analysis_summary} Next, you can ask for trimming recommendations or batch comparison."
    )
