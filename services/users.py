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

"""
Cria a tabela de usuários caso ela ainda não exista
user_id: identificador único do usuário
name: nome do usuário
email: e-mail do usuário
password: senha criptografada do usuário
"""
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")
connection.commit()

"""
Função de login
    1. Padroniza o e-mail
    2. Procura o usuário no banco de dados
    3. Verifica se a senha digitada bate com a senha criptografada salva
    4. Retorna sucesso ou erro
"""
def login(email, password):
    email = email.strip().lower()

    cursor.execute(
        "SELECT name, password, user_id FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()

    # Se não encontrou esse e-mail, retorna mensagem de erro
    if user is None:
        return False, "Usuário não encontrado.", None, None

    name, saved_password, user_id = user

    # Verifica se a senha digitada corresponde ao hash salvo
    if not verify_value(password, saved_password):
        return False, "Senha incorreta.", None, None

    # Remove espaços extras do nome
    name = normalize_name(name)

    return True, "Login realizado com sucesso!", name, user_id

"""
Função de cadastro
    1. Padroniza o nome e e-mail
    2. Valida o nome, e-mail e senha
    3. Verifica se o e-mail já está cadastrado
    4. Criptografa a senha
    5. Salva o novo usuário no banco de dados
"""
def register(name, email, password):
    name = name.strip()
    email = email.strip().lower()

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

"""
Função que busca os dados do perfil do usuário com base no id. Retorna nome e e-mail em formato de dicionário
"""
def get_user_profile(user_id: int):
    # Executa uma consulta no banco para buscar o nome e o -email do usuário que possui o id recebido
    cursor.execute(
        "SELECT name, email FROM users WHERE user_id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    
    # Se não encontrou usuário, retorna None
    if user is None:
        return None

    # Se encontrou o usuário, name recebe nome, email recebe email
    name, email = user
    
    # Retorna um dicionário com os dados do perfil. O nome é normalizado para remover espaços extras
    return {
        "name": normalize_name(name),
        "email": email,
    }

"""
Função que atualiza o nome do usuário
    1. Padroniza o novo nome
    2. Valida se o nome é permitido
    3. Verifica se o usuário existe
    4. Atualiza o nome no banco
"""
def update_user_name(user_id: int, new_name: str):
    # Normaliza o nome, remove espaços no começo e no fim e também reduz os espaços duplicados no meio
    new_name = normalize_name(new_name)

    # Verifica se o nome do usuário é válido
    if not valid_name_users(new_name):
        return False, "O nome precisa ter pelo menos 2 caracteres e não pode conter números."

    # Verifica se existe um usuário com esse user_id
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
        (user_id,)
    )
    user_exists = bool(cursor.fetchone()[0])

    # Se usuário não existir, retorna mensagem
    if not user_exists:
        return False, "Usuário não encontrado."

    # Atualiza o nome do usuário no banco de dados
    cursor.execute(
        "UPDATE users SET name = ? WHERE user_id = ?",
        (new_name, user_id)
    )
    connection.commit()
    
    # Retorna mensagem de sucesso
    return True, "Nome alterado com sucesso."


"""
Função que altera a senha do usuário
    1. Busca a senha atual no banco
    2. Verifica se o usuário existe
    3. Confere se a senha atual digitada está correta
    4. Valida a nova senha
    5. Impede que a nova senha seja igual à antiga
    6. Criptografa e salva a nova senha
"""
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

    # Confere a senha atual digitada pelo usuário
    if not verify_value(current_password, saved_password):
        return False, "A senha atual está incorreta"

    # Valida a nova senha
    password_message = password_error_message(new_password)
    if password_message is not None:
        return False, password_message

    # Impede que a nova senha seja igual à senha atual
    if verify_value(new_password, saved_password):
        return False, "A nova senha deve ser diferente da senha atual"

    # Criptografa a nova senha
    new_password_hash = hash_value(new_password)

    cursor.execute(
        "UPDATE users SET password = ? WHERE user_id = ?",
        (new_password_hash, user_id)
    )
    connection.commit()

    return True, "Senha alterada com sucesso!"

"""
Função que deleta a conta do usuário
    1. Verifica se o usuário existe
    2. Remove o usuário da tabela users
    3. Confirma a alteração no banco
"""
def delete_user_account(user_id: int):
    # Verifica se o usuário existe antes de tentar deletar
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
        (user_id,)
    )
    user_exists = bool(cursor.fetchone()[0])

    # Se o usuário não existir, interrompe a exclusão
    if not user_exists:
        return False, "Usuário não encontrado."

    # Deleta o usuário da tabela de users com base no id
    cursor.execute(
        "DELETE FROM users WHERE user_id = ?",
        (user_id,)
    )
    connection.commit()
    
    # Retorna mensagem de sucesso
    return True, "Conta deletada com sucesso."

"""
Função auxiliar que busca o nome do usuário. É usada quando outra tela só precisa exibir o nome do usuário. Ex: Nome do usuário no "meu perfil" 
"""
def check_user_name(user_id: int):
    # Executa a consulta no banco procurando o nome
    cursor.execute(
        "SELECT name FROM users WHERE user_id = ?",
        (user_id,)
    )
    # Pega o primeiro resultado que encontrar
    user = cursor.fetchone()

    # Se não encontrar nenhum usuário com esse id, retorna None
    if user is None:
        return None

    #user[0] é o nome retornado pela consulta.
    #normalize_name remove espaços extras e padroniza o nome
    return normalize_name(user[0])
