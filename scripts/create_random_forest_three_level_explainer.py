from collections import Counter

from sklearn.tree import DecisionTreeClassifier


FEATURE_NAMES = (
    "magnitude",
    "depth_km",
    "longitude",
    "latitude",
    "month",
    "hour",
)

FEATURE_LABELS = {
    "magnitude": "震級",
    "depth_km": "深度",
    "longitude": "經度",
    "latitude": "緯度",
    "month": "月份",
    "hour": "時刻",
}

LOCATION_FEATURE_INDICES = frozenset((2, 3))
EXPECTED_CLASS_LABELS = frozenset(range(8))


def _validate_model(model):
    estimators = getattr(model, "estimators_", None)
    if not estimators:
        raise ValueError("Model must expose non-empty estimators_")

    if getattr(model, "n_features_in_", None) != len(FEATURE_NAMES):
        raise ValueError("Model must have six input features")

    classes = getattr(model, "classes_", None)
    if classes is None or len(classes) == 0:
        raise ValueError("Model must expose non-empty classes_")
    if not set(classes).issubset(EXPECTED_CLASS_LABELS):
        raise ValueError("Model classes must be compatible with 0-7")

    return estimators


def _nodes_through_depth(tree, max_depth=2):
    nodes = []
    pending = [(0, 0)]
    tree_data = tree.tree_
    while pending:
        node_id, depth = pending.pop()
        nodes.append((node_id, depth))
        if depth == max_depth:
            continue
        left_child = int(tree_data.children_left[node_id])
        if left_child == -1:
            continue
        right_child = int(tree_data.children_right[node_id])
        pending.append((right_child, depth + 1))
        pending.append((left_child, depth + 1))
    return nodes


def _count_nodes_through_depth_two(tree):
    return len(_nodes_through_depth(tree))


def _count_location_splits_through_depth_two(tree):
    tree_data = tree.tree_
    return sum(
        int(tree_data.feature[node_id]) in LOCATION_FEATURE_INDICES
        for node_id, _ in _nodes_through_depth(tree)
        if int(tree_data.children_left[node_id]) != -1
    )


def select_representative_tree(model) -> tuple[int, DecisionTreeClassifier]:
    """Return the most readable deterministic representative forest tree."""
    estimators = _validate_model(model)
    root_features = [int(estimator.tree_.feature[0]) for estimator in estimators]
    most_common_root_feature = Counter(root_features).most_common(1)[0][0]

    ranked_estimators = []
    for estimator_index, estimator in enumerate(estimators):
        root_feature = int(estimator.tree_.feature[0])
        rank = (
            root_feature != most_common_root_feature,
            -_count_nodes_through_depth_two(estimator),
            _count_location_splits_through_depth_two(estimator),
            estimator_index,
        )
        ranked_estimators.append((rank, estimator_index, estimator))

    _, estimator_index, estimator = min(ranked_estimators)
    return estimator_index, estimator


def extract_three_levels(estimator, feature_names, class_labels) -> list[dict]:
    """Extract root through depth two in left-to-right traversal order."""
    if not class_labels:
        raise ValueError("class_labels must not be empty")

    tree_data = estimator.tree_
    nodes = []
    pending = [(0, None, None, 0)]
    while pending:
        node_id, parent_id, branch, depth = pending.pop()
        left_child = int(tree_data.children_left[node_id])
        is_leaf = left_child == -1
        feature_index = None if is_leaf else int(tree_data.feature[node_id])
        class_counts = tuple(float(value) for value in tree_data.value[node_id][0])
        class_index = max(range(len(class_counts)), key=class_counts.__getitem__)

        nodes.append(
            {
                "node_id": int(node_id),
                "parent_id": parent_id,
                "branch": branch,
                "depth": depth,
                "feature_index": feature_index,
                "feature_name": (
                    None if feature_index is None else feature_names[feature_index]
                ),
                "threshold": (
                    None
                    if feature_index is None
                    else float(tree_data.threshold[node_id])
                ),
                "samples": int(tree_data.n_node_samples[node_id]),
                "dominant_class": int(class_labels[class_index]),
                "class_counts": class_counts,
                "is_leaf": is_leaf,
            }
        )

        if is_leaf or depth == 2:
            continue
        right_child = int(tree_data.children_right[node_id])
        pending.append((right_child, node_id, "no", depth + 1))
        pending.append((left_child, node_id, "yes", depth + 1))

    return nodes
