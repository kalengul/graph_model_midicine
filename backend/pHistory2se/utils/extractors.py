# pHistory2se/extractor.py
import re
from typing import Dict, List, Tuple, Optional


class SimpleMedicalExtractor:
    """Упрощенный извлекатель медицинских данных."""

    @classmethod
    def extract(cls, text: str) -> List[str]:
        """
        Извлекает разделы из текста, сначала находя заголовки, затем определяя границы.
        """
        def build_header_patterns(section_headers: Dict[str, List[str]]) -> List[Tuple[str, str]]:
            HSPACE = r'[ \t\r\f\v]'
            patterns = []
            for key, phrases in section_headers.items():
                normalized = []
                for ph in phrases:
                    # 1. Экранируем ВСЁ (включая скобки, точки и т.д.)
                    escaped = re.escape(ph)
                    # 2. Заменяем экранированные пробелы (т.е. '\\ ') на HSPACE+
                    normalized_ph = re.sub(r'\\ ', f'{HSPACE}+', escaped)
                    normalized.append(normalized_ph)
                
                alt = '|'.join(f'(?:{n})' for n in normalized)
                pattern_str = rf'(?:\n|^)(?:{alt})(?:{HSPACE}*:{HSPACE}*)?'
                patterns.append((key, pattern_str))
            return patterns

        # Определяем, какие заголовки мы ищем и какому ключу они соответствуют
        section_headers = {
            "human_data": [
                "ВЫПИСНОЙ ЭПИКРИЗ ИЗ ИСТОРИИ БОЛЕЗНИ №",
                "ВЫПИСНОЙ ЭПИКРИЗ"
            ],
            "clinical_diagnosis": [
                "ДИАГНОЗ КЛИНИЧЕСКИЙ",
                "Клинический диагноз"
            ],
            "main_diagnosis": [
                "Основной диагноз"
            ],
            "complications_main_diagnosis": [
                "Осложнения основного заболевания",
                "Осложнения"
            ],
            "related_diseases": [
                "Сопутствующие заболевания"
            ],
            "complaints": [
                "ЖАЛОБЫ ПРИ ПОСТУПЛЕНИИ",
                "ЖАЛОБЫ"
            ],
            "history_disease": [
                "АНАМНЕЗ ЗАБОЛЕВАНИЯ",
                "История заболевания"
            ],
            "history_life": [
                "АНАМНЕЗ ЖИЗНИ",
                "История жизни"
            ],
            "objective_exam": [
                "ДАННЫЕ ОБЪЕКТИВНОГО ОСМОТРА",
                "Объективный статус",
                "ОСМОТР",
                "ДАННЫЕ ОСМОТРА ПРИ ПОСТУПЛЕНИИ"
            ],
            "lab_instrumental": [
                "ЛАБОРАТОРНО-ИНСТРУМЕНТАЛЬНЫЕ ИССЛЕДОВАНИЯ",
                "ЛАБОРАТОРНЫЕ И ИНСТРУМЕНТАЛЬНЫЕ МЕТОДЫ",
                "ИНСТРУМЕНТАЛЬНЫЕ ИССЛЕДОВАНИЯ",
                "ЛАБОРАТОРНО-ИНСТРУМЕНТАЛЬНЫЕ ДАННЫЕ",
                "Данные лабораторно-инструментальных исследований"
            ],
            "treatment": [
                "ПРОВЕДЁННОЕ ЛЕЧЕНИЕ В СТАЦИОНАРЕ",
                "ПРОВЕДЁННОЕ ЛЕЧЕНИЕ",
                "ТЕРАПИЯ НА МОМЕНТ ПОСТУПЛЕНИЯ"
            ],
            "discharge_status": [
                "СОСТОЯНИЕ ПРИ ВЫПИСКЕ",
                "Выписной статус"
            ],
            "conclusion": [
                "Заключение"
            ],
            "recommendations": [
                "РЕКОМЕНДАЦИИ (НАЗНАЧЕННАЯ ТЕРАПИЯ)",
                "РЕКОМЕНДАЦИИ (НОВАЯ ТЕРАПИЯ)",
                "РЕКОМЕНДАЦИИ (ОТРАЖЕНИЕ НАЗНАЧЕННОЙ ТЕРАПИИ)",
                "Рекомендации"
            ],
            "additional_recommendations":[
                "ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ"
            ],
            "follow_up": [
                "ДИСПАНСЕРНОЕ НАБЛЮДЕНИЕ",
                "Наблюдение"
            ]
        }

        # Получаем строки паттернов
        raw_patterns = build_header_patterns(section_headers)
        # Компилируем один раз с флагами
        compiled_patterns = [
            (key, re.compile(pat, re.IGNORECASE))
            for key, pat in raw_patterns
        ]

        # Найдём все заголовки в тексте с их позициями и ключами
        matches: List[Tuple[int, int, str]] = []  # (start, end, key)

        for key, pattern in compiled_patterns:
            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()
                matches.append((start, end, key))

        # Отсортируем по позиции в тексте
        matches.sort(key=lambda x: x[0])

        # Удалим дубликаты (если один и тот же фрагмент попадает под несколько паттернов)
        # Оставим первый найденный ключ для каждой позиции начала
        seen_starts = set()
        unique_matches = []
        for start, end, key in matches:
            if start not in seen_starts:
                seen_starts.add(start)
                unique_matches.append((start, end, key))

        # Для каждого ключа остаётся только первое вхождение
        seen_keys = set()
        filtered_matches = []
        for start, end, key in unique_matches:
            if key not in seen_keys:
                seen_keys.add(key)
                filtered_matches.append((start, end, key))

        # Теперь извлекаем содержимое между заголовками
        sections = {}
        for i, (start, end, key) in enumerate(filtered_matches):
            # Начало содержимого — сразу после заголовка
            content_start = end

            # Конец содержимого — начало следующего заголовка или конец текста
            if i + 1 < len(filtered_matches):
                content_end = filtered_matches[i + 1][0]
            else:
                content_end = len(text)

            raw_content = text[content_start:content_end].strip()

            # Очистка: удаляем лишние пробелы и переносы
            clean_content = re.sub(r'[ \t\r\f\v]+', ' ', raw_content) if raw_content else ""
            
            if clean_content:
                # Для диагнозов постобработка
                if key in ('main_diagnosis',
                           'complications_main_diagnosis', 
                           'related_diseases'):
                    sections[key] = [cls._post_processing(content) for content in clean_content.split('\n')]
        
                else:
                    sections[key] = clean_content

        return sections
    
    @staticmethod
    def extract_contraindications(sections: Dict[str, List[str]]) -> List[str]:
        """
        Извлекает противопоказания из строк ключей
        'main_diagnosis', 'complications_main_diagnosis', 'related_diseases'.

        Возвращает список таких строк.
        """
        target_keys = [
            'main_diagnosis',
            'complications_main_diagnosis',
            'related_diseases'
        ]

        contraindications = []
        for key in target_keys:
            contraindications.extend(sections.get(key, []))

        return contraindications
    
    @staticmethod
    def _post_processing(text: str) -> str:
        """
        1. Удаление начальной кодировки (всего до " — ").
        2. Обрезка по первой запятой.
        3. Приведение к нижнему регистру.
        4. Удаление точки в конце (если есть).
        """
        # Шаг 1: Убрать всё до " — " и взять остаток
        if " — " in text:
            after_dash = text.split(" — ", 1)[1]
        else:
            after_dash = text

        # Шаг 2: Взять часть до первой запятой
        before_comma = after_dash.split(",", 1)[0].strip()

        # Шаг 3: Привести к нижнему регистру
        lower_text = before_comma.lower()

        # Шаг 4: Удалить точку в конце, если она есть
        if lower_text.endswith('.'):
            result = lower_text[:-1]
        else:
            result = lower_text

        return result
