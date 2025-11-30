from fpdf import FPDF
import markdown
import os

def generate_pdf(transcript, summary):
    path = f"/tmp/{os.urandom(8).hex()}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 8, "SUMMARY:\n" + summary)
    pdf.ln(10)
    pdf.multi_cell(0, 8, "TRANSCRIPT:\n" + transcript)

    pdf.output(path)
    return path


def generate_markdown(transcript, summary):
    path = f"/tmp/{os.urandom(8).hex()}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Summary\n\n")
        f.write(summary + "\n\n")
        f.write("# Transcript\n\n")
        f.write(transcript)

    return path
