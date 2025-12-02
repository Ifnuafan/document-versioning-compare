# src/ingestion/pdf_loader.py

import fitz  # PyMuPDF
from dataclasses import dataclass
from typing import List


@dataclass
class PageText:
    page_number: int
    text: str


class PDFLoader:
    """
    โหลดไฟล์ PDF แล้วดึงข้อความออกมาเป็นรายหน้า
    """

    def load(self, path: str) -> List[PageText]:
        try:
            doc = fitz.open(path)
        except Exception as e:
            raise RuntimeError(f"ไม่สามารถเปิดไฟล์ PDF ได้: {path} ({e})")

        pages: List[PageText] = []

        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text("text") or ""
            text = text.strip()

            pages.append(
                PageText(
                    page_number=i + 1,
                    text=text,
                )
            )

        doc.close()
        return pages


if __name__ == "__main__":
    loader = PDFLoader()
    # 👇 แก้ path ให้ตรงกับไฟล์จริงของคุณ
    pdf_path = "data/samples/17087276-3.pdf"

    pages = loader.load(pdf_path)

    print(f"โหลดได้ {len(pages)} หน้า")
    for p in pages:
        print(f"\n=== Page {p.page_number} ===")
        print(p.text[:400].replace("\n", " ") + "...")
