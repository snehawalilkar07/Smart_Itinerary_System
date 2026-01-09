from fpdf import FPDF
from helpers import clean_text

def export_pdf(itinerary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for i, day in enumerate(itinerary, 1):
        pdf.cell(0, 8, clean_text(f"Day {i}"), ln=True)
        for s, e, p in day:
            line = f"{s.strftime('%I:%M %p')} - {e.strftime('%I:%M %p')}  {p['name']} ({p['category']})"
            pdf.multi_cell(0, 6, clean_text(line))
        pdf.ln(3)

    return pdf.output(dest='S').encode('latin1')
