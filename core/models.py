from __future__ import annotations

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


Phase = Literal[1, 2]


class Level(BaseModel):
    code: str = "N"
    name: str = "Neutro"
    score: float = 0.0
    color: str = "#EAF4EC"
    description: str = ""


class Criterion(BaseModel):
    code: str
    name: str
    phase: Phase = 1
    selected: bool = True
    description: str = ""
    order: int = 0
    weight: float = 1.0
    is_cost: bool = False
    neutral_level: Optional[str] = "N"
    best_level: Optional[str] = "MM"
    levels: List[Level] = Field(default_factory=list)


class Alternative(BaseModel):
    name: str
    description: str = ""
    cost: float = 0.0
    selected_for_phase2: bool = False


class Analysis(BaseModel):
    name: str = "Nova análise"
    description: str = ""
    context: str = ""
    methodology: Literal["1fase", "2fases", "1e2fases"] = "1fase"
    alternatives: List[Alternative] = Field(default_factory=list)
    criteria: List[Criterion] = Field(default_factory=list)

    scores: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    semantic_scores: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    created_by: str = ""
    notes: str = ""


SEVEN_LEVEL_SCALE: List[Level] = [
    Level(code="MM", name="Muito Melhor", score=100, color="#0B6623"),
    Level(code="M", name="Melhor", score=50, color="#2F8F3A"),
    Level(code="LM", name="Ligeiramente Melhor", score=25, color="#74BF7B"),
    Level(code="N", name="Neutro", score=0, color="#EAF4EC"),
    Level(code="LP", name="Ligeiramente Pior", score=-25, color="#F7D08A"),
    Level(code="P", name="Pior", score=-50, color="#E6A4A4"),
    Level(code="MP", name="Muito Pior", score=-100, color="#B71C1C"),
]


def level_score(level_code: str) -> float:
    for level in SEVEN_LEVEL_SCALE:
        if level.code == level_code:
            return level.score
    return 0.0


def level_name(level_code: str) -> str:
    for level in SEVEN_LEVEL_SCALE:
        if level.code == level_code:
            return level.name
    return level_code
