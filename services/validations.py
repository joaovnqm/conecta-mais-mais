import re
from datetime import datetime

def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())

def valid_name_users(name: str) -> bool:
    normalized_name = normalize_name(name)
    pattern = r'^[A-Za-zÀ-ÿ ]{2,}$'
    return re.fullmatch(pattern, name.strip()) is not None

def valid_name_events(name: str) -> bool:
    pattern = r'^[A-Za-zÀ-ÿ0-9 ]{2,}$'
    return re.fullmatch(pattern, name.strip()) is not None

def valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.fullmatch(pattern, email.strip()) is not None

def password_error_message(password: str) -> str | None:
    if len(password) < 8:
        return "A senha precisa ter pelo menos 8 caracteres."
    if not any(char.isupper() for char in password):
        return "A senha precisa conter pelo menos uma letra maiúscula."
    if not any(char.islower() for char in password):
        return "A senha precisa conter pelo menos uma letra minúscula."
    if not any(char.isdigit() for char in password):
        return "A senha precisa conter pelo menos um número."
    return None

def valid_password(password: str) -> bool:
    return password_error_message(password) is None

def valid_date(date: str) -> bool:
    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def valid_hour(hour: str) -> bool:
    try:
        datetime.strptime(hour, "%H:%M")
        return True
    except ValueError:
        return False