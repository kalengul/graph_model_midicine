"""
Интерпретация выхода байесовской сети через теорию Демпстера-Шафера.

Комбинирование выполняется в три уровня, чтобы не нарушать
предположение о независимости источников:

  Уровень 1 (внутри кластера одного препарата).
      Пути, расходящиеся после общего узла-механизма, — одно и то же
      свидетельство, пересказанное несколько раз разной длины.
      Берём представителя с максимальным k (кратчайший путь в
      кластере), остальные не комбинируем.

  Уровень 2 (между кластерами одного препарата).
      Разные механизмы действия одного вещества независимы друг
      от друга в разумном приближении — комбинируются правилом
      Демпстера.

  Уровень 3 (между препаратами).
      Независимость обоснована лучше всего, но не гарантирована
      (общие пути метаболизма, общие ферменты и т.п.) —
      комбинируется правилом Ягера: конфликт уходит в
      неопределённость, а не отбрасывается, что даёт более
      консервативную (для медицинской задачи — более безопасную)
      оценку.

Разделение на структурный слой (paths.py — поиск путей и
кластеризация, зависит только от графа) и вероятностный слой
(этот модуль — зависит от текущих final_probs) сделано осознанно:
первый можно кэшировать между запросами с одинаковой комбинацией
препаратов, второй пересчитывается на каждый запрос.
"""

from typing import Any

import networkx as nx

from med_bayes.utils.ds_interpretation.masses import Mass, make_mass, vacuous_mass
from med_bayes.utils.ds_interpretation.paths import (
    DrugEffectPath,
    build_nx_graph,
    find_clustered_paths,
)

SIDE_EFFECT_LABELS = {"side_e", "side_effect", "effect"}


def _side_effects(graph_data: dict) -> dict[str, str]:
    """id → name только для side-effect-узлов."""
    return {
        n["id"]: n["name"]
        for n in graph_data["nodes"]
        if n.get("label") in SIDE_EFFECT_LABELS
    }


def _ru_count(n: int, one: str, few: str, many: str) -> str:
    """Русское согласование числительного с существительным."""
    n_abs = abs(n) % 100
    if 11 <= n_abs <= 14:
        return many
    tail = n_abs % 10
    if tail == 1:
        return one
    if 2 <= tail <= 4:
        return few
    return many


def _combine_drug_clusters(
    clusters: list[list[DrugEffectPath]],
    probability: float,
) -> tuple[Mass, list[DrugEffectPath]]:
    """
    Уровни 1 и 2 для одного препарата: из каждого кластера (пути,
    пересекающиеся хотя бы в одном промежуточном узле) берёт
    представителя с максимальным k и комбинирует получившиеся
    независимые кластеры правилом Демпстера.

    Возвращает (масса препарата, список представителей — по одному
    на кластер, то есть ровно те пути, что реально вошли в расчёт).
    """

    representatives = [
        max(cluster, key=lambda p: p.k)
        for cluster in clusters
    ]

    combined = vacuous_mass()
    for rep in representatives:
        combined = combined.combine(make_mass(probability, rep.k))

    return combined, representatives


def _build_explanation(
    *,
    drug_count: int,
    independent_evidence_count: int,
    shortest: DrugEffectPath,
    node_names: dict[str, str],
) -> str:
    """Готовая фраза для врача — без терминов belief/plausibility."""

    drug_name = node_names[shortest.drug_id]

    if shortest.length <= 1:
        base = (
            f"Прямая связь с «{drug_name}» — указана как известный "
            "эффект без промежуточных звеньев."
        )
    else:
        step_word = _ru_count(shortest.length, "шаг", "шага", "шагов")
        base = (
            f"Оценка получена через {shortest.length} {step_word} "
            f"от «{drug_name}», не напрямую, а через известный "
            "механизм действия."
        )

    if drug_count > 1:
        extra = drug_count - 1
        word = "препаратом" if extra == 1 else "препаратами"
        base += f" Подтверждается независимо ещё {extra} {word} из комбинации."
    elif independent_evidence_count > 1:
        extra = independent_evidence_count - 1
        word = "механизмом" if extra == 1 else "механизмами"
        base += f" Подтверждается ещё {extra} независимым {word} действия этого препарата."

    return base


def interpret_side_effect(
    *,
    graph: nx.DiGraph,
    effect_id: str,
    probability: float,
    selected_drug_ids: set[str],
    node_names: dict[str, str],
    max_chain_examples: int = 3,
) -> dict[str, Any] | None:
    """
    ТДШ-интерпретация одного побочного эффекта. Возвращает None,
    если для него не нашлось ни одного пути от выбранных препаратов.
    """

    per_drug_paths = find_clustered_paths(graph, selected_drug_ids, effect_id)

    if not per_drug_paths:
        return None

    per_drug_mass: dict[str, Mass] = {}
    all_representatives: list[DrugEffectPath] = []
    total_path_count = 0

    for drug_id, clusters in per_drug_paths.items():
        mass, representatives = _combine_drug_clusters(clusters, probability)
        per_drug_mass[drug_id] = mass
        all_representatives.extend(representatives)
        total_path_count += sum(len(cluster) for cluster in clusters)

    combined = vacuous_mass()
    for mass in per_drug_mass.values():
        combined = combined.combine_yager(mass)

    all_representatives.sort(key=lambda p: p.length)

    example_paths = [
        {
            "drug": node_names[p.drug_id],
            "length": p.length,
            "k": round(p.k, 4),
            "chain": " → ".join(node_names[n] for n in p.node_ids),
        }
        for p in all_representatives[:max_chain_examples]
    ]

    shortest = all_representatives[0]

    return {
        "belief": round(combined.belief, 6),
        "plausibility": round(combined.plausibility, 6),
        "uncertainty": round(combined.uncertainty, 6),
        # Число ТДШ, а не подобранная категория: доля массы, реально
        # закреплённой за H или not-H (т.е. не ушедшей в незнание).
        # 1.0 — вся масса определена, 0.0 — полная неопределённость.
        "evidence_strength": round(1.0 - combined.uncertainty, 4),
        "evidence_type": "direct" if shortest.length <= 1 else "mechanistic",
        "path_count": total_path_count,
        "independent_evidence_count": len(all_representatives),
        "paths": example_paths,
        "reasoning": {
            "chain": [node_names[n] for n in shortest.node_ids],
            "explanation": _build_explanation(
                drug_count=len(per_drug_mass),
                independent_evidence_count=len(all_representatives),
                shortest=shortest,
                node_names=node_names,
            ),
        },
    }


def tdsh_interpret(
    *,
    graph_data: dict,
    final_probs: dict[str, float],
    selected_prepare_ids: set[str],
    target_se_names: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """
    ТДШ-интерпретация побочных эффектов для выбранной комбинации
    препаратов.

    target_se_names ограничивает расчёт конкретным набором имён
    побочных эффектов — например, только теми, чья вероятность в
    комбинации реально выросла относительно одиночного приёма любого
    из препаратов (см. tdsh_target_effects). Какой именно пул отправлять
    на интерпретацию — решает вызывающий код (BayeseView), эта функция
    сама ничего не фильтрует по смыслу, только по переданному множеству
    имён. None — посчитать по всем side_e-узлам графа (нужно, например,
    demo_cli для полной трассировки без привязки к конкретному запросу).

    Возвращает se_name → {...}.
    """

    graph = build_nx_graph(graph_data)
    node_names = {n["id"]: n["name"] for n in graph_data["nodes"]}
    se_id2name = _side_effects(graph_data)

    out: dict[str, dict[str, Any]] = {}

    for se_id, se_name in se_id2name.items():
        if target_se_names is not None and se_name not in target_se_names:
            continue

        probability = float(final_probs.get(se_id, 0.0))

        result = interpret_side_effect(
            graph=graph,
            effect_id=se_id,
            probability=probability,
            selected_drug_ids=selected_prepare_ids,
            node_names=node_names,
        )

        if result is not None:
            out[se_name] = result

    return out


def tdsh_target_effects(
    *,
    combined_side_effects: dict[str, dict[str, Any]],
    individual_drug_effects: dict[str, dict[str, dict[str, Any]]],
    selected_drugs: list[str],
    min_probability: float,
    rank_change_epsilon: float,
) -> set[str]:
    """
    Определяет пул побочных эффектов, для которых стоит считать и
    показывать ТДШ: только те, где комбинация препаратов дала
    вероятность заметно выше, чем любой из препаратов по отдельности.

    Если вероятность в комбинации совпадает (в т.ч. с точностью до
    float) с максимальной вероятностью по одному из препаратов —
    значит, остальные выбранные препараты не внесли вклад в этот
    узел графа, и это не эффект полифармакотерапии, а обычный
    эффект одного препарата, который врач и так видит в SEFromDrug.
    Объяснять путём ТДШ в такой ситуации нечего.

    combined_side_effects — data["side_effects"] из get_result()
    для полной комбинации (se_name → {"probability": ...}).
    individual_drug_effects — {drug: individual_data["side_effects"]}
    для каждого препарата по отдельности, тот же формат.
    """

    baseline_by_se: dict[str, float] = {}
    for drug in selected_drugs:
        for se_name, se_data in individual_drug_effects.get(drug, {}).items():
            prob = float(se_data.get("probability", 0.0))
            if prob > baseline_by_se.get(se_name, 0.0):
                baseline_by_se[se_name] = prob

    target: set[str] = set()
    for se_name, se_data in combined_side_effects.items():
        combined_prob = float(se_data.get("probability", 0.0))

        if combined_prob < min_probability:
            continue

        baseline = baseline_by_se.get(se_name, 0.0)
        if combined_prob - baseline > rank_change_epsilon:
            target.add(se_name)

    return target
