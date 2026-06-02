import sqlite3
from pathlib import Path


def get_default_db_path() -> Path:
    """
    Retorna o caminho padrão do banco
    """
    project_root = Path(__file__).resolve().parents[1]
    return project_root / "conecta++.db"


def create_ranking_tables(db_path: str | Path | None = None) -> None:
    """
    Cria as tabelas necessárias para o sistema de ranking
    """

    database_path = Path(db_path) if db_path else get_default_db_path()

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS event_xp_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                points INTEGER NOT NULL CHECK(points >= 0),
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, event_id, action_type)
            );
            """)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_key TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(user_id, achievement_key)
            );
            """)

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_xp_event_id
            ON event_xp_entries(user_id);
            """)

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_xp_event_id
            ON event_xp_entries(event_id);
            """)

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_xp_action_type
            ON event_xp_entries(action_type);
            """)

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id
            ON user_achievements(user_id);
            """)

        conn.commit()
