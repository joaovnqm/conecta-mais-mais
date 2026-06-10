from dataclasses import dataclass
from typing import Optional

@dataclass
class Friend:
    """
    Representa um amigo dentro do sistema.
    - user_id: ID do usuário amigo
    - name: Nome do amigo
    - email: E-mail do amigo
    """
    user_id: int
    name: str
    email: str
    username: str
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None

@dataclass
class FriendRequest:
    """
    Representa uma solicitação de amizade recebida.
    - friendship_id: ID da relação de amizade na tabela friendships
    - requester_id: ID do usuário que enviou a solicitação
    - requester_name: Nome do usuário que enviou a solicitação
    - requester_email: E-mail do usuário que enviou a solicitação
    """
    
    friendship_id: int
    requester_id: int
    requester_name: str
    requester_email: str

@dataclass
class Friendship:
    """
    Representa uma relação de amizade entre dois usuários
    - friendship_id: ID da amizade no banco de dados
    - user_low_id: Menor ID entre dois usuários
    - user_high_id: Maior ID entre dois usuários
    - requester_id: ID de quem enviou a solicitação
    - status: Estado atual da relação
    """

    friendship_id: Optional[int]
    user_low_id: int
    user_high_id: int
    requester_id: int
    status: str
    