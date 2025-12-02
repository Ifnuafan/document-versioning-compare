# src/service/compare_service.py

from pathlib import Path
from typing import Dict, Any, List

from ingestion.pdf_loader_ocr import PDFLoaderWithOCR
from ingestion.paragraph_splitter import ParagraphSplitter
from matching.paragraph_matcher import ParagraphMatcher
from diff.diff_engine import DiffEngine
from report.report_builder import ReportBuilder

from analysis.summary_engine import build_summary_text, estimate_risk_level

from db.session import SessionLocal
from db.ops import (
    get_or_create_document,
    create_document_version,
    create_comparison,
    bulk_insert_changes,
)


def run_compare(
    doc_name: str,
    v1_path: str,
    v2_path: str,
    v1_label: str = "v1",
    v2_label: str = "v2",
) -> Dict[str, Any]:
    """
    ฟังก์ชัน core สำหรับเปรียบเทียบเอกสาร 2 เวอร์ชัน
    ใช้ได้ทั้งจาก:
      - main.py (รันผ่าน CLI)
      - API / งานอื่น ๆ ที่อยาก reuse logic เดิม

    คืนค่าเป็น dict ที่สรุปผลการเปรียบเทียบ + path ของ report
    """

    # ✅ เช็คไฟล์ก่อน
    if not Path(v1_path).exists():
        raise FileNotFoundError(f"ไม่พบไฟล์: {v1_path}")
    if not Path(v2_path).exists():
        raise FileNotFoundError(f"ไม่พบไฟล์: {v2_path}")

    # ✅ เตรียม component หลัก
    loader = PDFLoaderWithOCR()
    splitter = ParagraphSplitter()
    matcher = ParagraphMatcher(threshold=0.6)
    diff_engine = DiffEngine()
    reporter = ReportBuilder()

    # 1) โหลด + แยกย่อหน้า
    print("📥 โหลด + แยกย่อหน้า ...")
    pages_v1 = loader.load(v1_path)
    paras_v1 = splitter.split(pages_v1)

    pages_v2 = loader.load(v2_path)
    paras_v2 = splitter.split(pages_v2)

    print(f"- {v1_label}: pages={len(pages_v1)}, paragraphs={len(paras_v1)}")
    print(f"- {v2_label}: pages={len(pages_v2)}, paragraphs={len(paras_v2)}")

    # 2) จับคู่ย่อหน้า
    print("🔗 จับคู่ย่อหน้า ...")
    matches = matcher.match(paras_v1, paras_v2)

    # 3) สร้างรายการการเปลี่ยนแปลง
    print("🧮 สร้างรายการการเปลี่ยนแปลง ...")
    changes = diff_engine.build_changes(matches)
    print(f"- พบการเปลี่ยนแปลงทั้งหมด: {len(changes)} รายการ")

    # 4) สรุป + ประเมินความเสี่ยง
    summary_text = build_summary_text(changes)
    overall_risk_level = estimate_risk_level(changes)

    print("📊 Risk Level:", overall_risk_level)

    # 5) บันทึกลงฐานข้อมูล
    db = SessionLocal()
    try:
        # document หลัก
        doc = get_or_create_document(db, doc_name, category=None)

        # version แต่ละไฟล์
        ver1 = create_document_version(db, doc, v1_label, v1_path)
        ver2 = create_document_version(db, doc, v2_label, v2_path)

        # comparison run
        comp = create_comparison(db, doc, ver1, ver2, overall_risk_level, summary_text)

        # map Change objects → dicts สำหรับ bulk insert
        change_dicts: List[dict] = []
        for c in changes:
            change_dicts.append(
                {
                    "change_type": c.change_type,
                    "section_label": c.section_label,
                    "old_text": c.old_text,
                    "new_text": c.new_text,
                    "risk_level": None,
                    "ai_comment": None,
                }
            )

        bulk_insert_changes(db, comp, change_dicts)
        db.commit()
        run_id = comp.id
    finally:
        db.close()

    # 6) สร้าง report (JSON + HTML)
    print("📝 สร้างรายงาน ...")
    json_path = reporter.save_json(
        doc_name=doc_name,
        v1_label=v1_label,
        v2_label=v2_label,
        changes=changes,
        summary_text=summary_text,
        overall_risk_level=overall_risk_level,
    )
    html_path = reporter.save_html(
        doc_name=doc_name,
        v1_label=v1_label,
        v2_label=v2_label,
        changes=changes,
        summary_text=summary_text,
        overall_risk_level=overall_risk_level,
    )

    print("✅ เสร็จสิ้น")
    print(f"- JSON report: {json_path}")
    print(f"- HTML report: {html_path}")
    print("เปิด HTML ใน browser เพื่อดูผลได้เลย")

    # คืนข้อมูลสรุปให้ caller ใช้ต่อได้
    return {
        "doc_name": doc_name,
        "v1_label": v1_label,
        "v2_label": v2_label,
        "pages_v1": len(pages_v1),
        "pages_v2": len(pages_v2),
        "paragraphs_v1": len(paras_v1),
        "paragraphs_v2": len(paras_v2),
        "changes_count": len(changes),
        "risk_level": overall_risk_level,
        "summary_text": summary_text,
        "json_report_path": str(json_path),
        "html_report_path": str(html_path),
        "run_id": run_id,
    }
