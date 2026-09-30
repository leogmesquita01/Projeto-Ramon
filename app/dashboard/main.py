import os
import sys
from datetime import date, timedelta

# Garante que o diretório raiz do projeto esteja no caminho de busca de módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import importlib
import streamlit as st

import app.servicos.calculo_financeiro
import app.servicos.calculo_sacas
import app.servicos.dados

importlib.reload(app.servicos.calculo_financeiro)
importlib.reload(app.servicos.calculo_sacas)
importlib.reload(app.servicos.dados)

from app.servicos.calculo_financeiro import (
    obter_resumo_financeiro_safra,
    obter_vendas_por_cultura,
)
from app.servicos.calculo_sacas import obter_resumo_sacas_safra
from app.servicos.dados import (
    ICONES_CULTURAS,
    cadastrar_trabalhador,
    criar_safra_rapida,
    listar_safras_ativas,
    listar_trabalhadores,
    listar_ultimas_cargas,
    listar_ultimos_custos,
    listar_ultimos_pagamentos,
    salvar_carga,
    salvar_custo,
    salvar_pagamento_trabalhador,
    limpar_dados_teste,
    salvar_movimentacao_estoque,
    listar_movimentacoes_estoque,
    obter_resumo_estoque,
)

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AgroGestão — Controle da Lavoura",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. ESTILOS VISUAIS MODERNOS (TEMA ESCURO FLORESTA COM ESMERALDA)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Fonte e espaçamento global */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Espaçamento superior otimizado (sem cabeçalho) */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }

    /* Cabeçalho transparente e não intrusivo (mantém o botão de reabrir a barra lateral acessível) */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background: transparent !important;
        pointer-events: none;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
    }

    /* Ocultar elementos desnecessários (menu padrão, decorações, deploy e rodapé) */
    #MainMenu, 
    [data-testid="stMainMenu"], 
    footer, 
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"],
    .stDeployButton,
    [data-testid="stAppDeployButton"],
    [data-testid="stToolbarActions"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Botão de abrir/expandir a barra lateral quando recolhida (visível e destacado no tema do app) */
    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapsedControl"],
    header[data-testid="stHeader"] button {
        display: inline-flex !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }

    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #152420 !important;
        border: 2px solid #10B981 !important;
        border-radius: 12px !important;
        color: #10B981 !important;
        padding: 6px 14px !important;
        margin-top: 10px !important;
        margin-left: 14px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6), 0 0 12px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.25s ease !important;
        cursor: pointer !important;
        align-items: center !important;
    }

    [data-testid="stExpandSidebarButton"]::after,
    [data-testid="stSidebarCollapsedControl"]::after {
        content: " Abrir Menu";
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #10B981 !important;
        margin-left: 6px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    [data-testid="stExpandSidebarButton"]:hover::after,
    [data-testid="stSidebarCollapsedControl"]:hover::after {
        color: #FFFFFF !important;
    }

    [data-testid="stExpandSidebarButton"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #10B981 !important;
        border-color: #34D399 !important;
        transform: scale(1.04);
        box-shadow: 0 6px 25px rgba(16, 185, 129, 0.45) !important;
    }

    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="stExpandSidebarButton"] span,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] span {
        color: #10B981 !important;
        fill: #10B981 !important;
    }

    [data-testid="stExpandSidebarButton"]:hover svg,
    [data-testid="stExpandSidebarButton"]:hover span,
    [data-testid="stSidebarCollapsedControl"]:hover svg,
    [data-testid="stSidebarCollapsedControl"]:hover span {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    /* Desativar e ocultar completamente o botão de recuar/fechar a barra lateral */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Cartão base estilo container escuro sofisticado */
    .agro-card {
        background: linear-gradient(145deg, #13221C 0%, #172B23 100%);
        border: 1px solid rgba(16, 185, 129, 0.22);
        border-radius: 18px;
        padding: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.2rem;
    }

    /* Cartão de Destaque da Carga (com borda e brilho dourado suave) */
    .agro-card-gold {
        background: linear-gradient(145deg, #1A281E 0%, #203325 100%);
        border: 1.5px solid rgba(245, 158, 11, 0.4);
        border-radius: 18px;
        padding: 1.6rem;
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.1);
        margin-bottom: 1.2rem;
        text-align: center;
    }

    /* Cartão de Lucro Real Máximo */
    .agro-card-lucro {
        background: linear-gradient(145deg, #064E3B 0%, #065F46 100%);
        border: 2px solid #10B981;
        border-radius: 20px;
        padding: 1.8rem;
        text-align: center;
        box-shadow: 0 12px 35px rgba(16, 185, 129, 0.25);
        margin-bottom: 1.5rem;
    }

    /* Pílulas de badges informativos */
    .agro-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-verde {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-ouro {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    /* Botão primário grande, moderno e com gradiente (fácil de tocar no celular) */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 14px;
        padding: 0.8rem 1.4rem;
        font-size: 1.1rem;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
    }
    div.stButton > button:active {
        transform: translateY(0);
    }

    /* Top banner elegante */
    .hero-banner {
        background: linear-gradient(90deg, #13221C 0%, #1A3327 100%);
        border-left: 5px solid #10B981;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (MENU DE NAVEGAÇÃO E IDENTIDADE)
# -----------------------------------------------------------------------------
# Busca as safras/produtos cadastrados no banco
try:
    safras = listar_safras_ativas()
except Exception as e:
    st.error(f"Erro ao conectar com o banco: {e}")
    safras = []

opcoes_safras = {s["rotulo"]: s for s in safras} if safras else {}

with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
            <span style="font-size: 2rem;">🌾</span>
            <div>
                <h2 style="margin: 0; font-size: 1.35rem; color: #34D399; font-weight: 800;">AgroGestão</h2>
                <span style="font-size: 0.8rem; color: #94A3B8;">Controle do Campo & Vendas</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # Navegação entre telas do aplicativo
    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>Navegação</p>", unsafe_allow_html=True)
    menu = st.radio(
        "Ir para a tela:",
        [
            "💰 Meu Bolso",
            "📦 Controle de Estoque",
            "🚛 Carga do Caminhão",
            "👷 Trabalhadores & Diárias",
            "💸 Custos & Insumos",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("<p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;'>Disponível em Estoque</p>", unsafe_allow_html=True)
    try:
        resumo_sidebar = obter_resumo_estoque()
        com_estoque = [c for c in resumo_sidebar if c["saldo_disponivel"] > 0]
        if com_estoque:
            badges_html = "".join([
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 5px 10px; margin-bottom: 5px;">
                    <span style="font-size: 0.85rem; color: #F8FAFC; font-weight: 600;">{c['icone']} {c['cultura_nome']}</span>
                    <span style="font-size: 0.8rem; font-weight: 700; color: #34D399;">{int(c['saldo_disponivel']):,} sc</span>
                </div>
                """
                for c in com_estoque
            ])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.caption("⚪ Nenhum produto com saldo no galpão.")
    except Exception:
        st.caption("⚪ Nenhum produto com saldo no galpão.")

    st.caption("🔒 Conectado com segurança ao Supabase")


# -----------------------------------------------------------------------------
# 4. TELAS DO SISTEMA
# -----------------------------------------------------------------------------

# =============================================================================
# TELA 1: "MEU BOLSO" (DIVISÃO FINANCEIRA & RENDIMENTO TOTAL CONSOLIDADO)
# =============================================================================
if menu == "💰 Meu Bolso":
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
            else "Moedor, sacos, combustível"
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


# =============================================================================
# TELA: CONTROLE DE ESTOQUE & ARMAZENAMENTO
# =============================================================================
elif menu == "📦 Controle de Estoque":
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

    # FORMULÁRIOS DE LANÇAMENTO
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


# =============================================================================
# TELA 2: CARGA DO CAMINHÃO (Calculadora e Registro Instantâneo)
# =============================================================================
elif menu == "🚛 Carga do Caminhão":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                🚛 Carga do Caminhão
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not safras:
        st.warning("Nenhum produto cadastrado ainda.")
    else:
        col_form, col_calculo = st.columns([1.1, 1], gap="large")

        with col_form:
            with st.container(border=True):
                st.markdown("<h3 style='color: #34D399; margin-top: 0; font-size: 1.2rem;'>📝 Dados da Carga</h3>", unsafe_allow_html=True)

                tipo_operacao_selecionada = st.radio(
                    "Operação do Caminhão:",
                    ["🟢 Venda (Saída p/ Comprador)", "🔵 Compra (Aquisição p/ Revenda)"],
                    index=0,
                    horizontal=True,
                    key="tipo_op_carga",
                    help="Escolha se este caminhão é uma venda da lavoura ou uma compra de produto de terceiros para revender",
                )
                eh_venda = "Venda" in tipo_operacao_selecionada
                tipo_op_db = "venda" if eh_venda else "compra"

                produto_carga_rotulo = st.selectbox(
                    "🌾 Produto / Cultura Carregada:",
                    options=list(opcoes_safras.keys()),
                    help="Escolha qual produto comercial está sendo negociado neste caminhão",
                )
                safra_da_carga = opcoes_safras[produto_carga_rotulo]

                try:
                    if eh_venda:
                        resumo_est_prod = obter_resumo_estoque(safra_id=safra_da_carga["id"])
                        saldo_prod = int(resumo_est_prod[0]["saldo_disponivel"]) if resumo_est_prod else 0
                        if saldo_prod > 0:
                            st.caption(f"📦 **Estoque disponível no galpão:** :green[{saldo_prod} sacas]")
                        else:
                            st.caption("📦 **Estoque no galpão:** :orange[0 sacas registradas]")
                except Exception:
                    pass

                data_carga = st.date_input(
                    "📅 Data do Carregamento / Negociação:",
                    value=date.today(),
                    help="Data em que o caminhão foi negociado",
                )

                if eh_venda:
                    qtd_sacas = st.number_input(
                        "📦 Quantidade de Sacas (Inteiras):",
                        min_value=1,
                        max_value=100000,
                        value=50,
                        step=1,
                        help="Número total de sacas cheias carregadas no caminhão",
                    )
                    preco_saca = st.number_input(
                        "🏷️ Preço Combinado de Venda por Saca (R$):",
                        min_value=0.0,
                        max_value=5000.0,
                        value=40.0,
                        step=0.50,
                        help="Preço acordado para a venda de cada saca",
                    )
                    valor_total_calculado = qtd_sacas * preco_saca
                else:
                    qtd_sacas = 0
                    preco_pago = st.number_input(
                        "🏷️ Preço pago (R$):",
                        min_value=0.0,
                        max_value=5000000.0,
                        value=1500.0,
                        step=50.0,
                        help="Valor total pago pelo caminhão / carrada adquirida",
                    )
                    preco_saca = preco_pago
                    valor_total_calculado = preco_pago

                texto_btn = "💾 Salvar Venda da Carga" if eh_venda else "💾 Salvar Compra no Sistema"
                btn_salvar = st.button(texto_btn, type="primary")

        with col_calculo:
            if eh_venda:
                st.markdown(
                    f"""
                    <div class="agro-card-gold">
                        <span class="agro-badge badge-ouro">⚡ TOTAL BRUTO A RECEBER</span>
                        <h1 style="color: #FBBF24; margin: 0.6rem 0; font-size: 2.8rem; font-weight: 800;">
                            R$ {valor_total_calculado:,.2f}
                        </h1>
                        <div style="background: rgba(0,0,0,0.25); border-radius: 10px; padding: 0.6rem; display: inline-block; margin-top: 0.3rem;">
                            <span style="color: #CBD5E1; font-size: 1.05rem;">
                                <strong>{produto_carga_rotulo}</strong>: <strong>{qtd_sacas}</strong> sacas × <strong>R$ {preco_saca:,.2f}</strong>/saca
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="agro-card" style="border: 2px solid #3B82F6; text-align: center; padding: 1.6rem;">
                        <span class="agro-badge" style="background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.4);">
                            💸 PREÇO PAGO NA COMPRA
                        </span>
                        <h1 style="color: #60A5FA; margin: 0.6rem 0; font-size: 2.8rem; font-weight: 800;">
                            R$ {valor_total_calculado:,.2f}
                        </h1>
                        <div style="background: rgba(0,0,0,0.25); border-radius: 10px; padding: 0.6rem; display: inline-block; margin-top: 0.3rem;">
                            <span style="color: #CBD5E1; font-size: 1.05rem;">
                                <strong>{produto_carga_rotulo}</strong>: Carrada / Carga Adquirida
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if btn_salvar:
            try:
                carga_id = salvar_carga(
                    safra_id=safra_da_carga["id"],
                    cultura_id=safra_da_carga["cultura_id"],
                    data_carga=data_carga,
                    quantidade_sacas=qtd_sacas,
                    valor_por_saca=preco_saca,
                    tipo_operacao=tipo_op_db,
                )
                if eh_venda:
                    st.success(
                        f"✅ Venda #{carga_id} salva! ({qtd_sacas} sacas = R$ {valor_total_calculado:,.2f})"
                    )
                else:
                    st.success(
                        f"✅ Compra #{carga_id} salva! (Preço pago: R$ {valor_total_calculado:,.2f})"
                    )
                st.balloons()
            except Exception as err:
                st.error(f"Erro ao salvar a carga no banco: {err}")

        # Histórico de cargas de caminhões
        st.markdown(
            """
            <div style="margin: 1.4rem 0 0.5rem 0;">
                <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                    📋 Histórico dos Últimos Caminhões Negociados
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            ultimas_cargas = listar_ultimas_cargas(safra_id=None, limite=50)
            if ultimas_cargas:
                dados_tabela = [
                    {
                        "Carga #": f"#{c['id']}",
                        "Data": c["data"].strftime("%d/%m/%Y") if hasattr(c["data"], "strftime") else str(c["data"]),
                        "Operação": c.get("tipo_rotulo", "🟢 Venda"),
                        "Produto": f"{c.get('icone', '🌾')} {c.get('cultura_nome', '')}",
                        "Total de Sacas": f"{int(c['quantidade_sacas'])} sacas" if c.get("quantidade_sacas", 0) > 0 else "Carrada Fechada",
                        "Preço / Valor": f"R$ {c['valor_por_saca']:,.2f}/sc" if c.get("quantidade_sacas", 0) > 0 else f"R$ {c['valor_total']:,.2f}",
                        "Valor Total": f"R$ {c['valor_total']:,.2f}",
                    }
                    for c in ultimas_cargas
                ]
                st.dataframe(dados_tabela, use_container_width=True)
            else:
                st.info("Nenhuma carga registrada no sistema ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar lista de cargas: {e}")


# =============================================================================
# TELA 3: TRABALHADORES & DIÁRIAS (Controle de Mão de Obra)
# =============================================================================
elif menu == "👷 Trabalhadores & Diárias":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                👷 Trabalhadores & Diárias
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        trabalhadores = listar_trabalhadores()
    except Exception as e:
        st.error(f"Erro ao carregar lista de trabalhadores: {e}")
        trabalhadores = []

    col_lancamento, col_resumo = st.columns([1.1, 1], gap="large")

    with col_lancamento:
        with st.container(border=True):
            st.markdown("<h3 style='color: #34D399; margin-top: 0; font-size: 1.2rem;'>📝 Lançar Pagamento de Diária</h3>", unsafe_allow_html=True)

            opcoes_trab = {t["nome"]: t["id"] for t in trabalhadores}

            if opcoes_trab:
                nome_escolhido = st.selectbox("👷 Escolha o Trabalhador:", options=list(opcoes_trab.keys()))
                trab_id = opcoes_trab[nome_escolhido]
            else:
                st.warning("Nenhum trabalhador cadastrado ainda.")
                trab_id = None
                nome_escolhido = ""

            with st.expander("➕ Cadastrar Novo Trabalhador no Sistema"):
                novo_nome = st.text_input("Nome do Trabalhador (ex: Zé da Roça, João, Maria):")
                if st.button("Salvar Novo Trabalhador"):
                    if novo_nome.strip():
                        cadastrar_trabalhador(novo_nome.strip())
                        st.success(f"Trabalhador '{novo_nome.strip()}' cadastrado com sucesso!")
                        st.rerun()

            safra_padrao_id = safras[0]["id"] if safras else None

            data_pgto = st.date_input("📅 Data do Pagamento / Acerto:", value=date.today())

            qtd_diarias = st.number_input(
                "📆 Quantidade de Diárias Trabalhadas:",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                help="Quantos dias essa pessoa trabalhou",
            )

            valor_diaria = st.number_input(
                "💵 Valor Combinado por Diária (R$):",
                min_value=1.0,
                max_value=2000.0,
                value=80.0,
                step=5.0,
                help="Preço acordado pelo dia de trabalho",
            )

            btn_salvar_pgto = st.button("💾 Registrar Pagamento de Diária", type="primary", disabled=(trab_id is None or safra_padrao_id is None))

    with col_resumo:
        total_pgto_calculado = qtd_diarias * valor_diaria

        st.markdown(
            f"""
            <div class="agro-card-gold">
                <span class="agro-badge badge-ouro">⚡ TOTAL DO ACERTO</span>
                <h1 style="color: #FBBF24; margin: 0.6rem 0; font-size: 2.8rem; font-weight: 800;">
                    R$ {total_pgto_calculado:,.2f}
                </h1>
                <div style="background: rgba(0,0,0,0.25); border-radius: 10px; padding: 0.6rem; display: inline-block; margin-top: 0.3rem;">
                    <span style="color: #CBD5E1; font-size: 1.05rem;">
                        <strong>{qtd_diarias}</strong> diárias × <strong>R$ {valor_diaria:,.2f}</strong>/dia
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if btn_salvar_pgto and trab_id and safra_padrao_id:
        try:
            pgto_id = salvar_pagamento_trabalhador(
                trabalhador_id=trab_id,
                safra_id=safra_padrao_id,
                data_pagamento=data_pgto,
                valor=total_pgto_calculado,
            )
            st.success(f"✅ Pagamento #{pgto_id} de R$ {total_pgto_calculado:,.2f} registrado com sucesso para {nome_escolhido}!")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar pagamento: {e}")

    # Histórico de pagamentos
    st.markdown(
        """
        <div style="margin: 1.4rem 0 0.5rem 0;">
            <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                📋 Histórico Geral de Diárias Pagas
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        pagamentos = listar_ultimos_pagamentos(safra_id=None, limite=50)
        if pagamentos:
            dados_pgto = [
                {
                    "ID #": f"#{p['id']}",
                    "Data": p["data"].strftime("%d/%m/%Y") if hasattr(p["data"], "strftime") else str(p["data"]),
                    "Trabalhador": p["trabalhador_nome"],
                    "Valor Pago": f"R$ {p['valor']:,.2f}",
                }
                for p in pagamentos
            ]
            st.dataframe(dados_pgto, use_container_width=True)
        else:
            st.info("Nenhum pagamento registrado no sistema ainda.")
    except Exception as e:
        st.error(f"Erro ao buscar histórico de pagamentos: {e}")


# =============================================================================
# TELA 4: CUSTOS & INSUMOS (Energia do Moedor, Embalagens, etc.)
# =============================================================================
elif menu == "💸 Custos & Insumos":
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                💸 Custos & Insumos
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_form_custo, col_preview_custo = st.columns([1.1, 1], gap="large")

    with col_form_custo:
        with st.container(border=True):
            st.markdown("<h3 style='color: #34D399; margin-top: 0; font-size: 1.2rem;'>📝 Lançar Nova Despesa</h3>", unsafe_allow_html=True)

            categoria = st.radio(
                "Tipo de Gasto:",
                [
                    "⚡ Energia do Moedor",
                    "📦 Embalagens & Sacaria",
                    "⛽ Óleo Diesel / Combustível",
                    "🚜 Peças & Manutenção",
                    "📝 Outro Gasto",
                ],
                horizontal=True,
            )

            cultura_custo_rotulo = st.selectbox(
                "🌾 Cultura / Destino do Gasto:",
                options=list(opcoes_safras.keys()),
                help="Selecione para qual cultura ou atividade esse custo foi destinado",
            )
            safra_custo = opcoes_safras[cultura_custo_rotulo] if opcoes_safras else None

            data_custo = st.date_input("📅 Data da Despesa:", value=date.today())

            # Se for embalagens, oferece calculadora rápida opcional
            if categoria == "📦 Embalagens & Sacaria":
                tipo_calculo = st.radio(
                    "Forma de Lançamento:",
                    ["🧮 Calcular por Quantidade de Sacos", "💵 Digitar Valor Total Direto"],
                    horizontal=True,
                )
                if tipo_calculo == "🧮 Calcular por Quantidade de Sacos":
                    qtd_embalagens = st.number_input("Quantidade de Sacos Comprados:", min_value=1, value=100, step=10)
                    preco_unitario_saco = st.number_input("Preço de Cada Saco (R$):", min_value=0.10, value=2.50, step=0.10)
                    valor_final_custo = qtd_embalagens * preco_unitario_saco
                    descricao_custo = f"Embalagens ({qtd_embalagens} sacos a R$ {preco_unitario_saco:,.2f})"
                else:
                    valor_final_custo = st.number_input("Valor Total Gasto com Embalagens (R$):", min_value=1.0, value=250.0, step=10.0)
                    descricao_custo = "Embalagens & Sacaria"
            else:
                valor_final_custo = st.number_input("Valor da Despesa (R$):", min_value=1.0, value=150.0, step=10.0)
                detalhe_extra = st.text_input("Observação / Detalhe (opcional):", placeholder="Ex: Conta de luz do moedor set/2026, correia, etc.")
                if detalhe_extra.strip():
                    descricao_custo = f"{categoria} - {detalhe_extra.strip()}"
                else:
                    descricao_custo = categoria

            btn_salvar_custo = st.button("💾 Salvar Esta Despesa no Sistema", type="primary", disabled=(safra_custo is None))

    with col_preview_custo:
        st.markdown(
            f"""
            <div class="agro-card-gold">
                <span class="agro-badge badge-ouro">⚡ TOTAL DA DESPESA</span>
                <h1 style="color: #FBBF24; margin: 0.6rem 0; font-size: 2.8rem; font-weight: 800;">
                    R$ {valor_final_custo:,.2f}
                </h1>
                <div style="background: rgba(0,0,0,0.25); border-radius: 10px; padding: 0.6rem; display: inline-block; margin-top: 0.3rem;">
                    <span style="color: #CBD5E1; font-size: 1rem;">
                        <strong>{descricao_custo}</strong>
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if btn_salvar_custo and safra_custo:
        try:
            custo_id = salvar_custo(
                safra_id=safra_custo["id"],
                descricao=descricao_custo,
                valor=valor_final_custo,
                data_custo=data_custo,
            )
            st.success(f"✅ Despesa #{custo_id} de R$ {valor_final_custo:,.2f} ({descricao_custo}) registrada com sucesso!")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar despesa: {e}")

    # Histórico de custos
    st.markdown(
        """
        <div style="margin: 1.4rem 0 0.5rem 0;">
            <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                📋 Histórico Geral de Despesas
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        custos = listar_ultimos_custos(safra_id=None, limite=50)
        if custos:
            dados_custos = [
                {
                    "ID #": f"#{c['id']}",
                    "Data": c["data"].strftime("%d/%m/%Y") if hasattr(c["data"], "strftime") else str(c["data"]),
                    "Descrição do Gasto": c["descricao"],
                    "Cultura / Destino": f"{c.get('icone', '🌾')} {c.get('cultura_nome', 'Geral')}",
                    "Valor": f"R$ {c['valor']:,.2f}",
                }
                for c in custos
            ]
            st.dataframe(dados_custos, use_container_width=True)
        else:
            st.info("Nenhuma despesa registrada no sistema ainda.")
    except Exception as e:
        st.error(f"Erro ao buscar despesas: {e}")
