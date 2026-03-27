from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class Topology(str, Enum):
    CENTRALIZED = "Centralized"
    DECENTRALIZED_FLAT = "Decentralized-Flat"
    HIERARCHICAL = "Hierarchical"
    DYNAMIC = "Dynamic"


class CommunicationProtocol(str, Enum):
    NATURAL_LANGUAGE = "NaturalLanguage"
    STRUCTURED_ARTIFACTS = "StructuredArtifacts"
    SHARED_MEMORY = "SharedMemory"
    EVENT_BUS = "EventBus"


class ConflictResolution(str, Enum):
    ARBITRATOR = "Arbitrator"
    VOTING = "Voting"
    DEBATE = "Debate"
    CONSENSUS = "Consensus"
    METACOGNITIVE = "Metacognitive"


class TaskDecomposition(str, Enum):
    NONE = "None"
    PREDEFINED = "Predefined"
    LLM_PLANNED = "LLMPlanned"
    ADAPTIVE = "Adaptive"


@dataclass(frozen=True)
class Strategy:
    name: str
    topology: Topology
    communication: CommunicationProtocol
    resolution: ConflictResolution
    decomposition: TaskDecomposition


STRATEGIES: List[Strategy] = [
    Strategy("S1-Solo", Topology.CENTRALIZED, CommunicationProtocol.NATURAL_LANGUAGE, ConflictResolution.ARBITRATOR, TaskDecomposition.NONE),
    Strategy("S2-SoloSelfRefine", Topology.CENTRALIZED, CommunicationProtocol.STRUCTURED_ARTIFACTS, ConflictResolution.METACOGNITIVE, TaskDecomposition.LLM_PLANNED),
    Strategy("S3-SequentialChain", Topology.CENTRALIZED, CommunicationProtocol.STRUCTURED_ARTIFACTS, ConflictResolution.CONSENSUS, TaskDecomposition.PREDEFINED),
    Strategy("S4-Hierarchical", Topology.HIERARCHICAL, CommunicationProtocol.STRUCTURED_ARTIFACTS, ConflictResolution.ARBITRATOR, TaskDecomposition.PREDEFINED),
    Strategy("S5-Debate", Topology.DECENTRALIZED_FLAT, CommunicationProtocol.NATURAL_LANGUAGE, ConflictResolution.DEBATE, TaskDecomposition.LLM_PLANNED),
    Strategy("S6-MajorityVoting", Topology.DECENTRALIZED_FLAT, CommunicationProtocol.EVENT_BUS, ConflictResolution.VOTING, TaskDecomposition.NONE),
    Strategy("S7-SharedMemory", Topology.DYNAMIC, CommunicationProtocol.SHARED_MEMORY, ConflictResolution.CONSENSUS, TaskDecomposition.ADAPTIVE),
    Strategy("S8-SupervisorWorker", Topology.HIERARCHICAL, CommunicationProtocol.EVENT_BUS, ConflictResolution.ARBITRATOR, TaskDecomposition.ADAPTIVE),
    Strategy("S9-AdaptiveSwarm", Topology.DYNAMIC, CommunicationProtocol.SHARED_MEMORY, ConflictResolution.METACOGNITIVE, TaskDecomposition.ADAPTIVE),
]


FRAMEWORK_MAP: Dict[str, Strategy] = {
    "autogen": Strategy("AutoGen", Topology.DYNAMIC, CommunicationProtocol.EVENT_BUS, ConflictResolution.CONSENSUS, TaskDecomposition.ADAPTIVE),
    "crewai": Strategy("CrewAI", Topology.HIERARCHICAL, CommunicationProtocol.STRUCTURED_ARTIFACTS, ConflictResolution.ARBITRATOR, TaskDecomposition.PREDEFINED),
    "metagpt": Strategy("MetaGPT", Topology.HIERARCHICAL, CommunicationProtocol.STRUCTURED_ARTIFACTS, ConflictResolution.ARBITRATOR, TaskDecomposition.PREDEFINED),
    "langgraph": Strategy("LangGraph", Topology.DYNAMIC, CommunicationProtocol.EVENT_BUS, ConflictResolution.CONSENSUS, TaskDecomposition.LLM_PLANNED),
    "swarm": Strategy("Swarm", Topology.DECENTRALIZED_FLAT, CommunicationProtocol.SHARED_MEMORY, ConflictResolution.METACOGNITIVE, TaskDecomposition.ADAPTIVE),
    "devin": Strategy("Devin", Topology.CENTRALIZED, CommunicationProtocol.NATURAL_LANGUAGE, ConflictResolution.ARBITRATOR, TaskDecomposition.LLM_PLANNED),
}


def classify(framework_name: str) -> Strategy:
    key = framework_name.strip().lower()
    if key not in FRAMEWORK_MAP:
        supported = ", ".join(sorted(FRAMEWORK_MAP.keys()))
        raise ValueError(f"Unsupported framework '{framework_name}'. Supported: {supported}")
    return FRAMEWORK_MAP[key]


if __name__ == "__main__":
    print(classify("MetaGPT"))
