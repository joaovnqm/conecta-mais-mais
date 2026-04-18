import sqlite3
from services.validations import (
    normalize_name,
    valid_name_users,
    valid_email,
    password_error_message,
)
from services.security import hash_value, verify_value

# Conexão com o banco de dados

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Cria a tabela de usuários, caso ainda não exista

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")
connection.commit()

# Função de login

def login(email, password):
    email = email.strip().lower()

    cursor.execute(
        "SELECT name, password, user_id FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()

    # Se não encontrou usuário com esse e-mail, retorna mensagem de erro
    if user is None:
        return False, "Usuário não encontrado.", None, None

    name, saved_password, user_id = user
    
    # Verifica se a senha digitada corresponde ao hash salvo
    if not verify_value(password, saved_password):
        return False, "Senha incorreta.", None, None
    
    # Normaliza o nome para remover espaços extras
    name = normalize_name(name)

    return True, "Login realizado com sucesso!", name, user_id

# Função de registro

def register(name, email, password):
    name = name.strip()
    email = email.strip().lower()
    recovery_word = recovery_word.strip()
    
    # Valida o nome do usuário
    if not valid_name_users(name):
        return False, "O nome precisa ter pelo menos 2 caracteres e não pode conter números.", None
    
    # Valida o e-mail do usuário
    if not valid_email(email):
        return False, "Esse e-mail é inválido!", None
    
    # Valida a senha do usuário e retorna mensagem de erro se houver erro.
    password_message = password_error_message(password)
    if password_message is not None:
        return False, password_message, None

    # Verifica se já existe usuário com esse e-mail cadastrado
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    if email_registered:
        return False, "Esse e-mail já foi cadastrado. Prossiga para o login.", None

    # Criptografa a senha antes de salvar
    password_hash = hash_value(password)

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    connection.commit()
    
    # Obtém o ID do usuário recém-criado
    user_id = cursor.lastrowid

    return True, "Cadastro realizado!", user_id

# Função que altera a senha do usuário
def change_user_password(user_id, current_password: str, new_password: str):
    cursor.execute(
        "SELECT password FROM users WHERE user_id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    
    # Verfica se o usuário existe
    if user is None:
        return False, "Usuário não encontrado"
    
    saved_password = user[0]
    
    # Confere a senha atual
    if not verify_value(current_password, saved_password):
        return False, "A senha atual está incorreta"
    
    # Valida a nova senha
    password_message = password_error_message(new_password)
    if password_message is not None:
        return False, password_message
    
    # Impede que a nova senha seja igual à senha atual
    if verify_value(new_password, saved_password):
        return False, "A nova senha deve ser diferente da senha atual"
    
    # Criptografia a nova senha
    new_password_hash = hash_value(new_password)
    
    cursor.execute(
        "UPDATE users SET password = ? WHERE user_id = ?",
        (new_password_hash, user_id)
    )
    connection.commit()
    
    return True, "Senha alterada com sucesso!"
