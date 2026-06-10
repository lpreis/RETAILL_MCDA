from __future__ import annotations

from typing import Dict, List
import copy
import pandas as pd

from .models import Analysis, Criterion, Phase, level_score


def selected_criteria(analysis: Analysis, phase: Phase) -> List[Criterion]:
    return sorted(
        [c for c in analysis.criteria if c.selected and c.phase == phase],
        key=lambda c: (c.order, c.code),
    )


def normalize_weights(criteria: List[Criterion]) -> Dict[str, float]:
    if not criteria:
        return {}

    total = sum(max(0.0, c.weight) for c in criteria)
    if total <= 0:
        equal = 1.0 / len(criteria)
        return {c.code: equal for c in criteria}

    return {c.code: max(0.0, c.weight) / total for c in criteria}


def get_score(analysis: Analysis, alternative_name: str, criterion_code: str) -> float:
    semantic = analysis.semantic_scores.get(alternative_name, {}).get(criterion_code)
    if semantic:
        return level_score(semantic)

    return float(analysis.scores.get(alternative_name, {}).get(criterion_code, 0.0))


def get_level(analysis: Analysis, alternative_name: str, criterion_code: str) -> str:
    semantic = analysis.semantic_scores.get(alternative_name, {}).get(criterion_code)
    if semantic:
        return semantic

    value = float(analysis.scores.get(alternative_name, {}).get(criterion_code, 0.0))
    if value >= 75: return "MM"
    if value >= 37.5: return "M"
    if value >= 12.5: return "LM"
    if value > -12.5: return "N"
    if value > -37.5: return "LP"
    if value > -75: return "P"
    return "MP"


def evaluate_phase(analysis: Analysis, phase: Phase) -> pd.DataFrame:
    criteria = selected_criteria(analysis, phase)
    weights = normalize_weights(criteria)

    rows = []
    for alt in analysis.alternatives:
        total = 0.0
        detail = {}

        for criterion in criteria:
            score = get_score(analysis, alt.name, criterion.code)
            contribution = score * weights.get(criterion.code, 0.0)
            total += contribution

            level = get_level(analysis, alt.name, criterion.code)
            detail[f"{criterion.code} nível"] = level
            detail[f"{criterion.code} pontuação"] = score
            detail[f"{criterion.code} contribuição"] = round(contribution, 4)

        benefit_cost = None
        if alt.cost and alt.cost > 0:
            benefit_cost = total / (alt.cost / 1000.0)

        rows.append({
            "Alternativa": alt.name,
            "Fase": phase,
            "Valor Global": round(total, 4),
            "Custo": alt.cost,
            "Benefício/Custo": round(benefit_cost, 6) if benefit_cost is not None else None,
            **detail,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.sort_values(["Valor Global", "Benefício/Custo"], ascending=[False, False], na_position="last")
    df.insert(0, "Ranking", range(1, len(df) + 1))
    return df.reset_index(drop=True)


def evaluate_all(analysis: Analysis) -> Dict[int, pd.DataFrame]:
    result = {}
    for phase in (1, 2):
        if selected_criteria(analysis, phase):
            result[phase] = evaluate_phase(analysis, phase)
    return result


def criterion_contributions(analysis: Analysis, phase: Phase) -> pd.DataFrame:
    criteria = selected_criteria(analysis, phase)
    weights = normalize_weights(criteria)
    rows = []
    for alt in analysis.alternatives:
        for criterion in criteria:
            score = get_score(analysis, alt.name, criterion.code)
            rows.append({
                "Alternativa": alt.name,
                "Critério": criterion.code,
                "Nome": criterion.name,
                "Peso normalizado": weights.get(criterion.code, 0.0),
                "Pontuação": score,
                "Contribuição": score * weights.get(criterion.code, 0.0),
            })
    return pd.DataFrame(rows)


def apply_weight_scenario(analysis: Analysis, phase: Phase, weights_by_code: Dict[str, float]) -> Analysis:
    modified = copy.deepcopy(analysis)
    for criterion in modified.criteria:
        if criterion.phase == phase and criterion.code in weights_by_code:
            criterion.weight = float(weights_by_code[criterion.code])
    return modified


def sensitivity_scenarios(analysis: Analysis, phase: Phase) -> pd.DataFrame:
    base_criteria = selected_criteria(analysis, phase)
    current = {c.code: c.weight for c in base_criteria}

    scenarios = {
        "Base": current,
        "A — Pesos iguais": {c.code: 1 for c in base_criteria},
        "B — +10% Qualidade": {**current, "A1.1": current.get("A1.1", 1) + 10},
        "C — +10% Preço": {**current, "A1.2": current.get("A1.2", 1) + 10},
        "D — Sustentabilidade dominante": {**current, "A1.4": 100},
    }

    rows = []
    for scenario_name, weights in scenarios.items():
        modified = apply_weight_scenario(analysis, phase, weights)
        df = evaluate_phase(modified, phase)
        if df.empty:
            continue
        winner = df.iloc[0]["Alternativa"]
        for _, row in df.iterrows():
            rows.append({
                "Cenário": scenario_name,
                "Ranking": int(row["Ranking"]),
                "Alternativa": row["Alternativa"],
                "Valor Global": float(row["Valor Global"]),
                "Vencedor": winner,
            })
    return pd.DataFrame(rows)


def robustness_summary(analysis: Analysis, phase: Phase) -> pd.DataFrame:
    sens = sensitivity_scenarios(analysis, phase)
    if sens.empty:
        return pd.DataFrame()

    base_winner = sens[sens["Cenário"] == "Base"].sort_values("Ranking").iloc[0]["Alternativa"]

    rows = []
    for scenario in sens["Cenário"].unique():
        scenario_df = sens[sens["Cenário"] == scenario].sort_values("Ranking")
        winner = scenario_df.iloc[0]["Alternativa"]
        rows.append({
            "Cenário": scenario,
            "Vencedor": winner,
            "Mantém vencedor base?": winner == base_winner,
            "Conclusão": "Robusto" if winner == base_winner else "Sensível",
        })
    return pd.DataFrame(rows)
