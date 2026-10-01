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
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.2rem; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(184, 242, 45, 0.12); border: 1.5px solid #B8F22D; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">
                🌾
            </div>
            <div>
                <div style="font-family: 'Montserrat', sans-serif; font-size: 1.22rem; font-weight: 900; letter-spacing: -0.5px; color: #FFFFFF; line-height: 1.1;">
                    Agro<span style="color: #B8F22D;">Gestão</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #71717A; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 2px;">
                    Central da Lavoura
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu = st.radio(
        "Navegação:",
        [
            "📊 Visão Geral (Meu Bolso)",
            "📅 Agenda de Vendas",
            "📦 Controle de Estoque",
            "🚛 Carga do Caminhão",
            "👷 Trabalhadores & Diárias",
            "💸 Custos & Insumos",
        ],
        label_visibility="collapsed",
    )

    # Cartão de Estoque do Galpão (Estilo DevLeads "Limite do Plano")
    try:
        resumo_sidebar = obter_resumo_estoque()
        com_estoque = [c for c in resumo_sidebar if c["saldo_disponivel"] > 0]
        total_sacas_estoque = sum(c["saldo_disponivel"] for c in com_estoque)

        if com_estoque:
            linhas_itens = "".join([
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.04);">
                    <span style="font-size: 0.82rem; color: #A1A1AA; font-weight: 500;">{c['icone']} {c['cultura_nome']}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; color: #B8F22D;">{int(c['saldo_disponivel']):,} sc</span>
                </div>
                """
                for c in com_estoque[:5]
            ])
            st.markdown(
                f"""
                <div style="background: #0E0E0E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 12px; margin-top: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 700; color: #71717A; text-transform: uppercase; letter-spacing: 0.6px;">
                            Disponível no Galpão
                        </span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #B8F22D; font-weight: 700;">
                            {int(total_sacas_estoque):,} sc
                        </span>
                    </div>
                    {linhas_itens}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background: #0E0E0E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 12px; margin-top: 1.5rem; text-align: center;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #71717A;">
                        ⚪ Nenhum saldo no galpão
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    except Exception:
        pass

    # Perfil do Usuário no rodapé da Sidebar (Estilo DevLeads)
    st.markdown(
        """
        <div style="margin-top: 1.2rem; padding: 10px 12px; background: #0E0E0E; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; display: flex; align-items: center; gap: 10px;">
            <div style="width: 34px; height: 34px; border-radius: 50%; background: #18181B; border: 1.5px solid #B8F22D; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 800; color: #B8F22D; font-family: 'JetBrains Mono', monospace;">
                LM
            </div>
            <div style="flex: 1; min-width: 0;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">
                    Leonardo Mesquita
                </div>
                <div style="font-size: 0.65rem; font-weight: 700; color: #B8F22D; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">
                    Produtor • Conectado
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 5. ROTEAMENTO DAS TELAS
# -----------------------------------------------------------------------------
if "Meu Bolso" in menu:
    renderizar_tela_meu_bolso(safras, opcoes_safras)
elif "Agenda" in menu:
    renderizar_tela_agenda_vendas(safras, opcoes_safras)
elif "Estoque" in menu:
    renderizar_tela_estoque(safras, opcoes_safras)
elif "Carga" in menu:
    renderizar_tela_cargas(safras, opcoes_safras)
elif "Trabalhadores" in menu:
    renderizar_tela_trabalhadores(safras, opcoes_safras)
elif "Custos" in menu:
    renderizar_tela_custos(safras, opcoes_safras)
