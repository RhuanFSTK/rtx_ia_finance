from fastapi import APIRouter, Query, HTTPException
from mysql_conn import get_connection
from datetime import datetime

router = APIRouter()

@router.get("/")
def consultar_gastos(data_inicio: str = Query(...), data_fim: str = Query(...)):
    # Validação básica de datas (formato ISO)
    try:
        inicio = datetime.fromisoformat(data_inicio)
        fim = datetime.fromisoformat(data_fim)
    except ValueError:
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
        return {"gastos": gastos, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar gastos: {str(e)}")
