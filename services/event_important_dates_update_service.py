import sqlite3

from database.repositories.event_important_dates_repository import EventImportantDatesRepository
from services.important_dates_extractor import ImportantDatesExtractor
from services.official_event_page_service import OfficialEventPageService


class EventImportantDatesUpdateService:
    """
    Serviço responsável por atualizar as datas importantes de um evento.
    """

    def __init__(self, database_path: str):
        self.database_path = database_path
        self.page_service = OfficialEventPageService()
        self.extractor = ImportantDatesExtractor()

    def update_event_dates(
        self,
        event_id: int,
        official_url: str
    ) -> tuple[bool, str]:
        if not official_url:
            return False, "Evento sem URL oficial cadastrada."

        try:
            fallback_year = self._get_event_year(event_id)

            page_content = self.page_service.fetch_page_content(official_url)

            important_dates = self.extractor.extract(
                page_content,
                official_url,
                fallback_year=fallback_year
            )

            if not important_dates:
                return False, "Nenhuma data importante foi encontrada na fonte oficial."

            with sqlite3.connect(self.database_path) as connection:
                connection.execute("PRAGMA foreign_keys = ON;")

                repository = EventImportantDatesRepository(connection)
                repository.replace_auto_generated_dates(
                    event_id,
                    important_dates
                )

            return True, "Datas importantes atualizadas com sucesso."

        except Exception as error:
            return False, f"Erro ao atualizar datas importantes: {error}"

    def _get_event_year(self, event_id: int) -> int | None:
        """
        Retorna o ano da data principal do evento.

        A data principal no banco está no formato DD-MM-AAAA.
        """

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT date
                FROM events
                WHERE event_id = ?
                """,
                (event_id,)
            )

            row = cursor.fetchone()

        if not row or not row[0]:
            return None

        date_text = row[0]

        try:
            return int(date_text.split("-")[2])
        except (IndexError, ValueError):
            return None
