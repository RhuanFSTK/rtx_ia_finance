from fastapi import APIRouter, Form
from gpt_handler import classificar_texto
from mysql_conn import get_connection

router = APIRouter()

@router.post("/")
def registrar_gasto(descricao: str = Form(...)):
    classificacao = classificar_texto(descricao)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (descricao, classificacao) VALUES (%s, %s)", (descricao, classificacao))
    conn.commit()
    conn.close()
    return {"descricao": descricao, "classificacao": classificacao}
