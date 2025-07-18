from ufal.udpipe import Model, Pipeline

# Загрузка модели
model_path = "full_pipeline\\model_udpipe\\russian-syntagrus-ud-2.0-170801.udpipe"
model = Model.load(model_path)
if not model:
    raise RuntimeError("Не удалось загрузить модель!")

# Инициализация пайплайна
ud_pipeline = Pipeline(model, "tokenize", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")