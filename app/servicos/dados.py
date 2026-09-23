from datetime import date
from typing import Any, Optional

from app.database.conexao import obter_conexao


CULTURAS_PADRAO = [
    "Milho",
    "Feijão",
    "Fava",
    "Jerimum",
    "Macaxeira",
    "Batata",
    "Mandioca",
    "Melancia",
]

ICONES_CULTURAS = {
    "Milho": "🌽",
    "Feijão": "🌱",
    "Fava": "🌿",
    "Jerimum": "🎃",
    "Macaxeira": "🥔",
    "Batata": "🥔",
    "Mandioca": "🍠",
    "Melancia": "🍉",
}


def garantir_culturas_padrao() -> None:
    """
    Garante que todas as 8 culturas comerciais padrão existam no banco
    e tenham um registro ativo de controle para vendas.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            for cultura in CULTURAS_PADRAO:
                cursor.execute(
                    """
                    INSERT INTO culturas (nome)
                    VALUES (%s)
                    ON CONFLICT (nome) DO UPDATE SET nome = EXCLUDED.nome
                    RETURNING id;
                    """,
                    (cultura,),
                )
                cultura_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT id FROM safras WHERE cultura_id = %s LIMIT 1;
                    """,
                    (cultura_id,),
                )
                safra_existente = cursor.fetchone()
                if not safra_existente:
                    cursor.execute(
                        """
                        INSERT INTO safras (cultura_id, data_inicio, status)
                        VALUES (%s, CURRENT_DATE, 'em_andamento');
                        """,
                        (cultura_id,),
                    )
            conn.commit()
    except Exception:
        # Se houver qualquer falha transitória, segue a execução normal
        pass
    finally:
        conn.close()


def listar_safras_ativas() -> list[dict[str, Any]]:
    """
    Retorna a lista de culturas/produtos comerciais ativos no banco,
    com ícones representativos para facilitar a seleção.
    """
    # Garante que as 8 culturas padrão estejam cadastradas
    garantir_culturas_padrao()

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
                ORDER BY c.nome ASC;
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
                    "icone": ICONES_CULTURAS.get(linha[1], "🌾"),
                    "rotulo": f"{ICONES_CULTURAS.get(linha[1], '🌾')} {linha[1]}",
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
    safra_id: Optional[int] = None,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna as cargas cadastradas, com filtro opcional por cultura e por período.
    Se safra_id for None, traz as cargas de todas as culturas.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro = "WHERE 1=1"
            params: list[Any] = []
            if safra_id is not None:
                filtro += " AND car.safra_id = %s"
                params.append(safra_id)
            if data_inicio and data_fim:
                filtro += " AND car.data >= %s AND car.data <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT 
                    car.id,
                    car.data,
                    car.quantidade_sacas,
                    COALESCE(p.valor_por_saca, 0) AS valor_por_saca,
                    COALESCE(car.valor_total, car.quantidade_sacas * COALESCE(p.valor_por_saca, 0)) AS valor_total,
                    cul.nome AS cultura_nome
                FROM cargas car
                INNER JOIN safras s ON car.safra_id = s.id
                INNER JOIN culturas cul ON s.cultura_id = cul.id
                LEFT JOIN precos p ON car.preco_id = p.id
                {filtro}
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
                    "cultura_nome": linha[5],
                    "icone": ICONES_CULTURAS.get(linha[5], "🌾"),
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
    safra_id: Optional[int] = None,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna os custos lançados, com filtro opcional por cultura e por período.
    Se safra_id for None, traz todos os custos consolidados.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro = "WHERE 1=1"
            params: list[Any] = []
            if safra_id is not None:
                filtro += " AND c.safra_id = %s"
                params.append(safra_id)
            if data_inicio and data_fim:
                filtro += " AND c.data >= %s AND c.data <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT c.id, c.descricao, c.valor, c.data, cul.nome
                FROM custos c
                LEFT JOIN safras s ON c.safra_id = s.id
                LEFT JOIN culturas cul ON s.cultura_id = cul.id
                {filtro}
                ORDER BY c.data DESC, c.id DESC
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
                    "cultura_nome": linha[4] if linha[4] else "Geral",
                    "icone": ICONES_CULTURAS.get(linha[4], "🌾"),
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
    safra_id: Optional[int] = None,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna o histórico de pagamentos de trabalhadores, com filtro opcional por cultura e por período.
    Se safra_id for None, traz todos os pagamentos consolidados.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro = "WHERE 1=1"
            params: list[Any] = []
            if safra_id is not None:
                filtro += " AND p.safra_id = %s"
                params.append(safra_id)
            if data_inicio and data_fim:
                filtro += " AND p.data >= %s AND p.data <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT p.id, t.nome, p.valor, p.data, t.id, cul.nome
                FROM pagamentos_trabalhadores p
                INNER JOIN trabalhadores t ON p.trabalhador_id = t.id
                LEFT JOIN safras s ON p.safra_id = s.id
                LEFT JOIN culturas cul ON s.cultura_id = cul.id
                {filtro}
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
                    "cultura_nome": l[5] if l[5] else "Geral",
                    "icone": ICONES_CULTURAS.get(l[5], "🌾"),
                }
                for l in linhas
            ]
    finally:
        conn.close()
