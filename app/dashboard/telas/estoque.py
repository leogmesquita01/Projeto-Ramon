from datetime import date
from typing import Any

import streamlit as st
from app.servicos.dados import (
    listar_movimentacoes_estoque,
    obter_resumo_estoque,
    salvar_movimentacao_estoque,
)


def renderizar_tela_estoque(
    safras: list[dict[str, Any]],
    opcoes_safras: dict[str, dict[str, Any]],
) -> None:
    """
    Renderiza a tela 'Controle de Estoque' com saldos por cultura,
    formulários espelhados de entrada e baixa, e histórico de movimentações.
    """
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                📦 Controle de Estoque
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        resumo_est = obter_resumo_estoque()
    except Exception as e:
        st.error(f"Erro ao carregar dados do estoque: {e}")
        resumo_est = []

    # Cálculos Consolidados Gerais
    total_geral_colhido = sum(r["total_entradas"] for r in resumo_est)
    total_geral_compras = sum(r.get("total_compras", 0) for r in resumo_est)
    total_geral_vendido = sum(r["total_vendidas"] for r in resumo_est)
    total_geral_baixas = sum(r["total_baixas"] for r in resumo_est)
    saldo_geral_disponivel = sum(r["saldo_disponivel"] for r in resumo_est)

    # 4 Cartões de Métricas no Topo
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="agro-card" style="border: 2px solid #10B981;">
                <span style="color: #34D399; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">📦 Saldo Geral Disponível</span>
                <h2 style="color: #F8FAFC; margin: 0.4rem 0 0 0; font-size: 1.8rem; font-weight: 800;">
                    {int(saldo_geral_disponivel):,} sacas
                </h2>
                <span style="color: #A7F3D0; font-size: 0.8rem;">Prontas para comercialização</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="agro-card">
                <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">📥 Entradas no Galpão</span>
                <h2 style="color: #60A5FA; margin: 0.4rem 0 0 0; font-size: 1.6rem; font-weight: 800;">
                    {int(total_geral_colhido + total_geral_compras):,} sacas
                </h2>
                <span style="color: #64748B; font-size: 0.8rem;">{int(total_geral_colhido)} colhidas + {int(total_geral_compras)} compradas</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="agro-card">
                <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">🚛 Total Despachado / Vendas</span>
                <h2 style="color: #FBBF24; margin: 0.4rem 0 0 0; font-size: 1.6rem; font-weight: 800;">
                    {int(total_geral_vendido):,} sacas
                </h2>
                <span style="color: #64748B; font-size: 0.8rem;">Saídas via caminhões de venda</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="agro-card">
                <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">⚠️ Perdas / Consumo Próprio</span>
                <h2 style="color: #F87171; margin: 0.4rem 0 0 0; font-size: 1.6rem; font-weight: 800;">
                    {int(total_geral_baixas):,} sacas
                </h2>
                <span style="color: #64748B; font-size: 0.8rem;">Descartes e uso interno</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # VISÃO POR CULTURA EM CARDS DINÂMICOS (Focado nas ativas)
    culturas_ativas = [
        item for item in resumo_est
        if item["saldo_disponivel"] > 0
        or item["total_entradas"] > 0
        or item["total_vendidas"] > 0
        or item.get("total_compras", 0) > 0
        or item["total_baixas"] > 0
    ]
    culturas_inativas = [item for item in resumo_est if item not in culturas_ativas]

    if culturas_ativas:
        st.markdown(
            """
            <div style="margin: 1.2rem 0 0.6rem 0;">
                <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                    🌾 Saldo em Estoque por Cultura
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols_grid = st.columns(min(len(culturas_ativas), 3))
        for i, item in enumerate(culturas_ativas):
            with cols_grid[i % len(cols_grid)]:
                saldo = max(0, int(item["saldo_disponivel"]))
                colhidas = int(item["total_entradas"])
                compras = int(item.get("total_compras", 0))
                vendidas = int(item["total_vendidas"])
                baixas = int(item["total_baixas"])

                if saldo > 0:
                    badge_class = "badge-verde"
                    status_txt = f"🟢 {saldo} sacas disponíveis"
                    borda = "rgba(16, 185, 129, 0.4)"
                elif (colhidas + compras) == 0 and vendidas > 0:
                    badge_class = "badge-ouro"
                    status_txt = "🟡 0 em estoque (venda direta)"
                    borda = "rgba(245, 158, 11, 0.3)"
                else:
                    badge_class = "badge-ouro"
                    status_txt = "🟡 Estoque esgotado"
                    borda = "rgba(245, 158, 11, 0.3)"

                st.markdown(
                    f"""
                    <div class="agro-card" style="border: 1.5px solid {borda}; padding: 1.2rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="agro-badge {badge_class}" style="font-size: 0.85rem;">
                                {item['icone']} {item['cultura_nome']}
                            </span>
                            <span style="color: #CBD5E1; font-size: 0.82rem; font-weight: 700;">
                                {status_txt}
                            </span>
                        </div>
                        <h2 style="color: #F8FAFC; margin: 0.8rem 0 0.2rem 0; font-size: 1.7rem; font-weight: 800;">
                            {saldo} <span style="font-size: 0.95rem; font-weight: 500; color: #94A3B8;">sacas no galpão</span>
                        </h2>
                        <div style="background: rgba(0,0,0,0.25); border-radius: 8px; padding: 0.5rem 0.7rem; margin-top: 0.6rem; font-size: 0.8rem; color: #94A3B8;">
                            📥 <strong>{colhidas}</strong> colhidas &nbsp;|&nbsp; 🚚 <strong>{compras}</strong> compradas &nbsp;|&nbsp; 🚛 <strong>{vendidas}</strong> vendidas &nbsp;|&nbsp; ⚠️ <strong>{baixas}</strong> perdas
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        if culturas_inativas:
            with st.expander(f"👁️ Ver outras culturas cadastradas sem movimentação ({len(culturas_inativas)})"):
                nomes_inativas = ", ".join([f"{c['icone']} {c['cultura_nome']}" for c in culturas_inativas])
                st.caption(f"Sem movimentações no momento: {nomes_inativas}")
    else:
        st.info("Nenhuma cultura com movimentação registrada ainda. Registre a primeira colheita abaixo!")

    # FORMULÁRIOS DE LANÇAMENTO (Alinhamento em duas colunas espelhadas)
    col_entrada, col_ajuste = st.columns(2, gap="large")

    with col_entrada:
        with st.container(border=True):
            st.markdown("<h3 style='color: #34D399; margin-top: 0; font-size: 1.2rem;'>📥 Registrar Entrada no Galpão</h3>", unsafe_allow_html=True)
            
            cultura_entrada_rotulo = st.selectbox(
                "🌾 Produto / Cultura Colhida:",
                options=list(opcoes_safras.keys()),
                key="sel_est_entrada",
                help="Selecione qual produto está entrando no estoque",
            )
            safra_entrada = opcoes_safras[cultura_entrada_rotulo]

            col_data_e, col_qtd_e = st.columns(2)
            with col_data_e:
                data_entrada = st.date_input(
                    "📅 Data da Entrada:",
                    value=date.today(),
                    key="data_est_entrada",
                )
            with col_qtd_e:
                qtd_entrada = st.number_input(
                    "📦 Quantidade de Sacas:",
                    min_value=1,
                    max_value=100000,
                    value=50,
                    step=1,
                    key="qtd_est_entrada",
                )

            obs_entrada = st.text_input(
                "📝 Observação / Talhão (Opcional):",
                placeholder="Ex: Talhão norte, safra de inverno, saco de 60kg",
                key="obs_est_entrada",
            )

            btn_salvar_entrada = st.button("💾 Registrar Entrada", type="primary", key="btn_salvar_est_entrada")

            if btn_salvar_entrada:
                try:
                    salvar_movimentacao_estoque(
                        safra_id=safra_entrada["id"],
                        tipo="entrada",
                        data_mov=data_entrada,
                        quantidade_sacas=qtd_entrada,
                        local_armazenamento="Galpão",
                        observacao=obs_entrada,
                    )
                    st.success(f"✅ Entrada de {qtd_entrada} sacas de {safra_entrada['cultura_nome']} adicionada ao estoque com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao registrar entrada: {err}")

    with col_ajuste:
        with st.container(border=True):
            st.markdown("<h3 style='color: #FBBF24; margin-top: 0; font-size: 1.2rem;'>🔻 Registrar Baixa no Estoque</h3>", unsafe_allow_html=True)

            col_prod_b, col_tipo_b = st.columns(2)
            with col_prod_b:
                cultura_baixa_rotulo = st.selectbox(
                    "🌾 Produto / Cultura:",
                    options=list(opcoes_safras.keys()),
                    key="sel_est_baixa",
                )
                safra_baixa = opcoes_safras[cultura_baixa_rotulo]
            with col_tipo_b:
                tipo_baixa = st.selectbox(
                    "Tipo de Baixa:",
                    options=["Perda / Avaria / Mofo", "Consumo Próprio / Uso Interno"],
                    key="tipo_est_baixa",
                )

            col_data_b, col_qtd_b = st.columns(2)
            with col_data_b:
                data_baixa = st.date_input(
                    "📅 Data da Baixa:",
                    value=date.today(),
                    key="data_est_baixa",
                )
            with col_qtd_b:
                qtd_baixa = st.number_input(
                    "📦 Quantidade de Sacas:",
                    min_value=1,
                    max_value=10000,
                    value=5,
                    step=1,
                    key="qtd_est_baixa",
                )

            obs_baixa = st.text_input(
                "📝 Motivo / Detalhes (Opcional):",
                placeholder="Ex: Sacas molhadas pela chuva, ração para criação da fazenda",
                key="obs_est_baixa",
            )

            btn_salvar_baixa = st.button("🔻 Registrar Baixa", key="btn_salvar_est_baixa")

            if btn_salvar_baixa:
                try:
                    tipo_b_db = "perda" if "Perda" in tipo_baixa else "consumo"
                    salvar_movimentacao_estoque(
                        safra_id=safra_baixa["id"],
                        tipo=tipo_b_db,
                        data_mov=data_baixa,
                        quantidade_sacas=qtd_baixa,
                        local_armazenamento="Baixa",
                        observacao=obs_baixa,
                    )
                    st.success(f"Baixa de {qtd_baixa} sacas de {safra_baixa['cultura_nome']} registrada!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao registrar baixa: {err}")

    # TABELA DE HISTÓRICO DE MOVIMENTAÇÕES DE ESTOQUE
    st.markdown(
        """
        <div style="margin: 1.4rem 0 0.5rem 0;">
            <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                📋 Histórico das Últimas Entradas e Baixas no Armazém
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        movs = listar_movimentacoes_estoque(safra_id=None, limite=50)
        if movs:
            dados_tab_est = [
                {
                    "Registro #": f"#{m['id']}",
                    "Data": m["data"].strftime("%d/%m/%Y") if hasattr(m["data"], "strftime") else str(m["data"]),
                    "Cultura": f"{m['icone']} {m['cultura_nome']}",
                    "Tipo de Movimento": m["tipo_rotulo"],
                    "Quantidade": f"{int(m['quantidade_sacas'])} sacas",
                    "Observações": m["observacao"] or "-",
                }
                for m in movs
            ]
            st.dataframe(dados_tab_est, use_container_width=True)
        else:
            st.info("Nenhuma entrada de colheita ou baixa registrada manualmente ainda. Use o formulário acima para registrar a primeira colheita!")
    except Exception as e:
        st.error(f"Erro ao listar movimentações de estoque: {e}")
