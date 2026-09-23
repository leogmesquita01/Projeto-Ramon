from datetime import date
from typing import Any, Optional

from app.database.conexao import obter_conexao


def obter_resumo_financeiro_safra(
    safra_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> dict[str, Any]:
    """
    Calcula a receita bruta, custos operacionais, mão de obra, lucro líquido
    e margem de lucro. Se safra_id for None, consolida TODAS as culturas (Bolso Geral).

    :param safra_id: ID da safra/cultura específica (opcional, None para todas).
    :param data_inicio: Data inicial do período (opcional).
    :param data_fim: Data final do período (opcional).
    :return: Dicionário com os totais financeiros e a margem de lucro.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            # 1. Filtro dinâmico para receita (cargas)
            filtro_cargas = "WHERE 1=1"
            params_receita: list[Any] = []
            if safra_id is not None:
                filtro_cargas += " AND car.safra_id = %s"
                params_receita.append(safra_id)
            if data_inicio and data_fim:
                filtro_cargas += " AND car.data >= %s AND car.data <= %s"
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
                {filtro_cargas};
            """
            cursor.execute(query_receita, tuple(params_receita))
            receita_bruta = float(cursor.fetchone()[0])

            # 2. Filtro dinâmico para custos
            filtro_custos = "WHERE 1=1"
            params_custos: list[Any] = []
            if safra_id is not None:
                filtro_custos += " AND safra_id = %s"
                params_custos.append(safra_id)
            if data_inicio and data_fim:
                filtro_custos += " AND data >= %s AND data <= %s"
                params_custos.extend([data_inicio, data_fim])

            query_custos = f"""
                SELECT COALESCE(SUM(valor), 0)
                FROM custos
                {filtro_custos};
            """
            cursor.execute(query_custos, tuple(params_custos))
            custos_operacionais = float(cursor.fetchone()[0])

            # 3. Filtro dinâmico para mão de obra
            filtro_mo = "WHERE 1=1"
            params_mo: list[Any] = []
            if safra_id is not None:
                filtro_mo += " AND safra_id = %s"
                params_mo.append(safra_id)
            if data_inicio and data_fim:
                filtro_mo += " AND data >= %s AND data <= %s"
                params_mo.extend([data_inicio, data_fim])

            query_mao_de_obra = f"""
                SELECT COALESCE(SUM(valor), 0)
                FROM pagamentos_trabalhadores
                {filtro_mo};
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


def obter_vendas_por_cultura(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna o volume total de vendas e quantidade de sacas agrupadas por produto no período.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro = "WHERE 1=1"
            params: list[Any] = []
            if data_inicio and data_fim:
                filtro += " AND car.data >= %s AND car.data <= %s"
                params.extend([data_inicio, data_fim])

            query = f"""
                SELECT 
                    cul.nome AS cultura,
                    COALESCE(SUM(car.quantidade_sacas), 0) AS total_sacas,
                    COALESCE(SUM(
                        CASE 
                            WHEN car.valor_total IS NOT NULL THEN car.valor_total
                            WHEN p.valor_por_saca IS NOT NULL THEN car.quantidade_sacas * p.valor_por_saca
                            ELSE 0
                        END
                    ), 0) AS total_valor,
                    COUNT(car.id) AS total_cargas
                FROM cargas car
                INNER JOIN safras s ON car.safra_id = s.id
                INNER JOIN culturas cul ON s.cultura_id = cul.id
                LEFT JOIN precos p ON car.preco_id = p.id
                {filtro}
                GROUP BY cul.id, cul.nome
                ORDER BY total_valor DESC;
            """
            cursor.execute(query, tuple(params))
            linhas = cursor.fetchall()
            return [
                {
                    "cultura": l[0],
                    "total_sacas": int(l[1]),
                    "total_valor": float(l[2]),
                    "total_cargas": int(l[3]),
                }
                for l in linhas
            ]
    finally:
        conn.close()


def obter_historico_precos_cultura(cultura_id: int) -> list[dict[str, Any]]:
    """
    Retorna o histórico de preços por saca de uma cultura ordenado por data.
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
