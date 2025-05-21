from fastapi import FastAPI, UploadFile, File
from endpoints import registro, transcricao, imagem
from fastapi.middleware.cors import CORSMiddleware

# Criação do aplicativo FastAPI
app = FastAPI(title="Agente Financeiro com IA")

# Adiciona o middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou coloque o domínio do seu frontend, ex: "https://rtxiafinancefront-production.up.railway.app"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os endpoints do projeto
app.include_router(registro.router, prefix="/registro")
app.include_router(transcricao.router, prefix="/audio")
app.include_router(imagem.router, prefix="/imagem")

# Rota raiz
@app.get("/")
def read_root():
    return {"message": "Agente financeiro com IA está online!"}
