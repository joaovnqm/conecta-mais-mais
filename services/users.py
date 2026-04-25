import sqlite3
from services.validations import normalize_name, valid_name_users, valid_email, password_error_message
from services.security import hash_value, verify_value

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

"""
O seguinte comando query cria a tabela de usuários caso ela ainda não exista:
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

def login(email, password):
    """
    Essa função é responsável por realizar o login do usuário. Ela recebe o e-mail e a senha digitados, padroniza o e-mail, 
    busca o usuário no banco de dados, verifica se o usuário existe, confere se a senha digitada corresponde ao hash salvo no banco,
    e retorna mensagens de erro específicas caso haja algum problema. Se o login for bem-sucedido, a função retorna True, mensagem de
    sucesso, nome do usuário e id do usuário. O nome do usuário é normalizado para remover espaços extras. 
    """
    email = email.strip().lower()

    cursor.execute(
        "SELECT name, password, user_id FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()

    if user is None:
        return False, "Usuário não encontrado.", None, None

    name, saved_password, user_id = user

    if not verify_value(password, saved_password):
        return False, "Senha incorreta.", None, None

    name = normalize_name(name)

    return True, "Login realizado com sucesso!", name, user_id

def register(name, email, password):
    """
    Essa função é responsável por realizar o cadastro do usuário. Ela recebe o nome, e-mail e senha digitados, padroniza o nome e o e-mail,
    valida o nome, e-mail e senha, verifica se já existe um usuário com o mesmo e-mail, criptografa a senha, salva o usuário no banco
    de dados, e retorna mensagens de erro específicas caso haja algum problema. Se o cadastro for bem-sucedido, a função retorna True, 
    mensagem de sucesso e o id do usuário recém-criado. O nome do usuário é normalizado para remover espaços extras.
    """
    name = name.strip()
    email = email.strip().lower()

    if not valid_name_users(name):
        return False, "O nome precisa ter pelo menos 2 caracteres e não pode conter números.", None

    if not valid_email(email):
        return False, "Esse e-mail é inválido!", None

    password_message = password_error_message(password)
    if password_message is not None:
        return False, password_message, None

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    if email_registered:
        return False, "Esse e-mail já foi cadastrado. Prossiga para o login.", None

    password_hash = hash_value(password)

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    connection.commit()

    user_id = cursor.lastrowid

    return True, "Cadastro realizado!", user_id

def get_user_profile(user_id: int):
    """
    Função que busca os dados do perfil do usuário com base no id. Retorna nome e e-mail em formato de dicionário
    """
    cursor.execute(
        "SELECT name, email FROM users WHERE user_id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    if user is None:
        return None

    name, email = user

    return {
        "name": normalize_name(name),
        "email": email,
    }

def update_user_name(user_id: int, new_name: str):
    """
    Essa função é responsável por atualizar o nome do usuário. Ela recebe o id do usuário e o novo nome, normaliza o novo nome,
    valida o novo nome, verifica se o usuário existe, atualiza o nome do usuário no banco de dados, e retorna mensagens de erro 
    específicas caso haja algum problema. Se a atualização for bem-sucedida, a função retorna True e uma mensagem de sucesso. 
    O nome do usuário é normalizado para remover espaços extras.
    """
    new_name = normalize_name(new_name)

    if not valid_name_users(new_name):
        return False, "O nome precisa ter pelo menos 2 caracteres e não pode conter números."

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
        (user_id,)
    )
    user_exists = bool(cursor.fetchone()[0])

    if not user_exists:
        return False, "Usuário não encontrado."

    cursor.execute(
        "UPDATE users SET name = ? WHERE user_id = ?",
        (new_name, user_id)
    )
    connection.commit()
    
    return True, "Nome alterado com sucesso."

def change_user_password(user_id, current_password: str, new_password: str):
    """
    Essa função é responsável por alterar a senha do usuário. Ela recebe o id do usuário, a senha atual e a nova senha,
    busca o usuário no banco de dados, verifica se o usuário existe, confere se a senha atual digitada corresponde ao hash salvo 
    no banco, valida a nova senha, impede que a nova senha seja igual à senha atual, criptografa a nova senha, atualiza a senha 
    do usuário no banco de dados, e retorna mensagens de erro específicas caso haja algum problema. Se a alteração for bem-sucedida,
    a função retorna True e uma mensagem de sucesso.
    """
    cursor.execute(
        "SELECT password FROM users WHERE user_id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    if user is None:
        return False, "Usuário não encontrado"

    saved_password = user[0]

    if not verify_value(current_password, saved_password):
        return False, "A senha atual está incorreta"

    password_message = password_error_message(new_password)
    if password_message is not None:
        return False, password_message

    if verify_value(new_password, saved_password):
        return False, "A nova senha deve ser diferente da senha atual"

    new_password_hash = hash_value(new_password)

    cursor.execute(
        "UPDATE users SET password = ? WHERE user_id = ?",
        (new_password_hash, user_id)
    )
    connection.commit()

    return True, "Senha alterada com sucesso!"

def delete_user_account(user_id: int):
    """
    Essa função é responsável por deletar a conta do usuário. Ela recebe o id do usuário, verifica se o usuário existe, deleta o usuário
    do banco de dados, e retorna mensagens de erro específicas caso haja algum problema. Se a exclusão for bem-sucedida, a 
    função retorna True e uma mensagem de sucesso. A função também garante que, ao deletar o usuário, todos os dados relacionados a 
    ele em outras tabelas (como eventos favoritados e interesses) sejam deletados automaticamente graças às chaves estrangeiras 
    com a cláusula ON DELETE CASCADE.
    """
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)",
        (user_id,)
    )
    user_exists = bool(cursor.fetchone()[0])

    if not user_exists:
        return False, "Usuário não encontrado."

    cursor.execute(
        "DELETE FROM users WHERE user_id = ?",
        (user_id,)
    )
    connection.commit()
    
    return True, "Conta deletada com sucesso."

def check_user_name(user_id: int):
    """
    Função auxiliar que busca o nome do usuário. É usada quando outra tela só precisa exibir o nome do usuário que criou um evento.
    Ex: Nome do usuário no "Criado por" dos eventos. Retorna o nome do usuário ou None caso o usuário não seja encontrado.
    """
    cursor.execute(
        "SELECT name FROM users WHERE user_id = ?",
        (user_id,)
    )
    user = cursor.fetchone()

    if user is None:
        return None

    return normalize_name(user[0])