import sqlite3

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Criando a tabela de eventos favoritados caso não exista.
cursor.execute("CREATE TABLE IF NOT EXISTS favorite_events (" \
    "user_id INTEGER NOT NULL, " \
    "event_id INTEGER NOT NULL, " \
    "PRIMARY KEY(user_id, event_id), " \
    "FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, " \
    "FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE)"
    )