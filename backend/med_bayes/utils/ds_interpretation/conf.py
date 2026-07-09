LAMBDA = 0.85 


def k_by_length(length: int) -> float:
    """Коэффициент уверенности k = λ^(length-1)."""
    return LAMBDA ** max(length - 1, 0)
