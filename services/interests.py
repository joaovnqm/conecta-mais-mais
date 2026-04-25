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

def index_interest(interest: str) -> int:
    """
    Essa função retorna o id de um interesse. Se o interesse não existir, ele é criado e o id é retornado.
    """
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

def add_interests(user_id, interest):
    """
    Essa função adiciona um interesse à lista de interesses do usuário. Ela verifica se o interesse já foi adicionado e, se não,
    adiciona o interesse à lista de interesses do usuário.
    """
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

def check_interests_id(user_id) -> tuple:
    """
    Essa função retorna uma tupla de interesses com base no id do usuário. Ela consulta a tabela de interesses dos 
    usuários para obter os ids dos interesses, e retorna uma tupla contendo os ids dos interesses do usuário.
    """
    user_id = str(user_id)
    cursor.execute(
        "SELECT interest_id FROM users_interests WHERE user_id = ?",
        (user_id,)
        )
    user = cursor.fetchall()
    user_interests = user

    return user_interests

def check_interests_name(user_id) -> tuple:
    """
    Essa função retorna uma tupla de interesses com base no id do usuário. Ela consulta a tabela de interesses dos 
    usuários para obter os ids dos interesses, depois consulta a tabela de interesses para obter os nomes
    dos interesses, e retorna uma tupla contendo os nomes dos interesses do usuário.
    """
    interests_id = check_interests_id(user_id)
    interests_names = []
    for interest in interests_id:
        cursor.execute(
            "SELECT name FROM interests WHERE interest_id = ?",
            (interest[0],)
            )
        interest_result = cursor.fetchone()
        interests_names.append(interest_result[0])

    return interests_names

def check_all_interests() -> tuple:
    """
    Essa função retorna uma tupla de todos os interesses cadastrados. Ela consulta a tabela de interesses e retorna 
    uma tupla contendo os nomes de todos os interesses cadastrados.
    """
    cursor.execute(
        "SELECT name FROM interests"
    )
    interests = cursor.fetchall()

    return interests