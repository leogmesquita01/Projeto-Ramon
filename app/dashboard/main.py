import os
import sys
from datetime import date

# Garante que o diretório raiz do projeto esteja no caminho de busca de módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from app.servicos.calculo_financeiro import obter_resumo_financeiro_safra
from app.servicos.calculo_sacas import obter_resumo_sacas_safra
from app.servicos.dados import (
    criar_safra_rapida,
    listar_safras_ativas,
    listar_ultimas_cargas,
    salvar_carga,
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

    /* Espaçamento superior para não colar na barra do Streamlit Cloud */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 3rem !important;
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
# 3. BARRA LATERAL (MENU E SELEÇÃO DE SAFRA)
# -----------------------------------------------------------------------------
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

    # Busca as safras ativas no banco de dados
    try:
        safras = listar_safras_ativas()
    except Exception as e:
        st.error(f"Erro ao conectar com o banco: {e}")
        safras = []

    safra_selecionada = None

    if safras:
        opcoes_safras = {s["rotulo"]: s for s in safras}
        safra_escolhida_rotulo = st.selectbox(
            "🌱 Safra Ativa:",
            options=list(opcoes_safras.keys()),
            help="Selecione qual colheita você está gerenciando agora",
        )
        safra_selecionada = opcoes_safras[safra_escolhida_rotulo]
    else:
        st.warning("Nenhuma safra cadastrada ainda.")
        with st.expander("➕ Cadastrar 1ª Safra", expanded=True):
            nome_cultura_nova = st.text_input("Cultura (ex: Milho, Café, Soja):", value="Milho")
            data_inicio_nova = st.date_input("Data de Início:", value=date.today())
            if st.button("Criar Safra Agora"):
                if nome_cultura_nova.strip():
                    nova_id = criar_safra_rapida(nome_cultura_nova, data_inicio_nova)
                    st.success(f"Safra #{nova_id} iniciada com sucesso!")
                    st.rerun()

    st.divider()

    # Navegação entre telas do aplicativo
    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>Telas do Sistema</p>", unsafe_allow_html=True)
    menu = st.radio(
        "Ir para a tela:",
        [
            "🚛 Carga do Caminhão",
            "💰 'Meu Bolso' (Divisão do Dinheiro)",
            "👷 Trabalhadores & Diárias",
            "💸 Custos & Insumos",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("🔒 Conectado com segurança ao Supabase")


# -----------------------------------------------------------------------------
# 4. BANNER SUPERIOR INFORMATIVO
# -----------------------------------------------------------------------------
if safra_selecionada:
    data_formatada = (
        safra_selecionada["data_inicio"].strftime("%d/%m/%Y")
        if hasattr(safra_selecionada["data_inicio"], "strftime")
        else str(safra_selecionada["data_inicio"])
    )
    st.markdown(
        f"""
        <div class="hero-banner">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span class="agro-badge badge-verde">Safra Ativa</span>
                    <strong style="margin-left: 8px; font-size: 1.15rem; color: #F8FAFC;">{safra_selecionada['cultura_nome']}</strong>
                    <span style="color: #94A3B8; font-size: 0.9rem;"> • Iniciada em {data_formatada}</span>
                </div>
                <div>
                    <span class="agro-badge badge-ouro">Status: {safra_selecionada['status'].replace('_', ' ').title()}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 5. TELAS DO SISTEMA
# -----------------------------------------------------------------------------

# =============================================================================
# TELA 1: CARGA DO CAMINHÃO (Calculadora e Registro)
# =============================================================================
if menu == "🚛 Carga do Caminhão":
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

    if not safra_selecionada:
        st.info("👈 Por favor, crie ou selecione uma safra na barra lateral para começar.")
    else:
        col_form, col_calculo = st.columns([1.1, 1], gap="large")

        with col_form:
            with st.container(border=True):
                st.markdown("<h3 style='color: #34D399; margin-top: 0; font-size: 1.2rem;'>📝 Dados da Carga</h3>", unsafe_allow_html=True)
                
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
                            <strong>{qtd_sacas}</strong> sacas × <strong>R$ {preco_saca:,.2f}</strong>/saca
                        </span>
                    </div>
                    <p style="margin: 0.8rem 0 0 0; color: #94A3B8; font-size: 0.88rem;">
                        Valor total a receber do comprador antes de deduzir diárias de apanhadores, frete ou óleo diesel.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Ação ao clicar no botão salvar
        if btn_salvar:
            try:
                carga_id = salvar_carga(
                    safra_id=safra_selecionada["id"],
                    cultura_id=safra_selecionada["cultura_id"],
                    data_carga=data_carga,
                    quantidade_sacas=qtd_sacas,
                    valor_por_saca=preco_saca,
                )
                st.success(
                    f"✅ Carga #{carga_id} salva com sucesso! "
                    f"({qtd_sacas} sacas = R$ {valor_total_calculado:,.2f})"
                )
                st.balloons()
            except Exception as err:
                st.error(f"Erro ao salvar a carga no banco: {err}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabela com as últimas cargas registradas nesta safra
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                <h3 style="color: #F8FAFC; margin: 0; font-size: 1.25rem;">📋 Histórico de Cargas Desta Safra</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            ultimas_cargas = listar_ultimas_cargas(safra_selecionada["id"])
            if ultimas_cargas:
                dados_tabela = [
                    {
                        "Carga #": f"#{c['id']}",
                        "Data": c["data"].strftime("%d/%m/%Y") if hasattr(c["data"], "strftime") else str(c["data"]),
                        "Total de Sacas": f"{int(c['quantidade_sacas'])} sacas",
                        "Preço / Saca": f"R$ {c['valor_por_saca']:,.2f}",
                        "Valor da Carga": f"R$ {c['valor_total']:,.2f}",
                    }
                    for c in ultimas_cargas
                ]
                st.dataframe(dados_tabela, use_container_width=True)
            else:
                st.info("Nenhuma carga registrada para esta safra ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar lista de cargas: {e}")

# =============================================================================
# TELA 2: "MEU BOLSO" (DIVISÃO FINANCEIRA)
# =============================================================================
elif menu == "💰 'Meu Bolso' (Divisão do Dinheiro)":
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                💰 "Meu Bolso" — Separação Clara do Dinheiro
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Veja exatamente para onde foi o dinheiro das vendas e quanto realmente sobrou limpo para você.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not safra_selecionada:
        st.info("👈 Por favor, selecione uma safra na barra lateral.")
    else:
        try:
            resumo_fin = obter_resumo_financeiro_safra(safra_selecionada["id"])
            resumo_sacas = obter_resumo_sacas_safra(safra_selecionada["id"])

            receita = resumo_fin["receita_bruta"]
            custos_op = resumo_fin["custos_operacionais"]
            mao_obra = resumo_fin["custos_mao_de_obra"]
            lucro = resumo_fin["lucro_liquido"]
            margem = resumo_fin["margem_lucro_pct"]

            # Cartão de Destaque Máximo: Lucro Líquido Real
            st.markdown(
                f"""
                <div class="agro-card-lucro">
                    <span class="agro-badge badge-verde">🏆 SOBROU LIVRE NO SEU BOLSO (LUCRO REAL)</span>
                    <h1 style="color: #FFFFFF; font-size: 3.2rem; font-weight: 800; margin: 0.5rem 0;">
                        R$ {lucro:,.2f}
                    </h1>
                    <div style="background: rgba(0,0,0,0.25); border-radius: 999px; padding: 0.35rem 1rem; display: inline-block;">
                        <span style="color: #A7F3D0; font-size: 1rem; font-weight: 600;">
                            Margem de Lucro: <strong>{margem:.1f}%</strong> do total vendido
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
                        <span style="color: #64748B; font-size: 0.8rem;">Entrada bruta</span>
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
                        <span style="color: #64748B; font-size: 0.8rem;">Mão de obra</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f"""
                    <div class="agro-card">
                        <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">⛽ Insumos & Gastos</span>
                        <h2 style="color: #FBBF24; margin: 0.4rem 0 0 0; font-size: 1.6rem;">R$ {custos_op:,.2f}</h2>
                        <span style="color: #64748B; font-size: 0.8rem;">Combustível, adubo, etc.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m4:
                st.markdown(
                    f"""
                    <div class="agro-card">
                        <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">🌾 Volume Colhido</span>
                        <h2 style="color: #34D399; margin: 0.4rem 0 0 0; font-size: 1.6rem;">{int(resumo_sacas['total_sacas'])} sacas</h2>
                        <span style="color: #64748B; font-size: 0.8rem;">{resumo_sacas['total_cargas']} cargas registradas</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        except Exception as e:
            st.error(f"Erro ao carregar dados financeiros da safra: {e}")

# =============================================================================
# TELA 3: TRABALHADORES & DIÁRIAS (Próxima Etapa)
# =============================================================================
elif menu == "👷 Trabalhadores & Diárias":
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                👷 Trabalhadores & Diárias
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Controle de presença, diárias, apanhadores e pagamentos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="agro-card" style="text-align: center; padding: 2.5rem;">
            <span style="font-size: 3rem;">🚜</span>
            <h2 style="color: #34D399; margin: 0.8rem 0 0.3rem 0;">Tela em Construção</h2>
            <p style="color: #94A3B8; max-width: 500px; margin: 0 auto;">
                Em breve você poderá cadastrar os trabalhadores, lançar as diárias trabalhadas e dar baixa nos pagamentos com 1 clique!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# TELA 4: CUSTOS & INSUMOS (Próxima Etapa)
# =============================================================================
elif menu == "💸 Custos & Insumos":
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                💸 Custos & Insumos da Lavoura
            </h1>
            <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Anotação rápida de despesas: diesel, adubo, sacaria, frete e peças.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="agro-card" style="text-align: center; padding: 2.5rem;">
            <span style="font-size: 3rem;">⛽</span>
            <h2 style="color: #FBBF24; margin: 0.8rem 0 0.3rem 0;">Tela em Construção</h2>
            <p style="color: #94A3B8; max-width: 500px; margin: 0 auto;">
                Em breve você poderá lançar gastos rápidos direto da roça pelo celular para descontar automaticamente do seu lucro.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
