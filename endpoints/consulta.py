import logging
from fastapi import APIRouter, Query, HTTPException
from mysql_conn import get_connection
from datetime import datetime
from typing import Optional
import sys

router = APIRouter()

# Logger para terminal (Uvicorn)
logger = logging.getLogger("consulta_gastos")
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@router.get("/")
def consultar_gastos(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None)
):
    logger.info("===========================================")
    logger.info("🚀 Iniciando endpoint: GET /consulta_gastos")
    logger.info(f"🔎 Parâmetros recebidos -> data_inicio: {data_inicio}, data_fim: {data_fim}")

    try:
        logger.info("🔗 Estabelecendo conexão com o banco de dados...")
        with get_connection() as conn:
            logger.info("✅ Conexão com o banco estabelecida.")
            cursor = conn.cursor(dictionary=True)

            if not data_inicio or not data_fim:
                logger.error("❌ Parâmetros de data ausentes.")
                raise HTTPException(status_code=400, detail="Os parâmetros 'data_inicio' e 'data_fim' são obrigatórios.")

            # Validação das datas
            try:
                inicio = datetime.fromisoformat(data_inicio.strip())
                fim = datetime.fromisoformat(data_fim.strip())
                logger.info("✅ Datas validadas com sucesso.")
            except ValueError:
                logger.error("❌ Formato de data inválido. Esperado: AAAA-MM-DD")
                raise HTTPException(status_code=400, detail="Datas devem estar no formato ISO: AAAA-MM-DD")

            sql = """
                SELECT descricao, classificacao, valor, data_hora 
                FROM gastos 
                WHERE data_hora BETWEEN %s AND %s
                ORDER BY data_hora DESC
                LIMIT 100 OFFSET 0
            """
            logger.info("📄 Executando SQL com filtro de data...")
            logger.info(f"📝 SQL: {sql.strip()}")
            logger.info(f"📌 Parâmetros: ({data_inicio}, {data_fim})")
            cursor.execute(sql, (data_inicio, data_fim))

            gastos = cursor.fetchall()
            total = sum([float(g['valor']) for g in gastos if g['valor'] is not None])

            logger.info("📊 Consulta finalizada com sucesso.")
            logger.info(f"📦 Total de registros encontrados: {len(gastos)}")
            logger.info(f"💰 Soma total dos valores: {total:.2f}")
            logger.info("✅ Enviando resposta para o cliente.")

        return {"gastos": gastos, "total": total}

    except Exception as e:
        logger.exception("🔥 Erro inesperado durante a consulta de gastos.")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar gastos: {str(e)}")
