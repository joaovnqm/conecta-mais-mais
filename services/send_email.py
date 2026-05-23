import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


class EmailService:
    """
    Serviço responsável pelo envio de e-mails do sistema.

    Usa SMTP do Gmail com senha de aplicativo armazenada em variáveis de ambiente
    ou em arquivo .env.
    """

    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self):
        load_dotenv()

    def send_verification_email(
        self,
        destinatario: str,
        code: str,
        purpose: str
    ) -> None:
        """
        Envia um código de verificação por e-mail.

        Parâmetros:
            destinatario: e-mail da pessoa que receberá o código.
            code: código numérico gerado pelo sistema.
            purpose: finalidade do código. Pode ser "register" ou "reset_password".
        """
        remetente = os.getenv("APP_EMAIL")
        password_app = os.getenv("APP_EMAIL_PASSWORD")

        if not remetente or not password_app:
            raise ValueError(
                "Defina APP_EMAIL e APP_EMAIL_PASSWORD nas variáveis de ambiente ou no arquivo .env."
            )

        if purpose == "register":
            assunto = "Código de verificação de e-mail - Conecta++"
            mensagem = f"""
Olá!

Seu código para verificar seu e-mail é:

{code}

Esse código expira em 10 minutos.

Se você não solicitou esse cadastro, ignore este e-mail.
"""
        elif purpose == "reset_password":
            assunto = "Código de recuperação de senha - Conecta++"
            mensagem = f"""
Olá!

Seu código para recuperação de senha é:

{code}

Esse código expira em 10 minutos.

Se você não solicitou essa recuperação, ignore este e-mail.
"""
        else:
            raise ValueError("Finalidade de e-mail inválida.")

        msg = EmailMessage()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(mensagem)

        with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT) as smtp:
            smtp.login(remetente, password_app)
            smtp.send_message(msg)


email_service = EmailService()