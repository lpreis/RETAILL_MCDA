from __future__ import annotations

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, model_validator


Phase = Literal[1, 2]


class Level(BaseModel):
    id: int = 0
    code: str = "N"
    name: str = "Neutro"
    score: float = 0.0
    color: str = "#EAF4EC"
    description: str = ""


class Criterion(BaseModel):
    id: int = 0
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
    id: int = 0
    name: str
    description: str = ""
    cost: float = 0.0
    selected_for_phase2: bool = False


SEVEN_LEVEL_SCALE: List[Level] = [
    Level(id=1, code="MM", name="Muito Melhor", score=100, color="#0B6623"),
    Level(id=2, code="M", name="Melhor", score=50, color="#2F8F3A"),
    Level(id=3, code="LM", name="Ligeiramente Melhor", score=25, color="#74BF7B"),
    Level(id=4, code="N", name="Neutro", score=0, color="#EAF4EC"),
    Level(id=5, code="LP", name="Ligeiramente Pior", score=-25, color="#F7D08A"),
    Level(id=6, code="P", name="Pior", score=-50, color="#E6A4A4"),
    Level(id=7, code="MP", name="Muito Pior", score=-100, color="#B71C1C"),
]


def default_scale() -> List[Level]:
    return [level.model_copy(deep=True) for level in SEVEN_LEVEL_SCALE]


class Analysis(BaseModel):
    name: str = "Nova análise"
    description: str = ""
    context: str = ""
    methodology: Literal["1fase", "2fases", "1e2fases"] = "1fase"
    alternatives: List[Alternative] = Field(default_factory=list)
    criteria: List[Criterion] = Field(default_factory=list)
    levels: List[Level] = Field(default_factory=default_scale)

    scores: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    semantic_scores: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    created_by: str = ""
    notes: str = ""

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_levels_and_indexed_scores(cls, data):
        if not isinstance(data, dict):
            return data
        if not data.get("levels"):
            if data.get("scale"):
                data["levels"] = data["scale"]
            else:
                for criterion in data.get("criteria", []):
                    if isinstance(criterion, dict) and criterion.get("levels"):
                        data["levels"] = criterion["levels"]
                        break
        _ensure_ids(data.get("alternatives", []))
        _ensure_ids(data.get("criteria", []))
        _ensure_ids(data.get("levels", []))
        _migrate_indexed_score_maps(data)
        return data

    @model_validator(mode="after")
    def ensure_runtime_ids(self):
        _assign_model_ids(self.alternatives)
        _assign_model_ids(self.criteria)
        _assign_model_ids(self.levels)
        return self


def _assign_model_ids(items) -> None:
    used_ids = {item.id for item in items if getattr(item, "id", 0) > 0}
    next_id = 1
    for item in items:
        if getattr(item, "id", 0) > 0:
            continue
        while next_id in used_ids:
            next_id += 1
        item.id = next_id
        used_ids.add(next_id)
        next_id += 1


def _ensure_ids(items) -> None:
    if not isinstance(items, list):
        return
    used_ids = {item.get("id") for item in items if isinstance(item, dict) and isinstance(item.get("id"), int) and item.get("id", 0) > 0}
    next_id = 1
    for item in items:
        if not isinstance(item, dict):
            continue
        current = item.get("id")
        if isinstance(current, int) and current > 0:
            continue
        while next_id in used_ids:
            next_id += 1
        item["id"] = next_id
        used_ids.add(next_id)
        next_id += 1


def _migrate_indexed_score_maps(data: dict) -> None:
    alternatives = data.get("alternatives", [])
    criteria = data.get("criteria", [])
    levels = data.get("levels", [])
    alternative_names_by_id = {
        str(item.get("id")): item.get("name")
        for item in alternatives
        if isinstance(item, dict) and item.get("id") and item.get("name")
    }
    criterion_codes_by_id = {
        str(item.get("id")): item.get("code")
        for item in criteria
        if isinstance(item, dict) and item.get("id") and item.get("code")
    }
    level_codes_by_id = {
        str(item.get("id")): item.get("code")
        for item in levels
        if isinstance(item, dict) and item.get("id") and item.get("code")
    }

    def convert_outer_key(key):
        return alternative_names_by_id.get(str(key), str(key))

    def convert_inner_key(key):
        return criterion_codes_by_id.get(str(key), str(key))

    converted_scores = {}
    for alternative_key, criterion_scores in (data.get("scores") or {}).items():
        if not isinstance(criterion_scores, dict):
            continue
        converted_scores[convert_outer_key(alternative_key)] = {
            convert_inner_key(criterion_key): value
            for criterion_key, value in criterion_scores.items()
        }
    data["scores"] = converted_scores

    converted_semantic_scores = {}
    for alternative_key, criterion_scores in (data.get("semantic_scores") or {}).items():
        if not isinstance(criterion_scores, dict):
            continue
        converted_semantic_scores[convert_outer_key(alternative_key)] = {
            convert_inner_key(criterion_key): level_codes_by_id.get(str(level_key), str(level_key))
            for criterion_key, level_key in criterion_scores.items()
        }
    data["semantic_scores"] = converted_semantic_scores

def scale_for_analysis(analysis: Analysis | None = None) -> List[Level]:
    if analysis is not None and analysis.levels:
        return analysis.levels
    return SEVEN_LEVEL_SCALE


def neutral_level_code(scale: List[Level]) -> str:
    if not scale:
        return "N"
    for level in scale:
        if level.code == "N":
            return level.code
    return min(scale, key=lambda level: abs(level.score)).code


def closest_level_code(score: float, scale: List[Level] | None = None) -> str:
    active_scale = scale or SEVEN_LEVEL_SCALE
    if not active_scale:
        return "N"
    return min(active_scale, key=lambda level: abs(level.score - score)).code


def level_score(level_code: str, scale: List[Level] | None = None) -> float:
    active_scale = scale or SEVEN_LEVEL_SCALE
    for level in active_scale:
        if level.code == level_code:
            return level.score
    return 0.0


def level_name(level_code: str, scale: List[Level] | None = None) -> str:
    active_scale = scale or SEVEN_LEVEL_SCALE
    for level in active_scale:
        if level.code == level_code:
            return level.name
    return level_code
