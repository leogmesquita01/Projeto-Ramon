from datetime import date
from typing import Any, Optional

import streamlit as st
from app.database.conexao import obter_conexao


def limpar_cache_dados() -> None:
    try:
        st.cache_data.clear()
    except Exception:
        pass


CULTURAS_PADRAO = [
    "Milho",
    "Feijão",
    "Fava",
    "Jerimum",
    "Macaxeira",
    "Batata",
    "Mandioca",
    "Melancia",
    "Silagem",
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
    "Silagem": "🚜",
}


@st.cache_data(ttl=3600)
def garantir_culturas_padrao() -> None:
    """
    Garante que todas as culturas comerciais padrão existam no banco
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

    garantir_tabela_agendamentos()


def garantir_tabela_agendamentos() -> None:
    """
    Garante que a tabela agendamentos_vendas exista no banco.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agendamentos_vendas (
                    id SERIAL PRIMARY KEY,
                    safra_id INTEGER NOT NULL REFERENCES safras(id),
                    cliente_nome TEXT NOT NULL,
                    cliente_telefone TEXT,
                    data_prevista DATE NOT NULL,
                    quantidade_sacas NUMERIC NOT NULL,
                    preco_estimado_saca NUMERIC NOT NULL,
                    valor_total_estimado NUMERIC NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pendente',
                    local_entrega TEXT,
                    motorista_placa TEXT,
                    valor_adiantamento NUMERIC DEFAULT 0,
                    observacoes TEXT,
                    carga_id INTEGER REFERENCES cargas(id),
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


@st.cache_data(ttl=120)
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
    tipo_operacao: str = "venda",
) -> int:
    """
    Registra uma nova carga (venda ou compra para revenda), registrando também o preço unitário.
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

            if tipo_operacao == "compra" and quantidade_sacas == 0:
                valor_total = round(valor_por_saca, 2)
            else:
                valor_total = round(quantidade_sacas * valor_por_saca, 2)

            cursor.execute(
                """
                INSERT INTO cargas (safra_id, data, quantidade_sacas, preco_id, valor_total, tipo_operacao)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (safra_id, data_carga, quantidade_sacas, preco_id, valor_total, tipo_operacao),
            )
            carga_id = cursor.fetchone()[0]

            conn.commit()
            limpar_cache_dados()
            return carga_id
    finally:
        conn.close()


@st.cache_data(ttl=30)
def listar_ultimas_cargas(
    safra_id: Optional[int] = None,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    tipo_operacao: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Retorna as cargas cadastradas, com filtro opcional por cultura, tipo de operação e por período.
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
            if tipo_operacao is not None:
                filtro += " AND COALESCE(car.tipo_operacao, 'venda') = %s"
                params.append(tipo_operacao)
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
                    cul.nome AS cultura_nome,
                    COALESCE(car.tipo_operacao, 'venda') AS tipo_operacao
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
                    "tipo_operacao": linha[6],
                    "tipo_rotulo": "🟢 Venda" if linha[6] == "venda" else "🔵 Compra (Revenda)",
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
            limpar_cache_dados()
            return safra_id
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# OPERAÇÕES DE CUSTOS & DESPESAS (Energia, embalagens, insumos)
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
            limpar_cache_dados()
            return custo_id
    finally:
        conn.close()


@st.cache_data(ttl=30)
def listar_ultimos_custos(
    safra_id: Optional[int] = None,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna os custos lançados e também as compras de caminhões para revenda,
    com filtro opcional por cultura e por período.
    Se safra_id for None, traz todos os custos consolidados.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro_c = "WHERE 1=1"
            filtro_car = "WHERE car.tipo_operacao = 'compra'"
            params_c: list[Any] = []
            params_car: list[Any] = []

            if safra_id is not None:
                filtro_c += " AND c.safra_id = %s"
                params_c.append(safra_id)
                filtro_car += " AND car.safra_id = %s"
                params_car.append(safra_id)
            if data_inicio and data_fim:
                filtro_c += " AND c.data >= %s AND c.data <= %s"
                params_c.extend([data_inicio, data_fim])
                filtro_car += " AND car.data >= %s AND car.data <= %s"
                params_car.extend([data_inicio, data_fim])

            query = f"""
                SELECT 
                    c.id, 
                    c.descricao, 
                    c.valor, 
                    c.data, 
                    cul.nome
                FROM custos c
                LEFT JOIN safras s ON c.safra_id = s.id
                LEFT JOIN culturas cul ON s.cultura_id = cul.id
                {filtro_c}

                UNION ALL

                SELECT 
                    car.id, 
                    CASE 
                        WHEN car.quantidade_sacas > 0 THEN CONCAT('🚚 Compra de Caminhão (', CAST(car.quantidade_sacas AS INTEGER), ' sacas)')
                        ELSE CONCAT('🚚 Compra de Caminhão / Carrada (', cul.nome, ')')
                    END, 
                    COALESCE(car.valor_total, p.valor_por_saca, 0), 
                    car.data, 
                    cul.nome
                FROM cargas car
                LEFT JOIN safras s ON car.safra_id = s.id
                LEFT JOIN culturas cul ON s.cultura_id = cul.id
                LEFT JOIN precos p ON car.preco_id = p.id
                {filtro_car}

                ORDER BY data DESC, id DESC
                LIMIT %s;
            """
            params_total = params_c + params_car + [limite]
            cursor.execute(query, tuple(params_total))
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
@st.cache_data(ttl=60)
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
            limpar_cache_dados()
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
            limpar_cache_dados()
            return pagamento_id
    finally:
        conn.close()


@st.cache_data(ttl=30)
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


# -----------------------------------------------------------------------------
# OPERAÇÕES DE CONTROLE DE ESTOQUE (Entradas de Colheita, Armazém & Baixas)
# -----------------------------------------------------------------------------
def salvar_movimentacao_estoque(
    safra_id: int,
    tipo: str,
    data_mov: date,
    quantidade_sacas: float,
    local_armazenamento: str = "",
    observacao: str = "",
) -> int:
    """
    Registra uma movimentação no estoque (ex: 'entrada' de colheita, 'perda', 'consumo').
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO estoque_movimentacoes (safra_id, tipo, data, quantidade_sacas, local_armazenamento, observacao)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (safra_id, tipo, data_mov, quantidade_sacas, local_armazenamento.strip(), observacao.strip()),
            )
            mov_id = cursor.fetchone()[0]
            conn.commit()
            limpar_cache_dados()
            return mov_id
    finally:
        conn.close()


@st.cache_data(ttl=30)
def listar_movimentacoes_estoque(
    safra_id: Optional[int] = None,
    tipo: Optional[str] = None,
    limite: int = 50,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Retorna o histórico de movimentações manuais de estoque (entradas de colheita, perdas, etc).
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro = "WHERE 1=1"
            params: list[Any] = []
            if safra_id is not None:
                filtro += " AND em.safra_id = %s"
                params.append(safra_id)
            if tipo:
                filtro += " AND em.tipo = %s"
                params.append(tipo)
            if data_inicio and data_fim:
                filtro += " AND em.data >= %s AND em.data <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT 
                    em.id,
                    em.safra_id,
                    em.tipo,
                    em.data,
                    em.quantidade_sacas,
                    em.local_armazenamento,
                    em.observacao,
                    cul.nome AS cultura_nome
                FROM estoque_movimentacoes em
                INNER JOIN safras s ON em.safra_id = s.id
                INNER JOIN culturas cul ON s.cultura_id = cul.id
                {filtro}
                ORDER BY em.data DESC, em.id DESC
                LIMIT %s;
            """
            cursor.execute(query, tuple(params))
            linhas = cursor.fetchall()

            tipo_rotulos = {
                "entrada": "📥 Entrada (Colheita)",
                "perda": "⚠️ Perda / Avaria",
                "consumo": "🍽️ Consumo Próprio",
            }

            return [
                {
                    "id": l[0],
                    "safra_id": l[1],
                    "tipo": l[2],
                    "tipo_rotulo": tipo_rotulos.get(l[2], l[2]),
                    "data": l[3],
                    "quantidade_sacas": float(l[4]),
                    "local_armazenamento": l[5] or "Galpão Principal",
                    "observacao": l[6] or "",
                    "cultura_nome": l[7],
                    "icone": ICONES_CULTURAS.get(l[7], "🌾"),
                }
                for l in linhas
            ]
    finally:
        conn.close()


@st.cache_data(ttl=30)
def obter_resumo_estoque(safra_id: Optional[int] = None) -> list[dict[str, Any]]:
    """
    Calcula o saldo de estoque atual por cultura:
    Saldo = (Total Entradas de Colheita) - (Total Cargas Vendidas) - (Total Perdas/Consumo)
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro_safra = ""
            params: list[Any] = []
            if safra_id is not None:
                filtro_safra = "WHERE s.id = %s"
                params.append(safra_id)

            query = f"""
                SELECT 
                    s.id AS safra_id,
                    cul.id AS cultura_id,
                    cul.nome AS cultura_nome,
                    COALESCE((
                        SELECT SUM(em.quantidade_sacas) 
                        FROM estoque_movimentacoes em 
                        WHERE em.safra_id = s.id AND em.tipo = 'entrada'
                    ), 0) AS total_entradas,
                    COALESCE((
                        SELECT SUM(car.quantidade_sacas) 
                        FROM cargas car 
                        WHERE car.safra_id = s.id AND COALESCE(car.tipo_operacao, 'venda') = 'venda'
                    ), 0) AS total_vendidas,
                    COALESCE((
                        SELECT SUM(em.quantidade_sacas) 
                        FROM estoque_movimentacoes em 
                        WHERE em.safra_id = s.id AND em.tipo IN ('perda', 'consumo')
                    ), 0) AS total_baixas,
                    COALESCE((
                        SELECT SUM(car.quantidade_sacas) 
                        FROM cargas car 
                        WHERE car.safra_id = s.id AND car.tipo_operacao = 'compra'
                    ), 0) AS total_compras
                FROM safras s
                INNER JOIN culturas cul ON s.cultura_id = cul.id
                {filtro_safra}
                ORDER BY cul.nome ASC;
            """
            cursor.execute(query, tuple(params))
            linhas = cursor.fetchall()

            resumo = []
            for l in linhas:
                sid, cid, nome, entradas, vendidas, baixas, compras = l
                entradas = float(entradas)
                vendidas = float(vendidas)
                baixas = float(baixas)
                compras = float(compras)
                # O saldo físico disponível em mãos = (Colheitas + Compras p/ Revenda) - Vendas - Baixas
                saldo = max(0.0, (entradas + compras) - vendidas - baixas)
                resumo.append({
                    "safra_id": sid,
                    "cultura_id": cid,
                    "cultura_nome": nome,
                    "icone": ICONES_CULTURAS.get(nome, "🌾"),
                    "total_entradas": entradas,
                    "total_compras": compras,
                    "total_vendidas": vendidas,
                    "total_baixas": baixas,
                    "saldo_disponivel": saldo,
                })
            return resumo
    finally:
        conn.close()


def limpar_dados_teste() -> dict[str, int]:
    """
    Remove todos os registros de teste de cargas, pagamentos de trabalhadores,
    custos, estoque, trabalhadores, agendamentos e precos avulsos, mantendo intactas as culturas e safras.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM estoque_movimentacoes;")
            estoque_del = cursor.rowcount
            cursor.execute("DELETE FROM agendamentos_vendas;")
            agendamentos_del = cursor.rowcount
            cursor.execute("DELETE FROM cargas;")
            cargas_del = cursor.rowcount
            cursor.execute("DELETE FROM pagamentos_trabalhadores;")
            pagamentos_del = cursor.rowcount
            cursor.execute("DELETE FROM custos;")
            custos_del = cursor.rowcount
            cursor.execute("DELETE FROM trabalhadores;")
            trab_del = cursor.rowcount
            cursor.execute("DELETE FROM precos;")
            precos_del = cursor.rowcount
            conn.commit()
            limpar_cache_dados()
            return {
                "estoque": estoque_del,
                "agendamentos": agendamentos_del,
                "cargas": cargas_del,
                "pagamentos": pagamentos_del,
                "custos": custos_del,
                "trabalhadores": trab_del,
                "precos": precos_del,
            }
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# OPERAÇÕES DE AGENDAMENTO DE VENDAS (Compromissos, Entregas Futuras & Pedidos)
# -----------------------------------------------------------------------------
def salvar_agendamento(
    safra_id: int,
    cliente_nome: str,
    data_prevista: date,
    quantidade_sacas: float,
    preco_estimado_saca: float,
    status: str = "pendente",
    cliente_telefone: str = "",
    local_entrega: str = "",
    motorista_placa: str = "",
    valor_adiantamento: float = 0.0,
    observacoes: str = "",
) -> int:
    """
    Registra um novo agendamento ou pedido futuro de venda.
    """
    valor_total_estimado = round(quantidade_sacas * preco_estimado_saca, 2)
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agendamentos_vendas (
                    safra_id, cliente_nome, cliente_telefone, data_prevista,
                    quantidade_sacas, preco_estimado_saca, valor_total_estimado,
                    status, local_entrega, motorista_placa, valor_adiantamento,
                    observacoes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    safra_id,
                    cliente_nome.strip(),
                    cliente_telefone.strip(),
                    data_prevista,
                    quantidade_sacas,
                    preco_estimado_saca,
                    valor_total_estimado,
                    status,
                    local_entrega.strip(),
                    motorista_placa.strip().upper(),
                    valor_adiantamento,
                    observacoes.strip(),
                ),
            )
            agendamento_id = cursor.fetchone()[0]
            conn.commit()
            limpar_cache_dados()
            return agendamento_id
    finally:
        conn.close()


def atualizar_status_agendamento(agendamento_id: int, novo_status: str) -> None:
    """
    Atualiza o status de um agendamento (ex: 'pendente', 'confirmado', 'cancelado').
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE agendamentos_vendas SET status = %s WHERE id = %s;",
                (novo_status, agendamento_id),
            )
            conn.commit()
            limpar_cache_dados()
    finally:
        conn.close()


def efetivar_agendamento_como_carga(
    agendamento_id: int,
    data_carga: date,
    quantidade_sacas: int,
    valor_por_saca: float,
) -> int:
    """
    Converte um agendamento em uma Carga efetivamente vendida:
    - Cadastra o preço e a carga no sistema (impactando Meu Bolso e Estoque).
    - Atualiza o agendamento para 'concluido' com o vínculo da carga_id.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            # Recupera os dados da safra e cultura do agendamento
            cursor.execute(
                """
                SELECT a.safra_id, s.cultura_id
                FROM agendamentos_vendas a
                INNER JOIN safras s ON a.safra_id = s.id
                WHERE a.id = %s;
                """,
                (agendamento_id,),
            )
            res = cursor.fetchone()
            if not res:
                raise ValueError("Agendamento não encontrado.")
            safra_id, cultura_id = res

            # Registra preço
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

            # Registra carga
            cursor.execute(
                """
                INSERT INTO cargas (safra_id, data, quantidade_sacas, preco_id, valor_total, tipo_operacao)
                VALUES (%s, %s, %s, %s, %s, 'venda')
                RETURNING id;
                """,
                (safra_id, data_carga, quantidade_sacas, preco_id, valor_total),
            )
            carga_id = cursor.fetchone()[0]

            # Atualiza status e vincula carga ao agendamento
            cursor.execute(
                """
                UPDATE agendamentos_vendas
                SET status = 'concluido',
                    carga_id = %s
                WHERE id = %s;
                """,
                (carga_id, agendamento_id),
            )
            conn.commit()
            limpar_cache_dados()
            return carga_id
    finally:
        conn.close()


def excluir_agendamento(agendamento_id: int) -> None:
    """
    Remove definitivamente um agendamento do banco de dados.
    """
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM agendamentos_vendas WHERE id = %s;", (agendamento_id,))
            conn.commit()
            limpar_cache_dados()
    finally:
        conn.close()


@st.cache_data(ttl=30)
def listar_agendamentos(
    safra_id: Optional[int] = None,
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limite: int = 100,
) -> list[dict[str, Any]]:
    """
    Retorna a lista de agendamentos de vendas com filtros opcionais por safra/cultura, status e data.
    """
    garantir_tabela_agendamentos()
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            filtro = "WHERE 1=1"
            params: list[Any] = []
            if safra_id is not None:
                filtro += " AND a.safra_id = %s"
                params.append(safra_id)
            if status is not None and status != "todos":
                filtro += " AND a.status = %s"
                params.append(status)
            if data_inicio and data_fim:
                filtro += " AND a.data_prevista >= %s AND a.data_prevista <= %s"
                params.extend([data_inicio, data_fim])
            params.append(limite)

            query = f"""
                SELECT 
                    a.id,
                    a.safra_id,
                    a.cliente_nome,
                    COALESCE(a.cliente_telefone, ''),
                    a.data_prevista,
                    a.quantidade_sacas,
                    a.preco_estimado_saca,
                    a.valor_total_estimado,
                    a.status,
                    COALESCE(a.local_entrega, ''),
                    COALESCE(a.motorista_placa, ''),
                    COALESCE(a.valor_adiantamento, 0),
                    COALESCE(a.observacoes, ''),
                    a.carga_id,
                    cul.nome AS cultura_nome
                FROM agendamentos_vendas a
                INNER JOIN safras s ON a.safra_id = s.id
                INNER JOIN culturas cul ON s.cultura_id = cul.id
                {filtro}
                ORDER BY a.data_prevista ASC, a.id ASC
                LIMIT %s;
            """
            cursor.execute(query, tuple(params))
            linhas = cursor.fetchall()

            status_rotulos = {
                "pendente": "🟡 Pendente",
                "confirmado": "🔵 Confirmado",
                "concluido": "🟢 Concluído",
                "cancelado": "❌ Cancelado",
            }

            return [
                {
                    "id": l[0],
                    "safra_id": l[1],
                    "cliente_nome": l[2],
                    "cliente_telefone": l[3],
                    "data_prevista": l[4],
                    "quantidade_sacas": float(l[5]),
                    "preco_estimado_saca": float(l[6]),
                    "valor_total_estimado": float(l[7]),
                    "status": l[8],
                    "status_rotulo": status_rotulos.get(l[8], l[8]),
                    "local_entrega": l[9],
                    "motorista_placa": l[10],
                    "valor_adiantamento": float(l[11]),
                    "observacoes": l[12],
                    "carga_id": l[13],
                    "cultura_nome": l[14],
                    "icone": ICONES_CULTURAS.get(l[14], "🌾"),
                }
                for l in linhas
            ]
    finally:
        conn.close()


@st.cache_data(ttl=30)
def obter_resumo_agenda() -> dict[str, Any]:
    """
    Retorna métricas consolidadas dos agendamentos em aberto (pendentes ou confirmados).
    """
    garantir_tabela_agendamentos()
    conn = obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN status IN ('pendente', 'confirmado') THEN quantidade_sacas ELSE 0 END), 0) AS sacas_abertas,
                    COALESCE(SUM(CASE WHEN status IN ('pendente', 'confirmado') THEN valor_total_estimado ELSE 0 END), 0) AS faturamento_previsto,
                    COALESCE(SUM(CASE WHEN status IN ('pendente', 'confirmado') THEN valor_adiantamento ELSE 0 END), 0) AS total_adiantamento,
                    COALESCE(COUNT(CASE WHEN status IN ('pendente', 'confirmado') AND data_prevista BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days' THEN 1 END), 0) AS proximos_7_dias,
                    COALESCE(COUNT(CASE WHEN status IN ('pendente', 'confirmado') THEN 1 END), 0) AS total_abertos
                FROM agendamentos_vendas;
                """
            )
            row = cursor.fetchone()
            return {
                "sacas_abertas": float(row[0]),
                "faturamento_previsto": float(row[1]),
                "total_adiantamento": float(row[2]),
                "proximos_7_dias": int(row[3]),
                "total_abertos": int(row[4]),
            }
    finally:
        conn.close()



