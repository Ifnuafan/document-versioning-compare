# src/main.py

import sys

from service.compare_service import run_compare


def main():
    if len(sys.argv) < 4:
        print("วิธีใช้:")
        print("  python src/main.py <doc_name> <v1.pdf> <v2.pdf> [v1_label] [v2_label]")
        print("ตัวอย่าง:")
        print("  python src/main.py HR_Policy data/samples/hr_v1.pdf data/samples/hr_v2.pdf v1 v2")
        sys.exit(1)

    doc_name = sys.argv[1]
    v1_path = sys.argv[2]
    v2_path = sys.argv[3]
    v1_label = sys.argv[4] if len(sys.argv) > 4 else "v1"
    v2_label = sys.argv[5] if len(sys.argv) > 5 else "v2"

    result = run_compare(
        doc_name=doc_name,
        v1_path=v1_path,
        v2_path=v2_path,
        v1_label=v1_label,
        v2_label=v2_label,
    )

    # แสดงสรุปสั้น ๆ บน CLI
    print("\n===== SUMMARY =====")
    print(f"📄 Document   : {result['doc_name']}")
    print(f"🔁 Compare    : {result['v1_label']} -> {result['v2_label']}")
    print(f"📑 Pages      : v1={result['pages_v1']}, v2={result['pages_v2']}")
    print(f"🧩 Paragraphs : v1={result['paragraphs_v1']}, v2={result['paragraphs_v2']}")
    print(f"🔀 Changes    : {result['changes_count']}")
    print(f"⚠️  Risk Level : {result['risk_level']}")
    print(f"📝 JSON       : {result['json_report_path']}")
    print(f"🌐 HTML       : {result['html_report_path']}")
    print(f"🆔 Run ID     : {result['run_id']}")


if __name__ == "__main__":
    main()
