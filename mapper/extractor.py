# mapper/extractor.py

import pytesseract
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image

# Set the path to your Tesseract installation.
# Adjust this if you installed Tesseract to a different location.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _extract_from_pdf(filepath):
    """
    Attempts to extract text from a PDF using two strategies in sequence.

    Strategy 1 — Direct text extraction via pdfplumber:
        Most modern PDFs have a text layer that pdfplumber can read directly.
        This is fast and accurate. Each page is extracted individually and
        concatenated.

    Strategy 2 — OCR fallback via Tesseract:
        If a page returns no text from pdfplumber (indicating it is an image-
        only scanned page), that page is converted to an image using pdf2image
        and then passed through Tesseract OCR.

    The two strategies are applied per-page, not per-document. A single PDF
    can have some text-layer pages and some scanned pages, and each is handled
    by whichever strategy works for it.
    """
    text = ""
    scanned_pages = 0

    with pdfplumber.open(filepath) as pdf:
        total_pages = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()

            if page_text and page_text.strip():
                # Strategy 1 succeeded for this page
                text += page_text + "\n"
            else:
                # Strategy 1 returned nothing — try OCR
                scanned_pages += 1
                print(f"[*] Page {i+1}/{total_pages} has no text layer — running OCR...")

                try:
                    # Convert just this page to an image
                    # first_page and last_page are 1-indexed
                    images = convert_from_path(
                        filepath,
                        first_page=i + 1,
                        last_page=i + 1,
                        dpi=300  # 300 DPI gives Tesseract enough resolution to read cleanly
                    )
                    if images:
                        ocr_text = pytesseract.image_to_string(images[0])
                        text += ocr_text + "\n"
                except Exception as e:
                    print(f"[-] OCR failed on page {i+1}: {e}")

    if scanned_pages > 0:
        print(f"[+] OCR processed {scanned_pages} scanned page(s).")

    return text


def extract_text_from_file(filepath):
    """
    Public interface for text extraction.
    Routes to the correct extraction method based on file extension.
    """
    if filepath.endswith(".pdf"):
        return _extract_from_pdf(filepath)

    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported file type: {filepath}. Use .pdf or .txt")