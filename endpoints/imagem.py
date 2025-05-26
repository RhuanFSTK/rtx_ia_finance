import logging
from fastapi import APIRouter, Form, HTTPException
from gpt_handler import agent_master
from mysql_conn import get_connection

router = APIRouter()

# Cria um logger específico para este módulo
logger = logging.getLogger("registro_gastos")
if not logger.hasHandlers():
    # Configura o logger somente se ainda não estiver configurado
    handler = logging.FileHandler("registro_gastos.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@router.post("/")
def registrar_gasto(descricao: str = Form(...)):
    try:
        logger.info(f"Recebido: {descricao}")

        resultado = agent_master(descricao)
        
        desc = resultado.get("descricao", "Sem descrição").capitalize()
        valor = float(resultado.get("valor", 0.0))
        classificacao = resultado.get("classificacao", "Não classificado").capitalize()

        logger.info(f"Descrição: {desc}")
        logger.info(f"Valor: {valor}")
        logger.info(f"Classificação: {classificacao}")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (descricao, classificacao, valor) VALUES (%s, %s, %s)",
                (desc, classificacao, valor)
            )
            conn.commit()

        logger.info("Gasto registrado com sucesso no banco.")

        return {
            "mensagem": "Gasto classificado e salvo com sucesso!",
            "gpt": resultado,
            "salvo": True
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"ERRO AO REGISTRAR GASTO: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))
