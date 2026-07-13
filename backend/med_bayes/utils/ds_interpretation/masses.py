from dataclasses import dataclass


@dataclass(frozen=True)
class Mass:
    """Масс-функция для бинарного фрейма {H, not H}."""

    m_h: float
    m_not_h: float
    m_unknown: float

    @property
    def belief(self) -> float:
        return self.m_h

    @property
    def plausibility(self) -> float:
        return self.m_h + self.m_unknown

    @property
    def uncertainty(self) -> float:
        return self.plausibility - self.belief

    def _raw_combine(self, other: "Mass") -> tuple[float, float, float, float]:
        """
        Ненормированная часть комбинирования, общая для правил
        Демпстера и Ягера. Возвращает (m_h, m_not_h, m_unknown, conflict)
        до того, как конфликт будет либо отброшен через нормировку
        (Демпстер), либо возвращён в неопределённость (Ягер).
        """
        m_h = (
            self.m_h * other.m_h
            + self.m_h * other.m_unknown
            + self.m_unknown * other.m_h
        )
        m_not_h = (
            self.m_not_h * other.m_not_h
            + self.m_not_h * other.m_unknown
            + self.m_unknown * other.m_not_h
        )
        m_unknown = self.m_unknown * other.m_unknown
        conflict = self.m_h * other.m_not_h + self.m_not_h * other.m_h

        return m_h, m_not_h, m_unknown, conflict

    def combine(self, other: "Mass") -> "Mass":
        """
        Комбинирование по правилу Демпстера: конфликт нормируется
        (отбрасывается из результата). Подходит для источников,
        независимость которых обоснована.
        """
        m_h, m_not_h, m_unknown, conflict = self._raw_combine(other)

        if conflict >= 1.0:
            return Mass(m_h=0.0, m_not_h=0.0, m_unknown=1.0)

        denominator = 1.0 - conflict

        return Mass(
            m_h=float(m_h / denominator),
            m_not_h=float(m_not_h / denominator),
            m_unknown=float(m_unknown / denominator),
        )

    def combine_yager(self, other: "Mass") -> "Mass":
        """
        Комбинирование по правилу Ягера: конфликт не нормируется,
        а целиком уходит в неопределённость (m_unknown).

        Более консервативно, чем Демпстер — противоречащие друг
        другу источники расширяют интервал [Bel, Pl], а не сужают
        его искусственно за счёт отбрасывания конфликта. Используется
        там, где независимость источников вероятна, но не гарантирована
        (например, разные препараты с потенциально общими путями
        метаболизма).
        """
        m_h, m_not_h, m_unknown, conflict = self._raw_combine(other)

        return Mass(
            m_h=float(m_h),
            m_not_h=float(m_not_h),
            m_unknown=float(m_unknown + conflict),
        )


def make_mass(probability: float, confidence: float) -> Mass:
    """Создание масс-функции для одного пути."""

    probability = float(probability)
    confidence = float(confidence)

    probability = max(0.0, min(1.0, probability))
    confidence = max(0.0, min(1.0, confidence))

    return Mass(
        m_h=probability * confidence,
        m_not_h=(1.0 - probability) * confidence,
        m_unknown=1.0 - confidence,
    )


def vacuous_mass() -> Mass:
    """
    Нейтральный элемент комбинирования (полное незнание).

    combine(vacuous, X) == X и combine_yager(vacuous, X) == X —
    удобно как начальное значение аккумулятора вместо ручной
    проверки на None при первой итерации.
    """
    return Mass(m_h=0.0, m_not_h=0.0, m_unknown=1.0)
