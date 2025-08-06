from fastapi import UploadFile
import os
import shutil
import zipfile
import tempfile
import torch
import json
import uuid
from typing import Dict
from app.llm_processing import Process_Invoice

def process_zip(zip_file: UploadFile, output_dir: str) -> Dict[str, dict]:
    results = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, zip_file.filename)
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(zip_file.file, f)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        for root, _, files in os.walk(tmpdir):
            for fname in files:
                print(fname)
                full_path = os.path.join(root, fname)
                name, ext = os.path.splitext(fname)
                ext = ext.lower()
                output = {}

                try:
                    if ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", '.pdf']:
                        result = Process_Invoice(full_path)        
                    else:
                        output = {"error": f"Unsupported file type: {ext}"}

                except Exception as e:
                    output = {"error": str(e)}

                result_key = f"{uuid.uuid4().hex}_{fname}"
                results[result_key] = output

                json_filename = f"{result_key}.json"
                json_path = os.path.join(output_dir, json_filename)
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json.dump(output, json_file, indent=2)

    return results