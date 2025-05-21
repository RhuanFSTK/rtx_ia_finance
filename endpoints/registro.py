from fastapi import APIRouter, Form, HTTPException
from gpt_handler import classificar_texto
from mysql_conn import get_connection

router = APIRouter()

@router.post("/")
def registrar_gasto(descricao: str = Form(...)):
    try:
        print("Recebido:", descricao)

        resultado = classificar_texto(descricao)
        
        desc = resultado.get("descricao", "Sem descrição").capitalize()
        valor = float(resultado.get("valor", 0.0))
        classificacao = resultado.get("classificacao", "Não classificado").capitalize()

        print("Descrição:", desc)
        print("Valor:", valor)
        print("Classificação:", classificacao)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (descricao, classificacao, valor) VALUES (%s, %s, %s)",
                (desc, classificacao, valor)
            )
            conn.commit()

        return {
            "mensagem": "Gasto classificado e salvo com sucesso!",
            "gpt": resultado,  # Resultado bruto do GPT para exibir no front
            "salvo": True
        }

    except Exception as e:
        import traceback
        print("ERRO AO REGISTRAR GASTO:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
