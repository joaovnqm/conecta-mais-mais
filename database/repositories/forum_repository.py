import sqlite3
from typing import Any


class ForumService:
    """
    Serviço responsável pela regra de negócio do fórum.
    - Criar Tópicos; Listar Tópicos; Comentar; Curtir; Salvar e Denunciar
    """

    MAX_TITLE_LENGTH = 80
    MAX_DESCRIPTION_LENGTH = 900
    MAX_COMMENT_LENGTH = 500
    MAX_REPORT_REASON_LENGTH = 500

    def __init__(self, database_path: str = "conecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        """
        Cria as tabelas do fórum, caso ainda não existam
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_topics (
                topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CHECK(status IN ('active', 'removed')),
                FOREIGN KEY(author_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                parent_comment_id INTEGER,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(topic_id) REFERENCES forum_topics(topic_id) ON DELETE CASCADE,
                FOREIGN KEY(author_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(parent_comment_id) REFERENCES forum_comments(comment_id) ON DELETE CASCADE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_topic_likes (
                topic_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(topic_id, user_id),
                FOREIGN KEY(topic_id) REFERENCES forum_topics(topic_id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_topic_saves (
                topic_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(topic_id, user_id),
                FOREIGN KEY(topic_id) REFERENCES forum_topics(topic_id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_topic_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                reporter_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                reviewed_by INTEGER,
                reviewed_at TEXT,
                admin_note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CHECK(status IN ('pending', 'accepted', 'rejected')),
                UNIQUE(topic_id, reporter_id),
                FOREIGN KEY(topic_id) REFERENCES forum_topics(topic_id) ON DELETE CASCADE,
                FOREIGN KEY(reporter_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(reviewed_by) REFERENCES users(user_id) ON DELETE SET NULL
            )
            """
        )

        self._ensure_column(
            table_name="users",
            column_name="role",
            column_definition="role TEXT NOT NULL DEFAULT 'user'",
        )

        self._ensure_column(
            table_name="forum_topic_reports",
            column_name="reviewed_by",
            column_definition="reviewed_by INTEGER",
        )

        self._ensure_column(
            table_name="forum_topic_reports",
            column_name="reviewed_at",
            column_definition="reviewed_at TEXT",
        )

        self._ensure_column(
            table_name="forum_topic_reports",
            column_name="admin_note",
            column_definition="admin_note TEXT",
        )
        self._ensure_column(
            table_name="forum_comments",
            column_name="parent_comment_id",
            column_definition="parent_comment_id INTEGER",
        )
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_forum_topics_status
            ON forum_topics(status)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_forum_comments_topic
            ON forum_comments(topic_id)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_forum_reports_status
            ON forum_topic_reports(status)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_forum_comments_parent
            ON forum_comments(parent_comment_id)
            """
        )

        self.connection.commit()

    def create_topic(self, author_id: int, title: str | None, description: str | None) -> tuple[bool, str, int | None]:
        """
        Cria um Tópico no fórum
        """
        title = self._normalize_text(title)
        description = self._normalize_text(description)

        if not title:
            return False, 'O título do tópico é obrigatório', None

        if not description:
            return False, 'A descrição do tópico é obrigatória', None

        if len(title) > self.MAX_TITLE_LENGTH:
            return False, f'O título deve ter no máximo {self.MAX_TITLE_LENGTH} caracteres', None

        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            return False, f'A descrição teve ter no máximo {self.MAX_DESCRIPTION_LENGTH} caracteres', None

        self.cursor.execute(
            """
            INSERT INTO forum_topics (author_id, title, description)
            VALUES (?, ?, ?)
            """,
            (author_id, title, description)
        )
        self.connection.commit()

        return True, 'Tópico criado com sucesso', self.cursor.lastrowid
    
    def delete_topic(self, topic_id: int, requester_id: int) -> tuple[bool, str]:
        """
        Remove logicamente um tópico do fórum.
        """
        topic = self.cursor.execute(
            """
            SELECT
                topic_id,
                author_id,
                status
            FROM forum_topics
            WHERE topic_id = ?
            AND status = 'active'
            """,
            (topic_id,)).fetchone()

        if topic is None:
            return False, "Tópico não encontrado ou já removido."

        is_author = topic["author_id"] == requester_id
        is_admin = self.is_user_admin(requester_id)

        if not is_author and not is_admin:
            return False, "Você não tem permissão para remover este tópico."

        self.cursor.execute(
            """
            UPDATE forum_topics
            SET
                status = 'removed',
                updated_at = CURRENT_TIMESTAMP
            WHERE topic_id = ?
            """,
            (topic_id,),
        )

        self.connection.commit()
        return True, "Tópico removido com sucesso."
    
    def list_topics(self) -> list[dict[str, Any]]:
        """
        Lista os tópicos ativos do fórum com autor, likes e comentários
        """
        rows = self.cursor.execute(
            """
            SELECT
            ft.topic_id,
            ft.author_id,
            ft.title,
            ft.description,
            ft.status,
            ft.created_at,
            ft.updated_at,
            u.name AS author_name,
            u.username AS author_username,
            (
                SELECT COUNT(*)
                FROM forum_topic_likes fl
                WHERE fl.topic_id = ft.topic_id
            ) AS total_likes,
            (
                SELECT COUNT(*)
                FROM forum_comments fc
                WHERE fc.topic_id = ft.topic_id
            ) AS total_comments
            FROM forum_topics ft
            JOIN users u ON u.user_id = ft.author_id
            WHERE ft.status = 'active'
            ORDER BY ft.updated_at DESC, ft.created_at DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]
    
    def list_saved_topics(self, user_id: int) -> list[dict[str, Any]]:
        """
    Lista os tópicos salvos por um usuário. Só retorna tópicos ativos
    """
        rows = self.cursor.execute(
        """
        SELECT
            ft.topic_id,
            ft.author_id,
            ft.title,
            ft.description,
            ft.status,
            ft.created_at,
            ft.updated_at,
            fs.created_at AS saved_at,
            u.name AS author_name,
            u.username AS author_username,
            (
                SELECT COUNT(*)
                FROM forum_topic_likes fl
                WHERE fl.topic_id = ft.topic_id
            ) AS total_likes,
            (
                SELECT COUNT(*)
                FROM forum_comments fc
                WHERE fc.topic_id = ft.topic_id
            ) AS total_comments,
            (
                SELECT COUNT(*)
                FROM forum_topic_saves fsave
                WHERE fsave.topic_id = ft.topic_id
            ) AS total_saves

        FROM forum_topic_saves fs
        JOIN forum_topics ft ON ft.topic_id = fs.topic_id
        JOIN users u ON u.user_id = ft.author_id
        WHERE fs.user_id = ?
        AND ft.status = 'active'
        ORDER BY fs.created_at DESC
        """,
        (user_id,)).fetchall()
        return [dict(row) for row in rows]
    
    def get_topic(self, topic_id: int) -> dict[str, Any] | None:
        """
        Busca um Tópico específico
        """
        row = self.cursor.execute(
            """
            SELECT
                ft.topic_id,
                ft.author_id,
                ft.title,
                ft.description,
                ft.status,
                ft.created_at,
                ft.updated_at,
                u.name AS author_name,
                u.username AS author_username,
                u.email AS author_email,
                u.linkedin_url AS author_linkedin_url,
                u.github_url AS author_github_url
            FROM forum_topics ft
            JOIN users u ON u.user_id = ft.author_id
            WHERE ft.topic_id = ?
            AND ft.status = 'active'
            """,
            (topic_id,),
        ).fetchone()

        return dict(row) if row else None

    def add_comment(self, topic_id: int, author_id: int, content: str | None) -> tuple[bool, str]:
        """
        Adiciona comentário em um tópico
        """
        content = self._normalize_text(content)

        if not content:
            return False, 'O comentário não pode ficar vazio'

        if len(content) > self.MAX_COMMENT_LENGTH:
            return False, f'O comentário deve ter no máximo {self.MAX_COMMENT_LENGTH} caracteres'

        if self.get_topic(topic_id) is None:
            return False, 'Tópico não encontrado ou indisponível'

        self.cursor.execute(
            """
            INSERT INTO forum_comments (topic_id, author_id, content)
            VALUES (?, ?, ?)
            """,
            (topic_id, author_id, content),
        )

        self.cursor.execute(
            """
            UPDATE forum_topics
            SET updated_at = CURRENT_TIMESTAMP
            WHERE topic_id = ?
            """,
            (topic_id,),
        )
        self.connection.commit()

        return True, "comentário publicado com sucesso"

    def add_comment_reply(self,topic_id: int,parent_comment_id: int,author_id: int, content: str | None) -> tuple[bool, str]:
        """
        Adiciona uma resposta a qualquer comentário do fórum.
        """
        content = self._normalize_text(content)

        if not content:
            return False, "A resposta não pode ficar vazia."

        if len(content) > self.MAX_COMMENT_LENGTH:
            return False, f"A resposta deve ter no máximo {self.MAX_COMMENT_LENGTH} caracteres."

        if self.get_topic(topic_id) is None:
            return False, "Tópico não encontrado ou indisponível."

        parent_comment = self.cursor.execute(
            """
            SELECT comment_id
            FROM forum_comments
            WHERE comment_id = ?
            AND topic_id = ?
            """,
            (parent_comment_id, topic_id)).fetchone()

        if parent_comment is None:
            return False, "Comentário que você tentou responder não foi encontrado."

        self.cursor.execute(
            """
            INSERT INTO forum_comments (
                topic_id,
                author_id,
                parent_comment_id,
                content
            )
            VALUES (?, ?, ?, ?)
            """,
            (topic_id, author_id, parent_comment_id, content))

        self.cursor.execute(
            """
            UPDATE forum_topics
            SET updated_at = CURRENT_TIMESTAMP
            WHERE topic_id = ?
            """,
            (topic_id))

        self.connection.commit()

        return True, "Resposta publicada com sucesso."
    
    def list_comments(self, topic_id: int) -> list[dict[str, Any]]:
        """
        Lista apenas os comentários de um tópico
        """
        rows = self.cursor.execute(
            """
            SELECT
                fc.comment_id,
                fc.topic_id,
                fc.author_id,
                fc.parent_comment_id,
                fc.content,
                fc.created_at,
                u.name AS author_name,
                u.username AS author_username
            FROM forum_comments fc
            JOIN users u ON u.user_id = fc.author_id
            WHERE fc.topic_id = ?
            AND fc.parent_comment_id IS NULL
            ORDER BY fc.created_at ASC
            """,
            (topic_id,)).fetchall()

        return [dict(row) for row in rows]

    def list_comment_replies(self,topic_id: int, parent_comment_id: int) -> list[dict[str, Any]]:
        """
        Lista as respostas de um comentário
        """
        rows = self.cursor.execute(
            """
            SELECT
                fc.comment_id,
                fc.topic_id,
                fc.author_id,
                fc.parent_comment_id,
                fc.content,
                fc.created_at,
                u.name AS author_name,
                u.username AS author_username
            FROM forum_comments fc
            JOIN users u ON u.user_id = fc.author_id
            WHERE fc.topic_id = ?
            AND fc.parent_comment_id = ?
            ORDER BY fc.created_at ASC
            """,
            (topic_id, parent_comment_id)).fetchall()
        return [dict(row) for row in rows]

    def toggle_like(self, topic_id: int, user_id: int) -> tuple[bool, str]:
        """
        Alterna curtida de um usuário no tópico
        Se ainda não curtiu, curte
        Se curtiu, retira a curtida
        """
        if self.get_topic(topic_id) is None:
            return False, 'Tópico não encontrado ou indisponível'

        if self.user_liked_topic(topic_id, user_id):
            self.cursor.execute(
                """
                DELETE FROM forum_topic_likes
                WHERE topic_id = ? AND user_id = ?
                """,
                (topic_id, user_id),
            )
            self.connection.commit()
            return True, 'Curtida removida'

        self.cursor.execute(
            """
            INSERT INTO forum_topic_likes (topic_id, user_id)
            VALUES (?, ?)
            """,
            (topic_id, user_id),
        )
        self.connection.commit()
        return True, 'Tópico curtido'

    def toggle_save(self, topic_id: int, user_id: int) -> tuple[bool, str]:
        """
        Alterna o salvamento do tópico pelo usuário
        """
        if self.get_topic(topic_id) is None:
            return False, 'Tópico não encontrado ou indisponível'

        if self.user_saved_topic(topic_id, user_id):
            self.cursor.execute(
                """
                DELETE FROM forum_topic_saves
                WHERE topic_id = ? AND user_id = ?
                """,
                (topic_id, user_id),
            )
            self.connection.commit()
            return True, 'Tópico removido dos salvos'

        self.cursor.execute(
            """
            INSERT INTO forum_topic_saves (topic_id, user_id)
            VALUES (?, ?)
            """,
            (topic_id, user_id),
        )

        self.connection.commit()

        return True, 'Tópico salvo'

    def report_topic(self, topic_id: int, reporter_id: int, reason: str | None) -> tuple[bool, str]:
        """
        Registra denúncia do tópico
        """
        reason = self._normalize_text(reason)

        if not reason:
            return False, 'Informe o motivo da denúncia'

        if len(reason) > self.MAX_REPORT_REASON_LENGTH:
            return False, f'O motivo deve ter no máximo {self.MAX_REPORT_REASON_LENGTH} caracteres'

        topic = self.get_topic(topic_id)

        if topic is None:
            return False, 'Tópico não encontrado ou indisponível'

        if topic['author_id'] == reporter_id:
            return False, 'Você não pode denunciar seu próprio tópico'

        if self.user_reported_topic(topic_id, reporter_id):
            return False, 'Você Já denunciou este tópico'

        self.cursor.execute(
            """
            INSERT INTO forum_topic_reports (topic_id, reporter_id, reason)
            VALUES (?, ?, ?)
            """,
            (topic_id, reporter_id, reason),
        )
        self.connection.commit()

        return True, 'Denúncia registrada para análise'

    def get_topic_counts(self, topic_id: int) -> dict[str, int]:
        """
        Retorna contadores sociais do tópico
        """
        row = self.cursor.execute(
            """
            SELECT
                (
                    SELECT COUNT(*)
                    FROM forum_topic_likes
                    WHERE topic_id = ?
                ) AS total_likes,
                (
                    SELECT COUNT(*)
                    FROM forum_comments
                    WHERE topic_id = ?
                ) AS total_comments,
                (
                    SELECT COUNT(*)
                    FROM forum_topic_saves
                    WHERE topic_id = ?
                ) AS total_saves,
                (
                    SELECT COUNT(*)
                    FROM forum_topic_reports
                    WHERE topic_id = ?
                ) AS total_reports
            """,
            (
                topic_id,
                topic_id,
                topic_id,
                topic_id,
            ),
        ).fetchone()

        return dict(row)

    def user_liked_topic(self, topic_id: int, user_id: int) -> bool:
        return self._exists(
            """
            SELECT 1
            FROM forum_topic_likes
            WHERE topic_id = ? AND user_id = ?
            """,
            (topic_id, user_id),
        )

    def user_saved_topic(self, topic_id: int, user_id: int) -> bool:
        return self._exists(
            """
            SELECT 1
            FROM forum_topic_saves
            WHERE topic_id = ? AND user_id = ?
            """,
            (topic_id, user_id),
        )

    def user_reported_topic(self, topic_id: int, user_id: int) -> bool:
        return self._exists(
            """
            SELECT 1
            FROM forum_topic_reports
            WHERE topic_id = ? AND reporter_id = ?
            """,
            (topic_id, user_id),
        )
    
    def delete_comment(self, comment_id: int, requester_id: int, ) -> tuple[bool, str]:
        comment = self.cursor.execute(
            """
            SELECT
                comment_id,
                topic_id,
                author_id
            FROM forum_comments
            WHERE comment_id = ?
            """,
            (comment_id,),).fetchone()

        if comment is None:
            return False, "Comentário não encontrado."

        is_author = comment["author_id"] == requester_id
        is_admin = self.is_user_admin(requester_id)

        if not is_author and not is_admin:
            return False, "Você não tem permissão para remover este comentário."

        self._delete_comment_with_replies(comment_id)

        self.cursor.execute(
            """
            UPDATE forum_topics
            SET updated_at = CURRENT_TIMESTAMP
            WHERE topic_id = ?
            """,
            (comment["topic_id"],),
        )

        self.connection.commit()

        return True, "Comentário removido com sucesso."

    def _delete_comment_with_replies(self, comment_id: int) -> None:
        replies = self.cursor.execute(
            """
            SELECT comment_id
            FROM forum_comments
            WHERE parent_comment_id = ?
            """,
            (comment_id,),).fetchall()

        for reply in replies:
            self._delete_comment_with_replies(reply["comment_id"])

        self.cursor.execute(
            """
            DELETE FROM forum_comments
            WHERE comment_id = ?
            """,
            (comment_id,),)
        
    def _exists(self, query: str, params: tuple) -> bool:
        row = self.cursor.execute(query, params).fetchone()
        return row is not None

    def _normalize_text(self, value: str | None) -> str:
        return ' '.join((value or '').strip().split())

    def _column_exists(self, table_name: str, column_name: str) -> bool:
        """
        Verifica se uma coluna já existe em uma tabela SQLite
        """
        rows = self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
        return any(row["name"] == column_name for row in rows)

    def _ensure_column(self, table_name: str, column_name: str, column_definition: str) -> None:
        if self._column_exists(table_name, column_name):
            return

        self.cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_definition}
            """
        )

    def is_user_admin(self, user_id: int) -> bool:
        """
        Verifica se o usuário tem perfil de administrador.
        """
        row = self.cursor.execute(
            """
            SELECT role
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)).fetchone()

        if row is None:
            return False

        return row["role"] == "admin"

    def list_pending_reports(self) -> list[dict[str, Any]]:
        """
        Lista denúncias pendentes para análise administrativa.
        """
        rows = self.cursor.execute(
            """
            SELECT
                fr.report_id,
                fr.topic_id,
                fr.reporter_id,
                fr.reason,
                fr.status,
                fr.created_at,

                ft.title AS topic_title,
                ft.description AS topic_description,
                ft.status AS topic_status,
                ft.author_id AS topic_author_id,

                topic_author.name AS topic_author_name,
                topic_author.username AS topic_author_username,

                reporter.name AS reporter_name,
                reporter.username AS reporter_username

            FROM forum_topic_reports fr
            JOIN forum_topics ft ON ft.topic_id = fr.topic_id
            JOIN users topic_author ON topic_author.user_id = ft.author_id
            JOIN users reporter ON reporter.user_id = fr.reporter_id

            WHERE fr.status = 'pending'
            ORDER BY fr.created_at ASC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def get_report_details(self, report_id: int) -> dict[str, Any] | None:
        """
        Busca os detalhes completos de uma denúncia.
        """
        row = self.cursor.execute(
            """
            SELECT
                fr.report_id,
                fr.topic_id,
                fr.reporter_id,
                fr.reason,
                fr.status,
                fr.created_at,
                fr.reviewed_by,
                fr.reviewed_at,
                fr.admin_note,

                ft.title AS topic_title,
                ft.description AS topic_description,
                ft.status AS topic_status,
                ft.author_id AS topic_author_id,
                ft.created_at AS topic_created_at,

                topic_author.name AS topic_author_name,
                topic_author.username AS topic_author_username,

                reporter.name AS reporter_name,
                reporter.username AS reporter_username

            FROM forum_topic_reports fr
            JOIN forum_topics ft ON ft.topic_id = fr.topic_id
            JOIN users topic_author ON topic_author.user_id = ft.author_id
            JOIN users reporter ON reporter.user_id = fr.reporter_id

            WHERE fr.report_id = ?
            """,
            (report_id,)).fetchone()

        return dict(row) if row else None

    def accept_report(self, report_id: int, admin_id: int, admin_note: str | None = None,) -> tuple[bool, str]:
        """
        Aceita uma denúncia.
        """
        if not self.is_user_admin(admin_id):
            return False, "Apenas administradores podem aceitar denúncias."

        report = self.get_report_details(report_id)

        if report is None:
            return False, "Denúncia não encontrada."

        if report["status"] != "pending":
            return False, "Esta denúncia já foi analisada."

        admin_note = self._normalize_text(admin_note)

        self.cursor.execute(
            """
            UPDATE forum_topic_reports
            SET
                status = 'accepted',
                reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP,
                admin_note = ?
            WHERE report_id = ?
            """,
            (admin_id, admin_note, report_id),
        )

        self.cursor.execute(
            """
            UPDATE forum_topics
            SET
                status = 'removed',
                updated_at = CURRENT_TIMESTAMP
            WHERE topic_id = ?
            """,
            (report["topic_id"],),
        )

        self.connection.commit()

        return True, "Denúncia aceita. O tópico foi removido da listagem pública."

    def reject_report(self, report_id: int, admin_id: int, admin_note: str | None = None,) -> tuple[bool, str]:
        """
        Rejeita uma denúncia.
        """
        if not self.is_user_admin(admin_id):
            return False, "Apenas administradores podem rejeitar denúncias."

        report = self.get_report_details(report_id)

        if report is None:
            return False, "Denúncia não encontrada."

        if report["status"] != "pending":
            return False, "Esta denúncia já foi analisada."

        admin_note = self._normalize_text(admin_note)

        self.cursor.execute(
            """
            UPDATE forum_topic_reports
            SET
                status = 'rejected',
                reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP,
                admin_note = ?
            WHERE report_id = ?
            """,
            (admin_id, admin_note, report_id))

        self.connection.commit()

        return True, "Denúncia rejeitada. O tópico foi mantido no fórum."


forum_service = ForumService()
