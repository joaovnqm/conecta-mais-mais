import re
from datetime import datetime

def valid_name_users(name: str) -> bool:
    pattern = r'^[A-Za-zÀ-ÿ ]{2,}$'
    return re.fullmatch(pattern, name.strip()) is not None

def valid_name_events(name: str) -> bool:
    pattern = r'^[A-Za-zÀ-ÿ0-9 ]{2,}$'
    return re.fullmatch(pattern, name.strip()) is not None

def valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.fullmatch(pattern, email.strip()) is not None

def valid_password(password: str) -> bool:
    pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
    return re.fullmatch(pattern, password) is not None

def valid_recovery_word(recovery_word: str) -> bool:
    pattern = r'^[A-Za-z]+$'
    return re.fullmatch(pattern, recovery_word) is not None

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