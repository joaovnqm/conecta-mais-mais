import re
from datetime import datetime

def normalize_name(name: str) -> str:
    """
    Função que normaliza o nome, removendo espaços extras e padronizando o nome. Ela remove espaços extras no início, 
    no final e entre as palavras, deixando apenas um espaço entre as palavras. Isso garante que o nome seja armazenado de 
    forma consistente no banco de dados.
    """
    return " ".join(name.strip().split())

def valid_name_users(name: str) -> bool:
    """
    Função que valida nomes de usuários. Ela verifica se o nome tem pelo menos 2 caracteres, e se contém apenas letras 
    (incluindo acentos) e espaços. Números e caracteres especiais não são permitidos. A função retorna True se o nome for válido, 
    e False caso contrário.
    """
    normalized_name = normalize_name(name)
    pattern = r'^[A-Za-zÀ-ÿ ]{2,50}$'
    return re.fullmatch(pattern, normalized_name) is not None

def valid_name_events(name: str) -> bool:
    """
    Função que valida nomes de eventos. Ela verifica se o nome tem pelo menos 2 caracteres, e se contém apenas letras 
    (incluindo acentos), números, espaços e alguns caracteres especiais comuns em nomes de eventos. A função retorna True 
    se o nome for válido, e False caso contrário.
    """
    normalized_name = normalize_name(name)
    pattern = r'^[A-Za-zÀ-ÿ0-9 \-_.,()\'"&@!]{2,50}$'
    return re.fullmatch(pattern, normalized_name) is not None

def valid_email(email: str) -> bool:
    """
    Função que valida o formato do e-mail. Ela verifica se o e-mail segue um formato básico de e-mail, com um nome de usuário,
    um símbolo "@" e um domínio. A função retorna True se o e-mail for válido, e False caso contrário.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.fullmatch(pattern, email.strip()) is not None

def password_error_message(password: str) -> str | None:
    """
    Função que valida a senha e retorna uma mensagem de erro específica caso a senha não atenda aos critérios de segurança.
    Os critérios são: pelo menos 8 caracteres, pelo menos uma letra maiúscula, pelo menos uma letra minúscula, e pelo menos um número. 
    Se a senha atender a todos os critérios, a função retorna None, indicando que a senha é válida. Se a senha não atender a algum 
    critério, a função retorna uma mensagem de erro específica para o critério que não foi atendido.
    """
    if len(password) < 8:
        return "A senha precisa ter pelo menos 8 caracteres."
    if not any(char.isupper() for char in password):
        return "A senha precisa conter pelo menos uma letra maiúscula."
    if not any(char.islower() for char in password):
        return "A senha precisa conter pelo menos uma letra minúscula."
    if not any(char.isdigit() for char in password):
        return "A senha precisa conter pelo menos um número."
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
        return "A senha precisa conter pelo menos um caractere especial."
    return None

def valid_password(password: str) -> bool:
    """
    Função booleana para validar senha. Ela reaproveita a função password_error_message. Se não houver mensagem de erro, a senha 
    é válida.
    """
    return password_error_message(password) is None

def valid_date(date: str) -> bool:
    """
    Função que valida datas no formato dd-mm-aaaa.
    """
    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def valid_hour(hour: str) -> bool:
    """
    Função que valida horas no formato hh:mm.
    """
    try:
        datetime.strptime(hour, "%H:%M")
        return True
    except ValueError:
        return False