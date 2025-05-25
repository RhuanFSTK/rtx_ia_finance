import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from endpoints import registro, transcricao, imagem, consulta
from fastapi.middleware.cors import CORSMiddleware

# Criação do aplicativo FastAPI
app = FastAPI(title="Agente Financeiro com IA")

app.mount("/logs", StaticFiles(directory="logs"), name="logs")

# CORS com ambiente condicional
origens = [
    "https://rtxiafinancefront-production.up.railway.app"
]

if os.getenv("ENV") != "production":
    origens.append("http://localhost:3000")  # Ambiente local para desenvolvimento

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os módulos
app.include_router(registro.router, prefix="/registro")
app.include_router(transcricao.router, prefix="/audio")
app.include_router(imagem.router, prefix="/imagem")
app.include_router(consulta.router, prefix="/consulta")

# Rota raiz
@app.get("/")
def read_root():
    return {"message": "Agente financeiro com IA está online!"}
