from fastapi import UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from app.services.pdf_rag import train_pdf_to_faiss, PDF_FOLDER

load_dotenv()
router = APIRouter()

@router.post("/upload-train")
async def upload_pdf_for_training(file: UploadFile = File(...)):
    try:
        # Validasi ekstensi file
        if not file.filename.lower().endswith(".pdf"):
            return JSONResponse(status_code=400, content={
                "error": "Hanya file PDF yang diperbolehkan."
            })

        # Buat folder jika belum ada
        os.makedirs(PDF_FOLDER, exist_ok=True)

        # Cek apakah file sudah ada
        file_path = os.path.join(PDF_FOLDER, file.filename)
        if os.path.exists(file_path):
            return JSONResponse(status_code=400, content={
                "error": "File dengan nama yang sama sudah ada."
            })

        # Simpan file PDF ke disk
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Latih RAG dan simpan ke FAISS
        train_pdf_to_faiss()

        return JSONResponse(content={
            "filename": file.filename,
            "message": "✅ File berhasil diupload dan diproses ke FAISS vector index."
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "error": f"Gagal memproses file: {str(e)}"
        })
