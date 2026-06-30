"""
Демонстрационный запуск интерпретации результата сети Байеса
через теорию Демпстера-Шафера.

Запуск из корня Django-проекта:

    python -m med_bayes.utils.ds_interpretation.demo_cli

Если DJANGO_SETTINGS_MODULE не задан:

    python -m med_bayes.utils.ds_interpretation.demo_cli --settings config.settings

Название settings-модуля замени на фактическое имя своего проекта.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any

from med_bayes.utils.bayes_calculation_2 import (
            load_combined_data,
            build_network,
            calculate_probabilities,
            get_result,
        )


DEFAULT_DRUG_NAMES = [
    "бисопролол",
    "спиронолактон",
    "апиксабан",
    "гепарин натрия",
    "каптоприл",
]


def setup_django(settings_module: str | None = None) -> None:
    """
    Инициализация Django-окружения для доступа к settings.GRAPH_PATH.
    """

    if settings_module:
        os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        raise RuntimeError(
            "Не задан DJANGO_SETTINGS_MODULE. "
            "Передай --settings <project>.settings или задай переменную окружения."
        )

    import django

    django.setup()


def normalize_name(value: str) -> str:
    """
    Нормализация названия препарата для сопоставления с prepare-узлами.
    """

    return " ".join(value.lower().replace("ё", "е").split())


def make_drug_states(
    graph_data: dict[str, Any],
    selected_drug_names: list[str],
) -> dict[str, float]:
    """
    Формирует бинарный словарь состояний prepare-узлов:
    выбранные препараты получают 1.0, остальные 0.0.
    """

    selected_normalized = {
        normalize_name(name)
        for name in selected_drug_names
    }

    prepare_nodes = [
        node
        for node in graph_data.get("nodes", [])
        if node.get("label") == "prepare"
    ]

    name_to_id = {
        normalize_name(node["name"]): node["id"]
        for node in prepare_nodes
    }

    unknown_drugs = selected_normalized - set(name_to_id)

    if unknown_drugs:
        available = sorted(name_to_id)
        raise ValueError(
            "В графе не найдены препараты: "
            f"{', '.join(sorted(unknown_drugs))}\n"
            "Доступные prepare-узлы:\n"
            + "\n".join(f"  - {name}" for name in available)
        )

    return {
        node["id"]: 1.0 if normalize_name(node["name"]) in selected_normalized else 0.0
        for node in prepare_nodes
    }


def get_selected_drug_ids(drug_states: dict[str, float]) -> set[str]:
    """
    Возвращает UUID prepare-узлов, выбранных пользователем.
    """

    return {
        drug_id
        for drug_id, state in drug_states.items()
        if float(state) == 1.0
    }


def load_bayes_functions():
    """
    Импорт функций сети Байеса.

    В разных версиях проекта модуль может лежать либо в med_bayes.utils,
    либо в graphs. Поэтому оставлен безопасный fallback.
    """



    return load_combined_data, build_network, calculate_probabilities, get_result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="POC интерпретации Байеса через теорию Демпстера-Шафера."
    )
    parser.add_argument(
        "--settings",
        default=None,
        help="Django settings module, например config.settings",
    )
    parser.add_argument(
        "--output",
        default="ds_demo_result.json",
        help="Файл для сохранения результата.",
    )
    args = parser.parse_args()

    setup_django(args.settings)

    from django.conf import settings
    from graphs.utils.graph_storage import GraphStorage
    from med_bayes.utils.ds_interpretation.interpreter import interpret_ds

    (
        load_combined_data,
        build_network,
        calculate_probabilities,
        get_result,
    ) = load_bayes_functions()

    storage = GraphStorage()

    graph_data = storage.download_graph()
    drug_states = make_drug_states(
        graph_data=graph_data,
        selected_drug_names=DEFAULT_DRUG_NAMES,
    )
    selected_drug_ids = get_selected_drug_ids(drug_states)

    prob_data, drug_states_input_data, drugs_for_output, combination_description = (
        load_combined_data(
            graph_data=graph_data,
            prob_file=storage.probability_path,
            drug_states_input=drug_states,
        )
    )

    network = build_network(graph_data, prob_data)

    trace_path = Path(settings.GRAPH_PATH) / "ds_demo_bayes_calc_trace.txt"

    final_probs = calculate_probabilities(
        network,
        str(trace_path),
    )

    bayes_result = get_result(
        final_probs,
        graph_data,
        drug_states_input_data,
        drugs_for_output,
        combination_description,
    )

    ds_result = interpret_ds(
        graph_data=graph_data,
        selected_drug_ids=selected_drug_ids,
        bayes_probs=final_probs,
    )

    result = {
        "selected_drug_names": DEFAULT_DRUG_NAMES,
        "selected_drug_ids": sorted(selected_drug_ids),
        "bayes_result": bayes_result,
        "ds_interpretation": ds_result,
    }

    output_path = Path(args.output)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print("Расчет завершен.")
    print(f"Граф: {storage.graph_path}")
    print(f"Вероятности: {storage.probability_path}")
    print(f"Трассировка Байеса: {trace_path}")
    print(f"Результат: {output_path.resolve()}")
    print(f"Выбранные препараты: {', '.join(DEFAULT_DRUG_NAMES)}")
    print(f"Побочных эффектов в ds_interpretation: {len(ds_result.get('effects', []))}")


if __name__ == "__main__":
    main()
