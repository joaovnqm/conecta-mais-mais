from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

def generate_certificate(name: str, event_name: str, date: str, activities: list) -> bytes:
    activities = activities[0].split(";")
    template_path = "assets/certificate_template.png"
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    background = ImageReader(template_path)
    pdf.drawImage(background, 0, 0, width=width, height=height)

    pdf.setFont("Helvetica", 56)
    pdf.drawCentredString(width / 2, 450, "O Conecta++ certifica que")

    pdf.setFont("Helvetica-Bold", 38)
    pdf.drawCentredString(width / 2, 380, name)

    pdf.setFont("Helvetica", 32)
    pdf.drawCentredString(width / 2, 320, f"Participou do evento")

    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(width / 2, 270, event_name)

    pdf.setFont("Helvetica", 24)
    if len(activities) > 1:
        pdf.drawCentredString(width / 2, 230, "As atividades realizadas pelo participante foram:")
        y_position = 210
        pdf.setFont("Helvetica", 18)

        for activity in activities:
            pdf.drawCentredString(width / 2, y_position, f"• {activity.strip()}")
            y_position -= 25
    
    else:
        pdf.drawCentredString(width / 2, 240, "Atividade realizada pelo participante:")
        y_position = 210
        pdf.setFont("Helvetica", 18)
        pdf.drawCentredString(width / 2, y_position, f"• {activities[0]}")

    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(width / 2, 90, f"Evento realizado em {date}")

    pdf.save()

    buffer.seek(0)
    return buffer.getvalue()