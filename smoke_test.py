from core.storage import load_analysis
from core.calculation import evaluate_phase, sensitivity_scenarios, robustness_summary

a = load_analysis("data/fornecedores_fruta_alpha.json")
df = evaluate_phase(a, 1)
print(df[["Ranking", "Alternativa", "Valor Global", "Benefício/Custo"]])
assert df.iloc[0]["Alternativa"] == "ALPHA"

sens = sensitivity_scenarios(a, 1)
print(sens)
assert not sens.empty

rob = robustness_summary(a, 1)
print(rob)
