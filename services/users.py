import sqlite3
from services.validations import valid_name_users, valid_email, valid_password, valid_recovery_word
from services.security import hash_value, verify_value

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name NOT NULL, " \
                "email NOT NULL, password NOT NULL, recovery_word NOT NULL)")

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
        return False, "Senha incorreta.", None

    return True, "Login realizado com sucesso!", name, user_id

def register(name, email, password, recovery_word):
    name = name.strip()
    email = email.strip().lower()
    recovery_word = recovery_word.strip()

    if not valid_name_users(name):
        return False, "O nome precisa ter pelo menos 2 caracteres e não pode conter números.", None

    if not valid_email(email):
        return False, "Esse e-mail é inválido!", None

    if not valid_password(password):
        return False, "Essa senha é inválida!", None

    if not valid_recovery_word(recovery_word):
        return False, "Esse campo é inválido.", None

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
        "INSERT INTO users VALUES(?, ?, ?, ?, ?)",
        (None, name, email, password_hash, recovery_word_hash,)
    )
    connection.commit()

    cursor.execute(
    "SELECT user_id FROM users WHERE email = ?",
    (email,)
    )
    user = cursor.fetchone()
    user_id = user

    return True, "Cadastro realizado!", user_id