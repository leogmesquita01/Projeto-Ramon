from datetime import date
from typing import Any

import streamlit as st
from app.servicos.dados import (
    cadastrar_trabalhador,
    listar_trabalhadores,
    listar_ultimos_pagamentos,
    salvar_pagamento_trabalhador,
)


def renderizar_tela_trabalhadores(
    safras: list[dict[str, Any]],
    opcoes_safras: dict[str, dict[str, Any]],
) -> None:
    """
    Renderiza a tela 'Trabalhadores & Diárias' para controle de diárias,
    cadastro de diaristas e histórico de pagamentos de mão de obra.
    """
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
