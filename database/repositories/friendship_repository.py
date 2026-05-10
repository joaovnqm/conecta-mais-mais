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
        """
        """
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

    def list_pending_request(self, user_id: int) -> List[dict]:
        self.cursor.execute(
            """
            SELECT
                f.friendship_id,
                u.user_id,
                u.name,
                u.email
            FROM friendship f
            JOIN users u
            ON u.user_id = f.requester_id
            WHERE f.status = 'pending'
            AND f.requester_id != ?
            ORDER BY f.created_at DESC
            """,
            (user_id, user_id)
        )

        requests = self.cursor.fetchall()

        return [
            {
                "friendship_id": row[0],
                "user_id": row[1],
                "name": row[2],
                "email": row[3]
            }
            for row in requests
        ]

    def accept_friend_request(self, current_user_id: int, requester_id: int):
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id, requester_id)

        self.cursor.execute(
            """
            SELECT friendship_id, requester_id, status
            FROM friendships
            WHERE user_low_id = ?
            AND user_high_id = ?
            """,
            (user_low_id, user_high_id)
        )

        friendship = self.cursor.fetchone()

        if friendship is None:
            return False, "Solicitação não encontrada"

        friendship_id, original_requester_id, status = friendship

        if status != "pending":
            return False, "Essa solicitação não está pendente"

        if original_requester_id == current_user_id:
            return False, "Você não pode aceitar uma solicitação enviada por você mesmo"

        self.cursor.execute(
            """
            UPDATE friendships
            SET status = 'accepted',
            update_at = CURRENT_TIMESTAMP
            WHERE friendship_id = ?
            """,
            (friendship_id,)
        )

        self.connection.commit()

        return True, "Solicitação aceita. Vocês agora são amigos"

    def reject_friend_request(self, current_user_id: int, requester_id: int):
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id, requester_id)

        self.cursor.execute(
            """
            UPDATE friendship
            SET status = 'rejected'
            updated_at = CURRENT_TIMESTAMP
            WHERE user_low_id = ?
            AND user_high_id = ?
            AND requester_id = ?
            AND status = 'pending'
            """,
            (user_low_id, user_high_id, requester_id)
        )

        if self.cursor.rowcount == 0:
            return False, "Solicitação pendente não encontrada"

        self.connection.commit()

        return True, "Solicitação recusada"

    def list_friends(self, user_id: int) -> List[dict]:
        self.cursor.execute(
            """
            SELECT
                u.ser_id,
                u.name,
                u.email
            FROM friendship f
            JOIN users u
            ON u.user_id = CASE
                WHEN f.user_low_id = ? THEN f.user_high_id
                ELSE f.user_low_id
                END
            WHERE f.status = 'accepted'
            AND ? IN (f.user_low_id, f_user_high_id)
            ORDER BY u.name ASC
            """,
            (user_id, user_id)
        )

        friends = self.cursor.fetchall()

        return [
            {
                "user_id": row[0],
                "name": row[1],
                "email": row[2]
            }
            for row in friends
        ]

    def remove_friend(self, current_user_id: int, friend_id: int):
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id, friend_id)

        self.cursor.execute(
            """
            DELETE FROM friendships
            WHERE user_low_id = ?
            AND user_high_id = ?
            AND status = 'accepted'
            """,
            (user_low_id, user_high_id)
        )

        if self.cursor.rowcount == 0:
            return False, "Amizade não encontrada"

        self.connection.commit()

        return True, "Amizade removida com sucesso"


friendship_services = FriendshipServices()
