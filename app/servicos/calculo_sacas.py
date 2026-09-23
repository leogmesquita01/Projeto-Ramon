from datetime import date
from typing import Any, Optional

from app.database.conexao import obter_conexao


def obter_resumo_sacas_safra(
    safra_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> dict[str, Any]:
    """
    Calcula o total de sacas e métricas de transporte. Se safra_id for None,
    calcula consolidado para todas as culturas.
    
    :param safra_id: ID da safra/cultura (opcional, None para todas).
    :param data_inicio: Data inicial do período (opcional).
    :param data_fim: Data final do período (opcional).
    :return: Dicionário contendo total_sacas, total_cargas e media_sacas_por_carga.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro = "WHERE 1=1"
            params: list[Any] = []
            if safra_id is not None:
                filtro += " AND safra_id = %s"
                params.append(safra_id)
            if data_inicio and data_fim:
                filtro += " AND data >= %s AND data <= %s"
                params.extend([data_inicio, data_fim])

            query = f"""
                SELECT 
                    COALESCE(SUM(quantidade_sacas), 0) AS total_sacas,
                    COUNT(id) AS total_cargas,
                    COALESCE(AVG(quantidade_sacas), 0) AS media_sacas_por_carga
                FROM cargas
                {filtro};
            """
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            
            return {
                "safra_id": safra_id,
                "total_sacas": int(row[0]) if row else 0,
                "total_cargas": int(row[1]) if row else 0,
                "media_sacas_por_carga": round(float(row[2]), 2) if row else 0.0
            }
    finally:
        conn.close()


def obter_total_sacas_por_cultura() -> list[dict[str, Any]]:
    """
    Retorna o volume total de sacas acumulado agrupado por cultura.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    c.nome AS cultura,
                    COALESCE(SUM(car.quantidade_sacas), 0) AS total_sacas
                FROM culturas c
                LEFT JOIN safras s ON s.cultura_id = c.id
                LEFT JOIN cargas car ON car.safra_id = s.id
                GROUP BY c.id, c.nome
                ORDER BY total_sacas DESC;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                {"cultura": row[0], "total_sacas": int(row[1])}
                for row in rows
            ]
    finally:
        conn.close()
