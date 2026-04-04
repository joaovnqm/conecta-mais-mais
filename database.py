import sqlite3
import re

connection = sqlite3.connect("conecta++.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name NOT NULL, email NOT NULL, password NOT NULL,"
               "recovery_word NOT_NULL, interest, friends, pending_friend_request, blocked_users, confirmed_events, created_events)")


def valid_email(email):
    default = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.fullmatch(default, email) is not None


def valid_password(password):
    default = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
    return re.fullmatch(default, password) is not None


def valid_recovery_word(recovery_word):
    default = r'^[A-Za-z]+$'
    return re.fullmatch(default, recovery_word) is not None


def login(email, password):
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    account_password = str(cursor.fetchone()[0])
    if str(password) == account_password:
        cursor.execute("SELECT name FROM users WHERE email = ?", (email,))
        name = str(cursor.fetchone()[0])
        print("Login realizado com sucesso!")
        return name

    else:
        print("Login não realizado.")


def register(name, email, password, recovery_word):
    if valid_email(email) != True:
        return "Esse e-mail é inválido!"
    else:
        if valid_password(password) != True:
            return "Essa senha é inválida!"
        else:
            if valid_recovery_word(recovery_word) != True:
                return "Esse campo é inválido"
            else:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)", (email,))
                email_registered = bool(cursor.fetchone()[0])
                if email_registered == True:
                    print("Esse e-mail já foi cadastrado. Prossiga para o login.")
                    return False

                else:
                    cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                        None, name, email, password, recovery_word, None, None, None, None, None, None))
                    connection.commit()
                    print("Cadastro realizado!")
