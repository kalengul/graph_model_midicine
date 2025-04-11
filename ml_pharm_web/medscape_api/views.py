from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from interaction_retriever import InteractionRetriever


class InteractionMedScape(APIView):
    """
    Получение информации взаимодействии ЛС.

    Информация получена из MedScape.
    """

    def get(self, request):
        """Метод отвечающий на GET-запрос."""
        drugs = request.GET.get('drugs', '').lower()
        # classification_type = request.GET.get('classification_type', '')
        interactions = []
        # global word_count
        # word_count = {}
        if drugs:
            drugs_list = [drug.strip() for drug in drugs.split(',')]
            interactions = InteractionRetriever.get_interactions(drugs_list)
        context = {
            'drugs': drugs,
        #        'classification_type': classification_type,
            'interactions': interactions
        }
        return Response(data=context, status=status.HTTP_200_OK)
