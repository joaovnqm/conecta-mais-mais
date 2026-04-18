import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para dentro do programa
load_dotenv()

# Define o servidor SMTP do gmail
SMTP_HOST = "smtp.gmail.com"

# Define a porta segura SSL usado pelo gmail
SMTP_PORT = 465

"""
Função responsável por enviar o código de verificação por e-mail
destinatario é o e-mail da pessoa que vai receber o código
code é o código gerado pelo sistema
purpose é a finalidade do código register ou reset_password
"""

def send_verification_email(destinatario: str, code: str, purpose: str) -> None:
    # Lê do .env o e-mail do remetente
    remetente = os.getenv("APP_EMAIL")
    
    # Lê do .env a senha do app do e-mail remetente
    password_app = os.getenv("APP_EMAIL_PASSWORD")
    
    # Se alguma variável não existir, interrompe com erro
    if not remetente or not password_app:
        raise ValueError("Defina APP_EMAIL e APP_EMAIL_PASSWORD nas variáveis de ambiente. .env")
    
    # Se o código for para cadastro, monta assunto e mensagem de verificação de e-mail
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
        # Caso contrário, considera que o código é para recuperação de senha
        assunto = "Código de recuperação de senha - Conecta++"
        mensagem = f"""
    Olá!
    Seu código para recuperação de senha é:
    {code}
    Esse código expira em 10 minutos.
    Se você não solicitou essa recuperação, por favor ignore este email.
        """
    # Cria o objeto do e-mail
    msg = EmailMessage()
    
    # Define quem está enviando
    msg["From"] = remetente
    
    # Define quem vai receber 
    msg["To"] = destinatario
    
    # Define o assunto
    msg["Subject"] = assunto
    
    # Define o conteúdo da mensagem
    msg.set_content(mensagem)
    
    # Abre conexão segura com o servidor SMTP do gmail
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as email:
        
        # Faz login com o e-mail e a senha do app
        email.login(remetente, password_app)
        
        # Envia a mensagem montada
        email.send_message(msg)