from fastapi import APIRouter, Query
from mysql_conn import get_connection

router = APIRouter()

@router.get("/")
def consultar_gastos(data_inicio: str = Query(...), data_fim: str = Query(...)):
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
        return {"detail": str(e)}
