# src/diff/diff_engine.py

from dataclasses import dataclass
from typing import List, Optional
from matching.paragraph_matcher import ParagraphMatch
from ingestion.paragraph_splitter import Paragraph


@dataclass
class Change:
    change_type: str  # ADDED / REMOVED / MODIFIED
    section_label: str
    old_text: Optional[str]
    new_text: Optional[str]


class DiffEngine:
    def build_changes(self, matches: List[ParagraphMatch]) -> List[Change]:
        changes: List[Change] = []

        for m in matches:
            # กรณีแก้ไข
            if m.old and m.new:
                if m.similarity > 0.95:
                    # เหมือนเดิม ไม่ต้องใส่ใน change list
                    continue
                change_type = "MODIFIED"
                section_label = f"page {m.new.page_number}"
                old_text = m.old.text
                new_text = m.new.text

            # กรณีถูกลบ
            elif m.old and not m.new:
                change_type = "REMOVED"
                section_label = f"page {m.old.page_number}"
                old_text = m.old.text
                new_text = None

            # กรณีเพิ่มใหม่
            elif m.new and not m.old:
                change_type = "ADDED"
                section_label = f"page {m.new.page_number}"
                old_text = None
                new_text = m.new.text
            else:
                # safety
                continue

            changes.append(
                Change(
                    change_type=change_type,
                    section_label=section_label,
                    old_text=old_text,
                    new_text=new_text,
                )
            )

        return changes
