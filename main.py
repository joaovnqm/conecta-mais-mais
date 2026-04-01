import tkinter as tk
import database as db
from database import accounts

list = accounts

window = tk.Tk()
window.title("Conecta++")
window.geometry("600x450")

login_page = tk.Frame(window)
login_page.pack()

tk.Label(login_page, text="Usuário").pack()
user_entry = tk.Entry(login_page)
user_entry.pack()

tk.Label(login_page, text="Senha").pack()
password_entry = tk.Entry(login_page)
password_entry.pack()


def login():
    user = user_entry.get()
    password = password_entry.get()

    if (user, password) in accounts:
        login_page.pack_forget()
        system_page.pack()
    else:
        message_label['text'] = 'Usuário ou senha inválida!'


tk.Button(login_page, text="Login", command=login).pack()

system_page = tk.Frame()
tk.Label(system_page, text="Bem-vindo ao Conecta++").pack()

message_label = tk.Label(login_page)
message_label.pack()

window.mainloop()
