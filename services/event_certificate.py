from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from dataclasses import dataclass
from database.repositories.event_participation import event_participation_service
from services.send_email import email_service

@dataclass
class Certificate:
    """Classe responsável por gerar certificados em PDF para os participantes dos eventos."""

    def generate_certificate(self, name: str, event_name: str, date: str, activities: list, lang: str = "pt") -> bytes:
        """Gerar um certificado de participação em PDF com base nas informações fornecidas.
        Suporta `lang='pt'` (padrão) ou `lang='en'` para gerar texto em inglês.
        """
        activities = [activity.strip() for activity in activities]
        template_path = "assets/certificate_template.png"
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        background = ImageReader(template_path)
        pdf.drawImage(background, 0, 0, width=width, height=height)

        translations = {
            "Presença": "Presence",
            "Publicação de Artigo": "Article Publication",
            "Apresentação de Palestra": "Lecture Presentation",
            "Minicurso": "Mini-course",
            "Workshop": "Workshop",
        }

        if lang == "en":
            activities = [translations.get(a, a) for a in activities]

        # Textos em português ou inglês conforme `lang`
        if lang == "en":
            header = "Conecta++ certifies that"
            participated_text = "Participated in the event"
            activities_title_plural = "The activities performed by the participant were:"
            activities_title_single = "Activity performed by the participant:"
            date_text = f"Event held on {date}"
            
        else:
            header = "O Conecta++ certifica que"
            participated_text = "Participou do evento"
            activities_title_plural = "As atividades realizadas pelo participante foram:"
            activities_title_single = "Atividade realizada pelo participante:"
            date_text = f"Evento realizado em {date}"

        pdf.setFont("Helvetica", 56)
        pdf.drawCentredString(width / 2, 450, header)

        pdf.setFont("Helvetica-Bold", 38)
        pdf.drawCentredString(width / 2, 380, name)

        pdf.setFont("Helvetica", 32)
        pdf.drawCentredString(width / 2, 320, participated_text)

        pdf.setFont("Helvetica-Bold", 30)
        pdf.drawCentredString(width / 2, 270, event_name)

        pdf.setFont("Helvetica", 24)
        if len(activities) > 1:
            pdf.drawCentredString(width / 2, 230, activities_title_plural)
            y_position = 210
            pdf.setFont("Helvetica", 18)

            for activity in activities:
                pdf.drawCentredString(width / 2, y_position, f"• {activity.strip()}")
                y_position -= 25
        else:
            pdf.drawCentredString(width / 2, 240, activities_title_single)
            y_position = 210
            pdf.setFont("Helvetica", 18)
            pdf.drawCentredString(width / 2, y_position, f"• {activities[0]}")

        pdf.setFont("Helvetica", 18)
        pdf.drawCentredString(width / 2, 90, date_text)

        pdf.save()

        buffer.seek(0)
        return buffer.getvalue()
    
    def send_certificate(self, user_id: int, event_id: int, user_email: str, user_name: str, event_name: str, date: str, activities: list, lang: str = "pt"):
        """
        Gera um certificado de participação para o usuário e envia por email.
        """
        activities = event_participation_service.check_activities(user_id, event_id)
        certificate_bytes = self.generate_certificate(user_name, event_name, date, activities, lang=lang)

        # Enviar o certificado por email com assunto e corpo no idioma solicitado
        if lang == "en":
            subject = f"Participation Certificate - {event_name}"
            body = f"Hello {user_name},\n\nCongratulations on participating in the event {event_name}! Attached you will find your participation certificate.\n\nBest regards,\nConecta++ Team"
        else:
            subject = f"Certificado de Participação - {event_name}"
            body = f"Olá {user_name},\n\nParabéns por participar do evento {event_name}! Em anexo, você encontrará seu certificado de participação.\n\nAtenciosamente,\nEquipe Conecta++"

        email_service.send_email_with_attachment(user_email, subject, body, certificate_bytes, event_name)

certificate_service = Certificate()