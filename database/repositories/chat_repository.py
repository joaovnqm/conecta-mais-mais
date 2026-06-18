import sqlite3
from typing import List, Optional
from models.message import Conversation, Message

class MessageServices:
    """
    Classe responsável pelas operações de chat no banco de dados.
    Gerencia o envio, leitura e listagem de mensagens entre usuários,
    bem como o histórico de conversas do usuário logado.
    As mensagens são armazenadas na tabela `messages`, com referências
    às tabelas `users` via chaves estrangeiras.
    """
    def __init__(self, database_path: str = "conecta++.db") -> None:
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self) -> None:
        """
        Cria a tabela messages caso ela ainda não exista.
        Cada linha representa uma mensagem única entre dois usuários,
        com referência a quem enviou (sender_id) e quem recebeu (receiver_id).
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id   INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                content     TEXT    NOT NULL,
                sent_at     TEXT    DEFAULT CURRENT_TIMESTAMP,
                is_read     INTEGER DEFAULT 0,

                FOREIGN KEY (sender_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
            """
        )

        self.connection.commit()

    def send_message(self, sender_id: int, receiver_id: int, content: str) -> Optional[Message]:
        """
        Persiste uma nova mensagem no banco de dados.
        Retorna o objeto Message criado, ou None se o conteúdo for vazio.
        """
        content = content.strip()
        if not content:
            return None

        self.cursor.execute(
            """
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (?, ?, ?)
            """,
            (sender_id, receiver_id, content),
        )

        self.connection.commit()
        message_id = self.cursor.lastrowid
        self.cursor.execute(
            """
            SELECT sent_at FROM messages WHERE message_id = ?
            """,
            (message_id,),
        )

        row = self.cursor.fetchone()
        sent_at = row[0] if row else None
        return Message(
            message_id = message_id,
            sender_id = sender_id,
            receiver_id = receiver_id,
            content = content,
            sent_at = sent_at,
            is_read = 0,
        )

    def get_conversation(self, user_id_1: int, user_id_2: int) -> List[Message]:
        """
        Retorna todas as mensagens trocadas entre dois usuários, em ordem cronológica.
        """
        self.cursor.execute(
            """
            SELECT
                message_id,
                sender_id,
                receiver_id,
                content,
                sent_at,
                is_read
            FROM messages
            WHERE
                (sender_id = ? AND receiver_id = ?)
                OR
                (sender_id = ? AND receiver_id = ?)
            ORDER BY sent_at ASC, message_id ASC
            """,
            (user_id_1, user_id_2, user_id_2, user_id_1),
        )
        
        rows = self.cursor.fetchall()
        return [
            Message(
                message_id = row[0],
                sender_id = row[1],
                receiver_id = row[2],
                content = row[3],
                sent_at = row[4],
                is_read = row[5],
            )
            for row in rows
        ]

    def get_user_conversations(self, user_id: int) -> List[Conversation]:
        """
        Retorna o resumo de todas as conversas ativas do usuário logado.
        Para cada parceiro com quem o usuário trocou mensagens, retorna:
        - nome do parceiro;
        - última mensagem;
        - data/hora da última mensagem;
        - contagem de mensagens não lidas recebidas.
        Os resultados são ordenados da conversa mais recente para a mais antiga.
        """
        self.cursor.execute(
            """
            SELECT DISTINCT
                CASE
                    WHEN sender_id = ? THEN receiver_id
                    ELSE sender_id
                END AS partner_id
            FROM messages
            WHERE sender_id = ? OR receiver_id = ?
            """,
            (user_id, user_id, user_id),
        )
        partner_ids = [row[0] for row in self.cursor.fetchall()]
        conversations = []
        for partner_id in partner_ids:
            self.cursor.execute(
                """
                SELECT u.name
                FROM users u
                WHERE u.user_id = ?
                """,
                (partner_id,),
            )

            user_row = self.cursor.fetchone()
            if user_row is None:
                continue

            partner_name = user_row[0]
            self.cursor.execute(
                """
                SELECT content, sent_at
                FROM messages
                WHERE
                    (sender_id = ? AND receiver_id = ?)
                    OR
                    (sender_id = ? AND receiver_id = ?)
                ORDER BY sent_at DESC, message_id DESC
                LIMIT 1
                """,
                (user_id, partner_id, partner_id, user_id),
            )

            last_row = self.cursor.fetchone()
            last_message = last_row[0] if last_row else None
            last_message_at = last_row[1] if last_row else None
            self.cursor.execute(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
                """,
                (user_id, partner_id),
            )

            unread_count = self.cursor.fetchone()[0] or 0
            conversations.append(
                Conversation(
                    partner_id=partner_id,
                    partner_name=partner_name,
                    last_message=last_message,
                    last_message_at=last_message_at,
                    unread_count=unread_count,
                )
            )

        conversations.sort(
            key=lambda c: c.last_message_at or "",
            reverse=True,
        )

        return conversations

    def mark_conversation_as_read(self, receiver_id: int, sender_id: int) -> None:
        """
        Marca como lidas todas as mensagens recebidas de um parceiro específico.
        Deve ser chamado ao abrir uma conversa.
        """
        self.cursor.execute(
            """
            UPDATE messages
            SET is_read = 1
            WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
            """,
            (receiver_id, sender_id),
        )

        self.connection.commit()

    def delete_message(self, message_id: int, requester_id: int) -> tuple[bool, str]:
        """
        Remove uma mensagem pelo ID, somente se o solicitante for o remetente.
        """
        self.cursor.execute(
            """
            SELECT sender_id FROM messages WHERE message_id = ?
            """,
            (message_id,),
        )

        row = self.cursor.fetchone()
        if row is None:
            return False, "Mensagem não encontrada."

        if row[0] != requester_id:
            return False, "Você só pode remover mensagens enviadas por você."

        self.cursor.execute(
            "DELETE FROM messages WHERE message_id = ?",
            (message_id,),
        )

        self.connection.commit()
        return True, "Mensagem removida com sucesso."

message_services = MessageServices()