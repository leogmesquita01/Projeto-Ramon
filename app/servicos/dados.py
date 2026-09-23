from datetime import date
from typing import Any

from app.database.conexao import obter_conexao


def listar_safras_ativas() -> list[dict[str, Any]]:
    """
    Retorna a lista de safras em andamento ou cadastradas no banco,
    com o nome da respectiva cultura para exibição no formulário.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    s.id,
                    c.nome AS cultura_nome,
                    s.data_inicio,
                    s.status,
                    c.id AS cultura_id
                FROM safras s
                INNER JOIN culturas c ON s.cultura_id = c.id
                ORDER BY s.id DESC;
            """
            cursor.execute(query)
            linhas = cursor.fetchall()

            return [
                {
                    "id": linha[0],
                    "cultura_nome": linha[1],
                    "data_inicio": linha[2],
                    "status": linha[3],
                    "cultura_id": linha[4],
                    "rotulo": f"#{linha[0]} - {linha[1]} (Início: {linha[2].strftime('%d/%m/%Y') if hasattr(linha[2], 'strftime') else linha[2]})",
                }
                for linha in linhas
            ]
    finally:
        conn.close()


def salvar_carga(
    safra_id: int,
    cultura_id: int,
    data_carga: date,
    quantidade_sacas: int,
    valor_por_saca: float,
) -> int:
    """
    Registra uma nova carga colhida/vendida, registrando também o preço unitário.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            # 1. Registra o preço praticado nesta data para a cultura
            cursor.execute(
                """
                INSERT INTO precos (cultura_id, data, valor_por_saca)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (cultura_id, data_carga, valor_por_saca),
            )
            preco_id = cursor.fetchone()[0]

            valor_total = round(quantidade_sacas * valor_por_saca, 2)

            # 2. Registra a carga vinculada à safra e ao preço
            cursor.execute(
                """
                INSERT INTO cargas (safra_id, data, quantidade_sacas, preco_id, valor_total)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (safra_id, data_carga, quantidade_sacas, preco_id, valor_total),
            )
            carga_id = cursor.fetchone()[0]

            conn.commit()
            return carga_id
    finally:
        conn.close()


def listar_ultimas_cargas(
    safra_id: int,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna as cargas cadastradas para uma safra específica, com filtro opcional por período.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro_data = ""
            params: list[Any] = [safra_id]
            if data_inicio and data_fim:
                filtro_data = " AND car.data >= %s AND car.data <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT 
                    car.id,
                    car.data,
                    car.quantidade_sacas,
                    COALESCE(p.valor_por_saca, 0) AS valor_por_saca,
                    COALESCE(car.valor_total, car.quantidade_sacas * COALESCE(p.valor_por_saca, 0)) AS valor_total
                FROM cargas car
                LEFT JOIN precos p ON car.preco_id = p.id
                WHERE car.safra_id = %s {filtro_data}
                ORDER BY car.data DESC, car.id DESC
                LIMIT %s;
            """
            cursor.execute(query, tuple(params))
            linhas = cursor.fetchall()

            return [
                {
                    "id": linha[0],
                    "data": linha[1],
                    "quantidade_sacas": int(linha[2]),
                    "valor_por_saca": float(linha[3]),
                    "valor_total": float(linha[4]),
                }
                for linha in linhas
            ]
    finally:
        conn.close()


def criar_safra_rapida(nome_cultura: str, data_inicio: date) -> int:
    """
    Cria uma cultura (se não existir) e abre uma nova safra imediatamente.
    Útil para inicialização rápida sem complicação.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO culturas (nome)
                VALUES (%s)
                ON CONFLICT (nome) DO UPDATE SET nome = EXCLUDED.nome
                RETURNING id;
                """,
                (nome_cultura.strip().capitalize(),),
            )
            cultura_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO safras (cultura_id, data_inicio, status)
                VALUES (%s, %s, 'em_andamento')
                RETURNING id;
                """,
                (cultura_id, data_inicio),
            )
            safra_id = cursor.fetchone()[0]

            conn.commit()
            return safra_id
    finally:
        conn.close()
