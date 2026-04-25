import re
from datetime import datetime
"""
Função que normaliza o nome digitado pelo usuário
    1. Remove espaços no começo e no fim
    2. Reduz vários espaços internos para apenas um 
"""
def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())

"""
Função que valida nomes de usuário
    1. O nome deve conter pelo menos 2 caracteres
    2. Só pode conter letras, acentos e espaços, números e símbolos não são permitidos
"""
def valid_name_users(name: str) -> bool:
    # Normaliza o nome antes de validar
    normalized_name = normalize_name(name)
    
    # A-Za-zÀ-ÿ -> letras comuns e acentuadas, espaços são permitidos e pelo menos 2 caracteres
    pattern = r'^[A-Za-zÀ-ÿ ]{2,}$'
    # Retorna True se o nome estiver no formato correto, False caso contrário
    return re.fullmatch(pattern, name.strip()) is not None

"""
Função que valida nomes de eventos.
    1. O nome deve ter pelo menos 2 caracteres
    2. Pode conter letras, números, acentos e espaços
"""
def valid_name_events(name: str) -> bool:
    pattern = r'^[A-Za-zÀ-ÿ0-9 \-_.,()\'"&@!]{2,}$'
    return re.fullmatch(pattern, name.strip()) is not None

"""
Função que valida e-mails

"""
def valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.fullmatch(pattern, email.strip()) is not None

"""
Função que verifica a senha e retorna mensagem exata do erro
    1. Pelo menos 8 caracteres
    2. Pelo menos uma letra maiúscula
    3. Pelo menos uma letra minúscula
    4. Pelo menos um número
Se a senha estiver correta, retorna None
"""
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

"""
Função booleana para validar senha. Ela reaproveita a função password_error_message. Se não houver mensagem de erro, a senha é válida.
"""
def valid_password(password: str) -> bool:
    return password_error_message(password) is None


# Função que valida datas no formato dd-mm-aaaa.
def valid_date(date: str) -> bool:
    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        return False

# Função que valida horas no formato hh:mm
def valid_hour(hour: str) -> bool:
    try:
        datetime.strptime(hour, "%H:%M")
        return True
    except ValueError:
        return False