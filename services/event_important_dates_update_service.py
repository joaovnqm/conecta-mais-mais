import sqlite3

from database.repositories.event_important_dates_repository import EventImportantDatesRepository
from services.important_dates_extractor import ImportantDatesExtractor
from services.important_dates_policy import ImportantDatesPolicy
from services.official_event_page_service import OfficialEventPageService


class EventImportantDatesUpdateService:
    """
    Serviço responsável por atualizar as datas importantes de um evento.

    A atualização passa por uma camada de qualidade antes de salvar no banco.
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
            self._replace_dates(event_id, [])
            return False, "Evento sem URL oficial cadastrada."

        curated_dates = ImportantDatesPolicy.get_curated_dates_by_url(official_url)

        if curated_dates:
            self._replace_dates(event_id, curated_dates)
            return True, "Datas importantes atualizadas com fallback confiável."

        if ImportantDatesPolicy.should_block_url(official_url):
            self._replace_dates(event_id, [])
            return False, "Fonte oficial bloqueada para extração automática de datas importantes."

        try:
            fallback_year = self._get_event_year(event_id)
            page_content = self.page_service.fetch_page_content(official_url)

            raw_dates = self.extractor.extract(
                page_content,
                official_url,
                fallback_year=fallback_year
            )

            important_dates = ImportantDatesPolicy.prepare_dates_for_storage(
                raw_dates,
                official_url,
            )

            self._replace_dates(event_id, important_dates)

            if not important_dates:
                return False, "Nenhuma data importante confiável foi encontrada."

            return True, "Datas importantes atualizadas com sucesso."

        except Exception as error:
            self._replace_dates(event_id, [])
            return False, f"Erro ao atualizar datas importantes: {error}"

    def _replace_dates(self, event_id: int, important_dates: list[dict]) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON;")

            repository = EventImportantDatesRepository(connection)
            repository.replace_auto_generated_dates(
                event_id,
                important_dates
            )

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
