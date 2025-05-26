import logging
from fastapi import APIRouter, Form, HTTPException
from gpt_handler import agent_master
from mysql_conn import get_connection
from datetime import datetime
import pytz  # <- Import necessário para timezone

router = APIRouter()

# Configuração básica do logger
logging.basicConfig(
    filename='registro_gastos.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("registro_gastos")

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

        # Pega data e hora de Brasília
        fuso_brasilia = pytz.timezone("America/Sao_Paulo")
        data_hora_brasilia = datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")
        
        # Validações
        # Regras: valor deve ser válido e diferente de zero, classificação obrigatória, descrição abrigatoria
        
        if not desc:
            logger.warning("Descrição vazia. Não será salvo no banco.")
            return {
                "mensagem": "Gasto classificado, mas não salvo porque a descrição está vazia.",
                "response": resultado,
                "salvo": False
            }
            
            
        if not classificacao:
            logger.warning("Classificação vazia. Não será salvo no banco.")
            return {
                "mensagem": "Gasto classificado, mas não salvo porque a classificação está vazia.",
                "response": resultado,
                "salvo": False
            }

        try:
            if valor <= 0.0:
                logger.warning(f"Valor é zero. Não será salvo no banco.")
                return {
                    "mensagem": "Gasto classificado, mas não salvo porque o valor é zero.",
                    "response": resultado,
                    "salvo": False
                }
                
        except ValueError:
            logger.warning("Valor inválido. Não será salvo no banco.")
            return {
                "mensagem": "Gasto classificado, mas não salvo devido a valor inválido.",
                "response": resultado,
                "salvo": False
            }
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (descricao, classificacao, valor, data_hora) VALUES (%s, %s, %s, %s)",
                (desc, classificacao, valor, data_hora_brasilia)
            )
            conn.commit()

        logger.info("Gasto registrado com sucesso no banco.")

        return {
            "mensagem": "Gasto classificado e salvo com sucesso!",
            "response": resultado,
            "salvo": True
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"ERRO AO REGISTRAR GASTO: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))
