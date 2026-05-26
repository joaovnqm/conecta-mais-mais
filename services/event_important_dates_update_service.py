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
        """
        Atualiza as datas importantes de um evento a partir de sua URL oficial.
        """

        if not official_url:
            return False, "Evento sem URL oficial cadastrada."

        try:
            page_content = self.page_service.fetch_page_content(official_url)
            important_dates = self.extractor.extract(
                page_content, official_url)

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
