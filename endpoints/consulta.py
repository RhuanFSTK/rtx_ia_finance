import logging
from fastapi import APIRouter, Query, HTTPException
from mysql_conn import get_connection
from datetime import datetime

router = APIRouter()

# Configuração básica do logger para este módulo
logger = logging.getLogger("consulta_gastos")
if not logger.hasHandlers():
    handler = logging.FileHandler("consulta_gastos.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@router.get("/")
def consultar_gastos(data_inicio: str = Query(...), data_fim: str = Query(...)):
    logger.info(f"Consulta de gastos iniciada: data_inicio={data_inicio}, data_fim={data_fim}")
    
    # Validação básica de datas (formato ISO)
    try:
        inicio = datetime.fromisoformat(data_inicio)
        fim = datetime.fromisoformat(data_fim)
    except ValueError:
        logger.error("Datas inválidas recebidas (formato ISO esperado).")
        raise HTTPException(status_code=400, detail="Datas devem estar no formato ISO: AAAA-MM-DD")

    try:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT descricao, classificacao, valor, data_hora 
                FROM gastos 
                WHERE data_hora BETWEEN %s AND %s
                ORDER BY data_hora DESC
            """, (data_inicio, data_fim))
            gastos = cursor.fetchall()
            total = sum([float(g['valor']) for g in gastos if g['valor'] is not None])
        
        logger.info(f"Consulta realizada com sucesso. Total de gastos encontrados: {len(gastos)}; Soma total: {total}")
        return {"gastos": gastos, "total": total}
    
    except Exception as e:
        logger.error(f"Erro ao consultar gastos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao consultar gastos: {str(e)}")
