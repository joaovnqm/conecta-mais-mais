import sqlite3
from validations import valid_email, valid_password, valid_recovery_word
from security import hash_value, verify_value

connection = sqlite3.connect("conecta++.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name NOT NULL, email NOT NULL, password NOT NULL,"
               "recovery_word NOT_NULL, interest, friends, pending_friend_request, blocked_users, confirmed_events, created_events)")


def login(email, password):
    email = email.strip().lower()

    cursor.execute(
        "SELECT name, password FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()

    if user is None:
        return False, "Usuário não encontrado.", None

    name, saved_password = user

    if not verify_value(password, saved_password):
        return False, "Senha incorreta.", None

    return True, "Login realizado com sucesso!", name


def register(name, email, password, recovery_word):
    name = name.strip()
    email = email.strip().lower()
    recovery_word = recovery_word.strip()

    if len(name) < 2:
        return False, "O nome precisa ter pelo menos 2 caracteres."

    if not valid_email(email):
        return False, "Esse e-mail é inválido!"

    if not valid_password(password):
        return False, "Essa senha é inválida!"

    if not valid_recovery_word(recovery_word):
        return False, "Esse campo é inválido."

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    if email_registered:
        return False, "Esse e-mail já foi cadastrado. Prossiga para o login."

    password_hash = hash_value(password)
    recovery_word_hash = hash_value(recovery_word)

    cursor.execute(
        "INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (None, name, email, password_hash, recovery_word_hash,
         None, None, None, None, None, None)
    )
    connection.commit()

    return True, "Cadastro realizado!"
