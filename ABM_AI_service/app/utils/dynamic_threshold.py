import statistics

def compute_dynamic_threshold(scores: list[float]) -> float:
    """
    Analiza matemáticamente el listado de distancias/puntuaciones devuelto por Qdrant.
    Garantiza que el umbral nunca supere la puntuación máxima obtenida.
    """
    if not scores:
        return 0.0
    if len(scores) == 1:
        return scores[0] * 0.95

    mean = statistics.mean(scores)
    std = statistics.stdev(scores)
    max_score = max(scores)

    alpha = 1.2   
    beta = 0.88   

    threshold_stat = mean + alpha * std
    threshold_relative = beta * max_score

    final_threshold = max(threshold_stat, threshold_relative)

    return min(final_threshold, max_score)