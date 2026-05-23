import sqlite3
from datetime import datetime, timedelta
from random import randint

from services.send_email import email_service
from utils.security import security_utils_service
from utils.validations import validation_services


class PasswordResetService:
    """
    Serviço responsável por:
    - gerar códigos de verificação;
    - enviar códigos por e-mail;
    - validar códigos;
    - permitir cadastro com verificação de e-mail;
    - permitir redefinição de senha.
    """

    def __init__(self, database_path: str = "conecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """
        Cria a tabela responsável por armazenar códigos temporários de verificação.

        A combinação email + purpose é chave primária para permitir apenas um código ativo
        por finalidade para cada e-mail.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS verification_codes (
                email TEXT NOT NULL,
                purpose TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                PRIMARY KEY (email, purpose)
            )
            """
        )

        self.connection.commit()

    @staticmethod
    def generate_numeric_code() -> str:
        """
        Gera um código numérico de 6 dígitos.

        Como este método não depende de nenhum atributo da instância,
        ele deve ser estático.
        """
        return f"{randint(0, 999999):06d}"

    def _send_code(self, email: str, purpose: str) -> tuple[bool, str]:
        """
        Gera, salva e envia um código de verificação.

        Regras:
        - remove código anterior do mesmo e-mail e finalidade;
        - salva apenas o hash do código;
        - define expiração de 10 minutos;
        - envia o código por e-mail.
        """
        email = email.strip().lower()

        if purpose not in ("register", "reset_password"):
            return False, "Finalidade de código inválida."

        code = self.generate_numeric_code()
        code_hash = security_utils_service.hash_value(code)
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

        self.cursor.execute(
            """
            DELETE FROM verification_codes
            WHERE email = ?
            AND purpose = ?
            """,
            (email, purpose)
        )

        self.cursor.execute(
            """
            INSERT INTO verification_codes (
                email,
                purpose,
                code_hash,
                expires_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (email, purpose, code_hash, expires_at)
        )

        self.connection.commit()

        email_service.send_verification_email(email, code, purpose)

        return True, "Código enviado para o e-mail."

    def request_registration_code(self, email: str) -> tuple[bool, str]:
        """
        Solicita código para cadastro.

        O código só é enviado se:
        - o e-mail for válido;
        - o e-mail ainda não estiver cadastrado.
        """
        email = email.strip().lower()

        if not validation_services.valid_email(email):
            return False, "Esse e-mail é inválido."

        self.cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM users
                WHERE email = ?
            )
            """,
            (email,)
        )

        email_registered = bool(self.cursor.fetchone()[0])

        if email_registered:
            return False, "Esse e-mail já foi cadastrado."

        return self._send_code(email, "register")

    def request_password_reset(self, email: str) -> tuple[bool, str]:
        """
        Solicita código para redefinição de senha.

        O código só é enviado se:
        - o e-mail for válido;
        - o e-mail existir no sistema.
        """
        email = email.strip().lower()

        if not validation_services.valid_email(email):
            return False, "Esse e-mail é inválido."

        self.cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM users
                WHERE email = ?
            )
            """,
            (email,)
        )

        user_exists = bool(self.cursor.fetchone()[0])

        if not user_exists:
            return False, "E-mail não encontrado."

        return self._send_code(email, "reset_password")

    def verify_code(self, email: str, code: str, purpose: str) -> tuple[bool, str]:
        """
        Verifica se o código informado é válido.

        Regras:
        - precisa existir código para o e-mail e finalidade;
        - o código não pode estar expirado;
        - o código digitado precisa corresponder ao hash salvo;
        - depois de validado, o código é apagado para impedir reutilização.
        """
        email = email.strip().lower()
        code = code.strip()

        if purpose not in ("register", "reset_password"):
            return False, "Finalidade de código inválida."

        if not code:
            return False, "Digite o código recebido."

        self.cursor.execute(
            """
            SELECT code_hash, expires_at
            FROM verification_codes
            WHERE email = ?
            AND purpose = ?
            """,
            (email, purpose)
        )

        row = self.cursor.fetchone()

        if row is None:
            return False, "Nenhum código válido foi encontrado para este e-mail."

        code_hash, expires_at = row

        if datetime.now() > datetime.fromisoformat(expires_at):
            self.cursor.execute(
                """
                DELETE FROM verification_codes
                WHERE email = ?
                AND purpose = ?
                """,
                (email, purpose)
            )

            self.connection.commit()

            return False, "O código expirou."

        if not security_utils_service.verify_value(code, code_hash):
            return False, "Código inválido."

        self.cursor.execute(
            """
            DELETE FROM verification_codes
            WHERE email = ?
            AND purpose = ?
            """,
            (email, purpose)
        )

        self.connection.commit()

        return True, "Código validado com sucesso."

    def finalize_password_reset(self, email: str, new_password: str) -> tuple[bool, str]:
        """
        Finaliza a redefinição de senha.

        Regras:
        - valida a nova senha;
        - gera hash seguro;
        - atualiza a senha do usuário.
        """
        email = email.strip().lower()

        password_message = validation_services.password_error_message(new_password)

        if password_message is not None:
            return False, password_message

        new_password_hash = security_utils_service.hash_value(new_password)

        self.cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE email = ?
            """,
            (new_password_hash, email)
        )

        if self.cursor.rowcount == 0:
            return False, "Usuário não encontrado."

        self.connection.commit()

        return True, "Senha alterada com sucesso."


password_reset_service = PasswordResetService()