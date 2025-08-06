import os
import shutil
import tempfile
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.llm_processing import Process_Invoice
from app.Folder_Processing import process_zip
from typing import Dict

UPLOAD_DIR = "uploads"
JSON_OUTPUT_DIR = os.path.join(UPLOAD_DIR, "json_results")

os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)

router = APIRouter()

@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, f"{uuid.uuid4().hex}{ext}")
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            structured_json = Process_Invoice(temp_path)
            return structured_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

@router.post("/upload_zip")
async def upload_zip(file: UploadFile = File(...)) -> Dict[str, dict]:
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file")
    try:
        result = process_zip(file, JSON_OUTPUT_DIR)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk processing failed: {e}")