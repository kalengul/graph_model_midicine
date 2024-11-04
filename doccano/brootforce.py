import itertools
import subprocess
import spacy
from spacy import displacy
from spacy.training import Example

# Интервалы для каждого параметра
dropout_values = [0.1, 0.2, 0.3]
accumulate_gradient_values = [1, 2, 4]
max_epochs_values = [10, 20, 30]
eval_frequency_values = [50, 100, 150, 200]
tolerance_values = [0.001, 0.005, 0.010]
eps_values = [1e-6, 1e-5]
learn_rate_values = [0.0001, 0.001, 0.01]

# Файл для сбора метрик
directory = "auto_nosplitText_nosplitTestText"
metrics_file = "training_metrics.csv"

with open(f"{directory}\\{metrics_file}", "w") as file:
    file.write("dropout,accumulate_gradient,max_epochs,eval_frequency,tolerance,eps,learn_rate,precision,recall,f_score\n")

# Чтение оригинальной конфигурации из файла
with open("configs\\config_backup.cfg", 'r', encoding='utf-8') as file:
    original_config_data = file.read()  # Сохраняем оригинальный конфиг

# Перебор всех комбинаций параметров
for (dropout,
     accumulate_gradient,
     max_epochs,
     eval_frequency,
     tolerance,
     eps,
     learn_rate) in itertools.product(  dropout_values,
                                        accumulate_gradient_values,
                                        max_epochs_values,
                                        eval_frequency_values,
                                        tolerance_values,
                                        eps_values,
                                        learn_rate_values):
    


    # # Изменение config файла в соответствии с параметрами
    # config_file = "./configs/config.cfg"
    # with open(config_file, "r") as file:
    #     config_data = file.read()

    # Восстанавливаем конфигурацию к оригинальному состоянию
    config_data = original_config_data

    # Замена значений параметров в config файле
    config_data = config_data.replace("${dropout}", str(dropout))
    config_data = config_data.replace("${accumulate_gradient}", str(accumulate_gradient))
    config_data = config_data.replace("${max_epochs}", str(max_epochs))
    config_data = config_data.replace("${eval_frequency}", str(eval_frequency))
    config_data = config_data.replace("${tolerance}", str(tolerance))
    config_data = config_data.replace("${eps}", str(eps))
    config_data = config_data.replace("${learn_rate}", str(learn_rate))

    print(f"dropout {dropout}\naccumulate_gradient {accumulate_gradient}\nmax_epochs {max_epochs}\neval_frequency {eval_frequency}\ntolerance {tolerance}\neps {eps}\nlearn_rate {learn_rate}\n"
    )

    # Сохранение обновленного config файла
    with open("configs\\config.cfg", "w") as file:
        file.write(config_data)

    # Запуск команды обучения модели
    subprocess.run([
        "py", "-m", "spacy", "train", "./configs/config.cfg",
        "--output", "./output", "--paths.train", "./datasets/train.spacy",
        "--paths.dev", "./datasets/val.spacy"
    ], check=True)

    # Загрузка обученной модели и выполнение предсказаний
    model_path = r".\output\model-best"
    nlp1 = spacy.load(model_path)

    # Загрузка валидационного набора данных
    val_data = spacy.tokens.DocBin().from_disk("./datasets/test.spacy").get_docs(nlp1.vocab)

    # Создание списка объектов Example для оценки
    examples = [Example.from_dict(doc, {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}) for doc in val_data]

    # Оценка модели на валидационном наборе данных
    scorer = nlp1.evaluate(examples)
    precision = scorer["ents_p"]
    recall = scorer["ents_r"]
    f_score = scorer["ents_f"]

    # Запись метрик в файл
    with open(f"{directory}\\{metrics_file}", "a") as file:
        file.write( f"{dropout},"+\
                    f"{accumulate_gradient},"+\
                    f"{max_epochs},"+\
                    f"{eval_frequency},"+\
                    f"{tolerance},"+\
                    f"{eps},"+\
                    f"{learn_rate},"+\
                    f"{precision},"+\
                    f"{recall},"+\
                    f"{f_score}"+\
                    "\n"
                    )


    text = "Ингибирует циклооксигеназу (ЦОГ-1 и ЦОГ-2) и необратимо тормозит циклооксигеназный путь метаболизма арахидоновой кислоты, блокирует синтез ПГ (ПГA2, ПГD2, ПГF2aльфа, ПГE1, ПГE2 и др.) и тромбоксана. Уменьшает гиперемию, экссудацию, проницаемость капилляров, активность гиалуронидазы, ограничивает энергетическое обеспечение воспалительного процесса путем угнетения продукции АТФ. Влияет на подкорковые центры терморегуляции и болевой чувствительности. Снижение содержания ПГ (преимущественно ПГЕ1) в центре терморегуляции приводит к понижению температуры тела вследствие расширения сосудов кожи и увеличения потоотделения. Обезболивающий эффект обусловлен влиянием на центры болевой чувствительности, а также периферическим противовоспалительным действием и способностью салицилатов снижать альгогенное действие брадикинина. Уменьшение содержания тромбоксана А2 в тромбоцитах приводит к необратимому подавлению агрегации, несколько расширяет сосуды. Антиагрегантное действие сохраняется в течение 7 суток после однократного приема. В ходе ряда клинических исследований показано, что существенное ингибирование склеиваемости кровяных пластинок достигается при дозах до 30 мг. Увеличивает фибринолитическую активность плазмы и снижает концентрацию витамин K-зависимых факторов свертывания (II, VII, IX, X). Стимулирует выведение мочевой кислоты, поскольку нарушается ее реабсорбция в канальцах почек."
    doc = nlp1(text)

    # Визуализация в виде SVG
    svg = displacy.render(doc, style="ent", jupyter=False)
    model_name =    f"ml"+\
                    f"drpt_{dropout}-"+\
                    f"accum_{accumulate_gradient}-"+\
                    f"epo_{max_epochs}-"+\
                    f"efreq_{eval_frequency}-"+\
                    f"tlr_{tolerance}-"+\
                    f"eps_{eps}-"+\
                    f"lrnrt_{learn_rate}-"

    svg_filename = f"{directory}\\{model_name}.svg"

    # Сохранение SVG в файл
    with open(svg_filename, "w", encoding="utf-8") as file:
        file.write(svg)
    
    print(f"Модель {model_name} сохранена как {svg_filename}")
