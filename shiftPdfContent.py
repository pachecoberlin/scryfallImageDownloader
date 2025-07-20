import fitz  # PyMuPDF
import sys

def shift_pdf_content(input_path, output_path, shift_mm):
    # Umrechnung von mm in Punkte (1 inch = 25.4 mm, 1 inch = 72 Punkte)
    shift_points = shift_mm / 25.4 * 72

    # PDF öffnen
    doc = fitz.open(input_path)

    # Seiteninhalt verschieben
    for page in doc:
        matrix = fitz.Matrix(1, 0, 0, 1, -shift_points, 0)
        page.set_transformation(matrix)

    # Speichern
    doc.save(output_path)
    doc.close()

# Beispiel:
# shift_pdf_content("mtgCardback.pdf", "mtgCardback_shifted.pdf", 1.5)

# Für Kommandozeile:
# if __name__ == "__main__":
#     if len(sys.argv) != 4:
#         print("Usage: python shift_pdf.py input.pdf output.pdf shift_mm")
#     else:
#         shift_pdf_content(sys.argv[1], sys.argv[2], float(sys.argv[3]))
