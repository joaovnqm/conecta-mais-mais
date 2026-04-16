import sqlite3
from datetime import datetime, timedelta
from random import randint

from services.security import hash_value, verify_value
from services.send_email import send_verification_email
from services.validations import password_error_message

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS verification_codes (
    email TEXT NOT NULL,
    purpose TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    PRIMARY KEY (email, purpose)
)
""")
connection.commit()


def generate_numeric_code() -> str:
    return f"{randint(0, 999999):06d}"


def _send_code(email: str, purpose: str):
    code = generate_numeric_code()
    code_hash = hash_value(code)
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

    cursor.execute(
        "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )

    cursor.execute(
        "INSERT INTO verification_codes (email, purpose, code_hash, expires_at) VALUES (?, ?, ?, ?)",
        (email, purpose, code_hash, expires_at)
    )
    connection.commit()

    send_verification_email(email, code, purpose)
    return True, "Código enviado para o e-mail."


def request_registration_code(email: str):
    email = email.strip().lower()

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    if email_registered:
        return False, "Esse e-mail já foi cadastrado."

    return _send_code(email, "register")


def request_password_reset(email: str):
    email = email.strip().lower()

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    user_exists = bool(cursor.fetchone()[0])

    if not user_exists:
        return False, "E-mail não encontrado."

    return _send_code(email, "reset_password")


def verify_code(email: str, code: str, purpose: str):
    email = email.strip().lower()
    code = code.strip()

    cursor.execute(
        "SELECT code_hash, expires_at FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )
    row = cursor.fetchone()

    if row is None:
        return False, "Nenhum código válido foi encontrado para este e-mail."

    code_hash, expires_at = row

    if datetime.now() > datetime.fromisoformat(expires_at):
        cursor.execute(
            "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
            (email, purpose)
        )
        connection.commit()
        return False, "O código expirou."

    if not verify_value(code, code_hash):
        return False, "Código inválido."

    cursor.execute(
        "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )
    connection.commit()

    return True, "Código validado com sucesso."


def finalize_password_reset(email: str, new_password: str):
    email = email.strip().lower()

    password_message = password_error_message(new_password)
    if password_message is not None:
        return False, password_message

    new_password_hash = hash_value(new_password)

    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password_hash, email)
    )
    connection.commit()

    return True, "Senha alterada com sucesso."