"""Модуль загруки данных в БД из json-файлов."""

import os
import json
import logging

import django
from django.conf import settings

from medscape_api.models import (WarningsMedScape,
                                 TypeDrugsMedScape,
                                 NameDrugsMedScape,
                                 AdverseEffectsMedScape,
                                 SourceDrugsMedScape,
                                 InteractionMedScape,
                                 DrugsInformationMedScape,
                                 )


logger = logging.getLogger('medscape')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_pharm_web.settings')
django.setup()


class JSONLoader:
    """Загрузчик данных MedScape."""

    # Создаем список типов предупреждений
    WARNING_TYPES = [
        {'name': 'black_box_warning', 'category': 'common'},
        {'name': 'black_box_warning', 'category': 'specific'},
        {'name': 'contraindicators', 'category': 'common'},
        {'name': 'contraindicators', 'category': 'specific'},
        {'name': 'cautions', 'category': 'common'},
        {'name': 'cautions', 'category': 'specific'}
    ]

    def create_warning_objects(self, data, data_ru, warning_type, arr_warning):
        """Метод создания объектов Warnings_MedScape."""
        i = 0
        max_len = len(
            data['warnings'][warning_type['name']][warning_type['category']])
        if len(data_ru['warnings'][warning_type['name']][warning_type[
                'category']]) < max_len:
            max_len = len(data_ru['warnings'][warning_type['name']][
                warning_type['category']])
        while i < max_len:
            warning_en = (
                data['warnings'][warning_type['name']][warning_type[
                    'category']][i])
            warning_ru = data_ru['warnings'][warning_type['name']][
                warning_type['category']][i]
            warning_obj, _ = WarningsMedScape.objects.get_or_create(
                warnings_name_en=warning_en,
                warnings_name_ru=warning_ru,
                warnings_type='warnings;{};{}'.format(warning_type['name'],
                                                      warning_type['category'])
            )

            warning_obj.save()
            arr_warning.append(warning_obj)
            i = i + 1
        return arr_warning

    def load_json_medscape(self):
        """Загрузка данных."""
        json_folder_medscape_en = os.path.join(settings.BASE_DIR,
                                               'testmedscape_en')
        json_folder_medscape_ru = os.path.join(settings.BASE_DIR,
                                               'testmedscape_ru')
        s = 'START'
        # проходим по всем файлам в папке
        file_names = os.listdir(json_folder_medscape_en)
        for idx, file_name in enumerate(file_names, 1):
            s = s + file_name

            if file_name.endswith('.json'):  # если файл имеет расширение .json
                # Поиск аналогичного русского файла JSON
                f_ru = open(os.path.join(json_folder_medscape_ru, file_name),
                            'r',
                            encoding='utf-8')
                with open(os.path.join(json_folder_medscape_en, file_name),
                          'r',
                          encoding='utf-8') as f:  # открываем файл для чтения
                    # загружаем данные из файла в переменную data
                    data = json.load(f)
                    data_ru = json.load(f_ru)

                    # Создаем объекты Type_Drugs_MedScape
                    arr_drug_obj = []
                    i = 0
                    max_len = len(data['classes'])
                    if len(data_ru['classes']) < max_len:
                        max_len = len(data_ru['classes'])
                    while i < max_len:
                        type_drug_en = data['classes'][i].lower()
                        type_drug_ru = data_ru['classes'][i].lower()
                        type_drug_obj, _ = (
                            TypeDrugsMedScape.objects.get_or_create(
                                type_en=type_drug_en,
                                type_ru=type_drug_ru))

                        type_drug_obj.save()
                        arr_drug_obj.append(type_drug_obj)
                        i = i + 1

                    # Создаем объекты Name_Drugs_MedScape
                    arr_name_drugs = []

                    group_type_en = data['name'].lower()
                    group_type_ru = data_ru['name'].lower()
                    group_type_obj, _ = (
                        NameDrugsMedScape.objects.get_or_create(
                            name_en=group_type_en,
                            name_ru=group_type_ru))

                    i_arr_drug_obj = 0
                    while i_arr_drug_obj < len(arr_drug_obj):
                        group_type_obj.group_type.add(arr_drug_obj[
                            i_arr_drug_obj])
                        i_arr_drug_obj = i_arr_drug_obj + 1

                    group_type_obj.save()
                    arr_name_drugs.append(group_type_obj)
                    i = 0
                    max_len = len(data['other_names'])
                    if len(data_ru['other_names']) < max_len:
                        max_len = len(data_ru['other_names'])
                    while i < max_len:
                        group_type_en = data['other_names'][i].lower()
                        group_type_ru = data_ru['other_names'][i].lower()
                        group_type_obj, _ = (
                            NameDrugsMedScape.objects.get_or_create(
                                name_en=group_type_en,
                                name_ru=group_type_ru))
                        i_arr_drug_obj = 0
                        while i_arr_drug_obj < len(arr_drug_obj):
                            group_type_obj.group_type.add(arr_drug_obj[
                                i_arr_drug_obj])
                            i_arr_drug_obj = i_arr_drug_obj + 1

                        group_type_obj.save()
                        arr_name_drugs.append(group_type_obj)
                        i = i + 1

                    # Создаем объекты Adverse_Effects и связи с Drugs_information
                    arr_adverse_effects = []
                    i = 0
                    max_len = len(data['adverse effects'])
                    if len(data_ru['adverse effects']) < max_len:
                        max_len = len(data_ru['adverse effects'])
                    while i < max_len:
                        adverse_effect_en = (
                            data['adverse effects'][i]['name'].lower())
                        adverse_effect_ru = data_ru['adverse effects'][i]['name'].lower()
                        adverse_effect_percent = data['adverse effects'][i]['percent']

                        adverse_effect_obj, _ = AdverseEffectsMedScape.objects.get_or_create(
                            adverse_effects_name_en=adverse_effect_en,
                            adverse_effects_name_ru=adverse_effect_ru,
                            adverse_effects_percent=str(adverse_effect_percent)
                        )
                        adverse_effect_obj.save()
                        arr_adverse_effects.append(adverse_effect_obj)
                        i = i + 1

                    # Создаем объекты Source_Drugs и связи с Drugs_information
                    source_en = data['source']
                    source_obj, _ = SourceDrugsMedScape.objects.get_or_create(source=source_en)
                    source_obj.save()

                    # Создаем объекты Warnings и связи с Drugs_information
                    arr_warning = []
                    # Проходим по списку типов предупреждений и создаем объекты Warnings_MedScape для каждого типа
                    for warning_type in self.WARNING_TYPES:
                        arr_warning = self.create_warning_objects(data, data_ru, warning_type, arr_warning)

                    # Создаем объекты interactions и связи с Drugs_information

                    arr_interactions = []
                    i = 0
                    max_len = len(data['interactions'])
                    if len(data_ru['interactions']) < max_len:
                        max_len = len(data_ru['interactions'])
                    while i < max_len:
                        interaction_with_en = data['interactions'][i]['interaction_with'].lower()
                        interaction_with_ru = data_ru['interactions'][i]['interaction_with'].lower()
                        classification_type_en = data['interactions'][i]['classification_type'].lower()
                        classification_type_ru = data_ru['interactions'][i]['classification_type'].lower()
                        description_en = data['interactions'][i]['description']['common']
                        description_ru = data_ru['interactions'][i]['description']['common']
                        with_obj, _ = NameDrugsMedScape.objects.get_or_create(name_en=interaction_with_en,
                                                                              name_ru=interaction_with_ru)

                        interaction_obj, _ = InteractionMedScape.objects.get_or_create(
                            interaction_with=with_obj,
                            classification_type_en=classification_type_en,
                            classification_type_ru=classification_type_ru,
                            description_en=description_en,
                            description_ru=description_ru,
                        )

                        interaction_obj.save()
                        arr_interactions.append(interaction_obj)
                        i = i + 1

                    # Создаем объекты Drugs_information_MedScape
                    info_name_file = file_name
                    info_comment_en = data['comment']
                    info_comment_ru = data_ru['comment']

                    drugs_info_obj, _ = DrugsInformationMedScape.objects.get_or_create(name_file=info_name_file,
                                                                                        comment_en=info_comment_en,
                                                                                        comment_ru=info_comment_ru,
                                                                                        source_drugs=source_obj,
                                                                                        )

                    i_arr = 0
                    while i_arr < len(arr_name_drugs):
                        drugs_info_obj.name_drug.add(arr_name_drugs[i_arr])
                        i_arr = i_arr + 1
                    i_arr = 0
                    while i_arr < len(arr_adverse_effects):
                        drugs_info_obj.adverse_effects.add(arr_adverse_effects[i_arr])
                        i_arr = i_arr + 1
                    i_arr = 0
                    while i_arr < len(arr_warning):
                        drugs_info_obj.warnings.add(arr_warning[i_arr])
                        i_arr = i_arr + 1
                    i_arr = 0
                    while i_arr < len(arr_interactions):
                        drugs_info_obj.interaction.add(arr_interactions[i_arr])
                        i_arr = i_arr + 1

                    drugs_info_obj.save()

            logger.info(f"Прогресс: {idx}/{len(file_names)} итераций")

        return s
