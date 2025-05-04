"""Модуль исключений для обработки данных из MedScape."""


class WrongDrugNumberError(Exception):
    """Исключение при не правильном числе ЛС."""
    pass


class WrongInputDataError(Exception):
    """Исключение при некорректных входных данных."""
    pass
