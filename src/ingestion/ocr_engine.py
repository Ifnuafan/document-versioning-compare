# src/ingestion/ocr_engine.py

from PIL import Image
import pytesseract

# 👇 ชี้ path ไปหา tesseract.exe ของคุณ
pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract OCR\tesseract.exe"


class OCREngine:
    """
    ตัวห่อเรียก Tesseract OCR
    ตอนนี้เน้นอ่านข้อความภาษาไทย + อังกฤษ
    """

    def __init__(self, lang: str = "tha+eng"):
        self.lang = lang

    def ocr_image(self, image: Image.Image) -> str:
        text = pytesseract.image_to_string(image, lang=self.lang)
        text = text.replace("\r", " ").strip()
        return text

    def is_text_enough(self, text: str, min_chars: int = 30) -> bool:
        return len(text.strip()) >= min_chars
