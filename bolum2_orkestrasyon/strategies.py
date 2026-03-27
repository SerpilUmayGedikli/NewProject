from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .agent import Agent


@dataclass
class StrategyRun:
    final_answer: str
    rounds: List[Dict[str, str]]


def _round(agent: Agent, message: str) -> Dict[str, str]:
    content = agent.respond(message)
    return {"agent": agent.name, "role": agent.role, "message": content}


def run_solo(task: str) -> StrategyRun:
    solo = Agent("Solo", "generalist", "Tek ajan çözümü")
    r = _round(solo, task)
    return StrategyRun(final_answer=r["message"], rounds=[r])


def run_solo_self_refine(task: str, iterations: int = 2) -> StrategyRun:
    agent = Agent("Refiner", "generalist", "Kendi çıktısını iyileştir")
    rounds: List[Dict[str, str]] = []
    state = task
    for i in range(iterations + 1):
        msg = f"Iterasyon {i+1}: {state}"
        r = _round(agent, msg)
        rounds.append(r)
        state = r["message"] + " [iyileştirildi]"
    return StrategyRun(final_answer=rounds[-1]["message"], rounds=rounds)


def run_sequential_chain(task: str) -> StrategyRun:
    analyst = Agent("Analyst", "planner", "Problemi parçala")
    solver = Agent("Solver", "coder", "Çözümü uygula")
    reviewer = Agent("Reviewer", "critic", "Kontrol et")

    r1 = _round(analyst, task)
    r2 = _round(solver, r1["message"])
    r3 = _round(reviewer, r2["message"])
    return StrategyRun(final_answer=r3["message"], rounds=[r1, r2, r3])


def run_hierarchical(task: str) -> StrategyRun:
    lead = Agent("Lead", "planner", "Görevi dağıt")
    worker_a = Agent("Worker-A", "coder", "Alt görev A")
    worker_b = Agent("Worker-B", "critic", "Alt görev B")

    r1 = _round(lead, task)
    r2 = _round(worker_a, r1["message"])
    r3 = _round(worker_b, r1["message"])
    summary = f"{r2['message']} | {r3['message']} | Final synthesis by Lead"
    r4 = {"agent": lead.name, "role": lead.role, "message": summary}
    return StrategyRun(final_answer=summary, rounds=[r1, r2, r3, r4])


def run_debate(task: str) -> StrategyRun:
    pro = Agent("Agent-A", "proponent", "Lehte argüman")
    con = Agent("Agent-B", "opponent", "Aleyhte argüman")
    judge = Agent("Judge", "judge", "Hakem")

    r1 = _round(pro, task)
    r2 = _round(con, r1["message"])
    r3 = _round(pro, r2["message"])
    r4 = _round(judge, r1["message"] + "\n" + r2["message"] + "\n" + r3["message"])
    return StrategyRun(final_answer=r4["message"], rounds=[r1, r2, r3, r4])


def run_majority_voting(task: str, n: int = 3) -> StrategyRun:
    rounds: List[Dict[str, str]] = []
    answers: List[str] = []
    for i in range(n):
        agent = Agent(f"Voter-{i+1}", "generalist", "Bağımsız yanıt")
        r = _round(agent, task)
        rounds.append(r)
        answers.append(r["message"])

    winner = max(set(answers), key=answers.count)
    rounds.append({"agent": "VotingSystem", "role": "aggregator", "message": f"Seçilen yanıt: {winner}"})
    return StrategyRun(final_answer=winner, rounds=rounds)
