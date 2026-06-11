from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import Alternative, Analysis, SEVEN_LEVEL_SCALE
from core.sample_data import create_fruit_supplier_analysis
from core.storage import save_analysis


def main() -> None:
    base = create_fruit_supplier_analysis()
    levels = ["MM", "M", "LM", "N", "LP", "P", "MP"]
    profiles = [
        ("Elite Premium", "Fornecedor excelente, com desempenho muito forte na maioria dos criterios.", 118000, ["MM", "LM", "MM", "M", "MM", "M"]),
        ("Bio Sustentavel", "Fornecedor muito sustentavel e fiavel, com custo elevado.", 125000, ["M", "LP", "M", "MM", "M", "LM"]),
        ("Preco Agressivo", "Fornecedor muito competitivo em custo, mas fraco em qualidade e sustentabilidade.", 52000, ["LP", "MM", "N", "P", "LP", "M"]),
        ("Local Flexivel", "Fornecedor local com boa rapidez, custo aceitavel e escala limitada.", 64000, ["N", "M", "M", "N", "LM", "LP"]),
        ("Industrial Grande", "Fornecedor de grande escala, forte em capacidade e preco.", 76000, ["LM", "M", "LM", "LP", "N", "MM"]),
        ("Risco Alto", "Fornecedor barato, mas com qualidade, reputacao e continuidade fracas.", 43000, ["P", "MM", "LP", "MP", "P", "LP"]),
        ("Gourmet Qualidade", "Fornecedor de fruta premium, caro e com capacidade media.", 132000, ["MM", "P", "M", "M", "M", "N"]),
        ("Importador Longo Curso", "Boa variedade e capacidade, mas prazos e pegada ambiental fracos.", 88000, ["M", "N", "P", "P", "N", "M"]),
        ("Cooperativa Verde", "Cooperativa sustentavel, fiavel e equilibrada.", 81000, ["M", "N", "LM", "MM", "M", "LM"]),
        ("Fornecedor Critico", "Fornecedor com desempenho muito fraco e risco operacional elevado.", 39000, ["MP", "LM", "P", "MP", "MP", "P"]),
    ]

    level_to_score = {level.code: level.score for level in SEVEN_LEVEL_SCALE}
    alternatives = []
    semantic_scores = {}
    scores = {}

    for index in range(50):
        label, description, base_cost, pattern = profiles[index % len(profiles)]
        cycle = index // len(profiles)
        name = f"FORN_{index + 1:02d}_{label.upper().replace(' ', '_')}"
        cost = base_cost + cycle * 3500 + (index % 5) * 1200
        alternatives.append(
            Alternative(
                name=name,
                description=f"{description} Perfil {index + 1} com variacao operacional {cycle + 1}.",
                cost=float(cost),
                selected_for_phase2=index < 12,
            )
        )

        adjusted = []
        for criterion_index, level in enumerate(pattern):
            level_index = levels.index(level)
            shift = ((index + criterion_index) % 3) - 1
            if index < 5:
                shift = min(shift, 0)
            if index >= 45:
                shift = max(shift, 0)
            adjusted.append(levels[min(max(level_index + shift, 0), len(levels) - 1)])

        semantic_scores[name] = {
            criterion.code: adjusted[criterion_index]
            for criterion_index, criterion in enumerate(base.criteria)
        }
        scores[name] = {
            criterion_code: level_to_score[level]
            for criterion_code, level in semantic_scores[name].items()
        }

    analysis = Analysis(
        name="Selecao de Fornecedores de Fruta - 50 Fornecedores",
        description="Exemplo alargado com 50 fornecedores de fruta com perfis muito diferentes, desde fornecedores excelentes ate fornecedores de alto risco e baixo desempenho.",
        context="Cenario de comparacao alargada para testar ranking, robustez, exportacoes e leitura/gravacao JSON com muitos fornecedores.",
        methodology="1fase",
        alternatives=alternatives,
        criteria=base.criteria,
        scores=scores,
        semantic_scores=semantic_scores,
        created_by="MCDA Moderno",
        notes="Dataset sintetico deterministico para testes de interface, exportacao e analise de sensibilidade com 50 fornecedores.",
    )
    path = save_analysis(analysis, "data/fornecedores_fruta_50_variado.json")
    print(f"Created {path} with {len(alternatives)} suppliers")


if __name__ == "__main__":
    main()
