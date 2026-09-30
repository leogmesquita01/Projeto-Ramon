from datetime import date
from typing import Any

import streamlit as st
from app.servicos.dados import listar_ultimos_custos, salvar_custo


def renderizar_tela_custos(
    safras: list[dict[str, Any]],
    opcoes_safras: dict[str, dict[str, Any]],
) -> None:
    """
    Renderiza a tela 'Custos & Insumos' para lançamento de despesas operacionais
    (energia, embalagens, combustível, manutenção) e histórico.
    """
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
