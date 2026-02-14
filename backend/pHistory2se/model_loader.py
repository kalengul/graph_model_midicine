# backend/pHistory2se/utils/model_loader.py

import os
import json

from sentence_transformers import SentenceTransformer

# Пути (можно вынести в settings.py позже)
EMB_MODEL_PATH = 'backend\\data\\sentence_transformer_models\\all-MiniLM-L6-v2'
SYNONYM_DICT_PATH = "backend\\data\\dictionaries\\dict_synonym_contraindications.json"


# Глобальная переменная — будет инициализирована один раз
_model = None
_synonym_dict = None

def get_embedding_model():
    global _model
    if _model is None:
        print("Загрузка модели эмбеддингов...")
        _model = SentenceTransformer(EMB_MODEL_PATH)
        print("Модель загружена.")
    return _model

def get_synonym_dict():
    global _synonym_dict
    if _synonym_dict is None:
        with open(SYNONYM_DICT_PATH, encoding='utf-8') as f:
            _synonym_dict = json.load(f)
    return _synonym_dict