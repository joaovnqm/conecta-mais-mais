import sqlite3
from typing import List, Optional

from database.repositories.interest_repository import interest_services
from models.event import Event
from utils.validations import validation_services


class EventServices:
    """
    Classe responsável por operações relacionadas aos eventos e pela conexão com o banco de dados.
    """

    def __init__(self, database_path: str = "conecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """
        Cria a tabela events caso ela não exista e garante as colunas
        necessárias para a funcionalidade de datas importantes.
        """

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                event_location TEXT,
                date TEXT,
                hour TEXT,
                creator_id INTEGER NOT NULL,
                official_url TEXT,
                auto_update_dates INTEGER NOT NULL DEFAULT 1,

                FOREIGN KEY (creator_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        self._ensure_event_extra_columns()
        self.connection.commit()

    def _ensure_event_extra_columns(self) -> None:
        """
        Garante que bancos antigos recebam as colunas novas sem apagar dados.
        """

        self.cursor.execute("PRAGMA table_info(events)")
        columns = {column[1] for column in self.cursor.fetchall()}

        if "official_url" not in columns:
            self.cursor.execute(
                "ALTER TABLE events ADD COLUMN official_url TEXT")

        if "auto_update_dates" not in columns:
            self.cursor.execute(
                "ALTER TABLE events ADD COLUMN auto_update_dates INTEGER NOT NULL DEFAULT 1"
            )

    def _normalize_optional_text(self, value: Optional[str]) -> Optional[str]:
        """
        Normaliza campos opcionais de texto.
        """

        if value is None:
            return None

        value = value.strip()

        return value if value else None

    def create_event(
        self,
        name: str,
        description: str,
        event_location: Optional[str],
        date: Optional[str],
        hour: Optional[str],
        creator_id: int,
        interest: str = "Social",
        official_url: Optional[str] = None,
        auto_update_dates: int = 1
    ):
        """
        Cria um evento validando os campos obrigatórios e opcionais.
        """

        name = name.strip()
        description = description.strip()
        event_location = self._normalize_optional_text(event_location)
        date = self._normalize_optional_text(date)
        hour = self._normalize_optional_text(hour)
        official_url = self._normalize_optional_text(official_url)

        if not validation_services.valid_name_events(name):
            return False, "O nome precisa ter pelo menos 2 caracteres."

        if not validation_services.valid_description(description):
            return False, "A descrição precisa ter entre 30 e 500 caracteres."

        if date and not validation_services.valid_date(date):
            return False, "O formato da data está errado. Por favor, siga o padrão dd-mm-aaaa e tenha certeza que a data ainda não passou."

        if hour:
            if not date:
                return False, "Você precisa adicionar uma data para que a hora seja válida."

            if not validation_services.valid_hour(date, hour):
                return False, "O formato da hora está errado. Por favor, siga o padrão hh:mm e tenha certeza que colocou uma data e uma hora que ainda não passaram."

        if official_url and not official_url.startswith(("http://", "https://")):
            return False, "O link oficial precisa começar com http:// ou https://."

        self.cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM events
                WHERE name = ?
                  AND creator_id = ?
            )
            """,
            (name, creator_id)
        )

        event_registered = bool(self.cursor.fetchone()[0])

        if event_registered:
            return False, "Esse evento já foi cadastrado."

        self.cursor.execute(
            """
            INSERT INTO events (
                name,
                description,
                event_location,
                date,
                hour,
                creator_id,
                official_url,
                auto_update_dates
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                event_location,
                date,
                hour,
                creator_id,
                official_url,
                int(auto_update_dates)
            )
        )

        self.connection.commit()

        event_id = self.cursor.lastrowid

        interest_id = interest_services.index_interest(interest)

        self.cursor.execute(
            """
            INSERT INTO events_interests (
                event_id,
                interest_id
            )
            VALUES (?, ?)
            """,
            (event_id, interest_id)
        )

        self.connection.commit()

        return True, "Evento criado com sucesso!"

    def check_events_by_interests(self, user_id: int) -> List[Event]:
        """
        Retorna eventos com base nos interesses do usuário.
        """

        interests = interest_services.check_user_interests(user_id)
        events = []
        seen_ids = set()

        for interest in interests:
            self.cursor.execute(
                "SELECT event_id FROM events_interests WHERE interest_id = ?",
                (interest.interest_id,)
            )

            for row in self.cursor.fetchall():
                event_id = row[0]

                if event_id in seen_ids:
                    continue

                self.cursor.execute(
                    """
                    SELECT event_id, name, description
                    FROM events
                    WHERE event_id = ?
                    """,
                    (event_id,)
                )

                result = self.cursor.fetchone()

                if result:
                    seen_ids.add(event_id)
                    events.append(Event(result[0], result[1], result[2]))

        return events

    def check_events_by_interest(self, selected_interest: str):
        """
        Retorna eventos com base em um interesse selecionado.
        """

        events = []
        interest_id = interest_services.index_interest(selected_interest)

        self.cursor.execute(
            "SELECT event_id FROM events_interests WHERE interest_id = ?",
            (interest_id,)
        )

        for row in self.cursor.fetchall():
            event_id = row[0]

            self.cursor.execute(
                """
                SELECT event_id, name, description
                FROM events
                WHERE event_id = ?
                """,
                (event_id,)
            )

            result = self.cursor.fetchone()

            if result:
                events.append(Event(result[0], result[1], result[2]))

        return events

    def check_events_by_social(self, user_id: int):
        """
        Retorna eventos criados por amigos aceitos do usuário.
        """

        events = []
        friends = set()

        self.cursor.execute(
            """
            SELECT user_low_id
            FROM friendships
            WHERE user_high_id = ?
              AND status = 'accepted'
            """,
            (user_id,)
        )

        for friend in self.cursor.fetchall():
            friends.add(friend[0])

        self.cursor.execute(
            """
            SELECT user_high_id
            FROM friendships
            WHERE user_low_id = ?
              AND status = 'accepted'
            """,
            (user_id,)
        )

        for friend in self.cursor.fetchall():
            friends.add(friend[0])

        for friend in friends:
            self.cursor.execute(
                """
                SELECT event_id, name, description
                FROM events
                WHERE creator_id = ?
                """,
                (friend,)
            )

            for event in self.cursor.fetchall():
                events.append(Event(event[0], event[1], event[2]))

        return events

    def check_events_by_user(self, user_id: int):
        """
        Retorna eventos criados pelo usuário.
        """

        events = []

        self.cursor.execute(
            """
            SELECT event_id, name, description
            FROM events
            WHERE creator_id = ?
            """,
            (user_id,)
        )

        for event in self.cursor.fetchall():
            events.append(Event(event[0], event[1], event[2]))

        return events

    def check_event(self, event_id: int) -> Event:
        """
        Retorna os detalhes completos de um evento específico.
        """

        self.cursor.execute(
            """
            SELECT
                event_id,
                name,
                description,
                event_location,
                date,
                hour,
                creator_id,
                official_url,
                auto_update_dates
            FROM events
            WHERE event_id = ?
            """,
            (event_id,)
        )

        event = self.cursor.fetchone()

        if event is None:
            raise ValueError("Evento não encontrado.")

        return Event(
            event_id=event[0],
            name=event[1],
            description=event[2],
            event_location=event[3],
            date=event[4],
            hour=event[5],
            creator_id=event[6],
            official_url=event[7],
            auto_update_dates=event[8]
        )

    def edit_event(
        self,
        event_id: int,
        name: str,
        description: str,
        event_location: Optional[str],
        date: Optional[str],
        hour: Optional[str],
        official_url: Optional[str] = None,
        auto_update_dates: int = 1
    ):
        """
        Edita um evento específico.
        """

        name = name.strip()
        description = description.strip()
        event_location = self._normalize_optional_text(event_location)
        date = self._normalize_optional_text(date)
        hour = self._normalize_optional_text(hour)
        official_url = self._normalize_optional_text(official_url)

        if not validation_services.valid_name_events(name):
            return False, "O nome precisa ter pelo menos 2 caracteres."

        if not validation_services.valid_description(description):
            return False, "A descrição precisa ter entre 30 e 500 caracteres."

        if date and not validation_services.valid_date(date):
            return False, "O formato da data está errado. Por favor, siga o padrão dd-mm-aaaa e tenha certeza que a data ainda não passou."

        if hour:
            if not date:
                return False, "Você precisa adicionar uma data para que a hora seja válida."

            if not validation_services.valid_hour(date, hour):
                return False, "O formato da hora está errado. Por favor, siga o padrão hh:mm e tenha certeza que colocou uma data e uma hora que ainda não passaram."

        if official_url and not official_url.startswith(("http://", "https://")):
            return False, "O link oficial precisa começar com http:// ou https://."

        self.cursor.execute(
            """
            UPDATE events
            SET name = ?,
                description = ?,
                event_location = ?,
                date = ?,
                hour = ?,
                official_url = ?,
                auto_update_dates = ?
            WHERE event_id = ?
            """,
            (
                name,
                description,
                event_location,
                date,
                hour,
                official_url,
                int(auto_update_dates),
                event_id
            )
        )

        self.connection.commit()

        return True, "Evento editado com sucesso!"

    def delete_event(self, event_id: int):
        """
        Deleta um evento específico.
        """

        self.cursor.execute(
            "DELETE FROM events WHERE event_id = ?",
            (event_id,)
        )

        self.connection.commit()

        return True, "Evento deletado com sucesso!"


event_services = EventServices()
