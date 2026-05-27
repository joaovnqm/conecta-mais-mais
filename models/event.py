from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """
    Representa um evento no sistema.

    Atributos:
    - event_id: identificador único do evento.
    - name: nome do evento.
    - description: descrição do evento.
    - event_location: local do evento.
    - date: data principal do evento.
    - hour: hora principal do evento.
    - creator_id: usuário criador do evento.
    - official_url: link oficial usado para buscar datas importantes.
    - auto_update_dates: indica se as datas importantes devem ser atualizadas automaticamente.
    """

    event_id: Optional[int]
    name: str
    description: str
    event_location: Optional[str] = None
    date: Optional[str] = None
    hour: Optional[str] = None
    creator_id: Optional[int] = None
    official_url: Optional[str] = None
    auto_update_dates: int = 1
