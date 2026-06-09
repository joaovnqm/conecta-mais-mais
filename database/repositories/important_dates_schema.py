import sqlite3

class ImportantDatesRepository:
    """
    Repositório responsável por gerenciar a estrutura de dados relacionada
    às datas importantes dos eventos.
    """
    def _get_table_columns(self, connection: sqlite3.Connection, table_name: str) -> set[str]:
        """
        Retorna os nomes das colunas existentes em uma tabela do SQLite.
        """

        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")

        return {row[1] for row in cursor.fetchall()}


    def ensure_events_official_url_columns(self, connection: sqlite3.Connection) -> None:
        """
        Garante que a tabela events tenha as colunas necessárias para
        buscar datas importantes em fontes oficiais.
        """

        columns = self._get_table_columns(connection, "events")
        cursor = connection.cursor()

        if "official_url" not in columns:
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN official_url TEXT;
            """)

        if "auto_update_dates" not in columns:
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN auto_update_dates INTEGER NOT NULL DEFAULT 1;
            """)

        connection.commit()


    def create_event_important_dates_table(self, connection: sqlite3.Connection) -> None:
        """
        Cria a tabela responsável por armazenar datas importantes dos eventos.
        """

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_important_dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                event_id INTEGER NOT NULL,

                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT,

                source_url TEXT,
                confidence REAL NOT NULL DEFAULT 0.0,

                is_confirmed INTEGER NOT NULL DEFAULT 0,
                is_auto_generated INTEGER NOT NULL DEFAULT 1,

                last_checked_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (event_id)
                    REFERENCES events(event_id)
                    ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_important_dates_event_id
            ON event_important_dates(event_id);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_important_dates_date
            ON event_important_dates(date);
        """)

        connection.commit()


    def initialize_important_dates_feature(self, connection: sqlite3.Connection) -> None:
        """
        Inicializa toda a estrutura necessária para a funcionalidade
        de datas importantes.
        """

        self.ensure_events_official_url_columns(connection)
        self.create_event_important_dates_table(connection)

important_dates_repository = ImportantDatesRepository()