import json

from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set

from .SemanticEmbeddingProcessor import SemanticEmbeddingProcessor

def normalize_contraindications(
    contraindications: List[str],
    synonym_dict: Dict[str, List[str]],
    model_path: str,
    similarity_threshold: float = 0.85
) -> List[str]:
    """
    Нормализует список противопоказаний с использованием семантической модели.
    
    Args:
        contraindications: Список извлечённых противопоказаний.
        synonym_dict: Словарь вида {стандартный_термин: [синоним1, синоним2, ...]}.
        model_path: Путь к локальной модели SentenceTransformer.
        similarity_threshold: Порог косинусного сходства (0.0–1.0).
    
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

    # Инициализируем процессор и находим ближайшие синонимы
    processor = SemanticEmbeddingProcessor(model_path)
    matched_synonyms = processor.normalize_terms(
        raw_terms=contraindications,
        standard_terms=list(synonym_to_standard.keys()),
        threshold=similarity_threshold
    )

    # Преобразуем найденные синонимы в стандартные термины
    normalized = [
        synonym_to_standard[synonym]
        for synonym in matched_synonyms
        if synonym in synonym_to_standard
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
    # MODEL_PATH = DATA_DIR / "sentence_transformer_models" / "rubert-tiny2"
    # MODEL_PATH = DATA_DIR / "sentence_transformer_models" / "synonym-model_4"

    with open(SYNONYM_DICT_PATH, 'r', encoding='utf-8') as file:
        synonym_dict = json.load(file)

    # Извлечение текста и противопоказаний
    text = SimpleDocxParser.extract_text(MEDCARD_PATH)
    parsed_text = SimpleMedicalExtractor.extract(text)
    contraindications = SimpleMedicalExtractor.extract_contraindications(parsed_text)
    
    print(f"Исходные противопоказания: {contraindications}")
    
    # Вызов новой функции
    normalized_result = normalize_contraindications(
        contraindications=contraindications,
        synonym_dict=synonym_dict,
        model_path=MODEL_PATH,
        similarity_threshold=0.90
    )
    
    print(f"Нормализованные противопоказания: {normalized_result}")