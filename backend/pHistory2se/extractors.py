# pHistory2se/medical_extractor.py
import re
from typing import List, Dict


class SimpleMedicalExtractor:
    """Упрощенный извлекатель медицинских данных."""
    
    # Ключевые разделы и их разделители
    SECTIONS = {
        "основной диагноз": "newline",
        "диагноз клинический": "newline", 
        "клинический диагноз": "newline",
        "осложнения": "newline",
        "сопутствующие заболевания": "comma",
        "жалобы при поступлении": "comma"
    }
    
    @classmethod
    def extract(cls, text: str) -> List[str]:
        """Основной метод извлечения данных."""
        text_lower = text.lower()
        results = []
        
        for section_name, delimiter in cls.SECTIONS.items():
            # Ищем все вхождения раздела (регистронезависимо)
            pattern = f"{section_name}[:]?"
            matches = list(re.finditer(pattern, text_lower))
            
            for match in matches:
                # Находим начало текста после раздела
                start_pos = match.end()
                
                # Находим конец текста (до следующего раздела или конца)
                end_pos = cls._find_section_end(text_lower, start_pos)
                
                # Извлекаем текст раздела
                section_text = text[start_pos:end_pos].strip()
                
                if section_text:
                    # Обрабатываем в зависимости от разделителя
                    if delimiter == "newline":
                        items = cls._split_by_newline(section_text)
                    else:  # comma
                        items = cls._split_by_comma(section_text)
                    
                    results.extend(items)
        
        # Убираем дубликаты и пустые строки
        return [item for item in cls._deduplicate(results) if item.strip()]
    
    @staticmethod
    def _find_section_end(text_lower: str, start_pos: int) -> int:
        """Находит конец секции (до следующего ключевого слова или конца текста)."""
        # Список всех ключевых слов для поиска
        all_keywords = list(SimpleMedicalExtractor.SECTIONS.keys())
        
        # Ищем следующее ключевое слово после start_pos
        next_positions = []
        for keyword in all_keywords:
            pos = text_lower.find(keyword, start_pos)
            if pos != -1:
                next_positions.append(pos)
        
        # Если нашли следующее ключевое слово, возвращаем его позицию
        if next_positions:
            return min(next_positions)
        
        # Иначе возвращаем конец текста
        return len(text_lower)
    
    @staticmethod
    def _split_by_newline(text: str) -> List[str]:
        """Разделяет текст по переводам строк."""
        lines = text.split('\n')
        items = []
        
        for line in lines:
            line = line.strip()
            # Убираем нумерацию: 1., 2., и т.д.
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            # Убираем маркеры списков
            line = re.sub(r'^[-\*•]\s*', '', line)
            
            if line and line not in items:
                items.append(line)
        
        return items
    
    @staticmethod
    def _split_by_comma(text: str) -> List[str]:
        """Разделяет текст по запятым, учитывая вложенные конструкции."""
        items = []
        current = []
        parentheses = 0
        
        for char in text:
            if char == '(':
                parentheses += 1
                current.append(char)
            elif char == ')':
                parentheses -= 1
                current.append(char)
            elif char == ',' and parentheses == 0:
                item = ''.join(current).strip()
                if item:
                    items.append(item)
                current = []
            else:
                current.append(char)
        
        # Добавляем последний элемент
        if current:
            item = ''.join(current).strip()
            if item:
                items.append(item)
        
        return items
    
    @staticmethod
    def _deduplicate(items: List[str]) -> List[str]:
        """Убирает дубликаты, сохраняя порядок."""
        seen = set()
        unique = []
        
        for item in items:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        
        return unique