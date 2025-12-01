import fitz  # PyMuPDF

class PDFLoader:
    """
    โหลด PDF และดึงข้อความทีละหน้าออกมา
    คืนค่าเป็น list ของหน้า พร้อมข้อมูลพื้นฐาน
    """

    @staticmethod
    def load_pdf(path: str):
        try:
            doc = fitz.open(path)
        except Exception as e:
            raise RuntimeError(f"ไม่สามารถโหลดไฟล์ PDF: {path} — {e}")

        pages = []

        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            text = page.get_text("text")

            pages.append({
                "page": page_number + 1,
                "text": text.strip()
            })

        doc.close()
        return pages


if __name__ == "__main__":
    loader = PDFLoader()
    pdf_path = "../../data/samples/sample_v1.pdf"  # เปลี่ยนตามไฟล์จริง
    pages = loader.load_pdf(pdf_path)

    print(f"โหลด {len(pages)} หน้า")
    for p in pages:
        print(f"\n=== Page {p['page']} ===\n{p['text'][:200]}...")
