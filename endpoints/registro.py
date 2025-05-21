from fastapi import APIRouter, Form, HTTPException
from gpt_handler import classificar_texto
from mysql_conn import get_connection
import re

router = APIRouter()

def classificar_valor(texto: str) -> float:
    # Expressão regular: captura valores com ou sem R$, com ou sem centavos
    padrao = r'(?:R\$?\s*)?(\d+(?:[.,]\d{2})?)\s*(?:reais|rs)?'
    match = re.search(padrao, texto, re.IGNORECASE)
    
    if match:
        valor_str = match.group(1).replace(',', '.')
        try:
            return float(valor_str)
        except ValueError:
            pass
    return 0.0

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
