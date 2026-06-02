from pathlib import Path
import sqlite3
from typing import Any


class RankingRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            root_dir = Path(__file__).resolve().parents[2]
            db_path = root_dir / "conecta++.db"

        self.db_path = str(db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_ranking(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Retorna o ranking geral dos usuários por pontos.
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

        with self._connect() as conn:
            rows = conn.execute(query, (limit,)).fetchall()

        ranking: list[dict[str, Any]] = []

        for position, row in enumerate(rows, start=1):
            ranking.append(
                {
                    "position": position,
                    "user_id": row["user_id"],
                    "name": f"Usuário {row['user_id']}",
                    "total_points": row["total_points"],
                    "current_level": row["current_level"],
                    "events_attended": row["events_attended"],
                    "certificates_received": row["certificates_received"],
                    "presentations_done": row["presentations_done"],
                }
            )

        return ranking

    def add_points(
        self,
        user_id: int,
        event_id: int,
        action_type: str,
        points: int,
    ) -> None:
        """
        Registra uma ação do usuário e atualiza o ranking.
        """

        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
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

            cursor.execute(
                """
                INSERT INTO user_event_ranking (
                    user_id,
                    total_points,
                    current_level
                )
                VALUES (?, ?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET
                    total_points = total_points + excluded.total_points,
                    current_level = ?,
                    last_updated = CURRENT_TIMESTAMP;
                """,
                (
                    user_id,
                    points,
                    self.get_level_by_points(points),
                    self.get_level_by_points(
                        self.get_total_points(user_id, conn) + points),
                ),
            )

            if action_type == "event_attendance":
                cursor.execute(
                    """
                    UPDATE user_event_ranking
                    SET events_attended = events_attended + 1
                    WHERE user_id = ?;
                    """,
                    (user_id,),
                )

            elif action_type == "certificate_presence":
                cursor.execute(
                    """
                    UPDATE user_event_ranking
                    SET certificates_received = certificates_received + 1
                    WHERE user_id = ?;
                    """,
                    (user_id,),
                )

            elif action_type == "presentation":
                cursor.execute(
                    """
                    UPDATE user_event_ranking
                    SET presentations_done = presentations_done + 1
                    WHERE user_id = ?;
                    """,
                    (user_id,),
                )

            conn.commit()

    def get_total_points(self, user_id: int, conn: sqlite3.Connection | None = None) -> int:
        """
        Retorna a pontuação atual do usuário.
        """

        close_connection = False

        if conn is None:
            conn = self._connect()
            close_connection = True

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
        """
        Define o nível universal do usuário de acordo com os pontos.
        """

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
