from dataclasses import dataclass
from typing import Optional

@dataclass
class Interest:
    """Representa um usuário no sistema. O decorador dataclass já constroi o __init__ de forma automática dentro do programa.
    
    Atributos:
    - interest_id: Identificador único (None para interesses ainda não persistidos).
    - name: Nome do interesse (string).
    """

    interest_id: Optional[int]
    name: str