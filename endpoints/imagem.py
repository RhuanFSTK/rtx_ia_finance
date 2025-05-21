from fastapi import APIRouter, UploadFile, File, HTTPException
from gpt_handler import analisar_imagem
import base64
import io
from PIL import Image

router = APIRouter()

@router.post("/")
async def analisar(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        image = Image.open(io.BytesIO(file_content))
        image.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Arquivo não é uma imagem válida.")

    # Detecta MIME type automaticamente
    mime_type = file.content_type or "image/jpeg"
    conteudo = base64.b64encode(file_content).decode('utf-8')
    base64_img = f"data:{mime_type};base64,{conteudo}"

    try:
        resultado = analisar_imagem(base64_img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar a imagem: {str(e)}")

    return {"resultado": resultado}
