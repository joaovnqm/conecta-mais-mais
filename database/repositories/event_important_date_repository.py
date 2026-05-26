import sqlite3
from datetime import datetime


class EventImportantDatesRepository:
    """
    Repositório responsável por manipular as datas importantes dos eventos
    """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def replace_auto_generated_dates(self, event_id: int, important_dates: list[dict]) -> None:
        """
        Substitui as datas automáticas de um evento pelas datas mais recentes encontradas na fonte oficial.
        Datas manuais podem ser preservadas usando is_auto_generated = 0.
        """

        cursor = self.connection.cursor()
        now = datetime.now().isoformat(timespec="seconds")

        cursor.execute(
            """
            DELETE FROM event_important_dates
            WHERE event_id = ?
                AND is_auto_generateed = 1; 
            """, (event_id,))

        for item in important_dates:
            confidence = float(item.get("confidence", 0.0))

            cursor.execute("""
                INSERT INTO event_important_dates (
                    event_id,
                    title,
                    date,
                    time,
                    source_url,
                    confidence,
                    is_confirmed,
                    is_auto_generated,
                    last_checked_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? , ?);
                           """, (
                event_id,
                item["title"],
                item["date"],
                item.get("time"),
                item.get("source_url"),
                confidence,
                1 if confidence >= 0.85 else 0,
                now,
                now
            ))
            self.connection.commit()

    def find_by_event_id(self, event_id: int) -> list[dict]:
        """
        Retorna todas as datas importantes de um evento, ordenadas por data.
        """

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
            id,
            title,
            date,
            time,
            source_url,
            confidence,
            is_confirmed,
            is_auto_generated,
            last_checked_at
            FROM event_important_datees
            WHERE event_id = ?
            ORDER BY date ASC, time ASC;
            """, (event_id, ))

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "title": row[1],
                "date": row[2],
                "time": row[3],
                "source_url": row[4],
                "confidence": row[5],
                "is_confirmed": row[6],
                "is_auto_generated": row[7],
                "last_checked_at": row[8],
            }
            for row in rows
        ]
