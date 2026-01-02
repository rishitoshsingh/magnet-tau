from typing import List, Literal, Optional, Union

from pydantic import BaseModel


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
    user_id: str
    instruction: str
    persona: Persona

    def __repr__(self) -> str:
        return (
            f"TracerAgentOutput("
            f"user_id={self.user_id!r}, "
            f"instruction={self.instruction!r}, "
            f"persona={self.persona!r}"
            f")"
        )

class RunConfig(BaseModel):
    model_provider: str
    model: str
    verbose: bool = False
    env: str = "airline"
    temperature: float = 0.0
    start_index: int = 0
    end_index: int = None
    task_ids: Optional[List[int]] = None
    trace_path: str = "airline_adjacency_matrix_0.0_traces.json"
    output_dir: str = "output"
    seed: int = 10
    shuffle: int = 0
