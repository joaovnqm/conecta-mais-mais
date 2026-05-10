import sqlite3
from typing import List, Optional


class FriendshipServices:
    """
    Classe responsável pelas operações sociais de amizade:
    - criar tabela de amizades;
    - enviar solicitação
    - aceitar solicitação
    - recusar solicitação
    - listar amigos
    - listar solicitações pendentes.
    """

    def __init__(self, database_path: str = "connecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS friendships (
                friendship_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                
                user_low_id INTEGER NOT NULL,
                user_high_id INTEGER NOT NULL,  
                
                    
                
                status TEXT NOT NULL CHECK (
                    status IN ('pending', 'accepted', 'rejected', 'blocked')
                ),
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                update_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(user_low_id, user_high_id),
                
                FOREIGN KEY (user_low_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                
                FOREIGN KEY (user_high_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                    
                FOREIGN KEY (requester_id)
                    REFERENCES users(user_id)
                    ON DELETE  CASCADE,
                
                CHECK(user_low_id < user_high_id)
            )
            """)
        self.connection.commit()

    def make_user_pair(self, user_id_1: int, user_id_2: int) -> tuple[int, int]:
        if user_id_1 == user_id_2:
            raise ValueError("Usuário não pode adicionar a si mesmo")

        return min(user_id_1, user_id_2), max(user_id_1, user_id_2)

    def find_user_by_email(self, email: str) -> Optional[dict]:
        email = email.strip().lower()

        self.cursor.execute(
            """
            SELECT user_id, name, email
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        user = self.cursor.fetchone()

        if user is None:
            return None

        return {
            "user_id": user[0],
            "name": user[1],
            "email": user[2]
        }

    def send_friend_request(self, requester_id: int, target_email: str):
        target_user = self.find_user_by_email(target_email)

        if target_user is None:
            return False, "Usuário não encontrado"

        target_id = target_user["user_id"]

        if requester_id == target_id:
            return False, "Você não pode enviar solicitação para si mesmo"

        user_low_id, user_high_id = self.make_user_pair(
            requester_id, target_id)

        self.cursor.execute(
            """
            SELECT friendship_id, status
            FROM friendships
            WHERE user_low_id = ?
                AND user_high_id = ?
            """,
            (user_low_id, user_high_id)
        )

        friendship = self.cursor.fetchone()

        if friendship is not None:
            friendship_id, status = friendship

            if status == "pending":
                return False, "Já existe uma solicitação pendente entre vocês"

            if status == "accepted":
                return False, "Vocês já são amigos"

            if status == "blocked":
                return False, "Não é possível enviar solicitação para este usuário"

            if status == "rejected":
                self.cursor.execute(
                    """
                    UPDATE friendship
                    SET status = 'pending'
                        requester_id = ?
                        update_at = CURRENT_TIMESTAMP
                    WHERE friendship_id = ?
                    """,
                    (requester_id, friendship_id)
                )

                self.connection.commit()
                return True, "Solicitação reenviada com sucesso"

            self.cursor.execute(
                """
                INSERT INTO friendships (
                    user_low_id,
                    user_high_id,
                    requester_id,
                    status
                )
                VALUES (?, ?, ?, 'pending')
                """,
                (user_low_id, user_high_id, requester_id)
            )
            self.connection.commit()

            return True, "Solicitação de amizade enviada com sucesso"
