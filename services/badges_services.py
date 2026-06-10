from dataclasses import dataclass
from typing import Callable, List
from database.repositories.ranking_repository import RankingRepository
from models.badges import Badge, UserStats as _UserStats

def _get_user_stats(user_id: int) -> _UserStats:
    """Obtém as estatísticas relevantes para calcular as badges de um usuário."""
    repository = RankingRepository()
    row = repository.cursor.execute(
        """
        SELECT events_attended, presentations_done, total_points
        FROM user_event_ranking
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    stats = _UserStats()

    if row:
        stats.events_attended = int(row[0] or 0)
        stats.presentations_done = int(row[1] or 0)
        stats.total_points = int(row[2] or 0)

    workshop_count = repository.cursor.execute(
        """
        SELECT COUNT(*)
        FROM event_ranking_actions
        WHERE user_id = ?
        AND action_type = 'workshop'
        """,
        (user_id,),
    ).fetchone()

    if workshop_count:
        stats.workshops_done = int(workshop_count[0] or 0)

    return stats


# Lista de badges e suas condições (contem função lambda para verificar se a badge está desbloqueada com base nas estatísticas do usuário).
BADGES: List[dict[str, object]] = [
    {
        "id": "first_event",
        "name": "Primeiro Evento",
        "icon": "🎉",
        "description": "Confirmou presença no primeiro evento",
        "condition": lambda s: s.events_attended >= 1,
    },
    {
        "id": "participant_active",
        "name": "Participante Ativo",
        "icon": "🚀",
        "description": "Participou de 5 eventos",
        "condition": lambda s: s.events_attended >= 5,
    },
    {
        "id": "explorer",
        "name": "Explorador",
        "icon": "🧭",
        "description": "Participou de 10 eventos",
        "condition": lambda s: s.events_attended >= 10,
    },
    {
        "id": "veteran",
        "name": "Veterano de Eventos",
        "icon": "🏆",
        "description": "Participou de 25 eventos",
        "condition": lambda s: s.events_attended >= 25,
    },
    {
        "id": "legend",
        "name": "Lenda Acadêmica",
        "icon": "👑",
        "description": "Participou de 50 eventos",
        "condition": lambda s: s.events_attended >= 50,
    },
    {
        "id": "speaker",
        "name": "Palestrante",
        "icon": "🎤",
        "description": "Fez 1 apresentação",
        "condition": lambda s: s.presentations_done >= 1,
    },
    {
        "id": "speaker_senior",
        "name": "Palestrante Sênior",
        "icon": "🎙️",
        "description": "Fez 5 apresentações",
        "condition": lambda s: s.presentations_done >= 5,
    },
    {
        "id": "workshop_instructor",
        "name": "Instrutor de Workshop",
        "icon": "🛠️",
        "description": "Ministrou 1 workshop",
        "condition": lambda s: s.workshops_done >= 1,
    },
    {
        "id": "workshop_master",
        "name": "Mestre dos Workshops",
        "icon": "⚙️",
        "description": "Ministrou 5 workshops",
        "condition": lambda s: s.workshops_done >= 5,
    },
    {
        "id": "engaged",
        "name": "Engajado na Comunidade",
        "icon": "❤️",
        "description": "Favoritou 20 eventos (placeholder)",
        "condition": lambda s: s.events_attended >= 20,
    },
    {
        "id": "influencer",
        "name": "Influenciador Acadêmico",
        "icon": "⭐",
        "description": "Acumulou 10000 pontos no ranking",
        "condition": lambda s: s.total_points >= 10000,
    },
]


def get_user_badges(user_id: int) -> List[Badge]:
    """Retorna a lista de badges conquistados pelo usuário."""
    stats = _get_user_stats(user_id)
    unlocked: List[Badge] = []

    for badge in BADGES:
        condition: Callable[[ _UserStats ], bool] = badge["condition"]
        try:
            if condition(stats):
                unlocked.append(Badge(id=badge["id"], name=badge["name"], icon=badge["icon"], description=badge.get("description", "")))

        except Exception:

            continue

    return unlocked