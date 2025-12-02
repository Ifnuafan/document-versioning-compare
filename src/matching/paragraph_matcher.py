# src/matching/paragraph_matcher.py

from dataclasses import dataclass
from typing import List, Optional, Tuple
from difflib import SequenceMatcher

from ingestion.paragraph_splitter import Paragraph


@dataclass
class ParagraphMatch:
    old: Optional[Paragraph]   # ย่อหน้าใน V1 (อาจเป็น None ถ้าเป็น ADD)
    new: Optional[Paragraph]   # ย่อหน้าใน V2 (อาจเป็น None ถ้าเป็น REMOVE)
    similarity: float          # 0.0 - 1.0


class ParagraphMatcher:
    """
    จับคู่ย่อหน้า V1 ↔ V2 แบบง่าย ๆ ด้วย string similarity
    """

    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold

    def similarity_score(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def match(self, old_paras: List[Paragraph], new_paras: List[Paragraph]) -> List[ParagraphMatch]:
        matches: List[ParagraphMatch] = []

        used_new_indexes = set()

        # จับคู่จากฝั่ง V1 เป็นหลัก
        for old in old_paras:
            best_score = 0.0
            best_idx: Optional[int] = None

            for idx, new in enumerate(new_paras):
                if idx in used_new_indexes:
                    continue

                score = self.similarity_score(old.text, new.text)
                if score > best_score:
                    best_score = score
                    best_idx = idx

            if best_idx is not None and best_score >= self.threshold:
                matches.append(
                    ParagraphMatch(
                        old=old,
                        new=new_paras[best_idx],
                        similarity=best_score,
                    )
                )
                used_new_indexes.add(best_idx)
            else:
                # ไม่มีคู่ที่คล้ายพอ → ถือว่าโดนลบ
                matches.append(
                    ParagraphMatch(
                        old=old,
                        new=None,
                        similarity=0.0,
                    )
                )

        # หาอันที่เป็น "เพิ่มใหม่" ใน V2 (ยังไม่ถูกจับคู่)
        for idx, new in enumerate(new_paras):
            if idx not in used_new_indexes:
                matches.append(
                    ParagraphMatch(
                        old=None,
                        new=new,
                        similarity=0.0,
                    )
                )

        return matches


if __name__ == "__main__":
    from ingestion.pdf_loader import PDFLoader
    from ingestion.paragraph_splitter import ParagraphSplitter

    loader = PDFLoader()
    splitter = ParagraphSplitter()
    matcher = ParagraphMatcher(threshold=0.7)

    v1_path = "data/samples/policy_v1.pdf"
    v2_path = "data/samples/policy_v2.pdf"

    pages_v1 = loader.load(v1_path)
    paras_v1 = splitter.split(pages_v1)

    pages_v2 = loader.load(v2_path)
    paras_v2 = splitter.split(pages_v2)

    results = matcher.match(paras_v1, paras_v2)

    print(f"รวมการจับคู่ทั้งหมด: {len(results)}")
    for m in results[:10]:
        if m.old and m.new:
            print(f"\n[MOD?] {m.similarity:.2f}")
            print(f"OLD: {m.old.text[:80]}...")
            print(f"NEW: {m.new.text[:80]}...")
        elif m.old and not m.new:
            print(f"\n[REMOVED]")
            print(f"OLD: {m.old.text[:80]}...")
        elif m.new and not m.old:
            print(f"\n[ADDED]")
            print(f"NEW: {m.new.text[:80]}...")
