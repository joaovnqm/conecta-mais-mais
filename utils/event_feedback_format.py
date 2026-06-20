def format_stars(rating: int) -> str:
    """
    Formata a nota em estrelas com espaçamento entre elas.

    Exemplos:
    5 -> ★ ★ ★ ★ ★
    3 -> ★ ★ ★ ☆ ☆
    """
    rating = int(rating)
    filled_stars = ["★"] * rating
    empty_stars = ["☆"] * (5 - rating)
    return " ".join(filled_stars + empty_stars)


def _format_average_rating(average_rating) -> str:
    """
    Formata a média sem mostrar .0 quando for número inteiro.
    """
    if average_rating is None:
        return "0"

    average_rating = float(average_rating)
    return f"{average_rating:.1f}".rstrip("0").rstrip(".")


def format_feedback_summary(summary: dict) -> str:
    """
    Formata o resumo dos feedbacks em duas linhas.
    """
    total_feedbacks = int(summary.get("total_feedbacks") or 0)
    average_rating = summary.get("average_rating")

    if total_feedbacks == 0:
        return (
            "Avaliação média: ainda sem feedbacks\n"
            "Total de avaliações: 0"
        )

    formatted_average = _format_average_rating(average_rating)

    return (
        f"Avaliação média: {formatted_average} ★\n"
        f"Total de avaliações: {total_feedbacks}"
    )
