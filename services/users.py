import sqlite3
from services.validations import (
    normalize_name,
    valid_name_users,
    valid_email,
    password_error_message,
)
from services.security import hash_value, verify_value

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")
connection.commit()


def login(email, password):
    email = email.strip().lower()

    cursor.execute(
        "SELECT name, password, user_id FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()

    if user is None:
        return False, "Usuário não encontrado.", None, None

    name, saved_password, user_id = user

    if not verify_value(password, saved_password):
        return False, "Senha incorreta.", None, None

    name = normalize_name(name)

    return True, "Login realizado com sucesso!", name, user_id


def register(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not valid_name_users(name):
        return False, "O nome precisa ter pelo menos 2 caracteres e não pode conter números.", None

    if not valid_email(email):
        return False, "Esse e-mail é inválido!", None

    password_message = password_error_message(password)
    if password_message is not None:
        return False, password_message, None

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    if email_registered:
        return False, "Esse e-mail já foi cadastrado. Prossiga para o login.", None

    password_hash = hash_value(password)

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    connection.commit()

    user_id = cursor.lastrowid

    return True, "Cadastro realizado!", user_id

# Função que checa o nome do usuário com base em seu ID.
def check_user_name(user_id: int) -> str:
    cursor.execute(
        "SELECT name FROM users WHERE user_id = ?",
        (user_id,)
    )
    name = cursor.fetchone()
    name = name[0]
    return name