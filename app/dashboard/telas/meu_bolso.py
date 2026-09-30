from datetime import date, timedelta
from typing import Any

import streamlit as st
from app.servicos.calculo_financeiro import (
    obter_resumo_financeiro_safra,
    obter_vendas_por_cultura,
)
from app.servicos.calculo_sacas import obter_resumo_sacas_safra
from app.servicos.dados import (
    ICONES_CULTURAS,
    listar_ultimas_cargas,
    listar_ultimos_custos,
    listar_ultimos_pagamentos,
)


def renderizar_tela_meu_bolso(
    safras: list[dict[str, Any]],
    opcoes_safras: dict[str, dict[str, Any]],
) -> None:
    """
    Renderiza a tela 'Meu Bolso' com a divisão financeira, KPIs e rendimento consolidado.
    """
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                💰 Meu Bolso
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filtro_col1, filtro_col2 = st.columns(2, gap="medium")

    with filtro_col1:
        opcao_periodo = st.selectbox(
            "⏳ Filtrar por Período de Tempo:",
            options=[
                "🌾 Acumulado Geral (Tudo)",
                "📅 Semanal (Últimos 7 dias)",
                "📆 Quinzenal (Últimos 15 dias)",
                "🗓️ Mensal (Últimos 30 dias)",
                "🎯 Escolher Datas Livres",
            ],
            index=0,
        )

    with filtro_col2:
        opcoes_culturas_filtro = ["🌟 Todas as Culturas (Bolso Geral Consolidado)"] + list(opcoes_safras.keys())
        cultura_escolhida = st.selectbox(
            "🌾 Filtrar por Cultura Comercial:",
            options=opcoes_culturas_filtro,
            index=0,
            help="Mostra o lucro consolidado de todas as culturas juntas ou filtre apenas uma cultura.",
        )

    hoje = date.today()
    data_ini = None
    data_fim = None
    descricao_periodo = "Todo o acumulado"

    if opcao_periodo == "📅 Semanal (Últimos 7 dias)":
        data_ini = hoje - timedelta(days=7)
        data_fim = hoje
        descricao_periodo = f"Semana de {data_ini.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"
    elif opcao_periodo == "📆 Quinzenal (Últimos 15 dias)":
        data_ini = hoje - timedelta(days=15)
        data_fim = hoje
        descricao_periodo = f"Quinzena de {data_ini.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"
    elif opcao_periodo == "🗓️ Mensal (Últimos 30 dias)":
        data_ini = hoje - timedelta(days=30)
        data_fim = hoje
        descricao_periodo = f"Mês de {data_ini.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"
    elif opcao_periodo == "🎯 Escolher Datas Livres":
        datas_escolhidas = st.date_input(
            "Selecione início e fim:",
            value=(hoje - timedelta(days=7), hoje),
            help="Escolha o dia inicial e o dia final do acerto",
        )
        if isinstance(datas_escolhidas, (tuple, list)) and len(datas_escolhidas) == 2:
            data_ini, data_fim = datas_escolhidas
            descricao_periodo = f"De {data_ini.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"

    # Define se o cálculo é consolidado ou filtrado por produto
    if cultura_escolhida == "🌟 Todas as Culturas (Bolso Geral Consolidado)":
        safra_id_filtro = None
        rotulo_visualizacao = "🌟 Bolso Geral (Todas as Culturas Juntas)"
    else:
        safra_id_filtro = opcoes_safras[cultura_escolhida]["id"]
        rotulo_visualizacao = cultura_escolhida

    try:
        resumo_fin = obter_resumo_financeiro_safra(
            safra_id=safra_id_filtro,
            data_inicio=data_ini,
            data_fim=data_fim,
        )
        resumo_sacas = obter_resumo_sacas_safra(
            safra_id=safra_id_filtro,
            data_inicio=data_ini,
            data_fim=data_fim,
        )

        receita = resumo_fin["receita_bruta"]
        custos_op = resumo_fin["custos_operacionais"]
        mao_obra = resumo_fin["custos_mao_de_obra"]
        lucro = resumo_fin["lucro_liquido"]
        margem = resumo_fin["margem_lucro_pct"]
        total_cargas_periodo = resumo_sacas["total_cargas"]
        total_sacas_periodo = resumo_sacas["total_sacas"]

        # Cartão de Destaque Máximo: Lucro Líquido Real do Período
        cor_destaque = "#10B981" if lucro >= 0 else "#EF4444"
        bg_destaque = (
            "linear-gradient(145deg, #064E3B 0%, #065F46 100%)"
            if lucro >= 0
            else "linear-gradient(145deg, #7F1D1D 0%, #991B1B 100%)"
        )

        st.markdown(
            f"""
            <div style="background: {bg_destaque}; border: 2px solid {cor_destaque}; border-radius: 20px; padding: 1.8rem; text-align: center; box-shadow: 0 12px 35px rgba(16, 185, 129, 0.25); margin-bottom: 1.5rem;">
                <span class="agro-badge badge-verde">🏆 SOBROU LIVRE NO SEU BOLSO NESTE PERÍODO</span>
                <h1 style="color: #FFFFFF; font-size: 3.2rem; font-weight: 800; margin: 0.5rem 0;">
                    R$ {lucro:,.2f}
                </h1>
                <div style="background: rgba(0,0,0,0.25); border-radius: 999px; padding: 0.35rem 1rem; display: inline-block;">
                    <span style="color: #A7F3D0; font-size: 1rem; font-weight: 600;">
                        Margem Livre: <strong>{margem:.1f}%</strong> do faturamento deste período
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        compras_revenda = resumo_fin.get("compras_revenda", 0.0)
        total_gastos_operacionais = custos_op + compras_revenda
        subtitulo_gastos = (
            f"Insumos R$ {custos_op:,.0f} | Cargas p/ Revenda R$ {compras_revenda:,.0f}"
            if compras_revenda > 0
            else "Energia, sacos, combustível"
        )

        # Métricas em colunas com cartões estilizados
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f"""
                <div class="agro-card">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">💵 Total Vendido</span>
                    <h2 style="color: #F8FAFC; margin: 0.4rem 0 0 0; font-size: 1.6rem;">R$ {receita:,.2f}</h2>
                    <span style="color: #64748B; font-size: 0.8rem;">Faturamento bruto</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
                <div class="agro-card">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">👷 Pessoal / Diárias</span>
                    <h2 style="color: #F87171; margin: 0.4rem 0 0 0; font-size: 1.6rem;">R$ {mao_obra:,.2f}</h2>
                    <span style="color: #64748B; font-size: 0.8rem;">Mão de obra no campo</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f"""
                <div class="agro-card">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">⚡ Gastos & Insumos</span>
                    <h2 style="color: #FBBF24; margin: 0.4rem 0 0 0; font-size: 1.6rem;">R$ {total_gastos_operacionais:,.2f}</h2>
                    <span style="color: #64748B; font-size: 0.8rem;">{subtitulo_gastos}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown(
                f"""
                <div class="agro-card">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">🌾 Volume Vendido</span>
                    <h2 style="color: #34D399; margin: 0.4rem 0 0 0; font-size: 1.6rem;">{total_sacas_periodo} sacas</h2>
                    <span style="color: #64748B; font-size: 0.8rem;">{total_cargas_periodo} caminhão(ões)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Bloco de Detalhamento por Produto Comercial (quando estiver na visão consolidada)
        if safra_id_filtro is None:
            vendas_culturas = obter_vendas_por_cultura(data_inicio=data_ini, data_fim=data_fim)
            if vendas_culturas:
                st.markdown(
                    """
                    <div style="margin: 1.2rem 0 0.6rem 0;">
                        <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                            📊 Rendimento por Cultura no Período
                        </h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                cols_vendas = st.columns(min(len(vendas_culturas), 4))
                for idx, vc in enumerate(vendas_culturas):
                    with cols_vendas[idx % 4]:
                        icone = ICONES_CULTURAS.get(vc["cultura"], "🌾")
                        st.markdown(
                            f"""
                            <div class="agro-card">
                                <span class="agro-badge badge-ouro">{icone} {vc['cultura']}</span>
                                <h3 style="color: #FBBF24; margin: 0.5rem 0 0 0; font-size: 1.35rem;">
                                    R$ {vc['total_valor']:,.2f}
                                </h3>
                                <p style="color: #94A3B8; margin: 0.3rem 0 0 0; font-size: 0.85rem;">
                                    <strong>{vc['total_sacas']}</strong> sacas em <strong>{vc['total_cargas']}</strong> caminhão(ões)
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        # Tabela detalhada dos caminhões/cargas que compõem este período
        st.markdown(
            f"""
            <div style="margin: 1.2rem 0 0.5rem 0;">
                <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                    🚚 Caminhões Negociados no Período
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cargas_do_periodo = listar_ultimas_cargas(
            safra_id=safra_id_filtro,
            limite=50,
            data_inicio=data_ini,
            data_fim=data_fim,
        )

        if cargas_do_periodo:
            dados_tabela_periodo = [
                {
                    "Carga #": f"#{c['id']}",
                    "Data": c["data"].strftime("%d/%m/%Y") if hasattr(c["data"], "strftime") else str(c["data"]),
                    "Operação": c.get("tipo_rotulo", "🟢 Venda"),
                    "Produto": f"{c.get('icone', '🌾')} {c.get('cultura_nome', '')}",
                    "Total de Sacas": f"{int(c['quantidade_sacas'])} sacas" if c.get("quantidade_sacas", 0) > 0 else "Carrada Fechada",
                    "Preço / Valor": f"R$ {c['valor_por_saca']:,.2f}/sc" if c.get("quantidade_sacas", 0) > 0 else f"R$ {c['valor_total']:,.2f}",
                    "Valor Total": f"R$ {c['valor_total']:,.2f}",
                }
                for c in cargas_do_periodo
            ]
            st.dataframe(dados_tabela_periodo, use_container_width=True)
        else:
            st.info(f"Nenhum caminhão registrado para {descricao_periodo.lower()}.")

        # Extrato detalhado de despesas abatidas
        with st.expander("🔍 Ver Extrato de Despesas (Diárias e Insumos)"):
            tab_mo, tab_custo = st.tabs(["👷 Diárias de Trabalhadores Pagas", "⚡ Insumos, Energia & Embalagens"])

            with tab_mo:
                pgtos_periodo = listar_ultimos_pagamentos(
                    safra_id=safra_id_filtro,
                    data_inicio=data_ini,
                    data_fim=data_fim,
                )
                if pgtos_periodo:
                    dados_pgto_tab = [
                        {
                            "ID": f"#{p['id']}",
                            "Data": p["data"].strftime("%d/%m/%Y") if hasattr(p["data"], "strftime") else str(p["data"]),
                            "Trabalhador": p["trabalhador_nome"],
                            "Valor Pago": f"R$ {p['valor']:,.2f}",
                        }
                        for p in pgtos_periodo
                    ]
                    st.dataframe(dados_pgto_tab, use_container_width=True)
                else:
                    st.write("Nenhum pagamento de diária lançado neste período.")

            with tab_custo:
                custos_periodo = listar_ultimos_custos(
                    safra_id=safra_id_filtro,
                    data_inicio=data_ini,
                    data_fim=data_fim,
                )
                if custos_periodo:
                    dados_custo_tab = [
                        {
                            "ID": f"#{c['id']}",
                            "Data": c["data"].strftime("%d/%m/%Y") if hasattr(c["data"], "strftime") else str(c["data"]),
                            "Descrição": c["descricao"],
                            "Cultura / Destino": f"{c.get('icone', '🌾')} {c.get('cultura_nome', 'Geral')}",
                            "Valor (R$)": f"R$ {c['valor']:,.2f}",
                        }
                        for c in custos_periodo
                    ]
                    st.dataframe(dados_custo_tab, use_container_width=True)
                else:
                    st.write("Nenhuma despesa lançada neste período.")

    except Exception as e:
        st.error(f"Erro ao carregar dados financeiros: {e}")
