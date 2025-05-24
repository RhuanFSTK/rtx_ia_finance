import logging
from fastapi import APIRouter, Form, HTTPException
from gpt_handler import classificar_texto
from mysql_conn import get_connection

router = APIRouter()

# Configuração básica do logger
logging.basicConfig(
    filename='registro_gastos.log',  # arquivo para salvar logs
    level=logging.INFO,              # nível mínimo para registrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("registro_gastos")

@router.post("/")
def registrar_gasto(descricao: str = Form(...)):
    try:
        logger.info(f"Recebido: {descricao}")

        resultado = classificar_texto(descricao)
        
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
