import json
import logging
from pathlib import Path
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings

from drugs.utils.custom_response import CustomResponse
from graphs.serializers import BayesSerializer
from med_bayes.serializers import BayesColorSerializer
from med_bayes.utils.bayes_calculation_2 import (load_combined_data,
                                                 get_result,
                                                 build_network,
                                                 calculate_probabilities)
from drugs.models import Drug
from graphs.utils.load_gender_side_effect import GENDER_SIDE_EFFECT
from graphs.utils.graph_storage import GraphStorage
from graphs.utils.text_builder import TextBuilder
from med_bayes.utils.color_management import colors, color_path
from ranker.utils.check_banned import DrugPairChecker
from med_bayes.utils.ds_interpretation.interpreter import (
    tdsh_interpret,
    tdsh_target_effects,
)
from med_bayes.utils.ds_interpretation.conf import (
    MIN_TDSH_PROBABILITY,
    RANK_CHANGE_EPSILON,
)

from accounts.auth import bearer_token_required


from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes


logger = logging.getLogger('med_bayes')
INCORRECT_DATA = 'Некорректные данные'
NAME = 'name'
NODES = 'nodes'
ID = 'id'

GRAPH_FOR_BAYES_PATH = Path(settings.GRAPH_PATH) / 'node_with_roots.json'
GREEN_COLOR = 'green'
YELLOW_COLOR = 'yellow'
RED_COLOR = 'red'
GREEN = colors.get(GREEN_COLOR, 0.15)
YELLOW = colors.get(YELLOW_COLOR, 0.25)
RED = colors.get(RED_COLOR, 0.26)


class BayeseView(APIView):
    """Вьюшка для бинарного словаря идентификаторов."""

    MAN = 'man'
    WOMAN = 'woman'
    GENDER = 'gender'
    SIDE_EFFECT = 'side_effects'
    EFFECT_NAME = "se_name"

    def _exist_contraindications(self, drug_ids, contra_ids):
        """
        Проверка наличия противопоказаний.

        Проверка пересечения противопоказаний у ЛС из комбинации
        и противопоказаний, указанных в запросе.
        """
        exist = False
        submessages = []

        drugs = Drug.objects.filter(id__in=drug_ids).prefetch_related(
            "contraindications")
        for drug in drugs:
            intersect = drug.contraindications.filter(id__in=contra_ids)
            logger.debug(f'drug = {drug.drug_name}')
            for contra in drug.contraindications.all():
                logger.debug(f'contra - {contra.id}, {contra.name}')
            if intersect.exists():
                logger.debug('Противопоказание у ЛС есть')
                names = ", ".join(list(intersect.values_list("name",
                                                             flat=True)))
                submessages.append(f'{drug.drug_name}: {names}')
                exist = True

        if submessages:
            *rest, last = submessages
            message = ';\n'.join(rest + [last + '.'])
        else:
            message = None

        return exist, message

    def _exclude_by_gender(self, source_effect, gender, gender_effects):
        """
        Исключение по полу.

        Если gender - man, не допускаются женские ПД,
        и наоборот, если woman, мужские ПД.
        """
        if gender == self.MAN:
            excluded = gender_effects[self.WOMAN]
        else:
            excluded = gender_effects[self.MAN]

        result = []
        for effect in source_effect:
            effect_name = TextBuilder(effect[self.EFFECT_NAME]).lower().text
            logger.debug(f'effect_name = {effect_name}')
            match_found = False
            for exc in excluded:
                exc = TextBuilder(exc).lower().text
                if exc in effect_name or effect_name in exc:
                    logger.debug(f'{effect_name} - половое ПД')
                    match_found = True
                    break

            if not match_found:
                logger.debug(f'{effect_name} - не половое ПД. Добавление')
                result.append(effect)

        return result

    def _get_bin_ids(self, drugs):
        """Получение бинаризированного словаря."""
        graph = GraphStorage().download_graph()
        bin_id = {}
        drug2id = {}

        for node in graph['nodes']:
            if node['label'] != 'prepare':
                continue
            drug2id[node[NAME]] = node['id']
            bin_id[node['id']] = 0

        for drug in drugs:
            bin_id[drug2id[drug.lower()]] = 1
        return bin_id

    @extend_schema(
        operation_id='bayes_calculate',
        request=BayesSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Расчёт сети Байеса успешно выполнен.',
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Некорректные входные данные.',
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Ошибка расчёта сети Байеса.',
            ),
        },
        tags=['med-bayes'],
    )
    # @bearer_token_required
    def post(self, request):
        """Вычисление сети Байеса."""
        graph_storage = GraphStorage()
        serializer = BayesSerializer(data=request.data)
        if not serializer.is_valid():
            message = 'Некорректные данные'
            logger.info(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=message
            )

        drug_ids = serializer.validated_data['drugs']

        human_data = serializer.validated_data.get('humanData')

        exist = False
        description = None
        gender = None
        compatibility_bayes = 'unknown'
        contraindication_ids = []

        banned = DrugPairChecker().check_banned(drug_ids)
        print('banned =', banned)
        logger.debug(f'banned = {banned}')
        if banned:
            return CustomResponse(
                status=status.HTTP_200_OK,
                message='Совместимость ЛС по сети Байеса успешно рассчитана',
                http_status=status.HTTP_200_OK,
                data={
                    "compatibility_bayes": "banned",
                    "combinations": [
                        {
                            "compatibility": "banned",
                            "drugs": banned

                        }],
                    "drugs": list(
                            Drug.objects.filter(id__in=drug_ids
                                                ).values_list(
                                                    'drug_name', flat=True)),
                    }
                )
        if human_data:
            age = human_data.get("age")
            gender = human_data.get('gender')
            contraindication_ids = human_data.get('cont_list', [])
        if contraindication_ids:
            exist, description = (
                self._exist_contraindications(drug_ids, contraindication_ids))
        if exist:
            logger.debug('Есть найдено противопоказание')
            compatibility_bayes = 'banned-contraindications'

        drugs = []
        for id in drug_ids:
            drug = Drug.objects.get(id=id)
            if not drug:
                logger.debug(f'ЛС с id {id} нет в БД')
                continue
            drugs.append(drug.drug_name.lower())

        with open(graph_storage.graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)

        diff = set(drugs) - set(graph[NAME])
        if diff:
            msg = ', '.join(list(diff))
            message = f'В сети Байеса нет данных о ЛС: {msg}'
            logger.error(message)
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=message)

        print('Все ЛС соответствуют')

        full_process_start = datetime.now()
        prob_data, drug_states_input_data, drugs_for_output, \
            combination_description = load_combined_data(
                graph_data=graph,
                prob_file=graph_storage.probability_path,
                drug_states_input=self._get_bin_ids(drugs)
            )

        # Построение сети с новыми параметрами
        network = build_network(graph, prob_data)

        # Перерасчет вероятностей (логирование не меняется)
        calculation_start = datetime.now()
        final_probs = calculate_probabilities(network, 'calculation_trace.txt')
        calculation_finish = datetime.now()

        data = get_result(
            final_probs,
            graph,
            drug_states_input_data,
            drugs_for_output,
            combination_description)

        full_process_finish = datetime.now()
        full_process = full_process_finish - full_process_start
        calculation = calculation_finish - calculation_start

        log_path = Path(settings.LOG_PATH)

        with open(log_path / 'calculation_time.txt', 'w',
                  encoding='utf-8') as f:
            f.write(f'время для выполнения вероятностей: {calculation}\n')
            f.write(('время для выполнения всех этапах '
                     f'сети Байеса {full_process}\n'))

        result = {
                    "rank_iteractions": "unknown",
                    "compatibility_bayes": compatibility_bayes,
                    "side_effects": [
                        {
                            "compatibility": "compatible",
                            "effects": []

                        },
                        {
                            "compatibility": "caution",
                            "effects": []

                        },
                        {
                            "compatibility": "incompatible",
                            "effects": []

                        }
                    ],
                    "combinations": "unknown",
                    "drugs": drugs,
                    "SEFromDrug": [],
            }

        individual_drug_effects = {}

        for drug in drugs:
            single_drug_prob_data, single_drug_states, \
                single_drugs_for_output, _ = load_combined_data(
                    graph_data=graph,
                    prob_file=graph_storage.probability_path,
                    drug_states_input=self._get_bin_ids([drug]))
            single_network = build_network(graph, single_drug_prob_data)
            single_probs = calculate_probabilities(
                single_network,
                'single_calculation_trace.txt')

            individual_data = get_result(
                single_probs,
                graph,
                single_drug_states,
                single_drugs_for_output,
                combination_description)

            individual_drug_effects[drug] = individual_data["side_effects"]

        for drug in drugs:
            drug_effects = []
            if drug in individual_drug_effects:
                for se_name, se_data in individual_drug_effects[drug].items():
                    drug_effects.append({
                        self.EFFECT_NAME: se_name,
                        "rank": round(se_data["probability"], 2)
                    })

            drug_effects.sort(key=lambda x: x["rank"], reverse=True)

            if gender:
                drug_effects = self._exclude_by_gender(drug_effects, gender,
                                                       GENDER_SIDE_EFFECT)

            result["SEFromDrug"].append({
                "d_name": drug,
                "effects": drug_effects
            })

        combinations = [
            {
                "compatibility": "cause",
                "drugs": []
            },
            {
                "compatibility": "incompatible",
                "drugs": []
            },
        ]

        # Общие побочки (от взаимодействия) оставляем как есть
        max_rank = 0
        for se in data["side_effects"]:
            rank = data["side_effects"][se]["probability"]
            if rank > max_rank:
                max_rank = rank

            if rank <= GREEN:
                result["side_effects"][0]["effects"].append({
                    self.EFFECT_NAME: se,
                    "rank": round(rank, 2),
                })

            elif GREEN < rank <= YELLOW:
                result["side_effects"][1]["effects"].append({
                    self.EFFECT_NAME: se,
                    "rank": round(rank, 2),
                })

            elif YELLOW < rank:
                result["side_effects"][2]["effects"].append({
                    self.EFFECT_NAME: se,
                    "rank": round(rank, 2),
                })

        if max_rank <= GREEN:
            compatibility_bayes = 'compatible'
        elif GREEN < max_rank <= YELLOW:
            compatibility_bayes = 'caution'
            combinations[0]["drugs"] = drugs
        elif max_rank > YELLOW:
            compatibility_bayes = 'incompatible'
            combinations[1]["drugs"] = drugs

        print('compatibility_bayes = ', compatibility_bayes)

        result['compatibility_bayes'] = compatibility_bayes

        result["side_effects"][0]["effects"].sort(key=lambda x: x["rank"],
                                                  reverse=True)

        result['rank_iteractions'] = round(max_rank, 2)

        result['combinations'] = list(combinations)

        if gender:
            logger.debug(f'Пол указан. gender = {gender}')
            result["side_effects"][0]["effects"] = (
                self._exclude_by_gender(result["side_effects"][0]["effects"],
                                        gender, GENDER_SIDE_EFFECT))

        selected_ids = {
            k for k, v in drug_states_input_data.items()
            if float(v) == 1.0
        }

        interpretation = serializer.validated_data.get("interpretation", False)

        if interpretation:
            target_se_names = tdsh_target_effects(
                combined_side_effects=data["side_effects"],
                individual_drug_effects=individual_drug_effects,
                selected_drugs=drugs,
                min_probability=MIN_TDSH_PROBABILITY,
                rank_change_epsilon=RANK_CHANGE_EPSILON,
            )

            tdsh_data = tdsh_interpret(
                graph_data=graph,
                final_probs=final_probs,
                selected_prepare_ids=selected_ids,
                target_se_names=target_se_names,
            )

            for side_effect_group in result["side_effects"]:
                for effect in side_effect_group["effects"]:
                    se_name = effect[self.EFFECT_NAME]
                    if se_name in tdsh_data:
                        effect["tdsh"] = tdsh_data[se_name]

        message = 'Совместимость ЛС по сети Байеса успешно рассчитана'
        logger.info(f'message = {message}')

        with (open(log_path / 'side_effects.txt', 'w', encoding='utf-8') as f1,
              open(log_path / 'weight.txt', 'w', encoding='utf-8') as f2):
            for side_effects in result['side_effects']:
                for effect in side_effects['effects']:
                    f1.write(f"{effect['se_name']}\n")
                    f2.write(f"{effect['rank']}\n")

        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message=message,
            data=result
        )


class BayesColor(APIView):
    """Управление цветами для Байеса."""

    @extend_schema(
        operation_id='bayes_color_update',
        request=BayesColorSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Цвета успешно обновлены.',
            ),
        },
        tags=['med-bayes'],
    )
    def post(self, request):
        """Указание значений для цветов."""
        with open(color_path, 'r', encoding='utf-8') as file:
            colors = json.load(file)

        colors[GREEN_COLOR] = request.data['green']
        colors[YELLOW_COLOR] = request.data['yellow']
        colors[RED_COLOR] = request.data['red']

        with open(color_path, 'w', encoding='utf-8') as file:
            json.dump(colors, file, ensure_ascii=False, indent=4)

        return Response(status=status.HTTP_200_OK,
                        data={'message': 'Цвета успешно обновлены',
                              'status': status.HTTP_200_OK})
