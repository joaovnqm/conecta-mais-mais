import sqlite3
from pathlib import Path
from typing import Any

from database.ranking_schema import create_ranking_tables, get_default_db_path
from models.ranking import ACHIEVEMENTS, XP_ACTIONS


class RankingRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else get_default_db_path()
        create_ranking_tables(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_xp_entry(
        self,
        user_id: int,
        event_id: int | None,
        action_type: str,
        description: str | None = None,
    ) -> bool:
        """
        Adiciona XP ao usuário.
        """

        if action_type not in XP_ACTIONS:
            return False

        action = XP_ACTIONS[action_type]
        final_description = description or action.description

        with self._connect() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO event_xp_entries (
                        user_id,
                        event_id,
                        action_type,
                        points,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?);
                """, (
                    user_id,
                    event_id,
                    action_type,
                    action.points,
                    final_description,
                ))

                conn.commit()
                return cursor.rowcount > 0

            except sqlite3.IntegrityError:
                return False

    def get_user_total_xp(self, user_id: int) -> int:
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COALESCE(SUM(points), 0) AS total_xp
                FROM event_xp_entries
                WHERE user_id = ?;
            """, (user_id,))

            row = cursor.fetchone()
            return int(row["total_xp"] or 0)

    def get_user_stats(self, user_id: int) -> dict[str, int]:
        """
        Retorna estatísticas usadas para liberar medalhas/conquistas.
        """

        total_xp = self.get_user_total_xp(user_id)

        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(DISTINCT event_id) AS total
                FROM event_xp_entries
                WHERE user_id = ?
                  AND action_type = 'event_attendance';
            """, (user_id,))
            events_attended = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM event_xp_entries
                WHERE user_id = ?
                  AND action_type IN (
                    'attendance_certificate',
                    'presentation_certificate'
                  );
            """, (user_id,))
            certificates_received = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM event_xp_entries
                WHERE user_id = ?
                  AND action_type = 'presentation';
            """, (user_id,))
            presentations_done = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM event_xp_entries
                WHERE user_id = ?
                  AND action_type = 'event_organization';
            """, (user_id,))
            events_organized = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM event_xp_entries
                WHERE user_id = ?
                  AND action_type = 'support_team';
            """, (user_id,))
            support_events = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM event_xp_entries
                WHERE user_id = ?
                  AND action_type = 'highlighted_participation';
            """, (user_id,))
            highlighted_participations = int(cursor.fetchone()["total"] or 0)

        return {
            "total_xp": total_xp,
            "events_attended": events_attended,
            "certificates_received": certificates_received,
            "presentations_done": presentations_done,
            "events_organized": events_organized,
            "support_events": support_events,
            "highlighted_participations": highlighted_participations,
        }

    def unlock_achievement(
        self,
        user_id: int,
        achievement_key: str,
        achievement_name: str,
        description: str,
        icon: str,
    ) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO user_achievements (
                        user_id,
                        achievement_key,
                        achievement_name,
                        description,
                        icon
                    )
                    VALUES (?, ?, ?, ?, ?);
                """, (
                    user_id,
                    achievement_key,
                    achievement_name,
                    description,
                    icon,
                ))

                conn.commit()
                return cursor.rowcount > 0

            except sqlite3.IntegrityError:
                return False

    def update_user_achievements(self, user_id: int) -> list[dict[str, Any]]:
        """
        Verifica as estatísticas do usuário e libera novas conquistas.
        """

        stats = self.get_user_stats(user_id)
        unlocked_now: list[dict[str, Any]] = []

        for achievement in ACHIEVEMENTS:
            current_value = stats.get(achievement.metric, 0)

            if current_value >= achievement.required_value:
                was_unlocked = self.unlock_achievement(
                    user_id=user_id,
                    achievement_key=achievement.key,
                    achievement_name=achievement.name,
                    description=achievement.description,
                    icon=achievement.icon,
                )

                if was_unlocked:
                    unlocked_now.append({
                        "key": achievement.key,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon,
                    })

        return unlocked_now

    def get_user_achievements(self, user_id: int) -> list[dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    achievement_key,
                    achievement_name,
                    description,
                    icon,
                    unlocked_at
                FROM user_achievements
                WHERE user_id = ?
                ORDER BY unlocked_at DESC;
            """, (user_id,))

            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_user_xp_history(self, user_id: int, limit: int = 30) -> list[dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    event_id,
                    action_type,
                    points,
                    description,
                    created_at
                FROM event_xp_entries
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?;
            """, (user_id, limit))

            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_leaderboard(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    user_id,
                    COALESCE(SUM(points), 0) AS total_xp
                FROM event_xp_entries
                GROUP BY user_id
                ORDER BY total_xp DESC, user_id ASC
                LIMIT ?;
            """, (limit,))

            rows = cursor.fetchall()

        return [dict(row) for row in rows]
