import unittest

from core.calculation import evaluate_phase, normalize_weights, robustness_summary, sensitivity_scenarios
from core.sample_data import create_fruit_supplier_analysis


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.analysis = create_fruit_supplier_analysis()

    def test_normalize_weights(self):
        weights = normalize_weights(self.analysis.criteria)

        self.assertAlmostEqual(sum(weights.values()), 1.0)
        self.assertAlmostEqual(weights["A1.1"], 100 / 370)
        self.assertAlmostEqual(weights["A1.2"], 80 / 370)
        self.assertAlmostEqual(weights["A1.4"], 50 / 370)

    def test_base_ranking_matches_expected_example(self):
        df = evaluate_phase(self.analysis, 1)

        self.assertEqual(list(df["Alternativa"]), ["ALPHA", "BETA", "GAMMA", "DELTA"])
        self.assertAlmostEqual(df.iloc[0]["Valor Global"], 41.8919, places=4)
        self.assertAlmostEqual(df.iloc[1]["Valor Global"], 29.0541, places=4)
        self.assertAlmostEqual(df.iloc[2]["Valor Global"], 12.1622, places=4)
        self.assertAlmostEqual(df.iloc[3]["Valor Global"], -7.4324, places=4)

    def test_benefit_cost_uses_value_per_thousand_cost(self):
        df = evaluate_phase(self.analysis, 1)
        alpha = df[df["Alternativa"] == "ALPHA"].iloc[0]

        self.assertAlmostEqual(alpha["Benefício/Custo"], 41.8919 / 78, places=6)

    def test_sensitivity_scenarios_keep_alpha_as_winner(self):
        summary = robustness_summary(self.analysis, 1)

        self.assertEqual(set(summary["Vencedor"]), {"ALPHA"})
        self.assertTrue(summary["Mantém vencedor base?"].all())

    def test_sustainability_dominant_scenario_increases_gamma_value(self):
        scenarios = sensitivity_scenarios(self.analysis, 1)
        base_gamma = scenarios[
            (scenarios["Cenário"] == "Base") & (scenarios["Alternativa"] == "GAMMA")
        ].iloc[0]["Valor Global"]
        dominant_gamma = scenarios[
            (scenarios["Cenário"] == "D — Sustentabilidade dominante")
            & (scenarios["Alternativa"] == "GAMMA")
        ].iloc[0]["Valor Global"]

        self.assertGreater(dominant_gamma, base_gamma)


if __name__ == "__main__":
    unittest.main()
