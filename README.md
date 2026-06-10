# RETAILL_MCDA

## MMASSITI Moderno — Seleção de Fornecedores de Fruta

Protótipo funcional em Python inspirado no MMASSI/IT e adaptado ao exemplo MCDA de seleção de fornecedores de fruta. A aplicação corre localmente em Streamlit, guarda análises em JSON e calcula rankings multicritério por soma ponderada.

## Estado atual

Versão conceptual: `v0.1.0`

Estado: protótipo funcional inicial.

Inclui:

- Interface Streamlit com navegação por secções.
- Dashboard com contexto, ranking resumido, fornecedor recomendado e 8 etapas MMASSI/IT.
- Gestão de análises, fornecedores, critérios, pesos e avaliações.
- Escala semântica de 7 níveis: `MM`, `M`, `LM`, `N`, `LP`, `P`, `MP`.
- Ranking final por valor global.
- Métrica auxiliar benefício/custo.
- Cenários de sensibilidade e resumo de robustez.
- Menu lateral para criar, ler e gravar análises JSON, com nome da análise atual visível.
- Exportação da análise completa para CSV, Excel e PDF.
- Smoke test e testes unitários para os cálculos principais.

## Como executar

Instalar dependências:

```bash
pip install -r requirements.txt
```

Executar a aplicação:

```bash
streamlit run app.py
```

## Testes

Teste rápido do exemplo base:

```bash
python smoke_test.py
```

Testes unitários:

```bash
python -m unittest discover
```

## Modelo de decisão

A agregação segue a fórmula:

```text
Valor Global = soma(peso normalizado do critério × pontuação na escala de 7 níveis)
```

Os pesos podem ser introduzidos numa escala relativa. A aplicação normaliza automaticamente os pesos para soma 1.

## Dados de exemplo

O exemplo principal está em:

```text
data/fornecedores_fruta_alpha.json
```

Existe também um exemplo alargado com 50 fornecedores muito diferentes:

```text
data/fornecedores_fruta_50_variado.json
```

Com os dados base, o ranking esperado é:

| Ranking | Alternativa | Valor Global aproximado |
|---:|---|---:|
| 1 | ALPHA | 41.89 |
| 2 | BETA | 29.05 |
| 3 | GAMMA | 12.16 |
| 4 | DELTA | -7.43 |

Fornecedor recomendado: `ALPHA`.

## Screenshots

Ainda não há screenshots versionadas no repositório. Quando existirem, devem ser adicionadas a uma pasta `screenshots/` e referenciadas aqui.

## Próximos passos

- Validar o exemplo com utilizadores.
- Melhorar a análise de sensibilidade com cenários configuráveis.
- Melhorar os modelos de exportação Excel/PDF.
- Comparar outputs com referências da aplicação legacy, caso fiquem disponíveis.
