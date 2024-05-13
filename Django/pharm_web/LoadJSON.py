import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_pharm_web.settings')
django.setup()
from django.conf import settings
from pharm_web.models import *

# Создаем список типов предупреждений
warning_types = [
    {'name': 'black_box_warning', 'category': 'common'},
    {'name': 'black_box_warning', 'category': 'specific'},
    {'name': 'contraindicators', 'category': 'common'},
    {'name': 'contraindicators', 'category': 'specific'},
    {'name': 'cautions', 'category': 'common'},
    {'name': 'cautions', 'category': 'specific'}
]


# Определяем процедуру для создания объектов Warnings_MedScape
def create_warning_objects(data, data_ru, warning_type, arr_warning):
    i = 0
    max_len = len(data['warnings'][warning_type['name']][warning_type['category']])
    if len(data_ru['warnings'][warning_type['name']][warning_type['category']]) < max_len:
        max_len = len(data_ru['warnings'][warning_type['name']][warning_type['category']])
    while i < max_len:
        warning_en = data['warnings'][warning_type['name']][warning_type['category']][i]
        warning_ru = data_ru['warnings'][warning_type['name']][warning_type['category']][i]
        warning_obj, _ = Warnings_MedScape.objects.get_or_create(
            warnings_name_en=warning_en,
            warnings_name_ru=warning_ru,
            warnings_type='warnings;{};{}'.format(warning_type['name'], warning_type['category'])
        )
        print(warning_obj)
        warning_obj.save()
        arr_warning.append(warning_obj)
        i = i + 1
    return arr_warning


def load_json_Medscape():
    #    json_folder_medscape_en = 'D:\\Programs\\ml_palm1\\data_collection\\medscape\\data\\medscape_en\\testmedscape_en'
    #    json_folder_medscape_ru = 'D:\\Programs\\ml_palm1\\data_collection\\medscape\\data\\medscape_ru\\testmedscape_ru'
    json_folder_medscape_en = '/testmedscape_en'
    json_folder_medscape_ru = '/testmedscape_ru'
    s = 'START'
    # json_folder = 'D:\\Programs\\ml_palm1\\data_collection\\drugs\\data\\drugs_en\\all_medications' # путь к папке с JSON файлами
    for file_name in os.listdir(json_folder_medscape_en):  # проходим по всем файлам в папке
        s = s + file_name
        print(file_name)
        if file_name.endswith('.json'):  # если файл имеет расширение .json
            # Поиск аналогичного русского файла JSON
            f_ru = open(os.path.join(json_folder_medscape_ru, file_name), 'r', encoding='utf-8')
            with open(os.path.join(json_folder_medscape_en, file_name), 'r',
                      encoding='utf-8') as f:  # открываем файл для чтения
                data = json.load(f)  # загружаем данные из файла в переменную data
                data_ru = json.load(f_ru)

                # Создаем объекты Type_Drugs_MedScape
                print('CLASS')
                arr_drug_obj = []
                i = 0
                max_len = len(data['classes'])
                if len(data_ru['classes']) < max_len:
                    max_len = len(data_ru['classes'])
                while i < max_len:
                    type_drug_en = data['classes'][i].lower()
                    type_drug_ru = data_ru['classes'][i].lower()
                    type_drug_obj, _ = Type_Drugs_MedScape.objects.get_or_create(Type_en=type_drug_en,
                                                                                 Type_ru=type_drug_ru)
                    print(type_drug_obj)
                    type_drug_obj.save()
                    arr_drug_obj.append(type_drug_obj)
                    i = i + 1
                print(arr_drug_obj)

                # Создаем объекты Name_Drugs_MedScape
                arr_name_drugs = []
                print('NAME')
                group_type_en = data['name'].lower()
                group_type_ru = data_ru['name'].lower()
                group_type_obj, _ = Name_Drugs_MedScape.objects.get_or_create(Name_en=group_type_en,
                                                                              Name_ru=group_type_ru)

                i_arr_drug_obj = 0
                while i_arr_drug_obj < len(arr_drug_obj):
                    group_type_obj.Group_Type.add(arr_drug_obj[i_arr_drug_obj])
                    i_arr_drug_obj = i_arr_drug_obj + 1
                print(group_type_obj)
                group_type_obj.save()
                arr_name_drugs.append(group_type_obj)
                i = 0
                max_len = len(data['other_names'])
                if len(data_ru['other_names']) < max_len:
                    max_len = len(data_ru['other_names'])
                while i < max_len:
                    group_type_en = data['other_names'][i].lower()
                    group_type_ru = data_ru['other_names'][i].lower()
                    group_type_obj, _ = Name_Drugs_MedScape.objects.get_or_create(Name_en=group_type_en,
                                                                                  Name_ru=group_type_ru)
                    i_arr_drug_obj = 0
                    while i_arr_drug_obj < len(arr_drug_obj):
                        group_type_obj.Group_Type.add(arr_drug_obj[i_arr_drug_obj])
                        i_arr_drug_obj = i_arr_drug_obj + 1
                    print(group_type_obj)
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
                    adverse_effect_en = data['adverse effects'][i]['name'].lower()
                    adverse_effect_ru = data_ru['adverse effects'][i]['name'].lower()
                    adverse_effect_percent = data['adverse effects'][i]['percent']
                    print(adverse_effect_en, adverse_effect_ru, adverse_effect_percent)
                    adverse_effect_obj, _ = Adverse_Effects_MedScape.objects.get_or_create(
                        adverse_effects_name_en=adverse_effect_en,
                        adverse_effects_name_ru=adverse_effect_ru,
                        adverse_effects_percent=str(adverse_effect_percent)
                    )
                    print(adverse_effect_obj)
                    adverse_effect_obj.save()
                    arr_adverse_effects.append(adverse_effect_obj)
                    i = i + 1

                # Создаем объекты Source_Drugs и связи с Drugs_information
                source_en = data['source']
                source_obj, _ = Source_Drugs_MedScape.objects.get_or_create(Source=source_en)
                print(source_obj)
                source_obj.save()

                # Создаем объект Pregnancy_and_lactation и связи с Drugs_information
               # i = 0
               # pregnancy_common_en = ''
               # pregnancy_common_ru = ''
                #max_len = len(data['pregnancy']['common'])
                #if len(data_ru['pregnancy']['common']) < max_len:
                #    max_len = len(data_ru['pregnancy']['common'])
                #while i < max_len:
               #     pregnancy_common_en = '; '.join(data['pregnancy']['common'][i])
               #     pregnancy_common_ru = '; '.join(data_ru['pregnancy']['common'][i])
                #    i = i + 1
                #i = 0
                #pregnancy_specific_en = ''
                #pregnancy_specific_ru = ''
               # max_len = len(data['pregnancy']['specific'])
                #if len(data_ru['pregnancy']['specific']) < max_len:
                #    max_len = len(data_ru['pregnancy']['specific'])
                #while i < max_len:
                #    pregnancy_specific_en = '; '.join(data['pregnancy']['specific'][i])
                #    pregnancy_specific_ru = '; '.join(data_ru['pregnancy']['specific'][i])
                #    i = i + 1
                #i = 0
                #lactation_common_en = ''
                #lactation_common_ru = ''
               # max_len = len(data['lactation']['common'])
                #if len(data_ru['lactation']['common']) < max_len:
                #    max_len = len(data_ru['lactation']['common'])
                #while i < max_len:
                #    lactation_common_en = '; '.join(data['lactation']['common'][i])
                #    lactation_common_ru = '; '.join(data_ru['lactation']['common'][i])
               #     i = i + 1

                #preg_lact_obj, _ = Pregnancy_and_lactation_MedScape.objects.get_or_create(
                #    Pregnancy_common_en=pregnancy_common_en,
                #    Pregnancy_specific_en=pregnancy_specific_en,
                #    Lactation_common_en=lactation_common_en,
                    # Lactation_specific_en=lactation_specific_en,
                #    Pregnancy_common_ru=pregnancy_common_ru,
                #    Pregnancy_specific_ru=pregnancy_specific_ru,
                #    Lactation_common_ru=lactation_common_ru,
                    # Lactation_specific_ru=lactation_specific_ru
               # )
                #print(preg_lact_obj)
                #preg_lact_obj.save()

                # Создаем объекты Warnings и связи с Drugs_information
                arr_warning = []
                # Проходим по списку типов предупреждений и создаем объекты Warnings_MedScape для каждого типа
                for warning_type in warning_types:
                    arr_warning = create_warning_objects(data, data_ru, warning_type, arr_warning)

                # Создаем объекты interactions и связи с Drugs_information
                print('interactions')
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
                    with_obj, _ = Name_Drugs_MedScape.objects.get_or_create(Name_en=interaction_with_en,
                                                                                      Name_ru=interaction_with_ru)
                    print(with_obj)
                    interaction_obj, _ = Interaction_MedScape.objects.get_or_create(
                        interaction_with=with_obj,
                        classification_type_en=classification_type_en,
                        classification_type_ru=classification_type_ru,
                        description_en=description_en,
                        description_ru=description_ru,
                    )
                    print(interaction_obj)
                    interaction_obj.save()
                    arr_interactions.append(interaction_obj)
                    i = i + 1
                print('Drugs_information_MedScape')
                # Создаем объекты Drugs_information_MedScape
                info_name_file = file_name
                info_comment_en = data['comment']
                info_comment_ru = data_ru['comment']
                #print(preg_lact_obj)
                print(source_obj)
                print(arr_name_drugs)
                print(arr_adverse_effects)
                print(arr_warning)
                print(arr_interactions)
                drugs_info_obj, _ = Drugs_information_MedScape.objects.get_or_create(Name_File=info_name_file,
                                                                                     Comment_en=info_comment_en,
                                                                                     Comment_ru=info_comment_ru,
                                                                                     #Pregnancy_and_lactation=preg_lact_obj,
                                                                                     Source_Drugs=source_obj,
                                                                                     )

                i_arr = 0
                while i_arr < len(arr_name_drugs):
                    drugs_info_obj.Name_Drug.add(arr_name_drugs[i_arr])
                    i_arr = i_arr + 1
                i_arr = 0
                while i_arr < len(arr_adverse_effects):
                    drugs_info_obj.Adverse_Effects.add(arr_adverse_effects[i_arr])
                    i_arr = i_arr + 1
                i_arr = 0
                while i_arr < len(arr_warning):
                    drugs_info_obj.Warnings.add(arr_warning[i_arr])
                    i_arr = i_arr + 1
                i_arr = 0
                while i_arr < len(arr_interactions):
                    drugs_info_obj.Interaction.add(arr_interactions[i_arr])
                    i_arr = i_arr + 1


                drugs_info_obj.save()

                print(drugs_info_obj)
                print('NEXT')



    return s


