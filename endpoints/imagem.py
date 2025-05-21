from fastapi import APIRouter, UploadFile, File
from gpt_handler import analisar_imagem
import base64

router = APIRouter()

@router.post("/")
def analisar(file: UploadFile = File(...)):
    conteudo = base64.b64encode(file.file.read()).decode('utf-8')
    base64_img = f"data:image/jpeg;base64,{conteudo}"
    resultado = analisar_imagem(base64_img)
    return {"resultado": resultado}
