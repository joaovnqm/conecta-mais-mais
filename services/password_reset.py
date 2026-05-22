import sqlite3
from datetime import datetime, timedelta
from random import randint
from utils.security import security_utils_service
from services.send_email import email_service
from utils.validations import validation_services

class PasswordResetService:
    """Classe responsável por operações relacionadas à redefinição de senha, incluindo geração e verificação de códigos de verificação enviados por e-mail."""

    def __init__(self, database_path: str = "conecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        """
        Cria a tabela que armazena os códigos de verificação enviados por e-mail
        email: e-mail do usuário
        purpose: finalidade do código register ou reset_password
        code_hash: hash do código enviado
        expires_at: data/hora de expiração do código
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_codes (
            email TEXT NOT NULL,
            purpose TEXT NOT NULL,
            code_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            PRIMARY KEY (email, purpose)
            )
        """)
        self.connection.commit()

    def generate_numeric_code() -> str:
        """
        Essa função gera um código numérico de 6 dígitos para verificação por e-mail. O código é gerado aleatoriamente usando a função randint,
        e é formatado para garantir que tenha exatamente 6 dígitos, preenchendo com zeros à esquerda se necessário.
        """
        return f"{randint(0, 999999):06d}"

    def _send_code(self,email: str, purpose: str):
        """
        Essa função é responsável por gerar um código de verificação, 
        salvar o hash do código no banco de dados com a finalidade e o e-mail,
        e enviar o código para o e-mail do usuário. Ela também remove qualquer código 
        anterior para o mesmo e-mail e finalidade antes de salvar o novo código, garantindo que 
        apenas um código válido exista para cada combinação de e-mail e finalidade. O código gerado tem uma validade de 10 minutos.
        """
        code = self.generate_numeric_code()
        code_hash = security_utils_service.hash_value(code)
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        self.cursor.execute(
            "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
            (email, purpose)
        )

        self.cursor.execute(
            "INSERT INTO verification_codes (email, purpose, code_hash, expires_at) VALUES (?, ?, ?, ?)",
            (email, purpose, code_hash, expires_at)
        )

        self.connection.commit()

        email_service.send_verification_email(email, code, purpose)
        return True, "Código enviado para o e-mail."

    def request_registration_code(self, email: str):
        """
        Essa função solicita um código para registro. Ela verifica se o e-mail já existe no sistema, e se não existir, 
        envia um código de verificação para o e-mail do usuário para que ele possa prosseguir com o registro. 
        Se o e-mail já estiver registrado, a função retorna uma mensagem de erro informando que o e-mail já foi cadastrado.
        """
        email = email.strip().lower()

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
            (email,)
        )
        email_registered = bool(self.cursor.fetchone()[0])

        if email_registered:
            return False, "Esse e-mail já foi cadastrado."

        return self._send_code(email, "register")

    def request_password_reset(self, email: str):
        """
        Essa função solicita um código para redefinição de senha. Ela verifica se o e-mail existe no sistema, e se existir,
        envia um código de verificação para o e-mail do usuário para que ele possa prosseguir com a redefinição de senha.
        Se o e-mail não estiver registrado, a função retorna uma mensagem de erro informando que o e-mail não foi encontrado.
        """
        email = email.strip().lower()

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
            (email,)
        )
        user_exists = bool(self.cursor.fetchone()[0])

        if not user_exists:
            return False, "E-mail não encontrado."

        return self._send_code(email, "reset_password")

    def verify_code(self, email: str, code: str, purpose: str):
        """
        Essa função verifica se o código digitado pelo usuário é válido
        Regras:
        1. O código precisa existir no banco para o e-mail e a finalidade.
        2. O código não pode estar expirado
        3. O código digitado deve bater com o hash salvo
        4. Se for válido, ele é apagado do banco para não ser reutilizado
        """
        email = email.strip().lower()
        code = code.strip()

        self.cursor.execute(
            "SELECT code_hash, expires_at FROM verification_codes WHERE email = ? AND purpose = ?",
            (email, purpose)
        )
        row = self.cursor.fetchone()

        if row is None:
            return False, "Nenhum código válido foi encontrado para este e-mail."

        code_hash, expires_at = row

        if datetime.now() > datetime.fromisoformat(expires_at):
            self.cursor.execute(
                "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
                (email, purpose)
            )
            self.connection.commit()
            return False, "O código expirou."
        
        if not security_utils_service.verify_value(code, code_hash):
            return False, "Código inválido."

        self.cursor.execute(
            "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
            (email, purpose)
        )
        self.connection.commit()

        return True, "Código validado com sucesso."

    def finalize_password_reset(self, email: str, new_password: str):
        """
        Essa função finaliza a redefinição da senha
        1. Valida a nova senha
        2. Gera o hash da nova senha
        3. Atualiza a senha do usuário no banco de dados
        """
        email = email.strip().lower()

        password_message = validation_services.password_error_message(new_password)
        if password_message is not None:
            return False, password_message

        new_password_hash = security_utils_service.hash_value(new_password)

        self.cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (new_password_hash, email)
        )
        self.connection.commit()

        return True, "Senha alterada com sucesso."
    
password_reset_service = PasswordResetService()
