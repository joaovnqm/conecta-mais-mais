import re


def valid_name(name: str) -> bool:
    return len(name.strip()) >= 3


def valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.fullmatch(pattern, email.strip()) is not None


def valid_password(password: str) -> bool:
    pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
    return re.fullmatch(pattern, password) is not None


def valid_recovery_word(recovery_word: str) -> bool:
    pattern = r'^[A-Za-z]+$'
    return re.fullmatch(pattern, recovery_word.strip()) is not None