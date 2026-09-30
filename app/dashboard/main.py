import os
import sys

# Garante que o diretório raiz do projeto esteja no caminho de busca de módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st

from app.dashboard.estilos import aplicar_estilos
from app.dashboard.telas.cargas import renderizar_tela_cargas
from app.dashboard.telas.custos import renderizar_tela_custos
from app.dashboard.telas.estoque import renderizar_tela_estoque
from app.dashboard.telas.meu_bolso import renderizar_tela_meu_bolso
from app.dashboard.telas.trabalhadores import renderizar_tela_trabalhadores
from app.servicos.dados import listar_safras_ativas, obter_resumo_estoque

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
# 2. ESTILOS VISUAIS MODERNOS
# -----------------------------------------------------------------------------
aplicar_estilos()

# -----------------------------------------------------------------------------
# 3. CARREGAMENTO DE SAFRAS / PRODUTOS ATIVOS
# -----------------------------------------------------------------------------
try:
    safras = listar_safras_ativas()
except Exception as e:
    st.error(f"Erro ao conectar com o banco: {e}")
    safras = []

opcoes_safras = {s["rotulo"]: s for s in safras} if safras else {}

# -----------------------------------------------------------------------------
# 4. BARRA LATERAL (MENU DE NAVEGAÇÃO E IDENTIDADE)
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

    st.markdown(
        "<p style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>Navegação</p>",
        unsafe_allow_html=True,
    )
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
    st.markdown(
        "<p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;'>Disponível em Estoque</p>",
        unsafe_allow_html=True,
    )
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
# 5. ROTEAMENTO DAS TELAS
# -----------------------------------------------------------------------------
if menu == "💰 Meu Bolso":
    renderizar_tela_meu_bolso(safras, opcoes_safras)
elif menu == "📦 Controle de Estoque":
    renderizar_tela_estoque(safras, opcoes_safras)
elif menu == "🚛 Carga do Caminhão":
    renderizar_tela_cargas(safras, opcoes_safras)
elif menu == "👷 Trabalhadores & Diárias":
    renderizar_tela_trabalhadores(safras, opcoes_safras)
elif menu == "💸 Custos & Insumos":
    renderizar_tela_custos(safras, opcoes_safras)
