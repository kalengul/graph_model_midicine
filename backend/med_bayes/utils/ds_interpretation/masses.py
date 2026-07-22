from dataclasses import dataclass


@dataclass(frozen=True)
class Mass:
    """Масс-функция для бинарного фрейма {H, not H}."""

    m_h: float
    m_not_h: float
    m_theta: float

    @property
    def belief(self) -> float:
        return self.m_h

    @property
    def plausibility(self) -> float:
        return self.m_h + self.m_theta

    @property
    def uncertainty(self) -> float:
        return self.plausibility - self.belief

    def _raw_combine(self, other: "Mass") -> tuple[float, float, float, float]:
        """
        Ненормированная часть комбинирования, общая для правил
        Демпстера и Ягера. Возвращает (m_h, m_not_h, m_theta, conflict)
        до того, как конфликт будет либо отброшен через нормировку
        (Демпстер), либо возвращён в неопределённость (Ягер).
        """
        m_h = (
            self.m_h * other.m_h
            + self.m_h * other.m_theta
            + self.m_theta * other.m_h
        )
        m_not_h = (
            self.m_not_h * other.m_not_h
            + self.m_not_h * other.m_theta
            + self.m_theta * other.m_not_h
        )
        m_theta = self.m_theta * other.m_theta
        conflict = self.m_h * other.m_not_h + self.m_not_h * other.m_h

        return m_h, m_not_h, m_theta, conflict

    def combine(self, other: "Mass") -> "Mass":
        """
        Комбинирование по правилу Демпстера: конфликт нормируется
        (отбрасывается из результата). Подходит для источников,
        независимость которых обоснована.
        """
        m_h, m_not_h, m_theta, conflict = self._raw_combine(other)

        if conflict >= 1.0:
            return Mass(m_h=0.0, m_not_h=0.0, m_theta=1.0)

        denominator = 1.0 - conflict

        return Mass(
            m_h=float(m_h / denominator),
            m_not_h=float(m_not_h / denominator),
            m_theta=float(m_theta / denominator),
        )

    def combine_yager(self, other: "Mass") -> "Mass":
        """
        Попарное комбинирование по правилу Ягера: конфликт не
        нормируется, а целиком уходит в неопределённость (m_theta).

        Более консервативно, чем Демпстер — противоречащие друг
        другу источники расширяют интервал [Bel, Pl], а не сужают
        его искусственно за счёт отбрасывания конфликта. Используется
        там, где независимость источников вероятна, но не гарантирована
        (например, разные препараты с потенциально общими путями
        метаболизма).

        ВАЖНО: эта операция не ассоциативна. Последовательные вызовы
        для 3 и более источников (a.combine_yager(b).combine_yager(c))
        дают результат, зависящий от порядка — см. combine_yager_many
        для корректного симметричного комбинирования N источников.
        Использовать этот метод напрямую можно только для ровно двух
        масс-функций.
        """
        m_h, m_not_h, m_theta, conflict = self._raw_combine(other)

        return Mass(
            m_h=float(m_h),
            m_not_h=float(m_not_h),
            m_theta=float(m_theta + conflict),
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
        m_theta=1.0 - confidence,
    )


def vacuous_mass() -> Mass:
    """
    Нейтральный элемент комбинирования (полное незнание).

    combine(vacuous, X) == X и combine_yager(vacuous, X) == X —
    удобно как начальное значение аккумулятора вместо ручной
    проверки на None при первой итерации.
    """
    return Mass(m_h=0.0, m_not_h=0.0, m_theta=1.0)


def combine_yager_many(masses: list[Mass]) -> Mass:
    """
    Симметричное (не последовательно-попарное) комбинирование N
    масс-функций правилом Ягера.

    В отличие от Демпстера, нормировка на (1-conflict) в правиле
    Ягера не выполняется — конфликт переносится в m(Θ) явным
    сложением, а это не ассоциативная операция. Если сворачивать
    источники последовательно парами (m.combine_yager(a).combine_yager(b)...),
    результат зависит от порядка перебора: конфликт от первой пары
    "застывает" в m(Θ) прежде, чем в комбинирование войдёт третий
    источник, и дальше участвует в нём уже как обычная
    неопределённость, а не как ещё не учтённый конфликт.

    Здесь вместо последовательного сворачивания общий конфликт между
    N источниками считается симметрично одним проходом и переносится
    в Θ один раз, в самом конце — результат не зависит от порядка
    источников. При N=2 совпадает с результатом combine_yager.

    Для комбинирования 3 и более источников правилом Ягера
    использовать нужно эту функцию, а не последовательные вызовы
    Mass.combine_yager.
    """

    if not masses:
        return vacuous_mass()

    prod_1_minus_not_h = 1.0
    prod_1_minus_h = 1.0
    prod_theta = 1.0

    for m in masses:
        prod_1_minus_not_h *= (1.0 - m.m_not_h)
        prod_1_minus_h *= (1.0 - m.m_h)
        prod_theta *= m.m_theta

    m_h = prod_1_minus_not_h - prod_theta
    m_not_h = prod_1_minus_h - prod_theta
    m_theta = 1.0 - m_h - m_not_h

    return Mass(m_h=float(m_h), m_not_h=float(m_not_h), m_theta=float(m_theta))
