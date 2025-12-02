# src/ingestion/paragraph_splitter.py

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Paragraph:
    page_number: int   # 👈 ให้ชื่อฟิลด์ตรงกับ diff_engine
    index: int
    text: str


class ParagraphSplitter:
    """
    รับรายการเพจจาก PDFLoader (list ของ dict: {"page": int, "text": str})
    แล้วแตกเป็นย่อหน้า ๆ
    """

    def split(self, pages: List[Dict]) -> List[Paragraph]:
        paragraphs: List[Paragraph] = []

        for page in pages:
            page_no = page.get("page", 0)
            raw_text = page.get("text", "") or ""

            # แบ่งย่อหน้าด้วย "\n\n" แล้วตัดช่องว่างส่วนเกิน
            blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]

            for idx, block in enumerate(blocks):
                paragraphs.append(
                    Paragraph(
                        page_number=page_no,   # 👈 ใช้ page_number
                        index=idx,
                        text=block,
                    )
                )

        return paragraphs
