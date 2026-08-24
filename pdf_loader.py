import os
from pypdf import PdfReader
import fitz
import pytesseract
from PIL import Image

if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def load_and_chunk_pdf(pdf_path: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Reads a PDF file and splits its text into overlapping chunks."""
    reader = PdfReader(pdf_path)
    full_text = ""
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    # Fallback to OCR if standard text extraction yields nothing
    if not full_text.strip():
        document = fitz.open(pdf_path)
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            text = pytesseract.image_to_string(image)
            if text:
                full_text += text + "\n"
        document.close()

    chunks = []
    for i in range(0, len(full_text), chunk_size - overlap):
        chunk = full_text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk.strip())
            
    return chunks  