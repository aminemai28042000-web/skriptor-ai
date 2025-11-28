import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# регистрируем шрифт с поддержкой кириллицы
pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))


# ---------------------------------------------------------
# Генерация PDF
# ---------------------------------------------------------
def generate_pdf(text: str) -> str:
    os.makedirs("exports", exist_ok=True)

    filename = f"exports/SkriptorAI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("DejaVu", 11)

    width, height = A4
    x = 40
    y = height - 50

    # перенос строк
    def split_line(line, max_chars=95):
        return [line[i:i + max_chars] for i in range(0, len(line), max_chars)]

    for paragraph in text.split("\n"):
        if not paragraph.strip():
            y -= 15
            continue

        for line in split_line(paragraph):
            c.drawString(x, y, line)
            y -= 15

            if y < 50:
                c.showPage()
                c.setFont("DejaVu", 11)
                y = height - 50

    c.save()
    return filename


# ---------------------------------------------------------
# Генерация Markdown
# ---------------------------------------------------------
def generate_markdown(text: str) -> str:
    os.makedirs("exports", exist_ok=True)

    filename = f"exports/SkriptorAI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    return filename
