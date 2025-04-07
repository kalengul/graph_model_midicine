import re
from itertools import chain

from django.shortcuts import redirect

from pharm_web.forms import *


def addDrugGroup(request):
    if request.method == 'POST':
        form = AddDrugGroupForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            try:
                DrugGroup.objects.create(**form.cleaned_data)
                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')
    else:
        form = AddDrugGroupForm()

    return form


# def addDrug(request):
#     if request.method == 'POST':
#         form = AddDrugForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#             try:
#                 DrugGroup.objects.create(**form.cleaned_data)
#                 return redirect('home')
#             except:
#                 form.add_error(None, 'Ошибка добавления поста')
#     else:
#         form = AddDrugForm()
#     return form


def addDrug(request):
    path_drugs = '..\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
    path_rangs = '..\\ml_pharm_web\\txt_files_db\\rangs.txt'
    path_side_effect = '..\\ml_pharm_web\\txt_files_db\\side_effects.txt'

    with open(path_drugs, 'r', encoding='utf-8') as file:
        for line in file:
            last_drug = {'id': int(line.strip().split('\t')[0]),
                         'drug': line.strip().split('\t')[1]}

    side_effect_number = 0

    with open(path_side_effect, 'r', encoding='utf-8') as file:
        for line in file:
            if line != '\n':
                side_effect_number += 1

    # print('Число ПД при добавлении ЛС:', side_effect_number)

    if request.method == 'POST':
        form = AddDrugForm(request.POST)
        if form.is_valid():
            drug_name = form.cleaned_data.get('name')
            try:
                with open(path_drugs, 'a', encoding='utf-8') as file:
                    file.write(f'\n{last_drug["id"]+1}\t{drug_name}')

                with open(path_rangs, 'a', encoding='utf-8') as rangs_file:
                    rangs_file.write('0.0\n')

                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')
    else:
        form = AddDrugForm()
    return form


# # Выбор отображения побочке (обчный список для удаления/добавления или по лекарствам с коэффициентами)
# def CheckSideEffectsView(request):
#     if request.method == 'POST':
#             form = DisplaySideEffectsForm(request.POST)
#             if form.is_valid():
#                 display_method = form.cleaned_data['display_method']
#                 #Определяем способ отображения побочек и добавляем их в список для отображения
#                 if(display_method == "all"): #Возвращем обычный список опобочек, для удаления или добавления
#                     side_effects = ["язва пищевода", "гепатит"]
#                     tipe_view = "all" # либо drug - побочки с коэффициентами для конкретного лс
#                     return tipe_view, "Побочные эффекты", side_effects, form
                
#                 if display_method=="amiodaron":
#                     side_effects = [{"index": 1, "name": "язва пищевода", "rang": 0.1}, 
#                                     {"index": 2, "name": "гепатит", "rang": 0.5}, 
#                                    ]
                    
#                     tipe_view = "drug"

#                     return tipe_view, "Амиодарон", side_effects, form

#                 return None, None, None, form
#     else: form = DisplaySideEffectsForm()
#     return None, None, None, form


# # Выбор отображения побочке (обчный список для удаления/добавления или по лекарствам с коэффициентами)
# def CheckSideEffectsView(request):
#     path_se = 'C:\\for the job\\web_drugs_side_effects\\Django_Pharm\\ml_pharm_web\\txt_files_db\\side_effects.txt'
#     path_drugs = 'C:\\for the job\\web_drugs_side_effects\\Django_Pharm\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
#     path_rangs = 'C:\\for the job\\web_drugs_side_effects\\Django_Pharm\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
#     if request.method == 'POST':
#         form = DisplaySideEffectsForm(request.POST)
#         if form.is_valid():
#             display_method = form.cleaned_data['display_method']
#             # Определяем способ отображения побочек и добавляем их в список для отображения
#             if (display_method == "all"):           # Возвращем обычный список опобочек, для удаления или добавления
#                 # side_effects = ["язва пищевода", "гепатит"]
#                 side_effects = []
#                 with open(path_se, 'r', encoding='utf-8') as file:
#                     for line in file:
#                         side_effects.append(line.split('\t')[1].replace(';', ''))

#                 tipe_view = "all"                   # либо drug - побочки с коэффициентами для конкретного лс
#                 return tipe_view, "Побочные эффекты", side_effects, form

#             all_side_effects = []
#             with open(path_se, 'r', encoding='utf-8') as file:
#                 for line in file:
#                     line = line.strip()
#                     all_side_effects.append(
#                         {
#                             'index': line.split('\t')[0],
#                             'name': line.split('\t')[1]
#                         }
#                     )
#             rangs = []
#             with open(path_rangs, 'r', encoding='utf-8') as file:
#                 rangs = [line.strip() for line in file]
#             with open(path_drugs, 'r', encoding='utf-8') as file:
#                 for line in file:
#                     if display_method == line.split('\t')[0]:
#                         side_effects = [{"index": 1, "name": "язва пищевода", "rang": 0.1},
#                                         {"index": 2, "name": "гепатит", "rang": 0.5},
#                                         ]

#             tipe_view = "drug"

#             return tipe_view, "Амиодарон", side_effects, form

#         return None, None, None, form

#     form = DisplaySideEffectsForm()
#     return None, None, None, form


def CheckSideEffectsView(request):
    path_se = '..\\ml_pharm_web\\txt_files_db\\side_effects.txt'
    path_drugs = '..\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
    path_rangs = '..\\ml_pharm_web\\txt_files_db\\rangs.txt'

    if request.method == 'POST':
        form = DisplaySideEffectsForm(request.POST)
        # print(form)
        if form.is_valid():
            display_method = form.cleaned_data['display_method']
            # print('display_method =', display_method)
            # Обычный список побочек
            if display_method == "all":
                side_effects = []
                with open(path_se, 'r', encoding='utf-8') as file:
                    for line in file:
                        side_effects.append(line.split('\t')[1].replace(';', ''))

                return "all", "Побочные эффекты", side_effects, form

            # Загружаем список побочных эффектов
            all_side_effects = []
            with open(path_se, 'r', encoding='utf-8') as file:
                for line in file:
                    if line == '\n':
                        continue
                    line = line.strip().split('\t')
                    all_side_effects.append({'index': line[0], 'name': line[1]})

            # Загружаем ранги
            with open(path_rangs, 'r', encoding='utf-8') as file:
                rangs = [line.strip() for line in file]

            # Определяем индекс выбранного препарата
            drug_index = None
            drug_name = None
            with open(path_drugs, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split('\t')
                    if display_method == parts[0]:  # Сравниваем с названием лекарства
                        drug_index = int(parts[0]) - 1  # Индекс в файле рангов (нумерация с 0)
                        drug_name = parts[1]
                        break

            if drug_index is None:
                return None, "Лекарство не найдено", [], form

            with open(path_se, 'r', encoding='utf-8') as file:
                counter_se = len(file.readlines()) - 1
            # Выбираем 79 строк рангов для данного лекарства
            start_idx = drug_index * counter_se
            end_idx = start_idx + counter_se
            drug_rangs = rangs[start_idx:end_idx]

            # print('all_side_effects =', all_side_effects)
            # print('all_side_effects =', len(all_side_effects))
            # print('counter_se =', counter_se)

            # Формируем список побочек с рангами
            side_effects = [
                {
                    "index": all_side_effects[i]['index'],
                    "name": all_side_effects[i]['name'],
                    "rang": float(drug_rangs[i])
                }
                for i in range(counter_se)
            ]
            # print('Сработало отображение!')
            return "drug", drug_name, side_effects, form

    # print('Сработало отображение!')
    form = DisplaySideEffectsForm()
    return None, None, None, form




# def AddNewSideEffect(request):
#     if request.method == 'POST':
#         form = AddSideEffect(request.POST)
#         if form.is_valid():
#             # Добавлениеновой побочки
#             return form
#     else: form = AddSideEffect()
#     return form

# def UpdateSeideEffectRande(request):
#     if request.method == 'POST':
#         form = updateSeideEffectRande(request.POST)
#         if form.is_valid():
#             # Добавлениеновой побочки
#             return form
#     else: form = AddSideEffect()
#     return form



def AddNewSideEffect(request):
    path_side_effects = '..\\ml_pharm_web\\txt_files_db\\side_effects.txt'
    path_drugs = '..\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
    path_rangs = '..\\ml_pharm_web\\txt_files_db\\rangs.txt'

    with open(path_drugs, 'r', encoding='utf-8') as file:
        drug_number = len(file.readlines())

    def insert_after_every_n(lst, new_elem, n, total_inserts):
        result = []
        count_inserts = 0  # Считаем вставленные элементы

        for i in range(0, len(lst), n):
            result.extend(lst[i:i+n])  # Добавляем блок из n элементов
            if count_inserts < total_inserts:  # Проверяем, не вставили ли уже все нужные элементы
                result.append(new_elem)
                count_inserts += 1

        return result

    with open(path_side_effects, 'r', encoding='utf-8') as file:
        last_line = file.readlines()
        last_side_effect = {'id': int(last_line[-1].strip().split('\t')[0]),
                            'side effect': last_line[-1].strip().split('\t')[1],
                            'coef': last_line[-1].strip().split('\t')[2]}

    side_effect_count = 0
    with open(path_side_effects, 'r', encoding='utf-8') as file:
        for line in file:
            if line != '\n':
                side_effect_count += 1

    # print('Число ПД при добавлении нового ПД:', side_effect_count)

    # for rang in rangs:
    #     print('rang =', rang)

    if request.method == 'POST':
        form = AddSideEffect(request.POST)
        if form.is_valid():
            # Добавлениеновой побочки
            side_effect_name = form.cleaned_data.get('name')
            if not re.search(r'[a-zA-Zа-яА-Я]', side_effect_name):
                # print('Не правильное название побочки!')
                return AddSideEffect()
            # print('Новой побочки:', side_effect_name)

            with open(path_rangs, 'r', encoding='utf-8') as file:
                rangs = [line for line in file if line != '\n']

            rangs = insert_after_every_n(rangs, '0.0\n', side_effect_count, drug_number)
            # print('Число добавленных рангов', rangs.count('0.0\n'))

            with open(path_rangs, 'w', encoding='utf-8') as file:
                for rang in rangs:
                    # print('rang =', rang)
                    file.write(f'{rang}')

            with open(path_side_effects, 'a', encoding='utf-8') as file:
                # print('Отработала запись новой побочки в файл!!!')
                file.write(f"\n{last_side_effect['id']+1}\t{side_effect_name}\t{0.0}")
            return form
    else: form = AddSideEffect()
    return form


# def UpdateSeideEffectRande(request, drug_id):
#     path_side_effect = '..\\ml_pharm_web\\txt_files_db\\side_effects.txt'
#     path_rang = '..\\ml_pharm_web\\txt_files_db\\rangs.txt'
#     path_drugs = '..\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'

#     # Загружаем список побочных эффектов
#     side_effects = []
#     with open(path_side_effect, 'r', encoding='utf-8') as file:
#         for line in file:
#             if line.strip():
#                 parts = line.strip().split('\t')
#                 side_effects.append({'id': parts[0], 'side effect': parts[1]})

#     if request.method == 'POST':
#         form = updateSeideEffectRande(request.POST)
#         if form.is_valid():
#             new_rang = form.cleaned_data.get('name').replace(',', '.')  # Получаем новый ранг
#             print('new_rang =', new_rang)
#             side_effect_id = form.cleaned_data.get('display_method')  # ID побочного эффекта
#             print('side_effect_id =', side_effect_id)
#             # Определяем номер лекарства
#             drug_number = None
#             with open(path_drugs, 'r', encoding='utf-8') as file:
#                 for line in file:
#                     parts = line.strip().split('\t')
#                     if parts[1] == drug_id:  # Ищем соответствующее лекарство
#                         drug_number = int(parts[0]) - 1  # Индекс лекарства в рангах (нумерация с 0)
#                         break

#             print('drug_number =', drug_number)
#             if drug_number is None:
#                 form.add_error(None, "Лекарство не найдено")
#                 return form

#             # Определяем количество побочных эффектов
#             total_se = len(side_effects)

#             print('total_se =', total_se)
#             # Определяем индекс ранга в файле
#             rank_index = drug_number * total_se + int(side_effect_id) - 1

#             print('rank_index =', rank_index)
#             # Загружаем текущие ранги
#             with open(path_rang, 'r', encoding='utf-8') as file:
#                 rangs = [line.strip() for line in file if line.strip()]

#             print('До измененений:', rangs)
#             if rank_index >= len(rangs):
#                 form.add_error(None, "Ошибка: индекс выходит за пределы списка рангов")
#                 return form

#             # Обновляем соответствующий ранг
#             rangs[rank_index] = new_rang
#             print('После измененений:', rangs)
#             # Перезаписываем файл рангов
#             with open(path_rang, 'w', encoding='utf-8') as file:
#                 file.write('\n'.join(rangs) + '\n')

#     else:
#         form = updateSeideEffectRande()

#     return form


def UpdateSeideEffectRande(request, drug_id):
    path_side_effect = '..\\ml_pharm_web\\txt_files_db\\side_effects.txt'
    path_rang = '..\\ml_pharm_web\\txt_files_db\\rangs.txt'
    path_drugs = '..\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
    side_effects = []
    # drugs = []
    with open(path_side_effect, 'r', encoding='utf-8') as file:
        for line in file:
            if line == '\n':
                continue
            side_effects.append(
                {
                    'id': line.strip().split('\t')[0],
                    'side effect': line.strip().split('\t')[1],
                    'rang': line.strip().split('\t')[2]
                }
            )
    with open(path_drugs, 'r', encoding='utf-8') as file:
        for line in file:
            if line == '\n':
                continue
            line = line.strip()
            if line.split('\t')[1] == drug_id:
                drug_true_id = int(line.split('\t')[0]) - 1
            # drugs.append(
            #     {
            #         'id': line.split('\t')[0],
            #         'drug_name': line.split('\t')[1],
            #     }
            # )
    with open(path_rang, 'r', encoding='utf-8') as file:
        rangs = [line.strip() for line in file if line != '\n']

    # print('Тип запроса =', request.method)

    if request.method == 'POST':
        form = updateSeideEffectRande(request.POST)
        if form.is_valid():
            # Добавлениеновой побочки
            # print(form)
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # print(drug_id)
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            rang = form.cleaned_data.get('name')
            rang = rang.replace(',', '.')
            # print('rang =', rang)

            side_effect_id = form.cleaned_data.get('display_method')
            side_effect_id = int(side_effect_id) - 1
            # print('side_effects =', side_effects)
            # for side_effect in side_effects:
            #     # print('side_effect =', side_effect)
            #     if side_effect['id'] == se_id:
            #         print('При id side_effect =', side_effect)
            # with open(path_side_effect, 'w', encoding='utf-8') as file:
            #     for side_effect in side_effects:
            #         print('side_effect при записи=', side_effect)
            #         print(f"{side_effect['id']}\t{side_effect['side effect']}")
            #         file.write(f"{side_effect['id']}\t{side_effect['side effect']}")
            count_side_effect = len(side_effects) - 1
            # print('Число побочек =', count_side_effect)
            # print('идентификатора ЛС =', drug_true_id)
            start = count_side_effect * drug_true_id
            # print('начало нужной последовательности =', start)
            rang_index = start + side_effect_id
            # print('Индекс ранга =', rang_index)
            rangs[rang_index] = rang
            with open(path_rang, 'w', encoding='utf-8') as file:
                for rang in rangs:
                    file.write(f'{rang}\n')
            #     # drugs = [line.strip().split('\n')[1] for line in file if line != '\n']
            #     for line in file:
            #         if line == '\n':
            #             continue
            #         line = line.strip()
            #         if line.split()[1] == drug_id:
            #             drug_number = int(line.split()[0])
            #         # drugs.append(
            #         #     {
            #         #         'id': line.split()[0],
            #         #         'drug name': line.split()[1],
            #         #     }
            #         # )
            # # for drug in drugs:
            # #     if drug ==
            # print('Возврат вормы')
            return form

    else:
        # print('Внимание!!!')
        # form = AddSideEffect()
        form = updateSeideEffectRande()
    return form
