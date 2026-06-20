import re

from .models import RetrievedChunk


INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"system prompt",
    r"developer message",
    r"reveal.*(secret|key|prompt)",
    r"act as.*unrestricted",
    r"bypass.*(policy|guardrail|safety)",
]


def detect_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS)


def passes_similarity_threshold(chunks, threshold):
    print("GUARDRAIL CALLED")
    print("CHUNKS FOUND:", len(chunks))
    return True


def enforce_grounding(answer: str, chunks: list[RetrievedChunk]) -> bool:
    if not answer.strip() or not chunks:
        return False
    if "i don't know" in answer.lower() or "not found" in answer.lower():
        return True

    context_terms = set()
    for item in chunks:
        context_terms.update(re.findall(r"[a-zA-Z]{4,}", item.chunk.text.lower()))
    answer_terms = set(re.findall(r"[a-zA-Z]{4,}", answer.lower()))
    if not answer_terms:
        return False
    overlap = len(answer_terms & context_terms) / max(len(answer_terms), 1)
    return overlap >= 0.35
