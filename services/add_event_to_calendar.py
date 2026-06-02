from ics import Calendar, Event
from datetime import datetime
from dataclasses import dataclass
from services.send_email import email_service

@dataclass
class CalendarService:
    """Classe responsável por criar eventos de calendário e enviar por email para os usuários."""
    
    def create_calendar_event(self, title: str, description: str, start_time: datetime) -> bytes:
        """
        Cria um evento de calendário no formato .ics e retorna os bytes do arquivo.
        """
        calendar = Calendar()
        event = Event()
        event.name = title
        event.description = description
        event.begin = start_time
        event.make_all_day()
        calendar.events.add(event)

        return calendar.serialize().encode('utf-8')

    def send_calendar_event(self, user_email: str, title: str, description: str, start_time: datetime):
        """
        Cria um evento de calendário e envia por email para o usuário.
        """
        calendar_bytes = self.create_calendar_event(title, description, start_time)
        subject = f"Convite para o evento: {title}"
        body = f"Olá,\n\nVocê foi convidado para participar do evento '{title}'.\n\nDescrição: {description}\nData: {start_time.strftime('%d/%m/%Y %H:%M')}\n\nAtenciosamente,\nEquipe Conecta++"
        
        email_service.send_email_with_calendar_attachment(user_email, subject, body, calendar_bytes, title)

calendar_service = CalendarService()