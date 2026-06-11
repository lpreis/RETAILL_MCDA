import copy
import json
import unittest

from core.calculation import evaluate_phase, get_level, normalize_weights, robustness_summary, sensitivity_scenarios
from core.models import Level
from core.sample_data import create_fruit_supplier_analysis
from core.storage import analysis_to_json


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

    def test_custom_three_level_scale_is_used_for_scores(self):
        analysis = copy.deepcopy(self.analysis)
        analysis.levels = [
            Level(code="BOM", name="Bom", score=10, color="#49B051"),
            Level(code="OK", name="Ok", score=0, color="#EAF4EC"),
            Level(code="MAU", name="Mau", score=-10, color="#B71C1C"),
        ]
        analysis.criteria = analysis.criteria[:1]
        analysis.criteria[0].weight = 1
        analysis.semantic_scores = {
            "ALPHA": {"A1.1": "BOM"},
            "BETA": {"A1.1": "OK"},
            "GAMMA": {"A1.1": "MAU"},
            "DELTA": {"A1.1": "OK"},
        }
        analysis.scores = {}

        df = evaluate_phase(analysis, 1)

        self.assertEqual(df.iloc[0]["Alternativa"], "ALPHA")
        self.assertEqual(df.iloc[0]["Valor Global"], 10)
        self.assertEqual(df.iloc[-1]["Alternativa"], "GAMMA")
        self.assertEqual(df.iloc[-1]["Valor Global"], -10)

    def test_numeric_score_maps_to_closest_custom_level(self):
        analysis = copy.deepcopy(self.analysis)
        analysis.levels = [
            Level(code="HIGH", name="High", score=100, color="#49B051"),
            Level(code="MID", name="Mid", score=20, color="#EAF4EC"),
            Level(code="LOW", name="Low", score=-100, color="#B71C1C"),
        ]
        analysis.semantic_scores = {}
        analysis.scores = {"ALPHA": {"A1.1": 30}}

        self.assertEqual(get_level(analysis, "ALPHA", "A1.1"), "MID")

    def test_json_serializes_levels_once_at_top_level(self):
        data = json.loads(analysis_to_json(self.analysis))

        self.assertIn("levels", data)
        self.assertNotIn("scale", data)
        self.assertTrue(data["levels"])
        self.assertTrue(data["criteria"])
        self.assertNotIn("levels", data["criteria"][0])
        self.assertIn("id", data["alternatives"][0])
        self.assertIn("id", data["criteria"][0])
        self.assertIn("id", data["levels"][0])

    def test_json_serializes_score_maps_with_numeric_ids(self):
        data = json.loads(analysis_to_json(self.analysis))
        first_alternative_id = str(data["alternatives"][0]["id"])
        first_criterion_id = str(data["criteria"][0]["id"])

        self.assertIn(first_alternative_id, data["semantic_scores"])
        self.assertIn(first_criterion_id, data["semantic_scores"][first_alternative_id])
        self.assertIsInstance(data["semantic_scores"][first_alternative_id][first_criterion_id], int)


if __name__ == "__main__":
    unittest.main()
