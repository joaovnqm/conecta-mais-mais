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

