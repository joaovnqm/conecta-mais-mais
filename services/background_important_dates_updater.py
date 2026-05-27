import asyncio
import sqlite3

from services.event_important_dates_update_service import EventImportantDatesUpdateService


class BackgroundImportantDatesUpdater:
    """
    Atualizador em segundo plano das datas importantes dos eventos.
    """

    def __init__(self, database_path: str, interval_seconds: int = 21600):
        self.database_path = database_path
        self.interval_seconds = interval_seconds
        self.is_running = False

    async def start(self) -> None:
        """
        Inicia a rotina periódica de atualização.
        """

        if self.is_running:
            return

        self.is_running = True

        while self.is_running:
            await asyncio.to_thread(self._update_all_events)
            await asyncio.sleep(self.interval_seconds)

    def stop(self) -> None:
        """
        Para a rotina de atualização.
        """

        self.is_running = False

    def _update_all_events(self) -> None:
        """
        Busca todos os eventos com URL oficial e tenta atualizar suas datas.
        """

        events = self._find_events_enabled_for_update()
        update_service = EventImportantDatesUpdateService(self.database_path)

        for event in events:
            update_service.update_event_dates(
                event_id=event["event_id"],
                official_url=event["official_url"]
            )

    def _find_events_enabled_for_update(self) -> list[dict]:
        """
        Retorna eventos que possuem URL oficial e atualização automática ativa.
        """

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT event_id, official_url
                FROM events
                WHERE official_url IS NOT NULL
                  AND official_url != ''
                  AND COALESCE(auto_update_dates, 1) = 1;
                """
            )

            rows = cursor.fetchall()

        return [
            {
                "event_id": row[0],
                "official_url": row[1]
            }
            for row in rows
        ]
