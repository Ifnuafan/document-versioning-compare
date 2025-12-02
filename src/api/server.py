# src/api/server.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid

from service.compare_service import run_compare

app = FastAPI(title="Document Versioning Compare API")

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_temp_file(upload: UploadFile) -> Path:
    ext = Path(upload.filename).suffix or ".pdf"
    tmp_name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / tmp_name
    with dest.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dest


@app.post("/compare")
async def compare_documents(
    doc_name: str = Form(...),
    v1_label: str = Form("v1"),
    v2_label: str = Form("v2"),
    file_v1: UploadFile = File(...),
    file_v2: UploadFile = File(...),
):
    """
    รับไฟล์ PDF 2 เวอร์ชัน + ชื่อเอกสาร
    แล้วเรียก run_compare() → คืนผล JSON
    """
    try:
        v1_path = save_temp_file(file_v1)
        v2_path = save_temp_file(file_v2)

        result = run_compare(
            doc_name=doc_name,
            v1_path=str(v1_path),
            v2_path=str(v2_path),
            v1_label=v1_label,
            v2_label=v2_label,
        )

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
