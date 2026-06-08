from dataclasses import dataclass
from typing import Optional
@dataclass(frozen=True)
class RankingLevel:
    name: str
    min_xp: int
    max_xp: Optional[int]


@dataclass(frozen=True)
class XpAction:
    key: str
    label: str
    points: int
    description: str

RANKING_LEVELS: list[RankingLevel] = [
    RankingLevel("Recém-chegado", 0, 99),
    RankingLevel("Participante", 100, 249),
    RankingLevel("Explorador", 250, 499),
    RankingLevel("Engajado", 500, 899),
    RankingLevel("Experiente", 900, 1399),
    RankingLevel("Influente", 1400, 2099),
    RankingLevel("Elite", 2100, 2999),
    RankingLevel("Mestre", 3000, 6499),
    RankingLevel("Lendário", 6500, None),
]


XP_ACTIONS: dict[str, XpAction] = {
    "event_registration": XpAction(
        key="event_registration",
        label="Inscrição em evento",
        points=5,
        description="Usuário se inscreveu em um evento",
    ),
    "event_attendance": XpAction(
        key="event_attendance",
        label="Comparecimento ao evento",
        points=15,
        description="Usuário compareceu ao evento",
    ),
    "attendance_certificate": XpAction(
        key="attendance_certificate",
        label="Certificado de presença",
        points=25,
        description="Usuário recebeu certificado de participação",
    ),
    "presentation": XpAction(
        key="presentation",
        label="Apresentação realizada",
        points=70,
        description="Usuário fez uma apresentação no evento",
    ),
    "presentation_certificate": XpAction(
        key="presentation_certificate",
        label="Certificado de apresentação",
        points=35,
        description="Usuário recebeu certificado como apresentador",
    ),
}

def get_level_by_xp(total_xp: int) -> RankingLevel:
    for level in RANKING_LEVELS:
        if level.max_xp is None:
            if total_xp >= level.min_xp:
                return level

        elif level.min_xp <= total_xp <= level.max_xp:
            return level

    return RANKING_LEVELS[0]


def get_next_level(total_xp: int) -> Optional[RankingLevel]:
    current_level = get_level_by_xp(total_xp)

    for level in RANKING_LEVELS:
        if level.min_xp > current_level.min_xp:
            return level

    return None


def get_missing_xp_for_next_level(total_xp: int) -> int:
    next_level = get_next_level(total_xp)

    if next_level is None:
        return 0

    return max(next_level.min_xp - total_xp, 0)
