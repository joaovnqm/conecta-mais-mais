from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    """Representa um evento no sistema. O decorador dataclass já constroi o __init__ de forma automática dentro do programa.

    Atributos:
    - event_id: Identificador único (None para eventos ainda não persistidos).
    - name: Nome do evento (string).
    - description: Descrição do evento (string).
    - event_location: Local do evento (string).
    - date: Data do evento (string).
    - hour: Hora do evento (string).
    - creator_id: Identificador do criador do evento (int).
    """
    event_id: Optional[int]
    name: str
    description: str
    event_location: Optional[str] = None
    date: Optional[str] = None
    hour: Optional[str] = None
    creator_id: int = None