from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import Analysis


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def analysis_to_dict(analysis: Analysis) -> dict:
    data = analysis.model_dump(exclude={"criteria": {"__all__": {"levels"}}})
    data.pop("scale", None)
    alternative_ids = {alternative.name: str(alternative.id) for alternative in analysis.alternatives}
    criterion_ids = {criterion.code: str(criterion.id) for criterion in analysis.criteria}
    level_ids = {level.code: level.id for level in analysis.levels}
    data["semantic_scores"] = {
        alternative_ids.get(alternative_name, alternative_name): {
            criterion_ids.get(criterion_code, criterion_code): level_ids.get(level_code, level_code)
            for criterion_code, level_code in criterion_scores.items()
        }
        for alternative_name, criterion_scores in analysis.semantic_scores.items()
    }
    data["scores"] = {
        alternative_ids.get(alternative_name, alternative_name): {
            criterion_ids.get(criterion_code, criterion_code): score
            for criterion_code, score in criterion_scores.items()
        }
        for alternative_name, criterion_scores in analysis.scores.items()
    }
    return data


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def list_analysis_files() -> List[Path]:
    ensure_data_dir()
    return sorted(DATA_DIR.glob("*.json"))


def load_analysis(path: str | Path) -> Analysis:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return Analysis.model_validate(raw)


def save_analysis(analysis: Analysis, path: str | Path | None = None) -> Path:
    ensure_data_dir()
    if path is None:
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in analysis.name).strip()
        if not safe_name:
            safe_name = "analysis"
        path = DATA_DIR / f"{safe_name}.json"
    else:
        path = Path(path)

    with path.open("w", encoding="utf-8") as f:
        json.dump(analysis_to_dict(analysis), f, ensure_ascii=False, indent=2)
    return path


def analysis_to_json(analysis: Analysis) -> str:
    return json.dumps(analysis_to_dict(analysis), ensure_ascii=False, indent=2)


def load_analysis_from_json_text(text: str) -> Analysis:
    raw = json.loads(text)
    return Analysis.model_validate(raw)
