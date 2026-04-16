import sqlite3
from datetime import datetime, timedelta
from random import randint

from services.security import hash_value, verify_value
from services.send_email import send_recovery_email
from services.validations import password_error_message

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS password_reset_codes (
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL
)
""")
connection.commit()


def generate_numeric_code() -> str:
    return f"{randint(0, 999999):06d}"


def request_password_reset(email: str):
    email = email.strip().lower()

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    user_exists = bool(cursor.fetchone()[0])

    if not user_exists:
        return False, "E-mail não encontrado."

    code = generate_numeric_code()
    code_hash = hash_value(code)
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

    cursor.execute(
        "DELETE FROM password_reset_codes WHERE email = ?",
        (email,)
    )

    cursor.execute(
        "INSERT INTO password_reset_codes (email, code_hash, expires_at) VALUES (?, ?, ?)",
        (email, code_hash, expires_at)
    )
    connection.commit()

    send_recovery_email(email, code)

    return True, "Código enviado para o e-mail."


def reset_password(email: str, code: str, new_password: str):
    email = email.strip().lower()
    code = code.strip()

    password_message = password_error_message(new_password)
    if password_message is not None:
        return False, password_message

    cursor.execute(
        "SELECT code_hash, expires_at FROM password_reset_codes WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()

    if row is None:
        return False, "Nenhum código de recuperação foi solicitado para este e-mail."

    code_hash, expires_at = row

    if datetime.now() > datetime.fromisoformat(expires_at):
        cursor.execute(
            "DELETE FROM password_reset_codes WHERE email = ?",
            (email,)
        )
        connection.commit()
        return False, "O código de recuperação expirou."

    if not verify_value(code, code_hash):
        return False, "Código inválido."

    new_password_hash = hash_value(new_password)

    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password_hash, email)
    )

    cursor.execute(
        "DELETE FROM password_reset_codes WHERE email = ?",
        (email,)
    )
    connection.commit()

    return True, "Senha alterada com sucesso."