from fastapi import APIRouter, UploadFile, File
from gpt_handler import transcrever_audio
import os

router = APIRouter()

@router.post("/")
def transcrever(file: UploadFile = File(...)):
    caminho = f"uploads/{file.filename}"
    with open(caminho, "wb") as f:
        f.write(file.file.read())
    texto = transcrever_audio(caminho)
    os.remove(caminho)
    return {"texto": texto}
