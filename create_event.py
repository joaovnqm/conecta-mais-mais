from services.events import create_event
import sqlite3

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

"""

cursor.execute("DELETE FROM users")
cursor.execute("DELETE FROM users_interests")
cursor.execute("DELETE FROM events_interests")
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'users'")
"""

"""
cursor.execute("DELETE FROM events")
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'events'")
"""

"""
create_event("Teste 1", "Aldeia, casa de João", "28-05-2026", "12:45", 1, "Inteligência Artificial", "Empreendedorismo", "Engenharia de Software")
create_event("Teste 2", "Aldeia, casa de João", "28-05-2026", "12:45", 1, "Cibersegurança", "Ciência de Dados")
create_event("Teste 3", "Aldeia, casa de João", "28-05-2026", "12:45", 1, "Empreendedorismo")
create_event("Teste 4", "Aldeia, casa de João", "28-05-2026", "12:45", 1, "Ciência de Dados")
create_event("Teste 5", "Aldeia, casa de João", "28-05-2026", "12:45", 1, "Engenharia de Software", "Cibersegurança")
"""

# cursor.execute("ALTER TABLE users DROP COLUMN recovery_word")


connection.commit()
