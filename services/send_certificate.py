from database.repositories.event_participation import event_participation_service
from services.certificate_generator import generate_certificate
from services.send_email import email_service

def send_certificate(user_id: int, event_id: int, user_email: str, user_name: str, event_name: str, date: str, activities: list):
    """
    Gera um certificado de participação para o usuário e envia por email.
    """
    activities = event_participation_service.check_activities(user_id, event_id)
    certificate_bytes = generate_certificate(user_name, event_name, date, activities)

    # Enviar o certificado por email
    subject = f"Certificado de Participação - {event_name}"
    body = f"Olá {user_name},\n\nParabéns por participar do evento {event_name}! Em anexo, você encontrará seu certificado de participação.\n\nAtenciosamente,\nEquipe Conecta++"
    
    email_service.send_email_with_attachment(user_email, subject, body, certificate_bytes, event_name)