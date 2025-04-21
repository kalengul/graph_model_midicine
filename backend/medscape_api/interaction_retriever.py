from django.db.models import Q
from .models import (NameDrugsMedScape,
                     InteractionMedScape,
                     DrugsInformationMedScape,)


class InteractionRetriever:
    """Класс для получения взаимодействий."""

    @classmethod
    def __get_two_interactions(cls, name, second_drug_name=None):
        """Метод взаимодействия двух ЛС."""
        drugs_info = DrugsInformationMedScape.objects.filter(
            Q(name_drug__name_ru__iexact=name) | Q(
                name_drug__name_en__iexact=name)
        )

        interactions = InteractionMedScape.objects.filter(
            drugsinformationmedscape__in=drugs_info,
        )

        if second_drug_name:
            second_drug_info = NameDrugsMedScape.objects.filter(
                Q(name_ru__iexact=second_drug_name) | Q(
                    name_en__iexact=second_drug_name)
            )
            second_interactions = interactions.filter(
                interaction_with__in=second_drug_info)
        results = []
        for interaction in second_interactions:
            result = {'name': name,
                      'classification': interaction.classification_type_ru,
                      'description': interaction.description_ru}
            if second_drug_name:
                result['interaction_with'] = (
                    interaction.interaction_with.name_ru
                )
            else:
                result['interaction_with'] = None
            results.append(result)

        return results

    def get_interactions(self, drugs):
        """Метод получения взаимодействия ЛС."""
        drugs = [x for x in drugs if x != '']
        interactions = []
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                drug1 = drugs[i].strip()
                drug2 = drugs[j].strip()
                interactions.append(self.__get_two_interactions(drug1, drug2))
        return interactions
