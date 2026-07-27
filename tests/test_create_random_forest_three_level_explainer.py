import unittest

from sklearn.ensemble import RandomForestClassifier

from scripts.create_random_forest_three_level_explainer import (
    FEATURE_LABELS,
    FEATURE_NAMES,
    extract_three_levels,
    select_representative_tree,
)


def fitted_model():
    features = []
    labels = []
    for repetition in range(6):
        for intensity in range(8):
            features.append(
                [
                    3.0 + intensity + repetition / 100,
                    5.0 + (intensity % 3) + repetition / 10,
                    120.0 + intensity / 10,
                    22.0 + repetition / 10,
                    float((intensity % 12) + 1),
                    float((repetition * 3 + intensity) % 24),
                ]
            )
            labels.append(intensity)

    model = RandomForestClassifier(
        n_estimators=9,
        max_depth=4,
        random_state=42,
    )
    model.fit(features, labels)
    return model


class RepresentativeTreeExtractionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = fitted_model()

    def test_selection_is_deterministic(self):
        index_a, tree_a = select_representative_tree(self.model)
        index_b, tree_b = select_representative_tree(self.model)

        self.assertEqual(index_a, index_b)
        self.assertIs(tree_a, tree_b)

    def test_feature_labels_match_the_presentation_contract(self):
        self.assertEqual(
            FEATURE_LABELS,
            {
                "magnitude": "\u9707\u7d1a",
                "depth_km": "\u6df1\u5ea6",
                "longitude": "\u7d93\u5ea6",
                "latitude": "\u7def\u5ea6",
                "month": "\u6708\u4efd",
                "hour": "\u6642\u523b",
            },
        )

    def test_extraction_matches_estimator_values_at_first_three_levels(self):
        _, tree = select_representative_tree(self.model)

        nodes = extract_three_levels(tree, FEATURE_NAMES, list(self.model.classes_))

        self.assertLessEqual(len(nodes), 7)
        self.assertEqual(nodes[0]["depth"], 0)
        self.assertTrue(all(node["depth"] <= 2 for node in nodes))
        self.assertEqual(
            [node["node_id"] for node in nodes],
            sorted(node["node_id"] for node in nodes),
        )
        self.assertTrue(
            any(node["depth"] == 2 and not node["is_leaf"] for node in nodes)
        )

        for node in nodes:
            tree_node = tree.tree_
            expected_counts = tuple(
                float(value) for value in tree_node.value[node["node_id"]][0]
            )
            expected_dominant_class = int(
                self.model.classes_[
                    max(range(len(expected_counts)), key=expected_counts.__getitem__)
                ]
            )
            self.assertEqual(
                node["samples"], int(tree_node.n_node_samples[node["node_id"]])
            )
            self.assertEqual(node["dominant_class"], expected_dominant_class)
            self.assertEqual(node["class_counts"], expected_counts)

            if not node["is_leaf"]:
                self.assertEqual(
                    node["feature_index"], int(tree_node.feature[node["node_id"]])
                )
                self.assertEqual(
                    node["threshold"], float(tree_node.threshold[node["node_id"]])
                )

        positions = {node["node_id"]: index for index, node in enumerate(nodes)}
        for node in nodes:
            if node["parent_id"] is not None:
                self.assertLess(positions[node["parent_id"]], positions[node["node_id"]])
        for parent_id in {
            node["parent_id"] for node in nodes if node["parent_id"] is not None
        }:
            children = [node for node in nodes if node["parent_id"] == parent_id]
            if len(children) == 2:
                self.assertEqual([child["branch"] for child in children], ["yes", "no"])


class RepresentativeTreeValidationTest(unittest.TestCase):
    def test_rejects_model_with_wrong_feature_count(self):
        model = RandomForestClassifier(n_estimators=1, random_state=42)
        model.fit([[0, 1, 2, 3, 4], [1, 2, 3, 4, 5]], [0, 1])

        with self.assertRaisesRegex(ValueError, "six input features"):
            select_representative_tree(model)


if __name__ == "__main__":
    unittest.main()
