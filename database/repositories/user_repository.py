import sqlite3

from models.user import User
from utils.security import security_utils_service
from utils.validations import validation_services


class UserServices:
    """
    Classe responsável por operações relacionadas aos usuários e pela conexão com o banco de dados.
    """

    def __init__(self, database_path: str = "conecta++.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """
        Cria a tabela users caso ela ainda não exista.

        Também garante, por migração, que bancos antigos recebam as colunas:
        - username
        - linkedin_url
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        self._ensure_profile_columns()
        self.connection.commit()

    def _ensure_profile_columns(self) -> None:
        """
        Garante que a tabela users tenha as colunas novas sem apagar dados antigos.

        Observação:
        - username é obrigatório para novos cadastros pela validação do register.
        - Em bancos antigos, usuários já existentes podem ficar com username NULL até serem atualizados manualmente.
        """
        self.cursor.execute("PRAGMA table_info(users)")
        columns = {column[1] for column in self.cursor.fetchall()}

        if "username" not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")

        if "linkedin_url" not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN linkedin_url TEXT")

        self.cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower
            ON users(LOWER(username))
            WHERE username IS NOT NULL AND username != ''
        """)

    def login(self, email: str, password: str):
        """
        Realiza o login do usuário.

        Retorna:
            tuple:
                - bool indicando sucesso ou falha;
                - mensagem;
                - nome do usuário;
                - id do usuário.
        """
        email = email.strip().lower()

        self.cursor.execute(
            """
            SELECT name, password, user_id
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        user = self.cursor.fetchone()

        if user is None:
            return False, "Usuário não encontrado.", None, None

        name, saved_password, user_id = user

        if not security_utils_service.verify_value(password, saved_password):
            return False, "Senha incorreta.", None, None

        name = validation_services.normalize_name(name)

        return True, "Login realizado com sucesso!", name, user_id

    def register(
        self,
        name: str,
        email: str,
        password: str,
        username: str,
        linkedin_url: str | None = None
    ):
        """
        Cadastra um novo usuário.

        Regras:
        - nome obrigatório e válido;
        - e-mail obrigatório, válido e único;
        - username obrigatório, válido e único;
        - LinkedIn opcional, mas se informado precisa ter formato válido;
        - senha obrigatória e válida;
        - senha armazenada com hash seguro.
        """
        name = validation_services.normalize_name(name)
        email = email.strip().lower()
        username = validation_services.normalize_username(username)
        linkedin_url = (linkedin_url or "").strip()

        if not validation_services.valid_name_users(name):
            return (
                False,
                "O nome precisa ter pelo menos 2 caracteres, no máximo 50 caracteres e não pode conter números.",
                None
            )

        if not validation_services.valid_email(email):
            return False, "Esse e-mail é inválido!", None

        if not validation_services.valid_username(username):
            return (
                False,
                "O username é obrigatório e precisa ter entre 3 e 20 caracteres. Use apenas letras, números, ponto ou underline.",
                None
            )

        if not validation_services.valid_linkedin_url(linkedin_url):
            return (
                False,
                "O LinkedIn precisa estar no formato https://www.linkedin.com/in/seu-perfil",
                None
            )

        password_message = validation_services.password_error_message(password)
        if password_message is not None:
            return False, password_message, None

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
            (email,)
        )
        email_registered = bool(self.cursor.fetchone()[0])

        if email_registered:
            return False, "Esse e-mail já foi cadastrado. Prossiga para o login.", None

        self.cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM users
                WHERE LOWER(username) = LOWER(?)
            )
            """,
            (username,)
        )
        username_registered = bool(self.cursor.fetchone()[0])

        if username_registered:
            return False, "Esse username já está em uso.", None

        password_hash = security_utils_service.hash_value(password)

        self.cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                username,
                linkedin_url,
                password
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, username, linkedin_url, password_hash)
        )

        self.connection.commit()

        user_id = self.cursor.lastrowid

        return True, "Cadastro realizado!", user_id

    def get_user_profile(self, user_id: int) -> User | None:
        """
        Busca os dados do perfil do usuário.
        """
        self.cursor.execute(
            """
            SELECT name, email, username, linkedin_url
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        user = self.cursor.fetchone()

        if user is None:
            return None

        name, email, username, linkedin_url = user

        return User(
            user_id=user_id,
            name=name,
            email=email,
            username=username or "",
            linkedin_url=linkedin_url
        )

    def update_user_name(self, user_id: int, new_name: str):
        """
        Atualiza o nome do usuário.
        """
        new_name = validation_services.normalize_name(new_name)

        if not validation_services.valid_name_users(new_name):
            return False, "O nome precisa ter pelo menos 2 caracteres, no máximo 50 caracteres e não pode conter números."

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
            (user_id,)
        )
        user_exists = bool(self.cursor.fetchone()[0])

        if not user_exists:
            return False, "Usuário não encontrado."

        self.cursor.execute(
            """
            UPDATE users
            SET name = ?
            WHERE user_id = ?
            """,
            (new_name, user_id)
        )

        self.connection.commit()

        return True, "Nome alterado com sucesso."

    def update_username(self, user_id: int, new_username: str):
        """
        Atualiza o username do usuário.

        O username é obrigatório, único e normalizado para minúsculas.
        """
        new_username = validation_services.normalize_username(new_username)

        if not validation_services.valid_username(new_username):
            return (
                False,
                "O username é obrigatório e precisa ter entre 3 e 20 caracteres. Use apenas letras, números, ponto ou underline."
            )

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
            (user_id,)
        )
        user_exists = bool(self.cursor.fetchone()[0])

        if not user_exists:
            return False, "Usuário não encontrado."

        self.cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM users
                WHERE LOWER(username) = LOWER(?)
                AND user_id != ?
            )
            """,
            (new_username, user_id)
        )
        username_registered = bool(self.cursor.fetchone()[0])

        if username_registered:
            return False, "Esse username já está em uso."

        self.cursor.execute(
            """
            UPDATE users
            SET username = ?
            WHERE user_id = ?
            """,
            (new_username, user_id)
        )

        self.connection.commit()

        return True, "Username alterado com sucesso."

    def update_linkedin_url(self, user_id: int, linkedin_url: str):
        """
        Atualiza o link do LinkedIn do usuário.

        O LinkedIn é opcional, mas se informado precisa seguir o formato validado.
        """
        linkedin_url = linkedin_url.strip()

        if not validation_services.valid_linkedin_url(linkedin_url):
            return False, "O LinkedIn precisa estar no formato https://www.linkedin.com/in/seu-perfil"

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
            (user_id,)
        )
        user_exists = bool(self.cursor.fetchone()[0])

        if not user_exists:
            return False, "Usuário não encontrado."

        self.cursor.execute(
            """
            UPDATE users
            SET linkedin_url = ?
            WHERE user_id = ?
            """,
            (linkedin_url, user_id)
        )

        self.connection.commit()

        return True, "LinkedIn alterado com sucesso."

    def change_user_password(self, user_id: int, current_password: str, new_password: str):
        """
        Altera a senha do usuário.
        """
        self.cursor.execute(
            """
            SELECT password
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        user = self.cursor.fetchone()

        if user is None:
            return False, "Usuário não encontrado."

        saved_password = user[0]

        if not security_utils_service.verify_value(current_password, saved_password):
            return False, "A senha atual está incorreta."

        password_message = validation_services.password_error_message(new_password)
        if password_message is not None:
            return False, password_message

        if security_utils_service.verify_value(new_password, saved_password):
            return False, "A nova senha deve ser diferente da senha atual."

        new_password_hash = security_utils_service.hash_value(new_password)

        self.cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE user_id = ?
            """,
            (new_password_hash, user_id)
        )

        self.connection.commit()

        return True, "Senha alterada com sucesso!"

    def delete_user_account(self, user_id: int):
        """
        Deleta a conta do usuário.
        """
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
            (user_id,)
        )
        user_exists = bool(self.cursor.fetchone()[0])

        if not user_exists:
            return False, "Usuário não encontrado."

        self.cursor.execute(
            """
            DELETE FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        self.connection.commit()

        return True, "Conta deletada com sucesso."

    def check_user_name(self, user_id: int) -> str | None:
        """
        Busca apenas o nome do usuário.
        """
        self.cursor.execute(
            """
            SELECT name
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        user = self.cursor.fetchone()

        if user is None:
            return None

        return validation_services.normalize_name(user[0])


user_services = UserServices()