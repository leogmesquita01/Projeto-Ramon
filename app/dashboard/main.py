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
            "💰 Meu Bolso (Divisão do Dinheiro)",
            "🚛 Carga do Caminhão",
            "👷 Trabalhadores & Diárias",
            "💸 Custos & Insumos",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>Culturas Disponíveis</p>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1rem;">
            <span class="agro-badge badge-verde">🌽 Milho</span>
            <span class="agro-badge badge-verde">🌱 Feijão</span>
            <span class="agro-badge badge-verde">🌿 Fava</span>
            <span class="agro-badge badge-verde">🎃 Jerimum</span>
            <span class="agro-badge badge-verde">🥔 Macaxeira</span>
            <span class="agro-badge badge-verde">🥔 Batata</span>
            <span class="agro-badge badge-verde">🍠 Mandioca</span>
            <span class="agro-badge badge-verde">🍉 Melancia</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("🔒 Conectado com segurança ao Supabase")


# -----------------------------------------------------------------------------
# 4. TELAS DO SISTEMA
# -----------------------------------------------------------------------------

# =============================================================================
# TELA 1: "MEU BOLSO" (DIVISÃO FINANCEIRA & RENDIMENTO TOTAL CONSOLIDADO)
# =============================================================================
if menu == "💰 Meu Bolso (Divisão do Dinheiro)":
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                💰 Meu Bolso — Separação Clara do Dinheiro & Lucro Total
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Veja exatamente para onde foi o dinheiro das vendas de todos os caminhões e quanto realmente sobrou limpo para você.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Painel de Filtros Integrados
    st.markdown(
        """
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 14px; padding: 0.8rem 1.2rem; margin-bottom: 1.2rem;">
            <span style="color: #34D399; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                ⏳ Filtro de Rendimentos & Período:
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filtro_col1, filtro_col2 = st.columns([1.6, 1.4], gap="medium")

    with filtro_col1:
        opcao_periodo = st.radio(
            "Escolha o intervalo de tempo:",
            [
                "📅 Semanal (Últimos 7 dias)",
                "📆 Quinzenal (Últimos 15 dias)",
                "🗓️ Mensal (Últimos 30 dias)",
                "🌾 Acumulado Geral (Tudo)",
                "🎯 Escolher Datas Livres",
            ],
            horizontal=False,
        )

    with filtro_col2:
        opcoes_culturas_filtro = ["🌟 Todas as Culturas (Bolso Geral Consolidado)"] + list(opcoes_safras.keys())
        cultura_escolhida = st.selectbox(
            "Filtrar por Cultura Comercial:",
            options=opcoes_culturas_filtro,
            index=0,
            help="Por padrão mostra o lucro total consolidado de todas as culturas juntas. Se quiser ver apenas uma cultura, selecione aqui.",
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

    # Banner informativo do filtro ativo
    st.markdown(
        f"""
        <div class="hero-banner">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span class="agro-badge badge-verde">Visualização Ativa</span>
                    <strong style="margin-left: 8px; font-size: 1.15rem; color: #F8FAFC;">
                        {rotulo_visualizacao}
                    </strong>
                </div>
                <div>
                    <span class="agro-badge badge-ouro">⏳ {descricao_periodo}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

        # Métricas em colunas com cartões estilizados
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f"""
                <div class="agro-card">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">💵 Total Vendido</span>
                    <h2 style="color: #F8FAFC; margin: 0.4rem 0 0 0; font-size: 1.6rem;">R$ {receita:,.2f}</h2>
                    <span style="color: #64748B; font-size: 0.8rem;">Entrada dos caminhões</span>
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
                    <span style="color: #64748B; font-size: 0.8rem;">Mão de obra do período</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f"""
                <div class="agro-card">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">⚡ Insumos & Gastos</span>
                    <h2 style="color: #FBBF24; margin: 0.4rem 0 0 0; font-size: 1.6rem;">R$ {custos_op:,.2f}</h2>
                    <span style="color: #64748B; font-size: 0.8rem;">Moedor, sacos, combustível</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown(
                f"""
                <div class="agro-card">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">🌾 Volume Entregue</span>
                    <h2 style="color: #34D399; margin: 0.4rem 0 0 0; font-size: 1.6rem;">{total_sacas_periodo} sacas</h2>
                    <span style="color: #64748B; font-size: 0.8rem;">{total_cargas_periodo} caminhões no período</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Bloco de Detalhamento por Produto Comercial (quando estiver na visão consolidada)
        if safra_id_filtro is None:
            vendas_culturas = obter_vendas_por_cultura(data_inicio=data_ini, data_fim=data_fim)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                    <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                        📊 Rendimento por Cultura no Período
                    </h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if vendas_culturas:
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
            else:
                st.info("Nenhuma venda registrada para o período selecionado.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabela detalhada dos caminhões/cargas que compõem este período
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                    🚚 Caminhões & Cargas no Período ({total_cargas_periodo})
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
                    "Produto": f"{c.get('icone', '🌾')} {c.get('cultura_nome', '')}",
                    "Total de Sacas": f"{int(c['quantidade_sacas'])} sacas",
                    "Preço / Saca": f"R$ {c['valor_por_saca']:,.2f}",
                    "Valor Bruto": f"R$ {c['valor_total']:,.2f}",
                }
                for c in cargas_do_periodo
            ]
            st.dataframe(dados_tabela_periodo, use_container_width=True)
        else:
            st.info(f"Nenhum caminhão registrado para {descricao_periodo.lower()}.")

        # Extrato detalhado de despesas abatidas
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔍 Ver Extrato de Onde Foi o Dinheiro (Diárias e Despesas)"):
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
# TELA 2: CARGA DO CAMINHÃO (Calculadora e Registro Instantâneo)
# =============================================================================
elif menu == "🚛 Carga do Caminhão":
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                🚛 Registro & Cálculo de Carga do Caminhão
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Calcule instantaneamente o valor bruto da carga negociada e registre a entrega.
            </p>
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

                produto_carga_rotulo = st.selectbox(
                    "🌾 Produto / Cultura Carregada:",
                    options=list(opcoes_safras.keys()),
                    help="Escolha qual produto comercial está sendo despachado neste caminhão",
                )
                safra_da_carga = opcoes_safras[produto_carga_rotulo]

                data_carga = st.date_input(
                    "📅 Data do Carregamento:",
                    value=date.today(),
                    help="Data em que o caminhão foi carregado e despachado",
                )

                qtd_sacas = st.number_input(
                    "📦 Quantidade de Sacas (Inteiras):",
                    min_value=1,
                    max_value=100000,
                    value=50,
                    step=1,
                    help="Número total de sacas cheias carregadas no caminhão",
                )

                preco_saca = st.number_input(
                    "🏷️ Preço Combinado por Saca (R$):",
                    min_value=0.0,
                    max_value=5000.0,
                    value=40.0,
                    step=0.50,
                    help="Preço acordado para a venda de cada saca",
                )

                st.markdown("<br>", unsafe_allow_html=True)
                btn_salvar = st.button("💾 Salvar Carga no Sistema", type="primary")

        with col_calculo:
            valor_total_calculado = qtd_sacas * preco_saca

            st.markdown(
                f"""
                <div class="agro-card-gold">
                    <span class="agro-badge badge-ouro">⚡ TOTAL BRUTO GERADO</span>
                    <h1 style="color: #FBBF24; margin: 0.6rem 0; font-size: 2.8rem; font-weight: 800;">
                        R$ {valor_total_calculado:,.2f}
                    </h1>
                    <div style="background: rgba(0,0,0,0.25); border-radius: 10px; padding: 0.6rem; display: inline-block; margin-top: 0.3rem;">
                        <span style="color: #CBD5E1; font-size: 1.05rem;">
                            <strong>{produto_carga_rotulo}</strong>: <strong>{qtd_sacas}</strong> sacas × <strong>R$ {preco_saca:,.2f}</strong>/saca
                        </span>
                    </div>
                    <p style="margin: 0.8rem 0 0 0; color: #94A3B8; font-size: 0.88rem;">
                        Valor total a receber do comprador. Entra automaticamente no somatório da tela Meu Bolso.
                    </p>
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
                )
                st.success(
                    f"✅ Carga #{carga_id} de {safra_da_carga['cultura_nome']} salva com sucesso! "
                    f"({qtd_sacas} sacas = R$ {valor_total_calculado:,.2f})"
                )
                st.balloons()
            except Exception as err:
                st.error(f"Erro ao salvar a carga no banco: {err}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Histórico de cargas de caminhões
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">
                    📋 Histórico dos Últimos Caminhões Registrados
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
                        "Produto": f"{c.get('icone', '🌾')} {c.get('cultura_nome', '')}",
                        "Total de Sacas": f"{int(c['quantidade_sacas'])} sacas",
                        "Preço / Saca": f"R$ {c['valor_por_saca']:,.2f}",
                        "Valor da Carga": f"R$ {c['valor_total']:,.2f}",
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
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                👷 Trabalhadores & Diárias
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Controle de presença, diárias trabalhadas e acerto de pagamentos da equipe no campo.
            </p>
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

            st.markdown("<br>", unsafe_allow_html=True)
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
                <p style="margin: 0.8rem 0 0 0; color: #94A3B8; font-size: 0.88rem;">
                    Este valor é abatido diretamente da receita na tela Meu Bolso.
                </p>
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

    st.markdown("<br>", unsafe_allow_html=True)

    # Histórico de pagamentos
    st.markdown("<h3 style='color: #F8FAFC; margin: 0 0 0.5rem 0; font-size: 1.25rem;'>📋 Histórico Geral de Diárias Pagas</h3>", unsafe_allow_html=True)
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
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                💸 Custos & Insumos da Lavoura
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Anotação rápida de despesas: energia do moedor, embalagens/sacaria, óleo diesel e manutenção.
            </p>
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

            st.markdown("<br>", unsafe_allow_html=True)
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
                <p style="margin: 0.8rem 0 0 0; color: #94A3B8; font-size: 0.88rem;">
                    Esse gasto será abatido diretamente na tela Meu Bolso do faturamento consolidado.
                </p>
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

    st.markdown("<br>", unsafe_allow_html=True)

    # Histórico de custos
    st.markdown("<h3 style='color: #F8FAFC; margin: 0 0 0.5rem 0; font-size: 1.25rem;'>📋 Histórico Geral de Despesas</h3>", unsafe_allow_html=True)
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
