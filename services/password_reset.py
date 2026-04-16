import sqlite3
from datetime import datetime, timedelta, timedelta
from random import randint

from services.security import hash_value, verify_value
from services.send_email import send_recovery_email


connection = sqlite3.connect("connecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS password_reset_codes (
    email TEXT NOT NULL
    code_hash TEXT NOT NULL
    expires_at TEXT NOT NULL
)               
"""
               )
connection.commit()

# Função para gerar código numérico de 6 dígitos

def generate_numeric_code() -> str:
    return f"{randint(0, 999999):06d}"

# Função para solicitar redefinição de senha

def request_password_reset(email: str) -> None:
    email = email.strip().lower()
    
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users, WHERE email = ?)",
        (email,)
        )
    user_exists = bool(cursor.fetchone()[0])
    
    if not user_exists:
        return False, "E-mail não encontrado."
    
    code = generate_numeric_code()
    code_hash = hash_value(code)
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    cursor.execute(
        "DELETE FROM password_reset_codes WHERE email = ?"
        (email,)
    )
    cursor.execute(
        "INSERT INTO password_reset_codes (email, code_hash, expires_at) VALUES (?, ?, ?)",
        (email, code_hash, expires_at)
    )
    connection.commit()
    
    send_recovery_email(email, code)
    
    return True, "Código enviado para o e-mail."