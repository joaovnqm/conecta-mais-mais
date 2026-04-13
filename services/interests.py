import sqlite3

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Criando tabela de interesses caso ela não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS interests(interest_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name NOT NULL)")

# Criando tabela de interesses dos usuários caso ela não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS users_interests(user_id INTEGER, interest_id INTEGER, PRIMARY KEY(user_id, interest_id), " \
    "FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, FOREIGN KEY (interest_id) REFERENCES interests(interest_id) " \
    "ON DELETE CASCADE)")

# Função que checa o id do interesse com base no nome de entrada da função, caso o interesse não exista, ele o cria e o insere na tabela.
def index_interest(interest: str):
    cursor.execute(
        "SELECT interest_id FROM interests WHERE name = ?",
        (interest,)
    )
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    cursor.execute(
        "INSERT INTO interests (name) VALUES (?)",
        (interest,)
    )
    connection.commit()
    
    return cursor.lastrowid

# Função que adiciona interesses ao perfil do usuário.
def add_interests(user_id, interest):
    interest_id = index_interest(interest)
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM users_interests WHERE user_id = ? AND interest_id = ?)",
        (user_id, interest_id,)
    )
    interest_registered = bool(cursor.fetchone()[0])

    if interest_registered:
        return "Algum desses interesses já foi cadastrado.", False
    
    cursor.execute(
        "INSERT INTO users_interests VALUES (?, ?)", (user_id, interest_id,)
    )
    connection.commit()

    return "Interesse(s) adicionado(s) com sucesso!", True

# Função que checa os interesses de um usuário.
def check_interests(user_id) -> tuple:
    user_id = str(user_id)
    cursor.execute(
        "SELECT interest_id FROM users_interests WHERE user_id = ?",
        (user_id,)
        )
    user = cursor.fetchall()
    user_interests = user

    return user_interests

def check_all_interests() -> tuple:
    cursor.execute(
        "SELECT name FROM interests"
    )
    interests = cursor.fetchall()

    return interests