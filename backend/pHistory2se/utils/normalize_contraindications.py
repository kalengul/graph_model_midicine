import json
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set

# from pHistory2se.utils.SemanticEmbeddingProcessor import SemanticEmbeddingProcessor

import requests
from django.conf import settings

class SemanticServiceClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # можно настроить таймауты и retries

    def find_similar(self, queries, corpus_terms, threshold=None, top_k=1):
        url = f"{self.base_url}/find_similar"
        payload = {
            "queries": queries,
            "corpus_terms": corpus_terms,
            "threshold": threshold,
            "top_k": top_k
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["results"]
    

def normalize_contraindications(
    contraindications: List[str],
    synonym_dict: Dict[str, List[str]],
    client: SemanticServiceClient,
    threshold: float = 0.85
) -> List[str]:
    """
    Нормализует список противопоказаний с использованием семантической модели.
    
    Args:
        contraindications: Список извлечённых противопоказаний.
        synonym_dict: Словарь вида {стандартный_термин: [синоним1, синоним2, ...]}.
        processor: SemanticEmbeddingProcessor
        threshold: Порог косинусного сходства (0.0–1.0).
    
    Returns:
        Список нормализованных стандартных терминов.
    """
    if not contraindications:
        return []

    # Создаём обратный маппинг: синоним → стандартный термин
    synonym_to_standard = {
        synonym: standard_term
        for standard_term, synonyms in synonym_dict.items()
        for synonym in synonyms
    }

    # Поиск ближайших синонимов
    matched_synonyms = client.find_similar(
        queries=contraindications,
        corpus_terms=list(synonym_to_standard.keys()),
        threshold=threshold
    )

    # Преобразуем найденные синонимы в стандартные термины
    normalized = [
        synonym_to_standard[standart[0]['term']]
        for raw, standart in matched_synonyms.items()
        if standart
    ]

    return normalized


# --- Блок для быстрой проверки ---
if __name__ == "__main__":
    from ..parsers import SimpleDocxParser
    from .extractors import SimpleMedicalExtractor

    # Пути (используем pathlib для кроссплатформенности)
    DATA_DIR = "backend\\data\\"
    SYNONYM_DICT_PATH =  f"{DATA_DIR}dictionaries\\dict_synonym_contraindications.json"
    MEDCARD_PATH = f"{DATA_DIR}medcard_files\\Выписка_ХСН_3.docx"
    MODEL_PATH = f"{DATA_DIR}sentence_transformer_models\\all-MiniLM-L6-v2"
    # MODEL_PATH = f"{DATA_DIR}sentence_transformer_models\\rubert-tiny2"
    # MODEL_PATH = f"{DATA_DIR}sentence_transformer_models\\synonym-model_4"

    with open(SYNONYM_DICT_PATH, 'r', encoding='utf-8') as file:
        synonym_dict = json.load(file)

    # Извлечение текста и противопоказаний
    text = SimpleDocxParser.extract_text(MEDCARD_PATH)
    parsed_text = SimpleMedicalExtractor.extract(text)
    contraindications = SimpleMedicalExtractor.extract_contraindications(parsed_text)
    
    # Инициализируем процессор
    processor = SemanticEmbeddingProcessor(MODEL_PATH)
    
    print(f"Исходные противопоказания: {contraindications}")
    
    # Вызов новой функции
    normalized_result = normalize_contraindications(
        contraindications=contraindications,
        synonym_dict=synonym_dict,
        processor=processor,
        threshold=0.90
    )
    
    print(f"Нормализованные противопоказания: {normalized_result}")