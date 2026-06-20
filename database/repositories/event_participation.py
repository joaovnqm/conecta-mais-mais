import sqlite3
from database.repositories.ranking_repository import ranking_repository_services


class EventParticipationService:
    """
    Serviço responsável pela presença social em eventos.
    """

    def __init__(self, database_path: str = "conecta++.db"):
        """Inicializa o serviço, garantindo que as tabelas necessárias existam."""
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """Cria as tabelas `event_participants` e `favorite_events` se não existirem."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS event_participants (
                user_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                extra_activity TEXT,
                status TEXT NOT NULL CHECK(status IN ('confirmed')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(user_id, event_id),
                FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                FOREIGN KEY(event_id)
                    REFERENCES events(event_id)
                    ON DELETE CASCADE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS favorite_events (
                user_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                PRIMARY KEY(user_id, event_id),
                FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                FOREIGN KEY(event_id)
                    REFERENCES events(event_id)
                    ON DELETE CASCADE
            )
            """
        )

        self.connection.commit()

    def confirm_presence(self, user_id: int, event_id: int, extra_activity: str = None) -> tuple[bool, str]:
        """
        Confirma presença do usuário em um evento.
        """
        if self.check_presence(user_id, event_id):
            return False, "Você já confirmou presença neste evento"

        self.cursor.execute(
            """
            INSERT INTO event_participants (
                user_id,
                event_id,
                extra_activity,
                status
            )
            VALUES (?, ?, ?, 'confirmed')
            """,
            (user_id, event_id, extra_activity)
        )

        self.connection.commit()

        return True, "Presença confirmada com sucesso."

    def cancel_presence(self, user_id: int, event_id: int) -> tuple[bool, str]:
        """
        Desmarca presença do usuário no evento.
        """
        self.cursor.execute(
            """
            DELETE FROM event_participants
            WHERE user_id = ?
            AND event_id = ?
            AND status = 'confirmed'
            """,
            (user_id, event_id)
        )

        if self.cursor.rowcount == 0:
            return False, "Você ainda não confirmou presença neste evento."

        self.connection.commit()
        removed = ranking_repository_services.remove_event_points(
            user_id, event_id)
        if removed:
            return True, "Presença desmarcada com sucesso. Pontuação do evento removida do ranking."

        else:
            return True, "Presença desmarcada com sucesso. Nenhuma pontuação encontrada para remoção."

    def check_presence(self, user_id: int, event_id: int) -> bool:
        """
        Verifica se o usuário confirmou presença no evento.
        """
        self.cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM event_participants
                WHERE user_id = ?
                AND event_id = ?
                AND status = 'confirmed'
            )
            """,
            (user_id, event_id)
        )

        return bool(self.cursor.fetchone()[0])

    def check_activities(self, user_id: int, event_id: int) -> list[str]:
        """
        Retorna as atividades registradas na participação do usuário.
        """

        self.cursor.execute(
            """
            SELECT extra_activity
            FROM event_participants
            WHERE user_id = ?
            AND event_id = ?
            AND status = 'confirmed'
            """,
            (user_id, event_id),
        )

        result = self.cursor.fetchone()

        if not result:
            return []

        activities_text = result[0]

        if not activities_text:
            return []

        return [
            activity.strip()
            for activity in activities_text.split(";")
            if activity.strip()
        ]

    def count_confirmed_presence(self, event_id: int) -> int:
        """
        Conta quantas pessoas confirmaram presença no evento.
        """
        self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM event_participants
            WHERE event_id = ?
            AND status = 'confirmed'
            """,
            (event_id,)
        )

        return self.cursor.fetchone()[0]

    def count_favorites(self, event_id: int) -> int:
        """
        Conta quantas pessoas favoritaram o evento.
        """
        self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM favorite_events
            WHERE event_id = ?
            """,
            (event_id,)
        )

        return self.cursor.fetchone()[0]

    def list_confirmed_users(self, event_id: int) -> list[dict]:
        """
        Lista todos os usuários que confirmaram presença.
        """
        self.cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.username,
                u.linkedin_url
            FROM event_participants ep
            JOIN users u
            ON u.user_id = ep.user_id
            WHERE ep.event_id = ?
            AND ep.status = 'confirmed'
            ORDER BY u.name ASC
            """,
            (event_id,)
        )

        users = self.cursor.fetchall()

        return [
            {
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "username": row[3],
                "linkedin_url": row[4],
            }
            for row in users
        ]

    def list_friends_confirmed_presence(
        self,
        user_id: int,
        event_id: int
    ) -> list[dict]:
        """
        Lista apenas amigos aceitos que confirmaram presença no evento.
        """
        self.cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.username,
                u.linkedin_url
            FROM event_participants ep
            JOIN users u
            ON u.user_id = ep.user_id
            JOIN friendships f
            ON (
                (f.user_low_id = ? AND f.user_high_id = u.user_id)
                OR
                (f.user_high_id = ? AND f.user_low_id = u.user_id)
            )
            WHERE ep.event_id = ?
            AND ep.status = 'confirmed'
            AND f.status = 'accepted'
            AND u.user_id != ?
            ORDER BY u.name ASC
            """,
            (user_id, user_id, event_id, user_id)
        )

        users = self.cursor.fetchall()

        return [
            {
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "username": row[3],
                "linkedin_url": row[4]
            }
            for row in users
        ]

    def list_friends_favorited_event(
        self,
        user_id: int,
        event_id: int
    ) -> list[dict]:
        """
        Lista amigos aceitos que favoritaram o evento.
        """
        self.cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.username,
                u.linkedin_url
            FROM favorite_events fe
            JOIN users u
            ON u.user_id = fe.user_id
            JOIN friendships f
            ON (
                (f.user_low_id = ? AND f.user_high_id = u.user_id)
                OR
                (f.user_high_id = ? AND f.user_low_id = u.user_id)
            )
            WHERE fe.event_id = ?
            AND f.status = 'accepted'
            AND u.user_id != ?
            ORDER BY u.name ASC
            """,
            (user_id, user_id, event_id, user_id)
        )

        users = self.cursor.fetchall()

        return [
            {
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "username": row[3],
                "linkedin_url": row[4]
            }
            for row in users
        ]

    def count_friends_confirmed_presence(self, user_id: int, event_id: int) -> int:
        """
        Conta quantos amigos confirmaram presença no evento.
        """
        return len(self.list_friends_confirmed_presence(user_id, event_id))

    def count_friends_favorited_event(self, user_id: int, event_id: int) -> int:
        """
        Conta quantos amigos favoritaram o evento.
        """
        return len(self.list_friends_favorited_event(user_id, event_id))


event_participation_service = EventParticipationService()
