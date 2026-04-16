import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

def send_recovery_email(destinatario: str, code: str) -> None:
    remetente = os.getenv("APP_EMAIL")
    password_app = os.getenv("APP_EMAIL_PASSWORD")
    
    if not remetente or not password_app:
        raise ValueError("Defina APP_EMAIL e APP_EMAIL_PASSWORD nas variáveis de ambiente.")
    
    assunto = "Código de recuperação de senha"
    mensagem = f"""
    Olá!
    Seu código de recuperação de senha é: 
    {code}
    Esse código expira em 10 minutos.
    Se você não solicitou essa recuperação, por favor ignore este email.
    """
    
    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(mensagem)
    
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as email:
        email.login(remetente, password_app)
        email.send_message(msg)