import json

from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from drugs.utils.custom_response import CustomResponse
from graphs.serializers import (GraphSerializer, UpdateGraphSerializer,
                                BayesSerializer)
from graphs.models import Graph
from graphs.utils.cleaner_graph_db import CleanProcessor
from graphs.utils.graph_loader import JSONGraphLoader
from graphs.utils.graph_manipulator import GraphManipulator
from graphs.utils.binarizer import Binarizer
from graphs.utils.merger import Merger
from graphs.utils.parse_ids import parse_ids
from graphs.bayes_calculation import (load_combined_data, get_result,
                                      build_network, calculate_probabilities,
                                      GRAPHS_4_PATH, PROBABILITIES_PATH)
from drugs.models import Drug
from graphs.utils.load_gender_side_effect import GENDER_SIDE_EFFECT


INCORRECT_DATA = 'Некорректные данные'
NAME = 'name'


class GraphView(APIView):
    """Вью для графов."""

    GRAPH_JSON = 'graph_json'
    GRAPH_XML = 'graph_xml'

    def _get_graph_from_file(self, request):
        """
        Получение файл из запроса.

        Достаёт файл из запроса и возвращает dict-граф
        или CustomResponse.
        """
        file = request.FILES.get('file')
        file2 = request.FILES.get('file2')

        if not file:
            return None, CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                message='JSON-файл не передан',
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not file2:
            return None, CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                message='XML-файл не передан',
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            graph_json = json.load(file)
            graph_xml = file2.read().decode('utf-8')
        except json.JSONDecodeError:
            return None, CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message="Ошибка чтения JSON-файла."
            )

        return graph_json, graph_xml, None

    def post(self, request):
        """Добавление графа."""
        graph_json, graph_xml, error = self._get_graph_from_file(request)

        if error:
            return error

        graph_serializer = GraphSerializer(data={
            NAME: '+'.join(graph_json[NAME]),
            self.GRAPH_JSON: graph_json,
            self.GRAPH_XML: graph_xml
        })
        if graph_serializer.is_valid():
            graph_serializer.save()
            return CustomResponse(
                status=status.HTTP_201_CREATED,
                http_status=status.HTTP_201_CREATED,
                message='Граф добавлен в БД успешно.'
            )
        else:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=(f'{INCORRECT_DATA}. Убедитесь что у него есть поля '
                         f'name, nodes, links. {graph_serializer.errors}')
            )

    def get(self, request, id=None):
        """Получнение графа по id или список."""
        if id:
            try:
                graph = Graph.objects.get(id=id)
            except Graph.DoesNotExist:
                return CustomResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    http_status=status.HTTP_404_NOT_FOUND,
                    message="Граф не найден"
                )

            return CustomResponse(
                data=GraphSerializer(graph).data,
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK,
                message="Граф найден успешно")

        return CustomResponse(
            data=GraphSerializer(Graph.objects.all(), many=True).data,
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message="Графы получены успешно")

    def put(self, request, id):
        """Изменение графа."""
        instance = get_object_or_404(Graph, pk=id)

        graph_json, graph_xml, error = self._get_graph_from_file(request)

        if error:
            return error

        graph_serializer = UpdateGraphSerializer(
            instance,
            data={self.GRAPH_JSON: graph_json,
                  self.GRAPH_XML: graph_xml})
        if graph_serializer.is_valid():
            graph_serializer.save()
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                message='Граф успешно обновлён',
                status=status.HTTP_200_OK
            )
        return CustomResponse(
            http_status=status.HTTP_400_BAD_REQUEST,
            message=INCORRECT_DATA,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        """Удаление графа."""
        if id:
            try:
                graph = Graph.objects.get(id=id)
                name = graph.name
                graph.delete()
                return CustomResponse(
                    status=status.HTTP_200_OK,
                    message=f"Графа {name} успешно удалён",
                    http_status=status.HTTP_200_OK
                )
            except ObjectDoesNotExist:
                return CustomResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Графа отсутствует",
                    http_status=status.HTTP_404_NOT_FOUND
                )
            except Exception as error:
                return CustomResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Внутренная ошибка сервера. {error}",
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class LoadGraphView(APIView):
    """Вью для загрузки данных в БД."""

    def post(self, request):
        """Загрузка графов в БД."""
        try:
            GraphManipulator(CleanProcessor().get_cleaner(),
                             JSONGraphLoader()).perform()

            return CustomResponse(
                message="Графы успешно загружены в БД",
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK)
        except Exception as error:
            return CustomResponse(
                message=(
                    "Ошибка загрузки графов в БД"
                    f"Ошибка: {error}"
                ),
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK)


class MergeView(APIView):
    """Вьюшка слияния."""

    @parse_ids
    def get(self, request, ids, *args, **kwargs):
        """Слияние графов."""
        try:
            merged_graph = Merger().merge(ids)
            return CustomResponse(
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK,
                message='графы слиты успешно',
                data=merged_graph
            )
        except Exception as error:
            print(f'При слиянии графа произошла ошибка. Ошибка {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='При слиянии графа произошла ошибка'
            )


class BayeseView(APIView):
    """Вьюшка для бинарного словаря идентификаторов."""

    MAN = 'man'
    WOMAN = 'woman'
    GENDER = 'gender'
    SIDE_EFFECT = 'side_effects'
    EFFECT_NAME = "se_name"

    def _exist_contraindications(self, drug_ids, contra_ids):
        """
        Проверка наличия противопаказаний.

        ПРоверка пересечения противопоказаний у ЛС из комбинации
        и противопоказаний, указаных в запросе.
        """
        exist = False
        submessages = []

        drugs = Drug.objects.filter(id__in=drug_ids).prefetch_related(
            "contraindications")
        for drug in drugs:
            intersect = drug.contraindications.filter(id__in=contra_ids)
            if intersect.exists():
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
            effect_name = effect[self.EFFECT_NAME]

            match_found = False
            for exc in excluded:
                if exc in effect_name or effect_name in exc:
                    match_found = True
                    break

            if not match_found:
                result.append(effect)

        return result

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
        serializer = BayesSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message='Некорректные данные'
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
            сompatibility_bayes = 'banned'

        short_id2long_id = {
            3: "38de65bc-cc45-49b8-bd94-d9bc3be57dea",
            6: "0f2b49cf-6635-4f1f-af0f-29c16c4f3e04",
            20: "79f54542-ae01-4088-b4fd-3079b0c03504",
            42: "c4b54c3f-93ef-4139-b4fa-cdad14c7ddc2"
        }

        id2drugs = {
            3: "Апиксабан",
            6: "Бисопролол",
            20: "Каптоприл",
            42: "Спиронолактон"
        }

        drug_states_input = {
            "38de65bc-cc45-49b8-bd94-d9bc3be57dea": 0,
            "0f2b49cf-6635-4f1f-af0f-29c16c4f3e04": 0,
            "79f54542-ae01-4088-b4fd-3079b0c03504": 0,
            "c4b54c3f-93ef-4139-b4fa-cdad14c7ddc2": 0
        }

        drugs = []

        for short_id in drug_ids:
            drugs.append(id2drugs[short_id])
            long_id = short_id2long_id[short_id]
            drug_states_input[long_id] = 1

        with open(GRAPHS_4_PATH, 'r', encoding='utf-8') as f:
            graph = json.load(f)

        prob_data, drug_states_input_data, drugs_for_output, \
            combination_description = load_combined_data(
                graph_data=graph,
                prob_file=PROBABILITIES_PATH,
                drug_states_input=drug_states_input
            )

        # Построение сети с новыми параметрами
        network = build_network(graph, prob_data)

        # Перерасчет вероятностей (логирование не меняется)
        final_probs = calculate_probabilities(network)

        data = get_result(
            final_probs,
            graph,
            drug_states_input_data,
            drugs_for_output,
            combination_description
        )

        result = {
                    "сompatibility_bayes": сompatibility_bayes,
                    "rank_iteractions": "undefined",
                    "side_effects": [
                        {
                            "сompatibility": "undefined",
                            "effects": []

                        }],
                    "combinations": "undefined",
                    "drugs": drugs
            }

        # result = {
        #             "сompatibility_bayes": сompatibility_bayes,
        #             "rank_iteractions": "undefined",
        #             "side_effects": [
        #                 {
        #                     "сompatibility": "undefined",
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
        #             "combinations": "undefined",
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
                self.EFFECT_NAME: se,
                "rank": data["side_effects"][se]["probability"],
            })

        result["side_effects"][0]["effects"].sort(key=lambda x: x["rank"],
                                                  reverse=True)

        if gender:
            result["side_effects"][0]["effects"] = (
                self._exclude_by_gender(result["side_effects"][0]["effects"],
                                        gender, GENDER_SIDE_EFFECT))

        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по сети Байеса успешно расcчитана',
            data=result
        )
