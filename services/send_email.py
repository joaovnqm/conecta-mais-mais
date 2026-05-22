import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

class EmailService:
    # Define o servidor SMTP do gmail
    SMTP_HOST = "smtp.gmail.com"

    # Define a porta segura SSL usado pelo gmail
    SMTP_PORT = 465

    def __init__(self):
        self.load_dotenv()

    def send_verification_email(destinatario: str, code: str, purpose: str) -> None:
        """
        Função responsável por enviar o código de verificação por e-mail
        destinatario é o e-mail da pessoa que vai receber o código
        code é o código gerado pelo sistema
        purpose é a finalidade do código register ou reset_password
        """
        remetente = os.getenv("APP_EMAIL")
        password_app = os.getenv("APP_EMAIL_PASSWORD")
        
        if not remetente or not password_app:
            raise ValueError("Defina APP_EMAIL e APP_EMAIL_PASSWORD nas variáveis de ambiente. .env")
        
        if purpose == "register":
            assunto = "Código de verificação de e-mail - Conecta++"
            mensagem = f"""
        Olá!
        Seu código para verificar seu e-mail é: 
        {code}
        Esse código expira em 10 minutos.
        Se você não solicitou esse cadastro, por favor ignore este email.
        """
        else:
            assunto = "Código de recuperação de senha - Conecta++"
            mensagem = f"""
        Olá!
        Seu código para recuperação de senha é:
        {code}
        Esse código expira em 10 minutos.
        Se você não solicitou essa recuperação, por favor ignore este email.
            """

        msg = EmailMessage()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(mensagem)
        
        # Abre conexão segura com o servidor SMTP do gmail
        with smtplib.SMTP_SSL(EmailService.SMTP_HOST, EmailService.SMTP_PORT) as email:
            email.login(remetente, password_app)
            email.send_message(msg)

email_service = EmailService()