from pathlib import Path
import sqlite3


def get_default_db_path() -> Path:
    """
    Retorna o caminho padrão do banco de dados do projeto.
    """
    root_dir = Path(__file__).resolve().parents[1]
    return root_dir / "conecta++.db"


def drop_ranking_tables(cursor: sqlite3.Cursor) -> None:
    """
    Remove apenas as tabelas relacionadas ao ranking.
    """
    cursor.execute("DROP TABLE IF EXISTS user_event_achievements;")
    cursor.execute("DROP TABLE IF EXISTS user_event_ranking;")
    cursor.execute("DROP TABLE IF EXISTS event_ranking_actions;")


def _table_has_column(
    cursor: sqlite3.Cursor,
    table_name: str,
    column_name: str,
) -> bool:
    """
    Verifica se uma tabela possui determinada coluna.
    """
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    return any(column[1] == column_name for column in columns)


def create_ranking_tables(
    db_path: Path | str | None = None,
    reset: bool = False,
) -> None:
    """
    Cria as tabelas necessárias para o sistema de ranking/gamificação.
    """

    if db_path is None:
        db_path = get_default_db_path()

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        if reset:
            drop_ranking_tables(cursor)

        cursor.execute(
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
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_event_ranking (
                user_id INTEGER PRIMARY KEY,
                total_points INTEGER NOT NULL DEFAULT 0,
                current_level TEXT NOT NULL DEFAULT 'Recém-chegado',
                events_attended INTEGER NOT NULL DEFAULT 0,
                certificates_received INTEGER NOT NULL DEFAULT 0,
                presentations_done INTEGER NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_event_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_name TEXT NOT NULL,
                achievement_description TEXT,
                unlocked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_name)
            );
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_event_ranking_actions_unique
            ON event_ranking_actions(user_id, event_id, action_type);
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_ranking_actions_user_id
            ON event_ranking_actions(user_id);
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_ranking_actions_event_id
            ON event_ranking_actions(event_id);
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_ranking_actions_action_type
            ON event_ranking_actions(action_type);
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_event_ranking_total_points
            ON user_event_ranking(total_points DESC);
            """
        )

        conn.commit()

    finally:
        conn.close()
