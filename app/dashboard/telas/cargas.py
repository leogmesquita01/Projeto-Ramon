from datetime import date
from typing import Any

import streamlit as st
from app.servicos.dados import (
    listar_ultimas_cargas,
    obter_resumo_estoque,
    salvar_carga,
)


def renderizar_tela_cargas(
    safras: list[dict[str, Any]],
    opcoes_safras: dict[str, dict[str, Any]],
) -> None:
    """
    Renderiza a tela 'Carga do Caminhão' para registro rápido de vendas ou compras para revenda,
    calculadora de faturamento/custo e histórico de cargas negociadas.
    """
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
        return

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
                        st.caption(f"📦 **Estoque disponível no galpão:** :green[{saldo_prod} sacos]")
                    else:
                        st.caption("📦 **Estoque no galpão:** :orange[0 sacos registrados]")
            except Exception:
                pass

            data_carga = st.date_input(
                "📅 Data do Carregamento / Negociação:",
                value=date.today(),
                help="Data em que o caminhão foi negociado",
            )

            if eh_venda:
                qtd_sacas = st.number_input(
                    "📦 Quantidade de Sacos (Inteiros):",
                    min_value=1,
                    max_value=100000,
                    value=50,
                    step=1,
                    help="Número total de sacos cheios carregados no caminhão",
                )
                preco_saca = st.number_input(
                    "🏷️ Preço Combinado de Venda por Saco (R$):",
                    min_value=0.0,
                    max_value=5000.0,
                    value=40.0,
                    step=0.50,
                    help="Preço acordado para a venda de cada saco",
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
                            <strong>{produto_carga_rotulo}</strong>: <strong>{qtd_sacas}</strong> sacos × <strong>R$ {preco_saca:,.2f}</strong>/saco
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
                    f"✅ Venda #{carga_id} salva! ({qtd_sacas} sacos = R$ {valor_total_calculado:,.2f})"
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
                    "Total de Sacos": f"{int(c['quantidade_sacas'])} sacos" if c.get("quantidade_sacas", 0) > 0 else "Carrada Fechada",
                    "Preço / Valor": f"R$ {c['valor_por_saca']:,.2f}/saco" if c.get("quantidade_sacas", 0) > 0 else f"R$ {c['valor_total']:,.2f}",
                    "Valor Total": f"R$ {c['valor_total']:,.2f}",
                }
                for c in ultimas_cargas
            ]
            st.dataframe(dados_tabela, use_container_width=True)
        else:
            st.info("Nenhuma carga registrada no sistema ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar lista de cargas: {e}")
