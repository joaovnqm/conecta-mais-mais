import sqlite3
from datetime import datetime, timedelta
from random import randint

from services.security import hash_value, verify_value
from services.send_email import send_verification_email
from services.validations import password_error_message

# Cria conexão com o banco de dados
connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

"""
Cria a tabela que armazena os códigos de verificação enviados por e-mail
email: e-mail do usuário
purpose: finalidade do código register ou reset_password
code_hash: hash do código enviado
expires_at: data/hora de expiração do código
"""

cursor.execute("""
CREATE TABLE IF NOT EXISTS verification_codes (
    email TEXT NOT NULL,
    purpose TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    PRIMARY KEY (email, purpose)
)
""")
connection.commit()

def generate_numeric_code() -> str:
    """
    Essa função gera um código numérico de 6 dígitos para verificação por e-mail. O código é gerado aleatoriamente usando a função randint,
    e é formatado para garantir que tenha exatamente 6 dígitos, preenchendo com zeros à esquerda se necessário.
    """
    return f"{randint(0, 999999):06d}"

def _send_code(email: str, purpose: str):
    """
    Essa função é responsável por gerar um código de verificação, 
    salvar o hash do código no banco de dados com a finalidade e o e-mail,
    e enviar o código para o e-mail do usuário. Ela também remove qualquer código 
    anterior para o mesmo e-mail e finalidade antes de salvar o novo código, garantindo que 
    apenas um código válido exista para cada combinação de e-mail e finalidade. O código gerado tem uma validade de 10 minutos.
    """
    code = generate_numeric_code()
    code_hash = hash_value(code)
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    cursor.execute(
        "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )

    cursor.execute(
        "INSERT INTO verification_codes (email, purpose, code_hash, expires_at) VALUES (?, ?, ?, ?)",
        (email, purpose, code_hash, expires_at)
    )

    connection.commit()

    send_verification_email(email, code, purpose)
    return True, "Código enviado para o e-mail."

def request_registration_code(email: str):
    """
    Essa função solicita um código para registro. Ela verifica se o e-mail já existe no sistema, e se não existir, 
    envia um código de verificação para o e-mail do usuário para que ele possa prosseguir com o registro. 
    Se o e-mail já estiver registrado, a função retorna uma mensagem de erro informando que o e-mail já foi cadastrado.
    """
    email = email.strip().lower()

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    if email_registered:
        return False, "Esse e-mail já foi cadastrado."

    return _send_code(email, "register")

def request_password_reset(email: str):
    """
    Essa função solicita um código para redefinição de senha. Ela verifica se o e-mail existe no sistema, e se existir,
    envia um código de verificação para o e-mail do usuário para que ele possa prosseguir com a redefinição de senha.
    Se o e-mail não estiver registrado, a função retorna uma mensagem de erro informando que o e-mail não foi encontrado.
    """
    email = email.strip().lower()

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    user_exists = bool(cursor.fetchone()[0])

    if not user_exists:
        return False, "E-mail não encontrado."

    return _send_code(email, "reset_password")

def verify_code(email: str, code: str, purpose: str):
    """
    Essa função verifica se o código digitado pelo usuário é válido
    Regras:
    1. O código precisa existir no banco para o e-mail e a finalidade.
    2. O código não pode estar expirado
    3. O código digitado deve bater com o hash salvo
    4. Se for válido, ele é apagado do banco para não ser reutilizado
    """
    email = email.strip().lower()
    code = code.strip()

    cursor.execute(
        "SELECT code_hash, expires_at FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )
    row = cursor.fetchone()

    if row is None:
        return False, "Nenhum código válido foi encontrado para este e-mail."

    code_hash, expires_at = row

    if datetime.now() > datetime.fromisoformat(expires_at):
        cursor.execute(
            "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
            (email, purpose)
        )
        connection.commit()
        return False, "O código expirou."
    
    if not verify_value(code, code_hash):
        return False, "Código inválido."

    cursor.execute(
        "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )
    connection.commit()

    return True, "Código validado com sucesso."

def finalize_password_reset(email: str, new_password: str):
    """
    Essa função finaliza a redefinição da senha
    1. Valida a nova senha
    2. Gera o hash da nova senha
    3. Atualiza a senha do usuário no banco de dados
    """
    email = email.strip().lower()

    password_message = password_error_message(new_password)
    if password_message is not None:
        return False, password_message

    new_password_hash = hash_value(new_password)

    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password_hash, email)
    )
    connection.commit()

    return True, "Senha alterada com sucesso."