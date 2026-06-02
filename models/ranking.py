from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RankingLevel:
    name: str
    min_xp: int
    max_xp: Optional[int]
    icon: str


@dataclass(frozen=True)
class XpAction:
    key: str
    label: str
    points: str
    description: str


@dataclass(frozen=True)
class Achievement:
    key: str
    name: str
    description: str
    metric: str
    required_value: int
    icon: str


RANKING_LEVELS: list[RankingLevel] = [
    RankingLevel("Recém-chegado", 0, 99),
    RankingLevel("Participante", 100, 249),
    RankingLevel("Explorador", 250, 499),
    RankingLevel("Engajado", 500, 899),
    RankingLevel("Experiente", 900, 1399),
    RankingLevel("Influente", 1400, 2099),
    RankingLevel("Elite", 2100, 2999),
    RankingLevel("Mestre", 3000, 6499),
    RankingLevel("Mestre", 6500, None),
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
    "event_review": XpAction(
        key="event_review",
        label="Avaliação do evento",
        points=5,
        description="Usuário avaliou ou comentou sobre o evento"
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
    "event_organization": XpAction(
        key="event_organization",
        label="Organização de evento",
        points=60,
        description="Usuário organizou ou ajudou a organizar um evento",
    ),
    "support_team": XpAction(
        key="support_team",
        label="Equipe de apoio",
        points=35,
        description="Usuário participou da equipe de apoio do evento",
    ),
    "highlighted_participation": XpAction(
        key="highlighted_participation",
        label="Participação em destaque",
        points=40,
        description="Usuário teve participação em destaque no evento",
    ),
}

ACHIVEMENTS: list[Achievement] = [
    Achievement(
        key="first_event",
        name="Primeiro evento",
        description="Participou do primeiro evento",
        metric="events_attended",
        required_value=1,
    ),
    Achievement(
        key="confirmed_presence",
        name="Presença confirmada",
        description="Compareceu a 5 eventos",
        metric="events_attended",
        required_value=5,
    ),
    Achievement(
        key="certificate_collector",
        name="Colecionador de Certificados",
        description="Recebeu 10 certificados",
        metric="certificates_received",
        required_value=10,
    ),
    Achievement(
        key="recurring_speaker",
        name="Apresentador Recorrente",
        description="Fez 5 apresentações",
        metric="presentations_done",
        required_value=5,
    ),
    Achievement(
        key="activate_organizer",
        name="Organizador ativo",
        description="Organizou ou ajudou em 3 eventos",
        metric="events_organized",
        required_value=3,
    ),
    Achievement(
        key="community_highlight",
        name="Destaque da comunidade",
        description="Recebeu destaque em evento",
        metric="highlighted_participations",
        required_value=1,
    ),
    Achievement(
        key="xp_1000",
        name="Mil pontos de experiência",
        description="Alcançou 1000 de XP de evento",
        metric="total_xp",
        required_value=1000,
    ),
]


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
