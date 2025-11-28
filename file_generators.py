import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


EXPORTS_DIR = "exports"
os.makedirs(EXPORTS_DIR, exist_ok=True)


# -----------------------------------
#  Регистрация шрифта для кириллицы
# -----------------------------------
try:
    pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
except:
    # fallback — если файл отсутствует на сервере
    pass


def generate_pdf(transcript: str, summary: str):
    """
    Создаёт красивый PDF-файл:
    - транскрипт
    - summary
    - заголовки
    """

    filename = "Skriptoria_Transcript.pdf"
    path = os.path.join(EXPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Заголовок
    story.append(Paragraph("<b>🟣 Скриптор AI — Транскрипт</b>", styles['Title']))
    story.append(Spacer(1, 0.5 * cm))

    # Summary
    story.append(Paragraph("<b>📌 Summary</b>", styles['Heading2']))
    for block in summary.split("\n"):
        story.append(Paragraph(block, styles['Normal']))
        story.append(Spacer(1, 0.3 * cm))

    story.append(Spacer(1, 1 * cm))

    # Транскрипт
    story.append(Paragraph("<b>🎙 Полная расшифровка</b>", styles['Heading2']))

    for paragraph in transcript.split("\n"):
        story.append(Paragraph(paragraph, styles['Normal']))
        story.append(Spacer(1, 0.2 * cm))

    doc.build(story)

    return path



def generate_markdown(transcript: str, summary: str):
    """
    Создаёт Markdown-файл (.md) с:
    - summary
    - транскриптом
    """

    filename = "Skriptoria_Transcript.md"
    path = os.path.join(EXPORT_DIR, filename)

    content = (
        "# 🟣 Скриптор AI — Summary\n\n"
        + summary
        + "\n\n---\n\n"
        + "# 🎙 Полный транскрипт\n\n"
        + transcript
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path
