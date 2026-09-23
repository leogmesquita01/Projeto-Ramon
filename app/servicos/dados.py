from datetime import date
from typing import Any, Optional

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


# -----------------------------------------------------------------------------
# OPERAÇÕES DE CUSTOS & DESPESAS (Energia do moedor, embalagens, insumos)
# -----------------------------------------------------------------------------
def salvar_custo(safra_id: int, descricao: str, valor: float, data_custo: date) -> int:
    """
    Registra uma despesa/custo operacional da safra.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO custos (safra_id, descricao, valor, data)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (safra_id, descricao.strip(), valor, data_custo),
            )
            custo_id = cursor.fetchone()[0]
            conn.commit()
            return custo_id
    finally:
        conn.close()


def listar_ultimos_custos(
    safra_id: int,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna os custos lançados para uma safra, com filtro opcional por período.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro_data = ""
            params: list[Any] = [safra_id]
            if data_inicio and data_fim:
                filtro_data = " AND data >= %s AND data <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT id, descricao, valor, data
                FROM custos
                WHERE safra_id = %s {filtro_data}
                ORDER BY data DESC, id DESC
                LIMIT %s;
            """
            cursor.execute(query, tuple(params))
            linhas = cursor.fetchall()

            return [
                {
                    "id": linha[0],
                    "descricao": linha[1],
                    "valor": float(linha[2]),
                    "data": linha[3],
                }
                for linha in linhas
            ]
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# OPERAÇÕES DE TRABALHADORES & DIÁRIAS (Mão de obra)
# -----------------------------------------------------------------------------
def listar_trabalhadores() -> list[dict[str, Any]]:
    """
    Retorna a lista de todos os trabalhadores cadastrados.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, tipo_pagamento FROM trabalhadores ORDER BY nome ASC;")
            linhas = cursor.fetchall()
            return [
                {"id": l[0], "nome": l[1], "tipo_pagamento": l[2]}
                for l in linhas
            ]
    finally:
        conn.close()


def cadastrar_trabalhador(nome: str, tipo_pagamento: str = "diaria") -> int:
    """
    Cadastra um novo trabalhador no sistema.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trabalhadores (nome, tipo_pagamento)
                VALUES (%s, %s)
                RETURNING id;
                """,
                (nome.strip().title(), tipo_pagamento),
            )
            trabalhador_id = cursor.fetchone()[0]
            conn.commit()
            return trabalhador_id
    finally:
        conn.close()


def salvar_pagamento_trabalhador(
    trabalhador_id: int,
    safra_id: int,
    data_pagamento: date,
    valor: float,
) -> int:
    """
    Registra o pagamento de diária ou serviço feito a um trabalhador em uma safra.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pagamentos_trabalhadores (trabalhador_id, safra_id, data, valor)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (trabalhador_id, safra_id, data_pagamento, valor),
            )
            pagamento_id = cursor.fetchone()[0]
            conn.commit()
            return pagamento_id
    finally:
        conn.close()


def listar_ultimos_pagamentos(
    safra_id: int,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna o histórico de pagamentos de trabalhadores feitos em uma safra.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro_data = ""
            params: list[Any] = [safra_id]
            if data_inicio and data_fim:
                filtro_data = " AND p.data >= %s AND p.data <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT p.id, t.nome, p.valor, p.data, t.id
                FROM pagamentos_trabalhadores p
                INNER JOIN trabalhadores t ON p.trabalhador_id = t.id
                WHERE p.safra_id = %s {filtro_data}
                ORDER BY p.data DESC, p.id DESC
                LIMIT %s;
            """
            cursor.execute(query, tuple(params))
            linhas = cursor.fetchall()

            return [
                {
                    "id": l[0],
                    "trabalhador_nome": l[1],
                    "valor": float(l[2]),
                    "data": l[3],
                    "trabalhador_id": l[4],
                }
                for l in linhas
            ]
    finally:
        conn.close()
