from typing import Any

from app.database.conexao import obter_conexao


def obter_resumo_sacas_safra(safra_id: int) -> dict[str, Any]:
    """
    Calcula o total de sacas e métricas de transporte para uma safra específica.
    
    :param safra_id: ID da safra a ser consultada.
    :return: Dicionário contendo:
        - total_sacas: Soma total de sacas colhidas/transportadas.
        - total_cargas: Quantidade de viagens/cargas registradas.
        - media_sacas_por_carga: Média de sacas carregadas por viagem.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    COALESCE(SUM(quantidade_sacas), 0) AS total_sacas,
                    COUNT(id) AS total_cargas,
                    COALESCE(AVG(quantidade_sacas), 0) AS media_sacas_por_carga
                FROM cargas
                WHERE safra_id = %s;
            """
            cursor.execute(query, (safra_id,))
            row = cursor.fetchone()
            
            return {
                "safra_id": safra_id,
                "total_sacas": float(row[0]) if row else 0.0,
                "total_cargas": int(row[1]) if row else 0,
                "media_sacas_por_carga": round(float(row[2]), 2) if row else 0.0
            }
    finally:
        conn.close()


def obter_total_sacas_por_cultura() -> list[dict[str, Any]]:
    """
    Retorna o volume total de sacas acumulado agrupado por cultura.
    
    :return: Lista de dicionários contendo o nome da cultura e o total de sacas.
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
                {"cultura": row[0], "total_sacas": float(row[1])}
                for row in rows
            ]
    finally:
        conn.close()
