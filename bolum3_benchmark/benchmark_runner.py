from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from bolum2_orkestrasyon.orchestrator import Orchestrator

STRATEGIES = [
    "solo",
    "solo_self_refine",
    "sequential_chain",
    "hierarchical",
    "debate",
    "majority_voting",
]


def load_tasks(path: str = "bolum3_benchmark/tasks.json") -> List[Dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_benchmark(output_dir: str = "bolum4_degerlendirme/results") -> List[Dict]:
    tasks = load_tasks()
    orchestrator = Orchestrator(logs_dir="logs")
    results: List[Dict] = []

    for strategy in STRATEGIES:
        for task in tasks:
            run_result = orchestrator.run(strategy, task["prompt"])
            success = _is_success(task, run_result.final_answer)
            row = {
                "strategy": strategy,
                "task_id": task["task_id"],
                "tier": task["tier"],
                "domain": task["domain"],
                "success": int(success),
                "total_tokens": run_result.total_tokens,
                "elapsed_time": run_result.elapsed_time,
                "final_answer": run_result.final_answer,
            }
            results.append(row)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "benchmark_results.json"
    csv_path = out / "benchmark_results.csv"

    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    return results


def _is_success(task: Dict, final_answer: str) -> bool:
    expected = task.get("expected_answer")
    if expected is None:
        return len(final_answer.strip()) > 30
    return str(expected).lower() in final_answer.lower()


if __name__ == "__main__":
    data = run_benchmark()
    print(f"Benchmark tamamlandı. Toplam kayıt: {len(data)}")
