from typing import Any

from app.database.conexao import obter_conexao


def obter_resumo_financeiro_safra(safra_id: int) -> dict[str, Any]:
    """
    Calcula a receita bruta, custos operacionais, mão de obra, lucro líquido
    e margem de lucro para uma safra específica.

    :param safra_id: ID da safra a ser calculada.
    :return: Dicionário com os totais financeiros e a margem de lucro.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            query_receita = """
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN car.valor_total IS NOT NULL THEN car.valor_total
                        WHEN p.valor_por_saca IS NOT NULL THEN car.quantidade_sacas * p.valor_por_saca
                        ELSE 0
                    END
                ), 0) AS receita_bruta
                FROM cargas car
                LEFT JOIN precos p ON car.preco_id = p.id
                WHERE car.safra_id = %s;
            """
            cursor.execute(query_receita, (safra_id,))
            receita_bruta = float(cursor.fetchone()[0])

            query_custos = """
                SELECT COALESCE(SUM(valor), 0)
                FROM custos
                WHERE safra_id = %s;
            """
            cursor.execute(query_custos, (safra_id,))
            custos_operacionais = float(cursor.fetchone()[0])

            query_mao_de_obra = """
                SELECT COALESCE(SUM(valor), 0)
                FROM pagamentos_trabalhadores
                WHERE safra_id = %s;
            """
            cursor.execute(query_mao_de_obra, (safra_id,))
            custos_mao_de_obra = float(cursor.fetchone()[0])

            custo_total = custos_operacionais + custos_mao_de_obra
            lucro_liquido = receita_bruta - custo_total

            margem_lucro_pct = (
                round((lucro_liquido / receita_bruta) * 100, 2)
                if receita_bruta > 0
                else 0.0
            )

            return {
                "safra_id": safra_id,
                "receita_bruta": round(receita_bruta, 2),
                "custos_operacionais": round(custos_operacionais, 2),
                "custos_mao_de_obra": round(custos_mao_de_obra, 2),
                "custo_total": round(custo_total, 2),
                "lucro_liquido": round(lucro_liquido, 2),
                "margem_lucro_pct": margem_lucro_pct,
            }
    finally:
        conn.close()


def obter_historico_precos_cultura(cultura_id: int) -> list[dict[str, Any]]:
    """
    Retorna o histórico de preços por saca de uma cultura ordenado por data.

    :param cultura_id: ID da cultura.
    :return: Lista de dicionários com data e valor por saca.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT data, valor_por_saca
                FROM precos
                WHERE cultura_id = %s
                ORDER BY data ASC;
            """
            cursor.execute(query, (cultura_id,))
            rows = cursor.fetchall()

            return [
                {
                    "data": str(row[0]),
                    "valor_por_saca": float(row[1]),
                }
                for row in rows
            ]
    finally:
        conn.close()
