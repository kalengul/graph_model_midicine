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

    def combine(self, other: "Mass") -> "Mass":
        """Комбинирование двух масс-функций по правилу Демпстера."""

        conflict = self.m_h * other.m_not_h + self.m_not_h * other.m_h

        if conflict >= 1.0:
            return Mass(m_h=0.0, m_not_h=0.0, m_unknown=1.0)

        denominator = 1.0 - conflict

        m_h = (
            self.m_h * other.m_h
            + self.m_h * other.m_unknown
            + self.m_unknown * other.m_h
        ) / denominator

        m_not_h = (
            self.m_not_h * other.m_not_h
            + self.m_not_h * other.m_unknown
            + self.m_unknown * other.m_not_h
        ) / denominator

        m_unknown = (self.m_unknown * other.m_unknown) / denominator

        return Mass(
            m_h=float(m_h),
            m_not_h=float(m_not_h),
            m_unknown=float(m_unknown),
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
