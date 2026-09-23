from datetime import date
from typing import Any, Optional

from app.database.conexao import obter_conexao


def obter_resumo_financeiro_safra(
    safra_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> dict[str, Any]:
    """
    Calcula a receita bruta, custos operacionais, mão de obra, lucro líquido
    e margem de lucro para uma safra específica, com filtro opcional por período.

    :param safra_id: ID da safra a ser calculada.
    :param data_inicio: Data inicial do período (opcional).
    :param data_fim: Data final do período (opcional).
    :return: Dicionário com os totais financeiros e a margem de lucro.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            # 1. Filtro dinâmico para receita (cargas)
            filtro_data_cargas = ""
            params_receita: list[Any] = [safra_id]
            if data_inicio and data_fim:
                filtro_data_cargas = " AND car.data >= %s AND car.data <= %s"
                params_receita.extend([data_inicio, data_fim])

            query_receita = f"""
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN car.valor_total IS NOT NULL THEN car.valor_total
                        WHEN p.valor_por_saca IS NOT NULL THEN car.quantidade_sacas * p.valor_por_saca
                        ELSE 0
                    END
                ), 0) AS receita_bruta
                FROM cargas car
                LEFT JOIN precos p ON car.preco_id = p.id
                WHERE car.safra_id = %s {filtro_data_cargas};
            """
            cursor.execute(query_receita, tuple(params_receita))
            receita_bruta = float(cursor.fetchone()[0])

            # 2. Filtro dinâmico para custos
            filtro_data_custos = ""
            params_custos: list[Any] = [safra_id]
            if data_inicio and data_fim:
                filtro_data_custos = " AND data >= %s AND data <= %s"
                params_custos.extend([data_inicio, data_fim])

            query_custos = f"""
                SELECT COALESCE(SUM(valor), 0)
                FROM custos
                WHERE safra_id = %s {filtro_data_custos};
            """
            cursor.execute(query_custos, tuple(params_custos))
            custos_operacionais = float(cursor.fetchone()[0])

            # 3. Filtro dinâmico para mão de obra
            filtro_data_mo = ""
            params_mo: list[Any] = [safra_id]
            if data_inicio and data_fim:
                filtro_data_mo = " AND data >= %s AND data <= %s"
                params_mo.extend([data_inicio, data_fim])

            query_mao_de_obra = f"""
                SELECT COALESCE(SUM(valor), 0)
                FROM pagamentos_trabalhadores
                WHERE safra_id = %s {filtro_data_mo};
            """
            cursor.execute(query_mao_de_obra, tuple(params_mo))
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
