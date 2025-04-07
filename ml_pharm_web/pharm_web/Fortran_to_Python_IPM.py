import numpy as np
import os
from pharm_web.models import *

# Определение размеров
n_rangs = 4266
n_j = 54
n_k = 79

files_all_iteractions = [
    {'name':'Общий','file':"rangbase.txt"},
    {'name': 'Нормированный', 'file': "rangfreq.txt"},
    {'name':'Мужчины до 65','file':"rangm1.txt"},
    {'name': 'Мужчины после 65', 'file': "rangm2.txt"},
    {'name':'Женщины до 65','file':"rangf1.txt"},
    {'name':'Женщины после 65','file':"rangf2.txt"}
    ]

# загрузка побочек из файла
def load_disease_chf_from_file(BASE_DIR):
    # Инициализируем пустой список для хранения данных
    file_path = os.path.join(BASE_DIR, 'txt_files_db', 'side_effects.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(';')  # Используем ';' как разделитель
            if len(parts) == 2:
                index_name = parts[0].strip().split(maxsplit=1)  # Разделяем индекс и название
                if len(index_name) == 2:
                    index = int(index_name[0])  # Получаем индекс
                    name = index_name[1].strip()  # Получаем название заболевания
                    value = float(parts[1].replace(',', '.'))  # Заменяем запятую на точку для float
                    disease_chf.objects.update_or_create(index=index, defaults={'name': name, 'value': value})

# загрузка названия ЛС 
def load_drugs_from_file(BASE_DIR):
    # Инициализируем пустой список для хранения данных
    data = []
    file_path = os.path.join(BASE_DIR, 'txt_files_db', 'drugs_xcn.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Убираем пробелы и символы новой строки, затем разбиваем строку по пробелам
            parts = line.strip().split(maxsplit=1)  # maxsplit=1 чтобы разделить только на индекс и значение
            if len(parts) == 2:  # Проверяем, что строка содержит индекс и значение
                index = int(parts[0])  # Преобразуем индекс в целое число
                value = parts[1].strip()  # Получаем значение
                drugs_chf.objects.update_or_create(index=index, defaults={'name': value})
                # Увеличиваем размер списка до нужного индекса, если необходимо
                while len(data) <= index:
                    data.append(None)  # Заполняем None для отсутствующих индексов
                data[index] = value  # Записываем значение по индексу

    return data


def load_data_in_file(BASE_DIR, file_name, nj):
    """Загрузка таблицы ЛС-Побочка."""
    # Инициализация массивов

    rang1 = np.zeros((n_j, n_k))
    rangsum = np.zeros(n_k)
    new_rangsum = np.zeros(n_k)
    ramax = np.zeros(n_k)
    num = np.zeros(n_k)
    nom = np.zeros(n_k)

    # Чтение данных о названиях ЛС из файла в БД
    #load_drugs_from_file(BASE_DIR)
    #load_disease_chf_from_file(BASE_DIR)

    # Чтение данных о рангах попарного взаимодействия из файла
    if file_name=='':
        file_name='rangbase.txt'
    file_path = os.path.join(BASE_DIR, 'txt_files_db', file_name)
    print('file_path:', file_path)
    with open(file_path, 'r') as file:
        rangs = np.array([float(line.strip()) for line in file.readlines()])
    # Составление таблицы рангов и эффектов для отдельных ЛС
    for j in range(1, n_j):
        for k in range(1, n_k):
            rang1[j, k] = rangs[n_k * (j - 1) + (k - 1)]

    for k in range(1, n_k):
        rang1[0, k] = 0.0
    # Вычисление максимального ранга по эффектам для заданного набора ЛС

    for k in range(1, n_k):
        rangsum[k] = sum(rang1[int(nj[m]), k] for m in range(n_j))

    # Максимальный ранг по совокупности эффектов
    ramax[0] = rangsum[0]
    for k in range(2, n_k):
        ramax[k] = max(ramax[k - 1], rangsum[k])

    ram = ramax[n_k - 1]
    print('ram=', ram)
    context = {
        'rand_iteractions': round(float(ram), 2),
    }

    for k in range(1, n_k):
        if rangsum[k] >= 1.0:
            num[k] = k

    # Классификация суммарных рангов воздействий
    if ram >= 1.0:
        numer = 'Запрещено'
    elif ram >= 0.5 and ram < 1.0:
        numer = 'Под наблюдением врача'
    else:
        numer = 'Разрешено'

    # Добавляем описание в контекст
    context['classification_description'] = numer

    side_effects = []
    # Распределение рангов по всей совокупности эффектов
    for k in range(1, n_k):
        if rangsum[k] >= 1.0:
            nom[k] = 3
        elif 0.5 <= rangsum[k] < 1.0:
            nom[k] = 2
        else:
            nom[k] = 1
        # Получение значения name из базы данных по индексу k
        disease = disease_chf.objects.get(index=k)

        # Сохранение названия и значения в контексте
        side_effects.append({'name': disease.name,
                             'class': int(nom[k]),
                             'rangsum': round(float(rangsum[k]), 2)})

        # Группировка элементов по номерам
        #groups[nom].append(context[k])
    # Обновление context с элементами из arr
    sorted_side_effects = sorted(side_effects,
                                 key=lambda x: x['rangsum'],
                                 reverse=True)
    # Фильтрация по классам
    class_1 = [effect for effect in sorted_side_effects
               if effect['class'] == 1]
    class_2 = [effect for effect in sorted_side_effects
               if effect['class'] == 2]
    class_3 = [effect for effect in sorted_side_effects
               if effect['class'] == 3]
    context.update({'side_effects_class_1': class_1,
                    'side_effects_class_2': class_2,
                    'side_effects_class_3': class_3})
    #print('context:')
    #print(context)

    drugs_class_1 = []
    drugs_class_2 = []
    drugs_class_3 = []
    for j in range(1, n_j):
        if not (j in nj):
            for k in range(1, n_k):
                new_rangsum[k] = rangsum[k]+rang1[j, k]
            drugs_class = 0
            for k in range(1, n_k):
                if new_rangsum[k] >= 1.0 and drugs_class < 3:
                    drugs_class = 3
                elif 0.5 <= new_rangsum[k] < 1.0 and drugs_class < 2:
                    drugs_class = 2
                elif drugs_class < 1:
                    drugs_class = 1
            if drugs_class == 1:
                drugs_class_1.append(j)
            elif drugs_class == 2:
                drugs_class_2.append(j)
            elif drugs_class == 3:
                drugs_class_3.append(j)

    arr_drugs = []
    for k in range(0, len(drugs_class_1)):
        # Получение значения name из базы данных по индексу k
        drugs = drugs_chf.objects.get(index=drugs_class_1[k])
        # Сохранение названия и значения в контексте
        arr_drugs.append({'name': drugs.name, 'class': 1})
    #context.update({'arr_drugs_class_1': arr_drugs})
    #arr_drugs = []
    for k in range(1, len(drugs_class_2)):
        # Получение значения name из базы данных по индексу k
        drugs = drugs_chf.objects.get(index=drugs_class_2[k])
        # Сохранение названия и значения в контексте
        arr_drugs.append({'name': drugs.name, 'class': 2})
    context.update({'arr_drugs_class_2': arr_drugs})
    arr_drugs = []
    for k in range(1, len(drugs_class_3)):
        # Получение значения name из базы данных по индексу k
        drugs = drugs_chf.objects.get(index=drugs_class_3[k])
        # Сохранение названия и значения в контексте
        arr_drugs.append({'name': drugs.name, 'class': 3})
    context.update({'arr_drugs_class_3': arr_drugs})
    return context


def go_all_iteractions(request, BASE_DIR):
    context = {}
    # Извлекаем названия ЛС из параметра 'drugs'
    drugs_param = request.GET.get('drugs', '')  # Получаем значение параметра 'drugs'
    # Разделяем названия по запятой и удаляем лишние пробелы
    drug_names = [name.strip().lower() for name in drugs_param.split(',')]
    # Ищем лекарства в базе данных
    drugs = drugs_chf.objects.filter(name__in=[name.lower()
                                               for name in drug_names])
    # Получаем индексы (или id) найденных объектов
    drug_indices = list(drugs.values_list('index', flat=True))
    for k in range(len(drug_indices), n_k):
        drug_indices.append(0)
    # Извлекаем названия файла из 'file_upload'
    file_name = request.GET.get('file_upload', '')  # Получаем значение параметра 'drugs'
    context = load_data_in_file(BASE_DIR, file_name, drug_indices)
    return context

#    nj = np.zeros(n_j)
#    nj[0] = 1
#    nj[1] = 24
#    nj[2] = 17