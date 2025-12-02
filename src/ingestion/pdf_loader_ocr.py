# src/ingestion/pdf_loader_ocr.py

import fitz  # PyMuPDF
from typing import List, Dict

from PIL import Image

from .ocr_engine import OCREngine


class PDFLoaderWithOCR:
    """
    โหลดไฟล์ PDF:
    - ถ้าเพจมี text จริง → ใช้ get_text() ปกติ
    - ถ้าเพจแทบไม่มี text → render เป็นรูป แล้วส่งเข้า OCR
    """

    def __init__(self, min_chars_for_direct_text: int = 30, ocr_dpi: int = 200):
        self.ocr_engine = OCREngine()
        self.min_chars_for_direct_text = min_chars_for_direct_text
        self.ocr_dpi = ocr_dpi

    def _page_to_image(self, page: "fitz.Page") -> Image.Image:
        """
        แปลงหน้า PDF เป็น PIL Image สำหรับส่งเข้า OCR
        """
        pix = page.get_pixmap(dpi=self.ocr_dpi)

        if pix.alpha:
            mode = "RGBA"
        else:
            mode = "RGB"

        img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

        if mode == "RGBA":
            img = img.convert("RGB")

        return img

    def load(self, path: str) -> List[Dict]:
        """
        โหลด PDF แบบผสม text + OCR
        """
        try:
            doc = fitz.open(path)
        except Exception as e:
            raise RuntimeError(f"ไม่สามารถเปิดไฟล์ PDF ได้: {path} ({e})")

        pages: List[Dict] = []

        for i in range(len(doc)):
            page = doc.load_page(i)

            # --- 1) ดึง text ปกติ ---
            base_text = page.get_text("text") or ""
            base_text = base_text.strip()

            final_text = base_text

            # --- 2) OCR ทุกหน้า แล้วเลือกข้อความที่ "ดีกว่า" ---
            try:
                img = self._page_to_image(page)
                ocr_text = self.ocr_engine.ocr_image(img).strip()

                base_letters = sum(ch.isalnum() for ch in base_text)
                ocr_letters = sum(ch.isalnum() for ch in ocr_text)

                # ถ้า OCR ได้ตัวหนังสือมากกว่า → ใช้ OCR
                if ocr_letters > base_letters:
                    final_text = ocr_text

            except Exception as e:
                print(f"[WARN] OCR เพจ {i+1} ผิดพลาด: {e}")

            pages.append(
                {
                    "page": i + 1,
                    "text": final_text or "",
                }
            )

        doc.close()
        return pages


if __name__ == "__main__":
    loader = PDFLoaderWithOCR()
    pdf_path = "data/samples/17087276-3.pdf"

    pages = loader.load(pdf_path)
    print(f"โหลดได้ {len(pages)} หน้า")
    for p in pages:
        print(f"\n=== Page {p['page']} ===")
        print(p["text"][:400].replace("\n", " ") + "...")
