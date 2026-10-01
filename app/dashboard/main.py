import os
import sys

# Garante que o diretório raiz do projeto esteja no caminho de busca de módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import importlib
import streamlit as st

from app.dashboard.estilos import aplicar_estilos

import app.servicos.dados as dados_service
try:
    importlib.reload(dados_service)
except Exception:
    pass

from app.servicos.dados import listar_safras_ativas, obter_resumo_estoque

from app.dashboard.telas.agenda_vendas import renderizar_tela_agenda_vendas
from app.dashboard.telas.cargas import renderizar_tela_cargas
from app.dashboard.telas.custos import renderizar_tela_custos
from app.dashboard.telas.estoque import renderizar_tela_estoque
from app.dashboard.telas.meu_bolso import renderizar_tela_meu_bolso
from app.dashboard.telas.trabalhadores import renderizar_tela_trabalhadores

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
# 4. BARRA LATERAL (MENU DE NAVEGAÇÃO E IDENTIDADE ESTILO DEVLEADS)
# -----------------------------------------------------------------------------
with st.sidebar:
    # Logo e Nome no topo da ilha
    logo_html = (
        '<div style="display: flex; align-items: center; gap: 11px; margin-bottom: 1.4rem; padding: 4px 2px 2px 2px;">'
        '<div style="width: 36px; height: 36px; border-radius: 11px; background: linear-gradient(135deg, rgba(184, 242, 45, 0.2), rgba(184, 242, 45, 0.04)); border: 1.5px solid #B8F22D; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 16px rgba(184, 242, 45, 0.18);">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#B8F22D" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>'
        '<path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>'
        '</svg>'
        '</div>'
        '<div>'
        '<div style="font-family: \'Montserrat\', sans-serif; font-size: 1.25rem; font-weight: 900; letter-spacing: -0.5px; color: #FFFFFF; line-height: 1;">'
        'Agro<span style="color: #B8F22D;">Gestão</span>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(logo_html, unsafe_allow_html=True)

    # Menu de Navegação moderno (Ícones de linha Material Symbols estilo DevLeads)
    menu_opcoes = [
        ":material/grid_view: Visão geral",
        ":material/calendar_today: Agenda de vendas",
        ":material/inventory_2: Controle de estoque",
        ":material/local_shipping: Cargas e entregas",
        ":material/group: Trabalhadores",
        ":material/payments: Custos e insumos",
    ]
    menu = st.radio(
        "Navegação:",
        menu_opcoes,
        label_visibility="collapsed",
    )

    # Divisor sutil estilo DevLeads
    st.markdown(
        """<div style="height: 1px; background: rgba(255, 255, 255, 0.06); margin: 1.5rem 0 1.2rem 0;"></div>""",
        unsafe_allow_html=True,
    )

    # Cartão de Capacidade & Status com barras de progresso (Fiel ao DevLeads)
    try:
        resumo_sidebar = obter_resumo_estoque()
        com_estoque = [c for c in resumo_sidebar if c["saldo_disponivel"] > 0]
        total_sacas_estoque = int(sum(c["saldo_disponivel"] for c in com_estoque))
    except Exception:
        total_sacas_estoque = 0

    capacidade_total = 2000
    pct_estoque = min(100, int((total_sacas_estoque / capacidade_total) * 100)) if total_sacas_estoque > 0 else 5

    card_html = (
        '<div style="background: #111113; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 16px; padding: 14px 15px; margin-bottom: 1.5rem;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-family: \'Manrope\', sans-serif; font-size: 0.8rem; color: #8E8E93; font-weight: 500;">Galpão (Sacas)</span>'
        f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.78rem; color: #F4F4F5; font-weight: 600;">{total_sacas_estoque:,} / {capacidade_total:,}</span>'
        '</div>'
        '<div style="width: 100%; height: 4px; background: #222226; border-radius: 2px; margin-bottom: 13px; overflow: hidden;">'
        f'<div style="width: {pct_estoque}%; height: 100%; background: #B8F22D; border-radius: 2px; box-shadow: 0 0 8px rgba(184, 242, 45, 0.5);"></div>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-family: \'Manrope\', sans-serif; font-size: 0.8rem; color: #8E8E93; font-weight: 500;">Cargas no Mês</span>'
        '<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.78rem; color: #F4F4F5; font-weight: 600;">14 / 20</span>'
        '</div>'
        '<div style="width: 100%; height: 4px; background: #222226; border-radius: 2px; margin-bottom: 13px; overflow: hidden;">'
        '<div style="width: 70%; height: 100%; background: #B8F22D; border-radius: 2px;"></div>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
        '<span style="font-family: \'Manrope\', sans-serif; font-size: 0.8rem; color: #8E8E93; font-weight: 500;">IA AgroGestão</span>'
        '<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.78rem; color: #B8F22D; font-weight: 600;">Ativo • Pro</span>'
        '</div>'
        '<div style="width: 100%; height: 4px; background: #222226; border-radius: 2px; overflow: hidden;">'
        '<div style="width: 100%; height: 100%; background: #B8F22D; border-radius: 2px; box-shadow: 0 0 6px rgba(184, 242, 45, 0.4);"></div>'
        '</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # Perfil do Usuário e Configurações no rodapé (Exato layout DevLeads)
    perfil_html = (
        '<div style="margin-top: auto; padding-top: 1.2rem; border-top: 1px solid rgba(255, 255, 255, 0.06);">'
        '<div style="font-family: \'Manrope\', sans-serif; font-size: 1.05rem; font-weight: 800; color: #FFFFFF; line-height: 1.2; letter-spacing: -0.3px;">'
        'Leonardo Mesquita'
        '</div>'
        '<div style="font-family: \'JetBrains Mono\', monospace; font-size: 0.65rem; font-weight: 600; color: #71717A; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; margin-bottom: 14px;">'
        'CRIADOR'
        '</div>'
        '<div style="display: flex; align-items: center; gap: 8px; color: #8E8E93; font-family: \'Manrope\', sans-serif; font-size: 0.88rem; font-weight: 500; cursor: pointer;">'
        '<span class="material-symbols-rounded" style="font-size: 1.15rem; color: #8E8E93;">settings</span>'
        'Configurações'
        '</div>'
        '</div>'
    )
    st.markdown(perfil_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. ROTEAMENTO DAS TELAS
# -----------------------------------------------------------------------------
if "Visão geral" in menu or "Meu Bolso" in menu:
    renderizar_tela_meu_bolso(safras, opcoes_safras)
elif "Agenda" in menu:
    renderizar_tela_agenda_vendas(safras, opcoes_safras)
elif "estoque" in menu or "Estoque" in menu:
    renderizar_tela_estoque(safras, opcoes_safras)
elif "Cargas" in menu or "Carga" in menu:
    renderizar_tela_cargas(safras, opcoes_safras)
elif "Trabalhadores" in menu:
    renderizar_tela_trabalhadores(safras, opcoes_safras)
elif "Custos" in menu:
    renderizar_tela_custos(safras, opcoes_safras)
