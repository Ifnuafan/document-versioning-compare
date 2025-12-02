# src/analysis/summary_engine.py

from collections import Counter
from typing import List
from diff.diff_engine import Change


# คีย์เวิร์ดแบบง่าย ๆ ไว้ประเมินความเสี่ยง
HIGH_RISK_KEYWORDS = [
    "terminate", "termination", "ยกเลิกสัญญา",
    "liability", "รับผิด", "ชดใช้",
    "penalty", "ค่าปรับ", "ความเสียหาย",
    "confidential", "ความลับ", "ไม่เปิดเผย",
]

MEDIUM_RISK_KEYWORDS = [
    "payment", "จ่ายเงิน", "ค่าใช้จ่าย",
    "credit", "debit", "ดอกเบี้ย",
    "scope", "ขอบเขตงาน",
    "sla", "service level",
]


def estimate_risk_level(changes: List[Change]) -> str:
    """
    ประเมินระดับความเสี่ยงแบบง่าย ๆ จากข้อความที่เปลี่ยน
    คืนค่า: "LOW" / "MEDIUM" / "HIGH"
    """
    text_all = " ".join(
        (c.new_text or "") + " " + (c.old_text or "") for c in changes
    ).lower()

    high_hits = sum(kw.lower() in text_all for kw in HIGH_RISK_KEYWORDS)
    med_hits = sum(kw.lower() in text_all for kw in MEDIUM_RISK_KEYWORDS)

    if high_hits >= 2:
        return "HIGH"
    if high_hits == 1 or med_hits >= 2:
        return "MEDIUM"
    return "LOW"


def build_summary_text(changes: List[Change]) -> str:
    """
    สร้างข้อความสรุปการเปลี่ยนแปลงแบบอ่านง่าย (ภาษาไทย)
    """
    if not changes:
        return "ไม่มีการเปลี่ยนแปลงเนื้อหาสำคัญระหว่างสองเวอร์ชัน"

    type_counter = Counter(c.change_type for c in changes)

    total = len(changes)
    added = type_counter.get("ADDED", 0)
    removed = type_counter.get("REMOVED", 0)
    modified = type_counter.get("MODIFIED", 0)

    lines: List[str] = []

    lines.append(
        f"โดยรวมมีการเปลี่ยนแปลงจำนวน {total} รายการ "
        f"(เพิ่ม {added} รายการ, ลบ {removed} รายการ, แก้ไข {modified} รายการ)"
    )

    # ดึงตัวอย่าง section ที่แก้ไข/เพิ่ม
    examples: List[str] = []
    for c in changes:
        if c.change_type in ("MODIFIED", "ADDED") and c.new_text:
            short_text = c.new_text[:140].replace("\n", " ")
            examples.append(f"- {c.section_label}: {short_text}...")
        if len(examples) >= 3:
            break

    if examples:
        lines.append("")
        lines.append("ตัวอย่างหัวข้อที่มีการปรับเปลี่ยน:")
        lines.extend(examples)

    return "\n".join(lines)
