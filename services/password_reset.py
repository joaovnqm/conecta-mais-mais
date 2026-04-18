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

# Gera um código aleatório de 6 dígitos
def generate_numeric_code() -> str:
    return f"{randint(0, 999999):06d}"

# Função para enviar o código
def _send_code(email: str, purpose: str):
    code = generate_numeric_code()
    code_hash = hash_value(code)
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    # Remove código anterior do mesmo e-mail e mesma finalidade
    cursor.execute(
        "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )
    # Salva o novo código no banco
    cursor.execute(
        "INSERT INTO verification_codes (email, purpose, code_hash, expires_at) VALUES (?, ?, ?, ?)",
        (email, purpose, code_hash, expires_at)
    )
    connection.commit()

    # Envia o código para o e-mail do usuário
    send_verification_email(email, code, purpose)
    return True, "Código enviado para o e-mail."


# Solicita um código de verificação para cadastro. Só envia se o e-mail ainda não estiver cadastrado.

def request_registration_code(email: str):
    email = email.strip().lower()

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    email_registered = bool(cursor.fetchone()[0])

    # Se o e-mail já existe, impede novo cadastro
    if email_registered:
        return False, "Esse e-mail já foi cadastrado."

    # Se não existe, envia código de verificação para cadastro
    return _send_code(email, "register")


# Solicita um código para recuperação de senha. Só envia se o e-mail já existir no sistema

def request_password_reset(email: str):
    email = email.strip().lower()

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)",
        (email,)
    )
    user_exists = bool(cursor.fetchone()[0])

    # Se o e-mail não existe, não envia o código de recuperação.
    if not user_exists:
        return False, "E-mail não encontrado."

    # Se existe, envia o código de recuperação
    return _send_code(email, "reset_password")

"""
Verifica se o código digitado pelo usuário é válido
    Regras:
    1. O código precisa existir no banco para o e-mail e a finalidade.
    2. O código não pode estar expirado
    3. O código digitado deve bater com o hash salvo
    4. Se for válido, ele é apagado do banco para não ser reutilizado
"""
def verify_code(email: str, code: str, purpose: str):
    email = email.strip().lower()
    code = code.strip()

    cursor.execute(
        "SELECT code_hash, expires_at FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )
    row = cursor.fetchone()

    # Se não encontrou nenhum código válido
    if row is None:
        return False, "Nenhum código válido foi encontrado para este e-mail."

    code_hash, expires_at = row

    # Se o código passou do tempo limite
    if datetime.now() > datetime.fromisoformat(expires_at):
        cursor.execute(
            "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
            (email, purpose)
        )
        connection.commit()
        return False, "O código expirou."
    
    # Compara o código digitado com o hash salvo no banco
    if not verify_value(code, code_hash):
        return False, "Código inválido."

    # Remove o código depois da validação correta
    cursor.execute(
        "DELETE FROM verification_codes WHERE email = ? AND purpose = ?",
        (email, purpose)
    )
    connection.commit()

    return True, "Código validado com sucesso."

"""
Finaliza a redefinição da senha
    1. Valida a nova senha
    2. Gera o hash da nova senha
    3. Atualiza a senha do usuário no banco de dados
"""
def finalize_password_reset(email: str, new_password: str):
    email = email.strip().lower()

    # Verifica se a nova senha atende às regras
    password_message = password_error_message(new_password)
    if password_message is not None:
        return False, password_message

    # Gera hash da nova senha
    new_password_hash = hash_value(new_password)

    # Atualiza a senha do banco
    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password_hash, email)
    )
    connection.commit()

    return True, "Senha alterada com sucesso."