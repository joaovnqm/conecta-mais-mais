import sqlite3
from typing import Any
from database.repositories.event_participation import EventParticipationService


class EventFeedbackService:
    """
    Serviço responsável por salvar, atualizar, remover e listar feedbacks de eventos.

    Regra principal:
    o usuário só pode avaliar um evento se tiver presença confirmada.
    """

    MIN_RATING = 1
    MAX_RATING = 5
    MAX_COMMENT_LENGTH = 700

    def __init__(self, database_path: str = "conecta++.db"):
        """
        Inicializa a conexão com o banco e garante que a tabela exista.
        """
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self.participation_service = EventParticipationService(database_path)
        self._create_table()

    def _create_table(self) -> None:
        """
        Cria a tabela de feedbacks caso ela ainda não exista.

        UNIQUE(user_id, event_id) impede que o mesmo usuário crie
        mais de um feedback para o mesmo evento.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS event_feedbacks (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                comment TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, event_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(event_id) REFERENCES events(event_id) ON DELETE CASCADE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_feedbacks_event
            ON event_feedbacks(event_id)
            """
        )

        self.connection.commit()

    def save_feedback(
        self,
        user_id: int,
        event_id: int,
        rating: int | str | None,
        comment: str | None,
    ) -> tuple[bool, str]:
        """
        Salva ou atualiza o feedback do usuário para um evento.

        Se o usuário ainda não avaliou, cria.
        Se já avaliou, atualiza.
        """
        rating = self._normalize_rating(rating)
        comment = self._normalize_comment(comment)

        if rating is None:
            return False, "Selecione uma nota de 1 a 5 estrelas."

        if len(comment) > self.MAX_COMMENT_LENGTH:
            return (
                False,
                f"O comentário precisa ter no máximo {self.MAX_COMMENT_LENGTH} caracteres.",
            )

        if not self.participation_service.check_presence(user_id, event_id):
            return (
                False,
                "Você precisa confirmar presença no evento antes de enviar feedback.",
            )

        self.cursor.execute(
            """
            INSERT INTO event_feedbacks (user_id, event_id, rating, comment)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, event_id) DO UPDATE SET
                rating = excluded.rating,
                comment = excluded.comment,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, event_id, rating, comment),
        )

        self.connection.commit()
        return True, "Feedback salvo com sucesso."

    def delete_feedback(self, user_id: int, event_id: int) -> tuple[bool, str]:
        """
        Remove o feedback do usuário em um evento.
        """
        self.cursor.execute(
            """
            DELETE FROM event_feedbacks
            WHERE user_id = ? AND event_id = ?
            """,
            (user_id, event_id),
        )

        if self.cursor.rowcount == 0:
            return False, "Nenhum feedback encontrado para remover."

        self.connection.commit()
        return True, "Feedback removido com sucesso."

    def get_user_feedback(self, user_id: int, event_id: int) -> dict[str, Any] | None:
        """
        Busca o feedback de um usuário específico em um evento.
        """
        row = self.cursor.execute(
            """
            SELECT *
            FROM event_feedbacks
            WHERE user_id = ? AND event_id = ?
            """,
            (user_id, event_id),
        ).fetchone()

        return dict(row) if row else None

    def list_event_feedbacks(self, event_id: int) -> list[dict[str, Any]]:
        """
        Lista todos os feedbacks de um evento.

        Também busca nome e username do usuário que avaliou.
        """
        rows = self.cursor.execute(
            """
            SELECT
                ef.feedback_id,
                ef.user_id,
                ef.event_id,
                ef.rating,
                ef.comment,
                ef.created_at,
                ef.updated_at,
                u.name AS user_name,
                u.username AS username
            FROM event_feedbacks ef
            JOIN users u ON u.user_id = ef.user_id
            WHERE ef.event_id = ?
            ORDER BY ef.updated_at DESC, ef.created_at DESC
            """,
            (event_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_feedback_summary(self, event_id: int) -> dict[str, Any]:
        """
        Retorna quantidade de feedbacks e média das avaliações do evento.
        """
        row = self.cursor.execute(
            """
            SELECT
                COUNT(*) AS total_feedbacks,
                ROUND(AVG(rating), 1) AS average_rating
            FROM event_feedbacks
            WHERE event_id = ?
            """,
            (event_id,),
        ).fetchone()

        return dict(row)

    def _normalize_rating(self, rating: int | str | None) -> int | None:
        """
        Converte a nota para inteiro e valida se está entre 1 e 5.
        """
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return None

        if self.MIN_RATING <= rating <= self.MAX_RATING:
            return rating

        return None

    def _normalize_comment(self, comment: str | None) -> str:
        """
        Limpa espaços extras do comentário.

        Exemplo:
        '  muito    bom  ' vira 'muito bom'
        """
        return " ".join((comment or "").strip().split())


event_feedback_service = EventFeedbackService()
