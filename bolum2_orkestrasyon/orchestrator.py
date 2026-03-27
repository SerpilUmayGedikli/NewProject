from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, List

from .strategies import (
    StrategyRun,
    run_debate,
    run_hierarchical,
    run_majority_voting,
    run_sequential_chain,
    run_solo,
    run_solo_self_refine,
)


@dataclass
class OrchestratorResult:
    strategy: str
    final_answer: str
    agent_logs: List[dict]
    total_tokens: int
    elapsed_time: float


class Orchestrator:
    def __init__(self, logs_dir: str = "logs") -> None:
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.strategies: Dict[str, Callable[[str], StrategyRun]] = {
            "solo": run_solo,
            "solo_self_refine": run_solo_self_refine,
            "sequential_chain": run_sequential_chain,
            "hierarchical": run_hierarchical,
            "debate": run_debate,
            "majority_voting": run_majority_voting,
        }

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return max(1, len(text.split()))

    def run(self, strategy_name: str, task: str) -> OrchestratorResult:
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        start = time.perf_counter()
        run_result = self.strategies[strategy_name](task)
        elapsed = time.perf_counter() - start

        total_tokens = self._estimate_tokens(task) + sum(
            self._estimate_tokens(r["message"]) for r in run_result.rounds
        )

        result = OrchestratorResult(
            strategy=strategy_name,
            final_answer=run_result.final_answer,
            agent_logs=run_result.rounds,
            total_tokens=total_tokens,
            elapsed_time=elapsed,
        )
        self._write_json_log(task, result)
        return result

    def _write_json_log(self, task: str, result: OrchestratorResult) -> None:
        payload = {
            "strategy": result.strategy,
            "task": task,
            "rounds": result.agent_logs,
            "final_answer": result.final_answer,
            "total_tokens": result.total_tokens,
            "elapsed_time_sec": round(result.elapsed_time, 4),
        }
        filename = self.logs_dir / f"{result.strategy}_{int(time.time()*1000)}.json"
        filename.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    orch = Orchestrator()
    out = orch.run("debate", "LLM tabanlı multi-agent sistemlerin avantajları nelerdir?")
    print(asdict(out))
