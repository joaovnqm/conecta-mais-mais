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

# Função que checa o id do interesse com base no nome de entrada da função.
def index_interest(interest):
    cursor.execute(
        "SELECT interest_id FROM interests WHERE name = ?",
        (str(interest),)
    )
    result = cursor.fetchone()
    if result is None:
        return None
    
    return result[0]

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


"""
cursor.execute("INSERT INTO interests(interest_id, name) VALUES (1, 'Inteligência Artificial'), (2, 'Engenharia de Software'), "
    "(3, 'Cibersegurança'), (4, 'Empreendedorismo'), (5, 'Ciência de Dados')")
"""