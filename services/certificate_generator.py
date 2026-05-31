from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

def generate_certificate(name: str, event_name: str, date: str, activities: list) -> bytes:
    template_path = "assets/certificate_template.png"
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    background = ImageReader(template_path)
    pdf.drawImage(background, 0, 0, width=width, height=height)

    # Conteúdo do certificado
    pdf.setFont("Helvetica", 56)
    pdf.drawCentredString(width / 2, 450, "O Conecta++ certifica que:")

    # Nome do participante
    pdf.setFont("Helvetica-Bold", 38)
    pdf.drawCentredString(width / 2, 370, name)

    # Nome do evento
    pdf.setFont("Helvetica", 30)
    pdf.drawCentredString(width / 2, 310, f"Participou do evento \"{event_name}\"")

    # Atividades
    pdf.setFont("Helvetica", 24)
    if len(activities) > 1:
        pdf.drawCentredString(width / 2, 260, "As atividades realizadas pelo participante foram:")
    
    else:
        pdf.drawCentredString(width / 2, 260, "A atividade realizada pelo participante foi:")

    y_position = 220
    pdf.setFont("Helvetica", 18)

    for activity in activities:
        pdf.drawCentredString(width / 2, y_position, f"• {activity}")
        y_position -= 20

    # Data
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, 100, f"Realizado em {date}")

    pdf.save()

    # Retorna os bytes do PDF
    buffer.seek(0)
    return buffer.getvalue()

pdf_bytes = generate_certificate(
    "João Victor Macêdo",
    "CESAR Beat 2026",
    "16 de maio de 2026",
    [
        "Palestra sobre IA",
        "Workshop de Python"
    ]
)

with open("certificate.pdf", "wb") as f:
    f.write(pdf_bytes)