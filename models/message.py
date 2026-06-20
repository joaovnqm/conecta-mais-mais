from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    """
    Representa uma mensagem trocada entre dois usuários no sistema de chat.
    Atributos:
    - message_id: identificador único da mensagem (None antes de ser salva).
    - sender_id: ID do usuário que enviou a mensagem.
    - receiver_id: ID do usuário que recebeu a mensagem.
    - content: conteúdo textual da mensagem.
    - sent_at: data e hora de envio (preenchido automaticamente pelo banco).
    - is_read: indica se a mensagem foi lida (0 = não lida, 1 = lida).
    """

    message_id: Optional[int]
    sender_id: int
    receiver_id: int
    content: str
    sent_at: Optional[str] = None
    is_read: int = 0

@dataclass
class Conversation:
    """
    Representa o resumo de uma conversa entre o usuário logado e outro usuário.
    Utilizada na listagem de conversas ativas, exibindo o parceiro,
    a última mensagem e a contagem de mensagens não lidas.
    Atributos:
    - partner_id: ID do usuário parceiro na conversa.
    - partner_name: nome do parceiro.
    - last_message: conteúdo da última mensagem trocada.
    - last_message_at: data e hora da última mensagem.
    - unread_count: quantidade de mensagens não lidas enviadas pelo parceiro.
    """

    partner_id: int
    partner_name: str
    last_message: Optional[str]
    last_message_at: Optional[str]
    unread_count: int = 0