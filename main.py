from fastapi import FastAPI, UploadFile, File
from endpoints import registro, transcricao, imagem

app = FastAPI(title="Agente Financeiro com IA")

# app.include_router(registro.router, prefix="/registro")
# app.include_router(transcricao.router, prefix="/audio")
# app.include_router(imagem.router, prefix="/imagem")

@app.get("/")
def read_root():
    return {"message": "Agente financeiro com IA está online!"}
