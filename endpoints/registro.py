from fastapi import APIRouter, Form, HTTPException
from gpt_handler import classificar_texto
from mysql_conn import get_connection
import re

router = APIRouter()

def classificar_valor(texto: str) -> float:
    # Procurar por padrões de valor como R$ 12,34 ou 12.34
    match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))', texto)
    if match:
        valor_str = match.group(1).replace('.', '').replace(',', '.')
        try:
            return float(valor_str)
        except ValueError:
            pass
    return 0.0  # valor padrão se nada for encontrado

@router.post("/")
def registrar_gasto(descricao: str = Form(...)):
    try:
        print("Recebido:", descricao)
        classificacao = classificar_texto(descricao)
        valor = classificar_valor(descricao)
        print("Classificação:", classificacao)
        print("Valor:", valor)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (descricao, classificacao, valor) VALUES (%s, %s, %s)",
                (descricao, classificacao, valor)
            )
            conn.commit()

        return {"descricao": descricao, "classificacao": classificacao, "valor": valor}
    
    except Exception as e:
        import traceback
        erro = traceback.format_exc()
        print("ERRO AO REGISTRAR GASTO:", erro)
        raise HTTPException(status_code=500, detail=str(e))
