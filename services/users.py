import sqlite3
from services.validations import (
    valid_name_users,
    valid_email,
    password_error_message,
    recovery_word_error_message,
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
    password TEXT NOT NULL,
    recovery_word TEXT NOT NULL
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

    return True, "Login realizado com sucesso!", name, user_id


def register(name, email, password, recovery_word):
    name = name.strip()
    email = email.strip().lower()
    recovery_word = recovery_word.strip()

    if not valid_name_users(name):
        return False, "O nome precisa ter pelo menos 2 caracteres e não pode conter números.", None

    if not valid_email(email):
        return False, "Esse e-mail é inválido!", None

    password_message = password_error_message(password)
    if password_message is not None:
        return False, password_message, None

    recovery_word_message = recovery_word_error_message(recovery_word)
    if recovery_word_message is not None:
        return False, recovery_word_message, None

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    if email_registered:
        return False, "Esse e-mail já foi cadastrado. Prossiga para o login.", None

    password_hash = hash_value(password)
    recovery_word_hash = hash_value(recovery_word)

    cursor.execute(
        "INSERT INTO users (name, email, password, recovery_word) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, recovery_word_hash)
    )
    connection.commit()

    user_id = cursor.lastrowid

    return True, "Cadastro realizado!", user_id