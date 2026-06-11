from __future__ import annotations

from .models import Analysis, Alternative, Criterion, SEVEN_LEVEL_SCALE


def create_fruit_supplier_analysis() -> Analysis:
    criteria = [
        Criterion(
            code="A1.1",
            name="Qualidade da Fruta",
            phase=1,
            selected=True,
            description="Calibre, aspeto, grau Brix, ausência de defeitos e conformidade com normas.",
            order=1,
            weight=100,
            levels=SEVEN_LEVEL_SCALE,
            neutral_level="N",
            best_level="MM",
        ),
        Criterion(
            code="A1.2",
            name="Preço / Custo Total",
            phase=1,
            selected=True,
            description="Preço por kg, descontos por volume, custos de transporte e embalagem.",
            order=2,
            weight=80,
            is_cost=True,
            levels=SEVEN_LEVEL_SCALE,
            neutral_level="N",
            best_level="MM",
        ),
        Criterion(
            code="A1.3",
            name="Prazo de Entrega",
            phase=1,
            selected=True,
            description="Tempo médio de entrega, cumprimento de prazos e flexibilidade de agendamento.",
            order=3,
            weight=60,
            levels=SEVEN_LEVEL_SCALE,
            neutral_level="N",
            best_level="MM",
        ),
        Criterion(
            code="A1.4",
            name="Sustentabilidade",
            phase=1,
            selected=True,
            description="Certificações bio, pegada carbónica e práticas agrícolas responsáveis.",
            order=4,
            weight=50,
            levels=SEVEN_LEVEL_SCALE,
            neutral_level="N",
            best_level="MM",
        ),
        Criterion(
            code="A1.5",
            name="Fiabilidade / Reputação",
            phase=1,
            selected=True,
            description="Histórico de incidentes, referências de clientes e anos de experiência.",
            order=5,
            weight=40,
            levels=SEVEN_LEVEL_SCALE,
            neutral_level="N",
            best_level="MM",
        ),
        Criterion(
            code="A1.6",
            name="Capacidade de Fornecimento",
            phase=1,
            selected=True,
            description="Volume disponível, variedade de espécies e continuidade ao longo do ano.",
            order=6,
            weight=40,
            levels=SEVEN_LEVEL_SCALE,
            neutral_level="N",
            best_level="MM",
        ),
    ]

    alternatives = [
        Alternative(
            name="ALPHA",
            cost=78000,
            description="Fornecedor equilibrado, forte em qualidade, prazo e sustentabilidade.",
        ),
        Alternative(
            name="BETA",
            cost=65000,
            description="Fornecedor competitivo em preço e capacidade, com qualidade intermédia.",
        ),
        Alternative(
            name="GAMMA",
            cost=82000,
            description="Fornecedor muito sustentável, mas menos competitivo em preço e capacidade.",
        ),
        Alternative(
            name="DELTA",
            cost=59000,
            description="Fornecedor local de baixo custo, mas com limitações de qualidade e escala.",
        ),
    ]

    semantic_scores = {
        "ALPHA": {
            "A1.1": "M",
            "A1.2": "N",
            "A1.3": "MM",
            "A1.4": "M",
            "A1.5": "LM",
            "A1.6": "LM",
        },
        "BETA": {
            "A1.1": "LM",
            "A1.2": "M",
            "A1.3": "LM",
            "A1.4": "LP",
            "A1.5": "M",
            "A1.6": "M",
        },
        "GAMMA": {
            "A1.1": "N",
            "A1.2": "LP",
            "A1.3": "LM",
            "A1.4": "MM",
            "A1.5": "LM",
            "A1.6": "LP",
        },
        "DELTA": {
            "A1.1": "LP",
            "A1.2": "LM",
            "A1.3": "N",
            "A1.4": "LP",
            "A1.5": "N",
            "A1.6": "LP",
        },
    }

    level_to_score = {level.code: level.score for level in SEVEN_LEVEL_SCALE}
    scores = {
        alt: {crit: level_to_score[level] for crit, level in crits.items()}
        for alt, crits in semantic_scores.items()
    }

    return Analysis(
        name="Seleção de Fornecedores de Fruta",
        description="Modelo MCDA/MCDA para selecionar fornecedores de fruta numa cadeia de abastecimento.",
        context=(
            "Uma empresa de distribuição de fruta precisa selecionar fornecedores. "
            "A decisão envolve conflitos entre qualidade, preço, prazo, sustentabilidade, reputação e capacidade de fornecimento."
        ),
        methodology="1fase",
        alternatives=alternatives,
        criteria=criteria,
        scores=scores,
        semantic_scores=semantic_scores,
        created_by="MCDA Moderno",
        notes=(
            "Problema exemplo baseado nos slides de MCDA para fornecedores de fruta. "
            "Os pesos seguem a lógica A1.1=100, A1.2=80, A1.3=60, A1.4=50, A1.5=40, A1.6=40."
        ),
    )
