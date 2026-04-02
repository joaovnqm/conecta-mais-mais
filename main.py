import sqlite3
import re

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
    password TEXT NOT NULL,
    recovery_word TEXT NOT NULL
)
""")

conn.commit()


def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.fullmatch(pattern, email) is not None


def valid_password(password):
    pattern = r'^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$'
    return re.fullmatch(pattern, password) is not None


def sign():
    email = input("Cadastre um email: ").strip().upper()

    if not valid_email(email):
        print("Email inválido!")
        return

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        print("Esse email já está cadastrado!.")
        return

    password = input("Cadastre uma senha: ").strip()

    if not valid_password(password):
        print("Senha inválida!")
        print("A senha deve ter: ")
        print("Ter pelo menos 8 caracteres")
        print("Ter pelo menos 1 letra maiúscula")
        print("Ter pelo menos 1 caracter especial")
        return

    confirm_password = input("Confirme a senha: ").strip()

    if password != confirm_password:
        print("As senhas não conferem!")
        return

    recovery_word = input("Cadastre uma palavra de recuperação: ").strip()
    if len(recovery_word) < 3:
        print("A palavra de recuperação deve ter pelo menos 3 caracteres.")
        return

    cursor.execute(
        "INSERT INTO users (email, password, recovery_word) VALUES (?, ?, ?)",
        (email, password, recovery_word)
    )

    conn.commit()
    print("Cadastro realizado com sucesso!")


def login():
    email = input("Email: ").strip().upper()
    password = input("Senha: ")

    cursor.execute(
        "SELECT password FROM users WHERE email = ?",
        (email,)
    )
    result = cursor.fetchone()

    if result is None:
        print("Email ou senha incorretos!")
        return

    saved_password = result[0]

    if saved_password == password:
        print("Login realizado com sucesso!")
    else:
        print("Email ou senha incorretos.")


def recover_password():
    email = input("Digite o seu email: ").strip().lower()

    if not valid_email(email):
        print("Email inválido!")
        return

    recovery_word = input("Digite sua palavra de recuperação: ").strip()

    cursor.execute(
        "SELECT recovery_word FROM users WHERE email = ?",
        (email,)
    )
    result = cursor.fetchone()

    if result is None:
        print("Email não encontrado!")
        return

    saved_recovery_word = result[0]

    if saved_recovery_word != recovery_word:
        print("Palavra de recuperação incorreta!")
        return

    new_password = input("Digite a nova senha: ").strip()

    if not valid_password(new_password):
        print("Senha inválida!")
        print("A senha deve:")
        print("- ter pelo menos 8 caracteres")
        print("- ter pelo menos 1 letra maiúscula")
        print("- ter pelo menos 1 caractere especial")
        return

    confirm_new_password = input("Confirme a nova senha: ").strip()

    if new_password != confirm_new_password:
        print("As senhas não conferem!")
        return

    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password, email)
    )

    conn.commit()

    print("Senha alterada com sucesso!")

while True:
    print("========== MENU INICIAL ==========")
    print('1 - Cadastrar')
    print('2 - Login')
    print('3 - Recuperar senha')
    print('4 - Sair')

    option = input("Escolha: ").strip()

    # Cadastro
    if option == '1':
        sign()

    # Login
    elif option == '2':
        login()

    # Recuperar senha
    elif option == '3':
        recover_password()

    elif option == '4':
        print("Saindo...")
        break

    else:
        print("Opção inválida!")

conn.close()
