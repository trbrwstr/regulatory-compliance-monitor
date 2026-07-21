from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from services.diffing import content_hash


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    expected_title: str
    expected_source_url: str
    expected_relevant: bool
    expected_summary_corrections: int = 0


@dataclass(frozen=True)
class EvaluationResult:
    fixture_set: str
    seeded: bool
    total_cases: int
    detected_cases: int
    true_positives: int
    false_negatives: int
    duplicate_count: int
    citation_validity: float
    relevance_acceptance: float
    summary_corrections: int
    latency_seconds: float | None
    missing_source_periods: list[str]
    generated_at: str


def evaluate_fixture(path: str | Path) -> EvaluationResult:
    payload = json.loads(Path(path).read_text())
    cases = [EvaluationCase(**case) for case in payload["cases"]]
    detected = payload.get("detected", [])
    seen_hashes: set[str] = set()
    duplicates = 0
    valid_citations = 0
    relevant_results = 0
    true_positives = 0
    false_negatives = 0
    corrections = 0
    for item in detected:
        item_hash = content_hash(item.get("title", "") + item.get("source_url", ""))
        if item_hash in seen_hashes:
            duplicates += 1
        seen_hashes.add(item_hash)
        citation = item.get("citation", {})
        if citation.get("source_url") == item.get("source_url") and citation.get("location"):
            valid_citations += 1
        match = next((case for case in cases if case.expected_title == item.get("title")), None)
        if match and match.expected_relevant:
            true_positives += 1
            if item.get("relevance_accepted"):
                relevant_results += 1
            corrections += max(0, int(item.get("summary_corrections", 0)))
    for case in cases:
        if case.expected_relevant and not any(item.get("title") == case.expected_title for item in detected):
            false_negatives += 1
    relevant_cases = sum(case.expected_relevant for case in cases)
    return EvaluationResult(
        fixture_set=payload.get("fixture_set", "unknown"),
        seeded=bool(payload.get("seeded", True)),
        total_cases=len(cases),
        detected_cases=len(detected),
        true_positives=true_positives,
        false_negatives=false_negatives,
        duplicate_count=duplicates,
        citation_validity=valid_citations / len(detected) if detected else 1.0,
        relevance_acceptance=relevant_results / relevant_cases if relevant_cases else 1.0,
        summary_corrections=corrections,
        latency_seconds=payload.get("latency_seconds"),
        missing_source_periods=payload.get("missing_source_periods", []),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
