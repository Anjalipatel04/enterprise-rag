import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import requests
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def call_backend(backend_url: str, question: str, top_k: int) -> dict[str, Any]:
    response = requests.post(
        f"{backend_url.rstrip('/')}/chat",
        json={"question": question, "top_k": top_k},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def reciprocal_rank(citations: list[dict[str, Any]], expected_contexts: list[str]) -> float:
    expected = " ".join(expected_contexts).lower()
    for rank, citation in enumerate(citations, start=1):
        text = citation.get("text", "").lower()
        if text and (text in expected or any(term in text for term in expected.split()[:12])):
            return 1.0 / rank
    return 0.0


def recall_at_k(citations: list[dict[str, Any]], expected_contexts: list[str]) -> float:
    retrieved = " ".join(c.get("text", "") for c in citations).lower()
    expected_terms = {term for ctx in expected_contexts for term in ctx.lower().split() if len(term) > 3}
    if not expected_terms:
        return 0.0
    return len({term for term in expected_terms if term in retrieved}) / len(expected_terms)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Enterprise RAG")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--backend-url", default="http://localhost:8000")
    parser.add_argument("--top-k", default=5, type=int)
    parser.add_argument("--out", default="results.json", type=Path)
    args = parser.parse_args()

    rows = load_jsonl(args.dataset)
    predictions: list[dict[str, Any]] = []
    for row in rows:
        result = call_backend(args.backend_url, row["question"], args.top_k)
        citations = result.get("citations", [])
        contexts = [citation.get("text", "") for citation in citations]
        predictions.append(
            {
                "question": row["question"],
                "answer": result.get("answer", ""),
                "contexts": contexts,
                "ground_truth": row.get("ground_truth", row.get("answer", "")),
                "recall_at_5": recall_at_k(citations, row.get("contexts", [])),
                "mrr": reciprocal_rank(citations, row.get("contexts", [])),
            }
        )

    ragas_dataset = Dataset.from_list(
        [
            {
                "question": item["question"],
                "answer": item["answer"],
                "contexts": item["contexts"],
                "ground_truth": item["ground_truth"],
            }
            for item in predictions
        ]
    )
    ragas_result = evaluate(ragas_dataset, metrics=[faithfulness])
    report = {
        "recall_at_5": float(np.mean([item["recall_at_5"] for item in predictions])) if predictions else 0.0,
        "mrr": float(np.mean([item["mrr"] for item in predictions])) if predictions else 0.0,
        "ragas": ragas_result.to_pandas().to_dict(orient="records"),
        "items": predictions,
    }
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"recall_at_5": report["recall_at_5"], "mrr": report["mrr"], "out": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
