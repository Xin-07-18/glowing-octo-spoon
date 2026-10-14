"""Refresh the cached Word TOC page numbers after expanding the thesis."""

import re

import fitz
from docx import Document


DOCX = "documents/pcb_thesis_deeppcb_revised.docx"
PDF = "/workspace/pcb_literature/pcb_thesis_deeppcb_revised.pdf"


def compact(value):
    return re.sub(r"\s+", "", value)


def main():
    doc = Document(DOCX)
    pdf = fitz.open(PDF)
    pages = [compact(page.get_text()) for page in pdf]
    updated = []
    for paragraph in doc.paragraphs:
        if "\t" not in paragraph.text or not re.search(r"\t\d+$", paragraph.text):
            continue
        title, old_page = paragraph.text.rsplit("\t", 1)
        needle = compact(title)
        matches = [idx + 1 for idx, page_text in enumerate(pages[4:], 4) if needle in page_text]
        if not matches:
            raise RuntimeError(f"Could not locate TOC entry in rendered PDF: {title}")
        new_page = matches[0]
        if new_page != int(old_page):
            # The page number is the final run, preserving the existing TOC formatting.
            paragraph.runs[-1].text = str(new_page)
            updated.append((title, int(old_page), new_page))
    doc.save(DOCX)
    print(f"updated {len(updated)} entries")
    for item in updated:
        print(item)


if __name__ == "__main__":
    main()
