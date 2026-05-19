from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """Representa um usuário no sistema. O decorador dataclass já constroi o __init__ de forma automática dentro do programa.

    Atributos:
    - user_id: Identificador único (None para usuários ainda não persistidos).
    - name: Nome do usuário (string).
    - email: E-mail do usuário (string).
    """

    user_id: Optional[int]
    name: str
    email: str