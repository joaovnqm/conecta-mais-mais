import sqlite3

connection = sqlite3.connect("conecta++.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name NOT NULL, email NOT NULL, password NOT NULL," \
"recovery_word NOT_NULL, interest, friends, pending_friend_request, blocked_users, confirmed_events, created_events)")

def login(email, password):
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    account_password = str(cursor.fetchone()[0])
    if str(password) == account_password:
        cursor.execute("SELECT name FROM users WHERE email = ?", (email,))
        name = str(cursor.fetchone()[0])
        print("Login realizado com sucesso!")
        return name
    
    else: 
        print("Login não realizado.")


def register(name, email, password, recovery_word):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)", (email,))
    email_registered = bool(cursor.fetchone()[0])
    if email_registered == True:
        print("Esse e-mail já foi cadastrado. Prossiga para o login.")
        return False
    
    else:
        cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, name, email, password, recovery_word, None, None, None, None, None, None))
        connection.commit()
        print("Cadastro realizado!")