# Copyright Sierra

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel
from typing import Literal


class Persona(BaseModel):
    emotional_state: Literal[
        "angry",
        "stressed",
        "calm",
        "anxious",
        "confused",
        "impatient",
        "polite",
    ]
    urgency: Literal["low", "medium", "high"]
    communication_style: Literal[
        "brief",
        "detailed",
        "persistent",
        "cooperative",
        "demanding",
    ]


class TracerAgentOutput(BaseModel):
    """Final JSON emitted by the generator agent.

    `trace` is a list of TURNs: [[TURN1],[TURN2],...]. The generator must emit one
    instruction per TURN, each containing all required params needed to execute
    that TURN's tool calls.
    """

    user_id: str
    instructions: List[str]
    story: str
    persona: Persona


class Action(BaseModel):
    name: str
    kwargs: Dict[str, Any]


class GeneratedTaskCandidate(BaseModel):
    # Candidate produced by the generator agent from a tool trace
    user_id: str
    instructions: List[str]
    story: str
    persona: Persona
    action_trace: Any  # raw trace JSON
    attempt: int = 0
    verifier_feedback: Optional[str] = None


class VerificationReport(BaseModel):
    solved: bool
    termination_reason: str
    stop_seen: bool
    max_steps_hit: bool
    tool_errors: List[Dict[str, Any]]
    unknown_actions: List[Dict[str, Any]]
    critique: str
    transcript: List[Dict[str, Any]]
    actions: List[Action]


RESPOND_ACTION_NAME = "respond"
RESPOND_ACTION_FIELD_NAME = "content"


class Task(BaseModel):
    user_id: str
    actions: List[Action]
    instruction: Union[str, List[str]]
    outputs: List[str]


class RewardOutputInfo(BaseModel):
    r_outputs: float
    outputs: Dict[str, bool]


class RewardActionInfo(BaseModel):
    r_actions: float
    gt_data_hash: str


class RewardResult(BaseModel):
    reward: float
    info: Union[RewardOutputInfo, RewardActionInfo]
    actions: List[Action]


class SolveResult(BaseModel):
    reward: float
    messages: List[Dict[str, Any]]
    info: Dict[str, Any]
    total_cost: Optional[float] = None


class EnvInfo(BaseModel):
    task: Task
    source: Optional[str] = None
    user_cost: Optional[float] = None
    reward_info: Optional[RewardResult] = None


class EnvResponse(BaseModel):
    observation: str
    reward: float
    done: bool
    info: EnvInfo


class EnvResetResponse(BaseModel):
    observation: str
    info: EnvInfo


class EnvRunResult(BaseModel):
    task_id: int
    reward: float
    info: Dict[str, Any]
    traj: List[Dict[str, Any]]
    trial: int


class RunConfig(BaseModel):
    model_provider: str
    user_model_provider: str
    model: str
    user_model: str = "gpt-4o"
    num_trials: int = 1
    env: str = "retail"
    agent_strategy: str = "tool-calling"
    temperature: float = 0.0
    task_split: str = "test"
    start_index: int = 0
    end_index: int = -1
    task_ids: Optional[List[int]] = None
    log_dir: str = "results"
    max_concurrency: int = 1
    seed: int = 10
    shuffle: int = 0
    user_strategy: str = "llm"
    few_shot_displays_path: Optional[str] = None
