import sqlite3
from typing import List, Optional

from models.friendship import Friend, FriendRequest


class FriendshipServices:
    """
    Classe responsável pelas operações sociais de amizade:
    A amizade é armazenada usando user_low_id e user_high_id para impedir duplicidade
    entre os mesmos dois usuários.
    """

    def __init__(self, database_path: str = "conecta++.db") -> None:
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self) -> None:
        """
        Cria a tabela friendships caso ela ainda não exista.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS friendships (
                friendship_id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_low_id INTEGER NOT NULL,
                user_high_id INTEGER NOT NULL,
                requester_id INTEGER NOT NULL,

                status TEXT NOT NULL CHECK (
                    status IN ('pending', 'accepted', 'rejected', 'blocked')
                ),

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(user_low_id, user_high_id),

                FOREIGN KEY (user_low_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_high_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (requester_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                CHECK(user_low_id < user_high_id)
            )
            """
        )

        self.connection.commit()

    def make_user_pair(self, user_id_1: int, user_id_2: int) -> tuple[int, int]:
        """
        Organiza dois IDs de usuário em ordem crescente.
        Isso impede duplicidade de amizade entre os mesmos usuários.
        """
        if user_id_1 == user_id_2:
            raise ValueError("Usuário não pode adicionar a si mesmo.")

        return min(user_id_1, user_id_2), max(user_id_1, user_id_2)

    def find_user_by_email(self, email: str) -> Optional[dict]:
        """
        Busca um usuário pelo e-mail.
        """
        email = email.strip().lower()

        self.cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                username,
                linkedin_url,
                github_url
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
            "email": user[2],
            "username": user[3],
            "linkedin_url": user[4] or "",
            "github_url": user[5] or ""
        }

    def find_user_by_username(self, username: str) -> Optional[dict]:
        """
        Busca um usuário pelo username.
        """
        username = username.strip().lower().lstrip("@")

        self.cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                username,
                linkedin_url,
                github_url
            FROM users
            WHERE LOWER(username) = LOWER(?)
            """,
            (username,)
        )

        user = self.cursor.fetchone()

        if user is None:
            return None

        return {
            "user_id": user[0],
            "name": user[1],
            "email": user[2],
            "username": user[3],
            "linkedin_url": user[4] or "",
            "github_url": user[5] or ""
        }

    def _create_or_update_friend_request(
        self,
        requester_id: int,
        target_id: int
    ) -> tuple[bool, str]:
        """
        Cria ou atualiza uma solicitação de amizade entre dois usuários.
        """
        if requester_id == target_id:
            return False, "Você não pode enviar solicitação para si mesmo."

        user_low_id, user_high_id = self.make_user_pair(requester_id, target_id)

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
                return False, "Já existe uma solicitação pendente entre vocês."

            if status == "accepted":
                return False, "Vocês já são amigos."

            if status == "blocked":
                return False, "Não é possível enviar solicitação para este usuário."

            if status == "rejected":
                self.cursor.execute(
                    """
                    UPDATE friendships
                    SET status = 'pending',
                        requester_id = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE friendship_id = ?
                    """,
                    (requester_id, friendship_id)
                )

                self.connection.commit()
                return True, "Solicitação reenviada com sucesso."

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

        return True, "Solicitação de amizade enviada com sucesso."

    def send_friend_request(self, requester_id: int, target_email: str) -> tuple[bool, str]:
        """
        Envia solicitação de amizade usando e-mail.
        Mantido por compatibilidade com versões anteriores.
        """
        target_user = self.find_user_by_email(target_email)

        if target_user is None:
            return False, "Usuário não encontrado."

        return self._create_or_update_friend_request(
            requester_id,
            target_user["user_id"]
        )

    def send_friend_request_by_username(
        self,
        requester_id: int,
        target_username: str
    ) -> tuple[bool, str]:
        """
        Envia solicitação de amizade usando username.
        """
        target_user = self.find_user_by_username(target_username)

        if target_user is None:
            return False, "Usuário não encontrado."

        return self._create_or_update_friend_request(
            requester_id,
            target_user["user_id"]
        )

    def list_pending_requests(self, user_id: int) -> List[FriendRequest]:
        """
        Lista as solicitações de amizade pendentes recebidas por um usuário.
        """
        self.cursor.execute(
            """
            SELECT
                f.friendship_id,
                u.user_id,
                u.name,
                u.email
            FROM friendships f
            JOIN users u
            ON u.user_id = f.requester_id
            WHERE f.status = 'pending'
            AND f.requester_id != ?
            AND ? IN (f.user_low_id, f.user_high_id)
            ORDER BY f.created_at DESC
            """,
            (user_id, user_id)
        )

        requests = self.cursor.fetchall()

        return [
            FriendRequest(
                friendship_id=row[0],
                requester_id=row[1],
                requester_name=row[2],
                requester_email=row[3]
            )
            for row in requests
        ]

    def list_pending_request(self, user_id: int) -> List[FriendRequest]:
        """
        Alias para compatibilidade com chamadas antigas.
        """
        return self.list_pending_requests(user_id)

    def accept_friend_request(
        self,
        current_user_id: int,
        requester_id: int
    ) -> tuple[bool, str]:
        """
        Aceita uma solicitação de amizade pendente.
        """
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id,
            requester_id
        )

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
            return False, "Solicitação não encontrada."

        friendship_id, original_requester_id, status = friendship

        if status != "pending":
            return False, "Essa solicitação não está pendente."

        if original_requester_id == current_user_id:
            return False, "Você não pode aceitar uma solicitação enviada por você mesmo."

        self.cursor.execute(
            """
            UPDATE friendships
            SET status = 'accepted',
                updated_at = CURRENT_TIMESTAMP
            WHERE friendship_id = ?
            """,
            (friendship_id,)
        )

        self.connection.commit()

        return True, "Solicitação aceita. Vocês agora são amigos."

    def reject_friend_request(
        self,
        current_user_id: int,
        requester_id: int
    ) -> tuple[bool, str]:
        """
        Recusa uma solicitação de amizade pendente.
        """
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id,
            requester_id
        )

        self.cursor.execute(
            """
            UPDATE friendships
            SET status = 'rejected',
                updated_at = CURRENT_TIMESTAMP
            WHERE user_low_id = ?
            AND user_high_id = ?
            AND requester_id = ?
            AND status = 'pending'
            """,
            (user_low_id, user_high_id, requester_id)
        )

        if self.cursor.rowcount == 0:
            return False, "Solicitação pendente não encontrada."

        self.connection.commit()

        return True, "Solicitação recusada."

    def list_friends(self, user_id: int) -> List[Friend]:
        """
        Lista todos os amigos aceitos de um usuário.
        Retorna nome, e-mail, username e LinkedIn.
        """
        self.cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.username,
                u.linkedin_url,
                u.github_url
            FROM friendships f
            JOIN users u
            ON u.user_id = CASE
                WHEN f.user_low_id = ? THEN f.user_high_id
                ELSE f.user_low_id
                END
            WHERE f.status = 'accepted'
            AND ? IN (f.user_low_id, f.user_high_id)
            ORDER BY u.name ASC
            """,
            (user_id, user_id)
        )

        friends = self.cursor.fetchall()

        return [
            Friend(
                user_id=row[0],
                name=row[1],
                email=row[2],
                username=row[3] or "",
                linkedin_url=row[4] or "",
                github_url=row[5] or ""
            )
            for row in friends
        ]

    def remove_friend(
        self,
        current_user_id: int,
        friend_id: int
    ) -> tuple[bool, str]:
        """
        Remove uma amizade aceita entre dois usuários.
        """
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id,
            friend_id
        )

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
            return False, "Amizade não encontrada."

        self.connection.commit()

        return True, "Amizade removida com sucesso."

    def block_user(
        self,
        current_user_id: int,
        target_id: int
    ) -> tuple[bool, str]:
        """
        Bloqueia um usuário.
        """
        if current_user_id == target_id:
            return False, "Você não pode bloquear a si mesmo."

        user_low_id, user_high_id = self.make_user_pair(
            current_user_id,
            target_id
        )

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

            if status == "blocked":
                return False, "Este usuário já está bloqueado."

            self.cursor.execute(
                """
                UPDATE friendships
                SET status = 'blocked',
                    requester_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE friendship_id = ?
                """,
                (current_user_id, friendship_id)
            )

            self.connection.commit()

            return True, "Usuário bloqueado com sucesso."

        self.cursor.execute(
            """
            INSERT INTO friendships (
                user_low_id,
                user_high_id,
                requester_id,
                status
            )
            VALUES (?, ?, ?, 'blocked')
            """,
            (user_low_id, user_high_id, current_user_id)
        )

        self.connection.commit()

        return True, "Usuário bloqueado com sucesso."

    def unblock_user(
        self,
        current_user_id: int,
        target_id: int
    ) -> tuple[bool, str]:
        """
        Desbloqueia um usuário bloqueado pelo usuário logado.

        Apenas quem bloqueou pode desbloquear.
        Ao desbloquear, a relação blocked é removida.
        """
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id,
            target_id
        )

        self.cursor.execute(
            """
            DELETE FROM friendships
            WHERE user_low_id = ?
            AND user_high_id = ?
            AND requester_id = ?
            AND status = 'blocked'
            """,
            (user_low_id, user_high_id, current_user_id)
        )

        if self.cursor.rowcount == 0:
            return False, "Bloqueio não encontrado para este usuário."

        self.connection.commit()

        return True, "Usuário desbloqueado com sucesso."

    def list_blocked_users(self, user_id: int) -> List[Friend]:
        """
        Lista usuários bloqueados pelo usuário logado.
        Retorna nome, e-mail, username e LinkedIn.
        """
        self.cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.username,
                u.linkedin_url,
                u.github_url
            FROM friendships f
            JOIN users u
            ON u.user_id = CASE
                WHEN f.user_low_id = ? THEN f.user_high_id
                ELSE f.user_low_id
                END
            WHERE f.status = 'blocked'
            AND f.requester_id = ?
            AND ? IN (f.user_low_id, f.user_high_id)
            ORDER BY u.name ASC
            """,
            (user_id, user_id, user_id)
        )

        blocked_users = self.cursor.fetchall()

        return [
            Friend(
                user_id=row[0],
                name=row[1],
                email=row[2],
                username=row[3] or "",
                linkedin_url=row[4] or "",
                github_url=row[5] or ""
            )
            for row in blocked_users
        ]


friendship_services = FriendshipServices()