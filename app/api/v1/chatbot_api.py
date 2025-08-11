from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.database.session import SessionLocal
from app.models.log_asn import LogASN
from app.services.gemini_client import ask_gemini_api
from app.services.google_sheet_imut import get_sheet_data_imut
from app.services.google_sheet_kp import get_sheet_data_kp
from app.services.pdf_rag import answer_question_with_rag

router = APIRouter()

user_last_active = {}
user_current_service = {}
INACTIVITY_TIMEOUT = timedelta(minutes=5)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PromptRequest(BaseModel):
    message: str
    sender: str

@router.post("/tanya-beken")
def ask_gemini(req: PromptRequest, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    sender = req.sender
    message = req.message.strip()

    welcome_message = (
        "👋 Selamat datang, ada yang bisa saya bantu? Pilih salah satu layanan kami:\n"
        "1. Layanan I-Mut\n2. Layanan KP (Kenaikan Pangkat)\n3. Informasi Umum\n4. Keluar percakapan"
    )

    last_active = user_last_active.get(sender)
    last_service = user_current_service.get(sender)

    if last_active is None or now - last_active > INACTIVITY_TIMEOUT:
        user_last_active[sender] = now
        user_current_service[sender] = None
        db.add(LogASN(id=str(uuid.uuid4()), sender=sender, message=message))
        db.commit()
        return {"sender": sender, "response": welcome_message}

    user_last_active[sender] = now
    db.add(LogASN(id=str(uuid.uuid4()), sender=sender, message=message))
    db.commit()

    # Pilih layanan
    if message == "1":
        user_current_service[sender] = "imut"
        return {"sender": sender, "response": "🗂 Anda memilih *Layanan I-Mut*. Silahkan ajukan pertanyaan tentang layanan I-Mut BKN"}
    elif message == "2":
        user_current_service[sender] = "kp"
        return {"sender": sender, "response": "💼 Anda memilih *Layanan KP (Kenaikan Pangkat)*. Silakan ajukan pertanyaan tentang layanan KP."}
    elif message == "3":
        user_current_service[sender] = "umum"
        return {"sender": sender, "response": "ℹ️ Anda memilih *Informasi Umum*. Silakan ajukan pertanyaan Anda."}
    elif message == "4":
        user_current_service[sender] = None
        return {"sender": sender, "response": "👋 Terima kasih telah menggunakan layanan kami. Sampai jumpa!"}

    # Ambil layanan aktif
    service = user_current_service.get(sender)

    try:
        if service == "imut":
            records = get_sheet_data_imut()
            if not records:
                raise Exception("Data kosong di Google Sheets.")
            context = "\n".join([f"{r['Topik']}: {r['Penjelasan']}" for r in records])
            prompt = f"""
            Berikut adalah informasi tentang layanan I-Mut:
            {context}

            Pertanyaan pengguna: "{message}"
            Jawablah pertanyaan tersebut secara relevan berdasarkan informasi di atas.
            """.strip()

        elif service == "kp":
            records = get_sheet_data_kp()
            if not records:
                raise Exception("Data kosong di Google Sheets.")
            context = "\n".join([f"{r['Topik']}: {r['Penjelasan']}" for r in records])
            prompt = f"""
            Berikut adalah informasi tentang layanan KP:
            {context}

            Pertanyaan pengguna: "{message}"
            Jawablah pertanyaan tersebut secara relevan berdasarkan informasi di atas.
            """.strip()

        elif service == "umum":
            pdf_answer = answer_question_with_rag(message)


            records_imut = get_sheet_data_imut()
            records_kp = get_sheet_data_kp()
            sheet_context = "\n".join([
                *[f"{r['Topik']}: {r['Penjelasan']}" for r in records_imut],
                *[f"{r['Topik']}: {r['Penjelasan']}" for r in records_kp]
            ])

            prompt = f"""
            Berikut adalah informasi dari dokumen PDF:
            {pdf_answer}

            Dan berikut adalah informasi dari Google Sheets:
            {sheet_context}

            Pertanyaan pengguna: "{message}"
            Jawablah pertanyaan tersebut secara lengkap dan relevan.
            """.strip()

        else:
            return {"sender": sender, "response": welcome_message}

        reply = ask_gemini_api(prompt)
        return {"sender": sender, "response": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses pertanyaan: {str(e)}")
