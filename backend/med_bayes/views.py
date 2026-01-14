import json
import logging
from pathlib import Path
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from drugs.utils.custom_response import CustomResponse
from graphs.serializers import BayesSerializer
from graphs.utils.binarizer import Binarizer
from graphs.utils.parse_ids import parse_ids
# from med_bayes.utils.bayes_calculation_ import (load_combined_data, get_result,
#                                                 build_network,
#                                                 calculate_probabilities)
from med_bayes.utils.bayes_calculation import (load_combined_data, get_result,
                                               build_network,
                                               calculate_probabilities)
from drugs.models import Drug
from graphs.utils.load_gender_side_effect import GENDER_SIDE_EFFECT
from graphs.utils.graph_storage import GraphStorage
from graphs.utils.text_builder import TextBuilder

from accounts.auth import bearer_token_required


logger = logging.getLogger('med_bayes')
INCORRECT_DATA = 'Некорректные данные'
NAME = 'name'
NODES = 'nodes'
ID = 'id'
GRAPH_FOR_BAYES_PATH = Path(settings.GRAPH_PATH) / 'node_with_roots.json'


class BayeseView(APIView):
    """Вьюшка для бинарного словаря идентификаторов."""

    MAN = 'man'
    WOMAN = 'woman'
    GENDER = 'gender'
    SIDE_EFFECT = 'side_effects'
    EFFECT_NAME = "se_name"
    RANK = "rank"

    def _exist_contraindications(self, drug_ids, contra_ids):
        """
        Проверка наличия противопаказаний.

        Проверка пересечения противопоказаний у ЛС из комбинации
        и противопоказаний, указаных в запросе.
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

        Если gender - man, недопускаются женские ПД,
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

    @parse_ids
    def get(self, request, ids, *args, **kwargs):
        """Получение бинарного словаря идентификаторов."""
        bin_ids = Binarizer().binarize(ids)

        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message='Бинарный словарь id-ов сформировался успешно',
            data=bin_ids)

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
        сompatibility_bayes = 'unknown'
        contraindication_ids = []
        if human_data:
            age = human_data.get("age")
            gender = human_data.get('gender')
            contraindication_ids = human_data.get('cont_list', [])
        if contraindication_ids:
            exist, description = (
                self._exist_contraindications(drug_ids, contraindication_ids))
        if exist:
            logger.debug('Есть найдено противопоказание')
            сompatibility_bayes = 'banned-contraindications'

        drugs = []
        for id in drug_ids:
            drug = Drug.objects.get(id=id)
            if not drug:
                logger.debug(f'ЛС с id {id} нет в БД')
                continue
            drugs.append(drug.drug_name.lower())

        with open(graph_storage.graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)

        # id2effects = {effect[ID]: effect[NAME] for effect in graph[NODES]}

        diff = set(drugs) - set(graph[NAME])
        if diff:
            msg = ', '.join(list(diff))
            message = f'В сети Байеса нет данных о ЛС: {msg}'
            logger.error(message)
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=message)

        print('Все ЛС соотвествуют')

        # with open(GRAPH_FOR_BAYES_PATH, 'r', encoding='utf-8') as f:
        #     most_relative_nodes = json.load(f)

        # graph = SimpleNonRelativeNodesDeleter().delete_nodes(
        #     nx.node_link_graph(graph, edges='links'),
        #     most_relative_nodes=most_relative_nodes,
        #     roots=[node['id'] for node in graph['nodes']
        #            if node['name'] in drugs]
        # )
        # graph = nx.node_link_data(graph, edges='links')

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
                    "сompatibility_bayes": сompatibility_bayes,
                    "rank_iteractions": "unknown",
                    "side_effects": [
                        {
                            "сompatibility": "unknown",
                            "effects": []

                        }],
                    "combinations": "unknown",
                    "drugs": drugs,
                    'SEFromDrug': []
            }

        # result = {
        #             "сompatibility_bayes": сompatibility_bayes,
        #             "rank_iteractions": "unknown",
        #             "side_effects": [
        #                 {
        #                     "сompatibility": "unknown",
        #                     "effects": []

        #                 },
        #                 {
        #                     "сompatibility": "compatible",
        #                     "effects": []

        #                 },
        #                 {
        #                     "сompatibility": "caution",
        #                     "effects": []

        #                 },
        #                 {
        #                     "сompatibility": "incompatible",
        #                     "effects": []

        #                 }
        #                 ],
        #             "combinations": "unknown",
        #             "drugs": drugs
        #     }

        # max_rank = 0
        # for se in data["side_effects"]:
        #     rank = data["side_effects"][se]["probability"]
        #     if rank > max_rank:
        #         max_rank = rank
        #     if not rank:
        #         result["side_effects"][0]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })
        #     elif rank < 0.5:
        #         result["side_effects"][1]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })
        #     elif rank < 0.75:
        #         result["side_effects"][2]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })
        #     elif rank >= 0.75:
        #         result["side_effects"][3]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })

        # if max_rank < 0.5:
        #     сompatibility_bayes = 'compatible'
        # elif max_rank < 0.75:
        #     сompatibility_bayes = 'caution'
        # else:
        #     сompatibility_bayes = 'incompatible'

        # if not exist:
        #     result['сompatibility_bayes'] = сompatibility_bayes

        for se in data["side_effects"]:
            result["side_effects"][0]["effects"].append({
                # self.EFFECT_NAME: id2effects[se],
                self.EFFECT_NAME: se,
                self.RANK: data["side_effects"][se]["probability"],
            })

        result["side_effects"][0]["effects"].sort(
            key=lambda x: x[self.RANK],
            reverse=True)
        # result["side_effects"][0]["effects"].sort(
        #     key=lambda x: x[self.EFFECT_NAME])

        if gender:
            logger.debug(f'Пол указан. gender = {gender}')
            result["side_effects"][0]["effects"] = (
                self._exclude_by_gender(result["side_effects"][0]["effects"],
                                        gender, GENDER_SIDE_EFFECT))

        message = 'Совместимость ЛС по сети Байеса успешно расcчитана'
        logger.info(f'message = {message}')

        with (open(log_path / 'side_effects.txt', 'w', encoding='utf-8') as f1,
              open(log_path / 'weight.txt', 'w', encoding='utf-8') as f2):
            for side_effects in result['side_effects']:
                for effect in side_effects['effects']:
                    f1.write(f"{effect['se_name']}\n")
                    f2.write(f"{effect['rank']}\n")

        for drug in drugs:
            prob_data, drug_states_input_data, drugs_for_output, \
                combination_description = load_combined_data(
                    graph_data=graph,
                    prob_file=graph_storage.probability_path,
                    drug_states_input=self._get_bin_ids([drug])
                )

            # Построение сети с новыми параметрами
            network = build_network(graph, prob_data)

            # Перерасчет вероятностей (логирование не меняется)
            final_probs = calculate_probabilities(network,
                                                  'calculation_trace.txt')

            data = get_result(
                final_probs,
                graph,
                drug_states_input_data,
                drugs_for_output,
                combination_description)

            drug_effects = {
                "d_name": drug,
                "effects": [],
            }

            for se in data['side_effects']:
                effect = {
                    self.EFFECT_NAME: se,
                    self.RANK: data["side_effects"][se]["probability"],
                }
                drug_effects["effects"].append(effect)

            drug_effects["effects"] = sorted(drug_effects["effects"],
                                             key=lambda x: x[self.RANK],
                                             reverse=True)

            result['SEFromDrug'].append(drug_effects)

        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message=message,
            data=result
        )
