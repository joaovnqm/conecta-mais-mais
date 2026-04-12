from services.events import create_event
import sqlite3

connection = sqlite3.connect("conecta++.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

"""
cursor.execute("DELETE FROM events")
cursor.execute("DELETE FROM users")
cursor.execute("DELETE FROM users_interests")
cursor.execute("DELETE FROM events_interests")
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'events'")
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'users'")
"""

create_event("Teste", "Aldeia, casa de João", "28-05-2026", "12:45", 1, "Inteligência Artificial", "Empreendedorismo", "Engenharia de Software")
connection.commit()

