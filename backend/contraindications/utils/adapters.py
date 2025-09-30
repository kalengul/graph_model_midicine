"""Адаптеры для загрузки и связывания противопоказаний ЛС."""


class ContraAdapter:
    """Адаптер для ключей пропивопоказаний."""

    def __init__(self, item, keys=None):
        """Создание адаптера для ключей противопоказаний."""
        self.item = item
        self.keys = keys or ['extracted_contraindication',]

    @property
    def contras(self):
        """Получение списка противоказаний по одному из ключей."""
        for key in self.keys:
            if key in self.item:
                return self.item[key]
        return []


class DrugAdapter:
    """Адаптер для ключей ЛС."""

    def __init__(self, item, keys=None):
        """Создание адаптера для ключей ЛС."""
        self.item = item
        self.keys = keys or ["drug", "name"]

    @property
    def name(self):
        """Получение название ЛС по одному из ключей."""
        for key in self.keys:
            if key in self.item:
                return self.item[key]
        return None
