# backend/pHistory2se/utils/model_loader.py
import os
import json
from pathlib import Path
from django.conf import settings

from pHistory2se.utils.SemanticEmbeddingProcessor import SemanticEmbeddingProcessor

# Пути (можно вынести в settings.py позже)
# EMB_MODEL_PATH = 'data\\sentence_transformer_models\\all-MiniLM-L6-v2'
EMB_MODEL_PATH = 'all-MiniLM-L6-v2'
SYNONYM_DICT_FILE = "dict_synonym_contraindications.json"

DIR_PATH = Path(settings.SYNONYM_PATH)
SYNONYM_DICT_PATH = DIR_PATH / SYNONYM_DICT_FILE

# Глобальная переменная — будет инициализирована один раз
_model = None
_synonym_dict = None

def get_embedding_processor():
    global _model
    if _model is None:
        print("Загрузка процессора эмбеддингов...")
        _processor = SemanticEmbeddingProcessor(EMB_MODEL_PATH)
        print("SemanticEmbeddingProcessor загружен.")
    return _processor

def get_synonym_dict():
    global _synonym_dict
    if _synonym_dict is None:
        with open(SYNONYM_DICT_PATH, encoding='utf-8') as f:
            _synonym_dict = json.load(f)
    return _synonym_dict

def set_synonym_dict(loaded_dict):
    global _synonym_dict
    _synonym_dict = loaded_dict
    return _synonym_dict
