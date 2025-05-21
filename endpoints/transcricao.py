from fastapi import APIRouter, UploadFile, File, HTTPException
from gpt_handler import transcrever_audio
import os
import tempfile

router = APIRouter()

@router.post("/")
async def transcrever(file: UploadFile = File(...)):
    # Verifica se o arquivo é de áudio
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é um áudio válido.")
    
    # Usa a extensão original se possível
    ext = os.path.splitext(file.filename)[1] or ".mp3"

    # Cria um arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        # Realiza a transcrição do áudio
        texto = transcrever_audio(temp_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao transcrever o áudio: {str(e)}")
    finally:
        os.remove(temp_file_path)

    return {"transcricao": texto}
