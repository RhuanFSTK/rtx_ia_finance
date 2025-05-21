from fastapi import APIRouter, Form, HTTPException
from gpt_handler import classificar_texto
from mysql_conn import get_connection

router = APIRouter()

@router.post("/")
def registrar_gasto(descricao: str = Form(...)):
    try:
        print("Recebido:", descricao)
        classificacao = classificar_texto(descricao)
        print("Classificação:", classificacao)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (descricao, classificacao) VALUES (%s, %s)",
                (descricao, classificacao)
            )
            conn.commit()

        return {"descricao": descricao, "classificacao": classificacao}
    
    except Exception as e:
        import traceback
        erro = traceback.format_exc()
        print("ERRO AO REGISTRAR GASTO:", erro)
        raise HTTPException(status_code=500, detail=str(e))
