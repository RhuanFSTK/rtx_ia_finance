import logging
from fastapi import APIRouter, Query, HTTPException
from mysql_conn import get_connection
from datetime import datetime
from typing import Optional
import sys  # Adicionado para log no console

router = APIRouter()


logger = logging.getLogger("consulta_gastos")

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)  # 🔁 Manda tudo pro terminal/log do Uvicorn
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
            if data_inicio and data_fim:
                logger.info("📅 Validação das datas informadas...")
                try:
                    inicio = datetime.fromisoformat(data_inicio)
                    fim = datetime.fromisoformat(data_fim)
                    logger.info("✅ Datas validadas com sucesso.")
                except ValueError:
                    logger.error("❌ Formato de data inválido. Esperado: AAAA-MM-DD")
                    raise HTTPException(status_code=400, detail="Datas devem estar no formato ISO: AAAA-MM-DD")

                sql = """
                    SELECT descricao, classificacao, valor, data_hora 
                    FROM gastos 
                    WHERE data_hora BETWEEN %s AND %s
                    ORDER BY data_hora DESC
                """
                logger.info("📄 Executando SQL filtrado por data...")
                logger.info(f"📝 SQL: {sql.strip()}")
                logger.info(f"📌 Parâmetros: ({data_inicio}, {data_fim})")
                cursor.execute(sql, (data_inicio, data_fim))

            else:
                sql = f"""
                        SELECT descricao, classificacao, valor, data_hora 
                        FROM gastos 
                        WHERE data_hora BETWEEN '{data_inicio}' AND '{data_fim}'
                        ORDER BY data_hora DESC
                        LIMIT 100 OFFSET 0
                    """
                logger.info("📄 Executando SQL sem filtro de data...")
                logger.info(f"📝 SQL: {sql.strip()}")
                cursor.execute(sql)

            gastos = cursor.fetchall()
            total = sum([float(g['valor']) for g in gastos if g['valor'] is not None])

            logger.info(f"📊 Consulta finalizada com sucesso.")
            logger.info(f"📦 Total de registros encontrados: {len(gastos)}")
            logger.info(f"💰 Soma total dos valores: {total:.2f}")
            logger.info("✅ Enviando resposta para o cliente.")

        return {"gastos": gastos, "total": total}

    except Exception as e:
        logger.exception("🔥 Erro inesperado durante a consulta de gastos.")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar gastos: {str(e)}")
