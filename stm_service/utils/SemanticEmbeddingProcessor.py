# SemanticEmbeddingProcessor.py

import re
from typing import Dict, List, Optional, Set
import json
from collections import defaultdict, OrderedDict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class SemanticEmbeddingProcessor:
    def __init__(self, model_path: str, abbr_dataset_path=None,
                 cache_size: int = 1000, threshold = 0.9):
        print("model_path", model_path)
        self.model = SentenceTransformer(model_path)
        self.cache_size = cache_size
        self.cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self.abbrev_map = {}
        self.threshold = threshold
        
        if abbr_dataset_path:
            with open(abbr_dataset_path, 'r', encoding='utf-8') as file:
                abbr_dataset = json.load(file)
            self.abbrev_map = {
                variant.strip(): key.strip()
                for key, variants in abbr_dataset.items()
                for variant in variants
            }
            print("Загружен датасет аббревиатур")
        else:
            print("Датасет аббревиатур не обнаружен. Замены не будет")

    def get_embedding(self, term: str) -> np.ndarray:
        term = term.strip()
        if term in self.cache:
            # Переместить в конец (сделать "недавно использованным")
            self.cache.move_to_end(term)
            return self.cache[term]
        
        # Генерируем новое эмбеддинг
        embedding = self.model.encode(term, convert_to_numpy=True)
        
        # Проверяем размер кэша
        if len(self.cache) >= self.cache_size:
            # Удаляем самый старый элемент (первый в OrderedDict)
            self.cache.popitem(last=False)
        
        # Добавляем новый элемент в конец
        self.cache[term] = embedding
        return embedding

    def get_embeddings_batch(self, terms: List[str]) -> np.ndarray:
        terms_clean = [t.strip() for t in terms]
        unique_terms = list(dict.fromkeys(terms_clean))  # сохраняем порядок

        # Найти отсутствующие
        missing = [t for t in unique_terms if t not in self.cache]

        if missing:
            embeddings = self.model.encode(missing, convert_to_numpy=True)
            for term, emb in zip(missing, embeddings):
                if len(self.cache) >= self.cache_size:
                    self.cache.popitem(last=False)
                self.cache[term] = emb

        # Возвращаем в том же порядке, что и вход
        return np.array([self.cache[t] for t in terms_clean])

    def cosine_similarity_matrix(self,
                                queries: List[str],
                                candidates: List[str],
                                apply_penalty = False,
                                ) -> np.ndarray:
        # Очищаем и нормализуем запросы и кандидаты
        cleaned_queries = [self._clean_term(q) for q in queries]
        cleaned_candidates = [self._clean_term(c) for c in candidates]

        # Получаем эмбеддинги для очищенных строк
        query_embs = self.get_embeddings_batch(cleaned_queries)
        candidate_embs = self.get_embeddings_batch(cleaned_candidates)

        # Считаем косинусное сходство
        sims_matrix = cosine_similarity(query_embs, candidate_embs)

        # Применяем штраф, если нужно
        if apply_penalty:
            sims_matrix = self._apply_number_penalty(
                sims_matrix, cleaned_queries, cleaned_candidates, penalty=0.05
            )

        return sims_matrix
    
    def _clean_term(self, term: str) -> str:
        """
        Удаляет содержимое в скобках, включая скобки, и расшифровывает аббревиатуры.
        """
        term = str(term).lower()
        # Удаляем всё, что в скобках (включая круглые скобки)
        term = re.sub(r'\([^)]*\)', '', term).strip()
        # Раскрываем аббревиатуры, если карта задана
        if self.abbrev_map:
            term = self._expand_abbreviations(term)
        return term
   

    def find_similar_terms(
        self,
        queries: List[str],
        corpus_terms: List[str],
        threshold: float = None,
        top_k: int = 1
    ) -> Dict[str, List[Dict[str, float]]]:
        """
        Находит наиболее похожие термины из corpus_terms для каждого запроса.

        :param queries: Список запросов.
        :param corpus_terms: Список терминов, среди которых ищем
        :param threshold: Порог синонимичности
        :param top_k: Количество лучших совпадений.
        :return: Словарь: {запрос: [{"term": ..., "similarity": ...}, ...]}
        """
        if not queries:
            return {}
        if not corpus_terms:
            return {q: [] for q in queries}
        
        # Используем порог из параметра или из поля класса
        threshold = threshold if threshold is not None else self.threshold

        sims_matrix = self.cosine_similarity_matrix(queries, corpus_terms, False)

        results = {}
        for i, query in enumerate(queries):
            sims = sims_matrix[i]
            top_indices = np.argsort(sims)[::-1][:top_k]
            matches = [
                {"term": corpus_terms[idx], "similarity": float(sims[idx])}
                for idx in top_indices if sims[idx] >= threshold
            ]
            results[query] = matches

        # print(f"Найдено совпадений: {sum(len(v) for v in results.values())}")
        return results
    
    def normalize_terms(
            self,
            raw_terms: List[str], 
            standard_terms: List[str],
            threshold: float = None,
            top_n: int = 1) -> Dict[str, List[str]]:
        """Нормализует исходные термины к эталонным с помощью семантической модели."""
        
        if not raw_terms or not standard_terms:
            return {}
        
        # Используем порог из параметра или из поля класса
        threshold = threshold if threshold is not None else self.threshold
        
        matches = self.find_similar_terms(raw_terms, standard_terms, threshold, top_n)
        
        result = defaultdict(list)
        for original, match_list in matches.items():
            if match_list:
                result[match_list[0]['term']].append(original)
        
        return dict(result)
    
    def cluster_similar_strings(self,
                                strings_list: list[str],
                                threshold: float = None
                                ) -> dict[str, list[str]]:
        """
        Кластеризация списка строк по семантической схожести.
        
        :param strings_list: Список строк для кластеризации
        :param similarity_threshold: Порог схожести для объединения в кластер
        :return: Словарь, где ключ - каноническая строка кластера,
                значение - список строк в кластере
        """
        if not strings_list:
            return {}
        
        # Используем порог из параметра или из поля класса
        threshold = threshold if threshold is not None else self.threshold
        
        # Уникализация и очистка списка
        unique_strings = list(dict.fromkeys(strings_list))  # сохраняем порядок первого появления
        unique_strings = [s.strip() for s in unique_strings if s and str(s).strip()]
        
        if not unique_strings:
            return {}
        
        # Получаем матрицу схожести
        sim_matrix = self.cosine_similarity_matrix(
            unique_strings, 
            unique_strings, 
            apply_penalty=True
        )
        
        # Словарь для результатов
        cluster_dict = {}
        used_indices = set()
        
        for i, term in enumerate(unique_strings):
            if i in used_indices:
                continue
            
            # Находим похожие строки
            similar_indices = np.where(sim_matrix[i] >= threshold)[0]
            new_indices = [idx for idx in similar_indices if idx not in used_indices]
            
            if not new_indices:
                # Если нет похожих строк, создаем кластер из одного элемента
                cluster_dict[term] = [term]
                used_indices.add(i)
                continue
            
            # Формируем кластер
            cluster = [unique_strings[idx] for idx in new_indices]
            
            # Определяем каноническую строку для кластера
            # Используем частоту в исходном списке для выбора наиболее популярной
            # term_counts = {t: strings_list.count(t) for t in cluster}
            # canonical = max(term_counts.items(), key=lambda x: x[1])[0]
            
            # Альтернативный вариант: использовать первую строку в кластере
            canonical = cluster[0]
            
            cluster_dict[canonical] = cluster
            used_indices.update(new_indices)
        
        return cluster_dict

    def size(self) -> int:
        return len(self.cache)
    

if __name__ == "__main__":
    FILENAME_SIDE_E_DICT = "make_side_effect_dataset\\data\\side_e_synonim_dict_all.json"
    FILENAME_DATASET_ORLOV = "bayes_network\\data\\Orlov.json"
    MODEL_PATH = "train_synonim_model\\data\\synonym-model_4"
    ABBR_MAP_PATH = "create_graph\\data\\abbrev_dict.json"

    import json

    with open(FILENAME_SIDE_E_DICT, "r", encoding="utf-8") as file:
        side_e_list = list(json.load(file)[0])
    # print("side_e_list:", side_e_list)

    with open(FILENAME_DATASET_ORLOV, "r", encoding="utf-8") as file:
        prepare_list = list(json.load(file))
    # print("prepare_list:", prepare_list)

    # print("reference_list:", reference_list)

    prepare_lemm_list = ["изосорбид динитрат", "гепарин натрий"]
    side_e_lemm_list = ["отек квинки", "головной боль", "отек сустав",
                        "аллергический отёк",
                        'гиперчувствительность, включая ангиоотечь',
                        'аллергический отёк и ангионевротический отёк']
    
    other_exapmle = [
        "альфа-адреномиметическое действие", "α-адреномиметическое действие",
        "β-адреномиметическое действие", "α-адреномиметическое действие",
        "бета-адреномиметическое действие", "альфа-адреномиметическое действие",
        "бета-адреномиметическое действие", "β-адреномиметическое действие"
    ]

    queries_list  = prepare_lemm_list + side_e_lemm_list + other_exapmle
    reference_list = side_e_list + prepare_list + other_exapmle
    print()
    semantic_comp = SemanticEmbeddingProcessor(MODEL_PATH,
                                               abbr_dataset_path=ABBR_MAP_PATH)
    semantic_res = semantic_comp.find_similar_terms(queries_list, reference_list,
                                                    0.85, 2)
    print("semantic_res", semantic_res)