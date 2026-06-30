from med_bayes.utils.ds_interpretation.masses import Mass, make_mass
from med_bayes.utils.ds_interpretation.paths import (
    build_nx_graph,
    get_side_effect_ids,
    iter_drug_to_effect_paths,
    length_to_confidence,
)


def _confidence_label(width: float) -> str:
    if width < 0.20:
        return "high"
    if width < 0.40:
        return "medium"
    return "low"


def _risk_label(belief: float) -> str:
    if belief < 0.05:
        return "low"
    if belief < 0.20:
        return "moderate"
    return "high"


def _round(value: float) -> float:
    return round(float(value), 6)


def interpret_ds(
    graph_data: dict,
    selected_drug_ids: set[str],
    bayes_probs: dict[str, float],
) -> dict:
    """
    Интерпретация результата байесовской сети через теорию Демпстера-Шафера.

    graph_data: JSON-граф из GraphStorage.
    selected_drug_ids: UUID prepare-узлов, выбранных пользователем.
    bayes_probs: результат calculate_probabilities, то есть dict[id узла, float].
    """

    graph = build_nx_graph(graph_data)
    node_by_id = {
        node["id"]: node
        for node in graph_data.get("nodes", [])
    }

    side_effect_ids = get_side_effect_ids(graph_data)
    interpreted_effects = []

    for effect_id in side_effect_ids:
        effect_probability = float(bayes_probs.get(effect_id, 0.0))

        combined_mass: Mass | None = None
        paths_info = []

        for drug_id in selected_drug_ids:
            drug_node = node_by_id.get(drug_id)
            if not drug_node:
                continue

            for path in iter_drug_to_effect_paths(graph, drug_id, effect_id):
                path_length = len(path) - 1
                confidence = length_to_confidence(path_length)

                path_mass = make_mass(
                    probability=effect_probability,
                    confidence=confidence,
                )

                combined_mass = (
                    path_mass
                    if combined_mass is None
                    else combined_mass.combine(path_mass)
                )

                paths_info.append({
                    "drug_id": drug_id,
                    "drug_name": drug_node.get("name"),
                    "length": path_length,
                    "confidence": confidence,
                    "node_ids": path,
                    "node_names": [
                        node_by_id.get(node_id, {}).get("name", node_id)
                        for node_id in path
                    ],
                })

        if combined_mass is None:
            continue

        belief = combined_mass.belief
        plausibility = combined_mass.plausibility
        uncertainty = combined_mass.uncertainty

        effect_node = node_by_id.get(effect_id, {})

        interpreted_effects.append({
            "effect_id": effect_id,
            "se_name": effect_node.get("name", effect_id),
            "bayes_probability": _round(effect_probability),
            "belief": _round(belief),
            "plausibility": _round(plausibility),
            "uncertainty": _round(uncertainty),
            "mass": {
                "H": _round(combined_mass.m_h),
                "not_H": _round(combined_mass.m_not_h),
                "unknown": _round(combined_mass.m_unknown),
            },
            "risk_level": _risk_label(belief),
            "confidence_level": _confidence_label(uncertainty),
            "paths": paths_info,
        })

    interpreted_effects.sort(
        key=lambda item: (
            item["belief"],
            item["bayes_probability"],
        ),
        reverse=True,
    )

    return {
        "method": "dempster_shafer_classic",
        "frame": ["H", "not_H"],
        "selected_drugs": list(selected_drug_ids),
        "effects": interpreted_effects,
    }
