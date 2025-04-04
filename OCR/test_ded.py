import json

from dedoc import DedocManager

# Инициализация менеджера
dedoc_manager = DedocManager()

# Путь к вашему PDF-документу
file_path = 'Амиодарон.pdf'

# Чтение документа
document_tree = dedoc_manager.parse(file_path)

# Преобразование в JSON
json_content = document_tree.to_api_schema().model_dump()

# Сохранение в файл
with open('Амиодарон.json', 'w', encoding='utf-8') as json_file:
    json.dump(json_content, json_file, ensure_ascii=False, indent=4)
