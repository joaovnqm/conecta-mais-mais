from pathlib import Path
import sqlite3
from typing import Any
from database.repositories.user_repository import user_services

class RankingRepository:
    def __init__(self, database_path: str = "conecta++.db"):
        """Inicializa o repositório de ranking, garantindo que as tabelas necessárias existam no banco de dados."""
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """Cria as tabelas necessárias para o sistema de ranking, incluindo: ações de ranking, ranking dos usuários e conquistas."""
        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS event_ranking_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                points INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, event_id, action_type)
            );

            CREATE TABLE IF NOT EXISTS user_event_ranking (
                user_id INTEGER PRIMARY KEY,
                total_points INTEGER NOT NULL DEFAULT 0,
                current_level TEXT NOT NULL DEFAULT 'Recém-chegado',
                events_attended INTEGER NOT NULL DEFAULT 0,
                certificates_received INTEGER NOT NULL DEFAULT 0,
                presentations_done INTEGER NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_event_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_name TEXT NOT NULL,
                achievement_description TEXT,
                unlocked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_name)
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_event_ranking_actions_unique
            ON event_ranking_actions(user_id, event_id, action_type);

            CREATE INDEX IF NOT EXISTS idx_event_ranking_actions_user_id
            ON event_ranking_actions(user_id);

            CREATE INDEX IF NOT EXISTS idx_event_ranking_actions_event_id
            ON event_ranking_actions(event_id);

            CREATE INDEX IF NOT EXISTS idx_event_ranking_actions_action_type
            ON event_ranking_actions(action_type);

            CREATE INDEX IF NOT EXISTS idx_user_event_ranking_total_points
            ON user_event_ranking(total_points DESC);
            """
        )

        self.connection.commit()

    def get_ranking(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Retorna o ranking geral dos usuários por pontos
        """

        query = """
            SELECT
                user_id,
                total_points,
                current_level,
                events_attended,
                certificates_received,
                presentations_done,
                last_updated
            FROM user_event_ranking
            ORDER BY total_points DESC, events_attended DESC, certificates_received DESC
            LIMIT ?;
        """

        rows = self.cursor.execute(query, (limit,)).fetchall()
        ranking: list[dict[str, Any]] = []

        for position, row in enumerate(rows, start=1):
            user_id = int(row["user_id"])

            user_name = user_services.check_user_name(user_id)

            if not user_name:
                user_name = f"Usuário sem nome ({user_id})"

            ranking.append(
                {
                    "position": position,
                    "user_id": user_id,
                    "name": user_name,
                    "total_points": int(row["total_points"]),
                    "current_level": row["current_level"],
                    "events_attended": int(row["events_attended"]),
                    "certificates_received": int(row["certificates_received"]),
                    "presentations_done": int(row["presentations_done"]),
                }
            )

        return ranking

    def add_points_once(self, user_id: int, event_id: int, action_type: str, points: int) -> bool:
        """
        Adiciona pontos uma única vez para cada usuário/evento/ação.
        """
        self.cursor = self.connection.cursor()

        already_exists = self.cursor.execute(
            """
            SELECT id
            FROM event_ranking_actions
            WHERE user_id = ?
                AND event_id = ?
                AND action_type = ?;
            """,
            (user_id, event_id, action_type),
        ).fetchone()

        if already_exists:
            return False

        current_total = self.get_total_points(user_id, self.connection)
        new_total = current_total + points
        new_level = self.get_level_by_points(new_total)

        self.cursor.execute(
            """
            INSERT INTO event_ranking_actions (
                user_id,
                event_id,
                action_type,
                points
            )
            VALUES (?, ?, ?, ?);
            """,
            (user_id, event_id, action_type, points),
        )

        self.cursor.execute(
            """
            INSERT INTO user_event_ranking (
                user_id,
                total_points,
                current_level
            )
            VALUES (?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET
                total_points = ?,
                current_level = ?,
                last_updated = CURRENT_TIMESTAMP;
            """,
            (
                user_id,
                new_total,
                new_level,
                new_total,
                new_level,
            ),
        )

        if action_type == "presence_confirmed":
            self.cursor.execute(
                """
                UPDATE user_event_ranking
                SET events_attended = events_attended + 1
                WHERE user_id = ?;
                """,
                (user_id,),
            )

        elif action_type == "certificate_presence":
            self.cursor.execute(
                """
                UPDATE user_event_ranking
                SET certificates_received = certificates_received + 1
                WHERE user_id = ?;
                """,
                (user_id,),
            )

        elif action_type == "lecture_presentation":
            self.cursor.execute(
                """
                UPDATE user_event_ranking
                SET presentations_done = presentations_done + 1
                WHERE user_id = ?;
                """,
                (user_id,),
            )

        self.connection.commit()
        return True

    def get_total_points(self, user_id: int, conn: sqlite3.Connection | None = None) -> int:
        """Retorna o total de pontos de um usuário, ou 0 se o usuário não tiver pontos registrados."""
        close_connection = False
        try:
            row = conn.execute(
                """
                SELECT total_points
                FROM user_event_ranking
                WHERE user_id = ?;
                """,
                (user_id,),
            ).fetchone()

            if row is None:
                return 0

            return int(row["total_points"])

        finally:
            if close_connection:
                conn.close()

    @staticmethod
    def get_level_by_points(points: int) -> str:
        """Retorna o nível do usuário com base na quantidade total de pontos acumulados, seguindo uma hierarquia de níveis que vai desde 
        "Recém-chegado" até "Lendário"""
        if points >= 5000:
            return "Lendário"
        if points >= 3000:
            return "Mestre"
        if points >= 2000:
            return "Elite"
        if points >= 1400:
            return "Referência"
        if points >= 900:
            return "Influente"
        if points >= 600:
            return "Experiente"
        if points >= 350:
            return "Engajado"
        if points >= 180:
            return "Explorador"
        if points >= 60:
            return "Participante"

        return "Recém-chegado"
