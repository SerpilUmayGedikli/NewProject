from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List


def load_results(path: str = "bolum4_degerlendirme/results/benchmark_results.json") -> List[Dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def tsr(rows: Iterable[Dict]) -> float:
    rows = list(rows)
    return 100.0 * sum(r["success"] for r in rows) / max(1, len(rows))


def token_expenditure(rows: Iterable[Dict]) -> float:
    rows = list(rows)
    return mean([r["total_tokens"] for r in rows]) if rows else 0.0


def wall_clock_latency(rows: Iterable[Dict]) -> float:
    rows = list(rows)
    return mean([r["elapsed_time"] for r in rows]) if rows else 0.0


def output_quality_score(answer: str, prompt: str) -> float:
    # Basit rubric: 5 ölçüt x 0-2 puan
    relevance = 2 if any(w in answer.lower() for w in prompt.lower().split()[:3]) else 1
    completeness = 2 if len(answer.split()) > 12 else 1
    coherence = 2 if "." in answer else 1
    depth = 2 if len(answer) > 80 else 1
    constraint = 2 if len(answer.strip()) > 0 else 0
    return float(relevance + completeness + coherence + depth + constraint)


def min_max_normalize(values: Dict[str, float], invert: bool = False) -> Dict[str, float]:
    mn = min(values.values())
    mx = max(values.values())
    if mx == mn:
        return {k: 1.0 for k in values}
    normalized = {k: (v - mn) / (mx - mn) for k, v in values.items()}
    if invert:
        normalized = {k: 1 - v for k, v in normalized.items()}
    return normalized


def compute_cei(rows: List[Dict], weights: Dict[str, float] | None = None) -> Dict[str, float]:
    weights = weights or {"tsr": 0.25, "oqs": 0.25, "te": 0.25, "wcl": 0.25}
    by_strategy: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        by_strategy[row["strategy"]].append(row)

    tsr_raw = {s: tsr(r) for s, r in by_strategy.items()}
    te_raw = {s: token_expenditure(r) for s, r in by_strategy.items()}
    wcl_raw = {s: wall_clock_latency(r) for s, r in by_strategy.items()}

    oqs_raw: Dict[str, float] = {}
    for strategy, s_rows in by_strategy.items():
        t34 = [r for r in s_rows if r["tier"] in (3, 4)]
        oqs_raw[strategy] = mean([output_quality_score(r["final_answer"], r["final_answer"]) for r in t34]) if t34 else 0.0

    tsr_n = min_max_normalize(tsr_raw)
    oqs_n = min_max_normalize(oqs_raw)
    te_n = min_max_normalize(te_raw)
    wcl_n = min_max_normalize(wcl_raw)

    return {
        s: weights["tsr"] * tsr_n[s] + weights["oqs"] * oqs_n[s] - weights["te"] * te_n[s] - weights["wcl"] * wcl_n[s]
        for s in by_strategy
    }


def cost_per_success(rows: List[Dict], input_price_per_million: float = 2.50, output_price_per_million: float = 10.00) -> Dict[str, float]:
    by_strategy: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        by_strategy[row["strategy"]].append(row)

    costs = {}
    for strategy, s_rows in by_strategy.items():
        total_tokens = sum(r["total_tokens"] for r in s_rows)
        # Simülasyonda input/output ayrımı yok: kabaca %70 input, %30 output
        input_tokens = total_tokens * 0.7
        output_tokens = total_tokens * 0.3
        total_cost = (input_tokens / 1_000_000) * input_price_per_million + (output_tokens / 1_000_000) * output_price_per_million
        successes = max(1, sum(r["success"] for r in s_rows))
        costs[strategy] = total_cost / successes
    return costs


if __name__ == "__main__":
    rows = load_results()
    balanced = compute_cei(rows)
    quality = compute_cei(rows, {"tsr": 0.4, "oqs": 0.3, "te": 0.15, "wcl": 0.15})
    cost_focus = compute_cei(rows, {"tsr": 0.2, "oqs": 0.2, "te": 0.3, "wcl": 0.3})
    print("Balanced CEI:", balanced)
    print("Quality CEI:", quality)
    print("Cost-focused CEI:", cost_focus)
    print("Cost per success:", cost_per_success(rows))
