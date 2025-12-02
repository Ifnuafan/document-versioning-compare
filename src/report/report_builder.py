# src/report/report_builder.py

import json
from pathlib import Path
from typing import List
from datetime import datetime

from diff.diff_engine import Change


class ReportBuilder:
    def __init__(self, output_dir: str = "data/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_json(
        self,
        doc_name: str,
        v1_label: str,
        v2_label: str,
        changes: List[Change],
        summary_text: str | None = None,
        overall_risk_level: str | None = None,
    ) -> Path:
        data = {
            "document_name": doc_name,
            "version_old": v1_label,
            "version_new": v2_label,
            "overall_risk_level": overall_risk_level,
            "summary_text": summary_text,
            "changes": [
                {
                    "change_type": c.change_type,
                    "section_label": c.section_label,
                    "old_text": c.old_text,
                    "new_text": c.new_text,
                }
                for c in changes
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

        filename = f"{self._safe_name(doc_name)}_{v1_label}_vs_{v2_label}.json"
        out_path = self.output_dir / filename
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return out_path

    def save_html(
        self,
        doc_name: str,
        v1_label: str,
        v2_label: str,
        changes: List[Change],
        summary_text: str | None = None,
        overall_risk_level: str | None = None,
    ) -> Path:
        rows_parts: list[str] = []
        for c in changes:
            old_html = (c.old_text or "").replace("\n", "<br>")
            new_html = (c.new_text or "").replace("\n", "<br>")

            row = (
                "<tr>"
                f"<td>{c.change_type}</td>"
                f"<td>{c.section_label}</td>"
                f"<td>{old_html}</td>"
                f"<td>{new_html}</td>"
                "</tr>"
            )
            rows_parts.append(row)

        rows_html = "\n".join(rows_parts)

        # เตรียม summary ให้ไม่มี backslash ใน f-string
        safe_summary = (summary_text or "").replace("\n", "<br>")
        risk_label = overall_risk_level or "-"

        if summary_text or overall_risk_level:
            summary_block = (
                "<section>\n"
                "  <h2>สรุปภาพรวม</h2>\n"
                f"  <p><strong>Risk Level:</strong> {risk_label}</p>\n"
                f"  <p>{safe_summary}</p>\n"
                "</section>"
            )
        else:
            summary_block = ""

        html = (
            "<!DOCTYPE html>\n"
            "<html lang=\"th\">\n"
            "<head>\n"
            "  <meta charset=\"utf-8\" />\n"
            f"  <title>Diff Report - {doc_name}</title>\n"
            "  <style>\n"
            "    body { font-family: sans-serif; margin: 20px; }\n"
            "    table { border-collapse: collapse; width: 100%; }\n"
            "    th, td { border: 1px solid #ccc; padding: 8px; vertical-align: top; }\n"
            "    th { background-color: #f0f0f0; }\n"
            "    .type-ADDED { background-color: #e6ffe6; }\n"
            "    .type-REMOVED { background-color: #ffe6e6; }\n"
            "    .type-MODIFIED { background-color: #fffbe6; }\n"
            "  </style>\n"
            "</head>\n"
            "<body>\n"
            f"  <h1>Document Versioning Compare</h1>\n"
            f"  <p><strong>Document:</strong> {doc_name}</p>\n"
            f"  <p><strong>Compare:</strong> {v1_label} → {v2_label}</p>\n"
            f"  {summary_block}\n"
            "  <h2>รายละเอียดการเปลี่ยนแปลง</h2>\n"
            "  <table>\n"
            "    <thead>\n"
            "      <tr>\n"
            "        <th>Type</th>\n"
            "        <th>Section</th>\n"
            "        <th>Old Text</th>\n"
            "        <th>New Text</th>\n"
            "      </tr>\n"
            "    </thead>\n"
            "    <tbody>\n"
            f"{rows_html}\n"
            "    </tbody>\n"
            "  </table>\n"
            "</body>\n"
            "</html>\n"
        )

        filename = f"{self._safe_name(doc_name)}_{v1_label}_vs_{v2_label}.html"
        out_path = self.output_dir / filename
        out_path.write_text(html, encoding="utf-8")
        return out_path

    def _safe_name(self, name: str) -> str:
        return "".join(
            ch if ch.isalnum() or ch in "-_" else "_" for ch in name
        )
