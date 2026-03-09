from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InMemoryVectorStore:
    docs: list[str] = field(default_factory=list)
    vectorizer: object | None = None
    matrix: object | None = None
    sklearn_available: bool = False

    def build(self, documents: list[str]) -> None:
        self.docs = documents
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.matrix = self.vectorizer.fit_transform(documents) if documents else None
            self.sklearn_available = True
        except Exception:
            self.vectorizer = None
            self.matrix = None
            self.sklearn_available = False

    def query(self, text: str, top_k: int = 3) -> list[str]:
        if not self.docs:
            return []

        if self.sklearn_available and self.vectorizer is not None and self.matrix is not None:
            from sklearn.metrics.pairwise import cosine_similarity

            qv = self.vectorizer.transform([text])
            sims = cosine_similarity(qv, self.matrix).flatten()
            idx = sims.argsort()[::-1][:top_k]
            return [self.docs[i] for i in idx if sims[i] > 0]

        # fallback: lexical overlap score
        q_terms = set(text.lower().split())
        scored = []
        for doc in self.docs:
            d_terms = set(doc.lower().split())
            score = len(q_terms.intersection(d_terms))
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for s, d in scored[:top_k] if s > 0] or self.docs[:top_k]
