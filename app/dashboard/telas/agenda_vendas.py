import re
from datetime import date, timedelta
from typing import Any, Optional
import urllib.parse

import streamlit as st
from app.servicos import dados


def _formatar_link_whatsapp(telefone: str, cliente_nome: str, cultura_nome: str) -> Optional[str]:
    """
    Formata link direto para o WhatsApp do cliente com mensagem pré-preenchida.
    """
    digitos = re.sub(r"\D", "", telefone)
    if not digitos:
        return None
    # Adiciona DDD e código do país se necessário
    if len(digitos) in (10, 11):
        numero_completo = f"55{digitos}"
    elif len(digitos) > 11 and digitos.startswith("55"):
        numero_completo = digitos
    else:
        numero_completo = f"55{digitos}"

    msg = f"Olá {cliente_nome}, tudo bem? Entro em contato sobre o agendamento de venda de {cultura_nome}."
    msg_codificada = urllib.parse.quote(msg)
    return f"https://wa.me/{numero_completo}?text={msg_codificada}"


def renderizar_tela_agenda_vendas(
    safras: list[dict[str, Any]],
    opcoes_safras: dict[str, dict[str, Any]],
) -> None:
    """
    Renderiza a tela 'Agenda de Vendas', permitindo planejar compromissos de venda,
    acompanhar entregas futuras e efetivar o carregamento com 1 clique.
    """
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h1 style="color: #F8FAFC; margin: 0; font-size: 1.85rem; font-weight: 800;">
                📅 Agenda de Vendas & Entregas
            </h1>
            <p style="color: #94A3B8; margin-top: 0.3rem; font-size: 0.95rem;">
                Planejamento de compromissos com compradores, previsão de receita e despacho de cargas.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not safras:
        st.warning("Nenhum produto cadastrado no sistema ainda.")
        return

    # 1. MÉTRICAS CONSOLIDADAS NO TOPO
    try:
        resumo_agenda = dados.obter_resumo_agenda()
    except Exception as e:
        st.error(f"Erro ao carregar métricas da agenda: {e}")
        resumo_agenda = {
            "sacas_abertas": 0.0,
            "faturamento_previsto": 0.0,
            "total_adiantamento": 0.0,
            "proximos_7_dias": 0,
            "total_abertos": 0,
        }

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="agro-card" style="border: 2px solid #10B981;">
                <span style="color: #34D399; font-size: 0.82rem; font-weight: 700; text-transform: uppercase;">📦 Sacas Comprometidas</span>
                <h2 style="color: #F8FAFC; margin: 0.4rem 0 0 0; font-size: 1.75rem; font-weight: 800;">
                    {int(resumo_agenda['sacas_abertas']):,} sacas
                </h2>
                <span style="color: #A7F3D0; font-size: 0.8rem;">{resumo_agenda['total_abertos']} pedidos em aberto</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="agro-card">
                <span style="color: #FBBF24; font-size: 0.82rem; font-weight: 700; text-transform: uppercase;">⚡ Faturamento Previsto</span>
                <h2 style="color: #FBBF24; margin: 0.4rem 0 0 0; font-size: 1.75rem; font-weight: 800;">
                    R$ {resumo_agenda['faturamento_previsto']:,.2f}
                </h2>
                <span style="color: #64748B; font-size: 0.8rem;">A receber dos pedidos abertos</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="agro-card">
                <span style="color: #60A5FA; font-size: 0.82rem; font-weight: 700; text-transform: uppercase;">🚚 Próximos 7 Dias</span>
                <h2 style="color: #60A5FA; margin: 0.4rem 0 0 0; font-size: 1.75rem; font-weight: 800;">
                    {resumo_agenda['proximos_7_dias']} entregas
                </h2>
                <span style="color: #64748B; font-size: 0.8rem;">Carregamentos desta semana</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="agro-card">
                <span style="color: #94A3B8; font-size: 0.82rem; font-weight: 700; text-transform: uppercase;">💵 Sinal / Adiantamento</span>
                <h2 style="color: #F8FAFC; margin: 0.4rem 0 0 0; font-size: 1.75rem; font-weight: 800;">
                    R$ {resumo_agenda['total_adiantamento']:,.2f}
                </h2>
                <span style="color: #64748B; font-size: 0.8rem;">Já recebido antecipadamente</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. NAVEGAÇÃO ENTRE ABAS
    tab_compromissos, tab_novo = st.tabs([
        f"📋 Compromissos & Pedidos ({resumo_agenda['total_abertos']})",
        "➕ Agendar Nova Venda",
    ])

    # -------------------------------------------------------------------------
    # ABA 1: LISTAGEM DE COMPROMISSOS & CARREGAMENTOS
    # -------------------------------------------------------------------------
    with tab_compromissos:
        # Filtros
        with st.container(border=True):
            f_col1, f_col2, f_col3 = st.columns([1.2, 1.2, 1.2])
            with f_col1:
                filtro_status = st.selectbox(
                    "Filtrar por Situação:",
                    options=["Todos", "🟡 Pendentes", "🔵 Confirmados", "🟢 Concluídos", "❌ Cancelados"],
                    index=0,
                )
            with f_col2:
                opcoes_culturas_filtro = ["Todas as Culturas"] + list(opcoes_safras.keys())
                filtro_cultura = st.selectbox("Filtrar por Produto:", options=opcoes_culturas_filtro, index=0)
            with f_col3:
                filtro_periodo = st.selectbox(
                    "Filtrar por Prazo:",
                    options=["Qualquer Data", "🔴 Somente Hoje", "🚚 Próximos 7 Dias", "📅 Este Mês"],
                    index=0,
                )

        # Mapeamento do status para o banco
        status_db_map = {
            "Todos": "todos",
            "🟡 Pendentes": "pendente",
            "🔵 Confirmados": "confirmado",
            "🟢 Concluídos": "concluido",
            "❌ Cancelados": "cancelado",
        }
        status_db = status_db_map.get(filtro_status, "todos")

        safra_id_filtro = None
        if filtro_cultura != "Todas as Culturas":
            safra_id_filtro = opcoes_safras[filtro_cultura]["id"]

        data_ini_filtro = None
        data_fim_filtro = None
        hoje = date.today()
        if filtro_periodo == "🔴 Somente Hoje":
            data_ini_filtro = hoje
            data_fim_filtro = hoje
        elif filtro_periodo == "🚚 Próximos 7 Dias":
            data_ini_filtro = hoje
            data_fim_filtro = hoje + timedelta(days=7)
        elif filtro_periodo == "📅 Este Mês":
            data_ini_filtro = hoje.replace(day=1)
            # Fim do mês aproximado
            proximo_mes = (hoje.replace(day=28) + timedelta(days=4)).replace(day=1)
            data_fim_filtro = proximo_mes - timedelta(days=1)

        try:
            agendamentos = dados.listar_agendamentos(
                safra_id=safra_id_filtro,
                status=status_db,
                data_inicio=data_ini_filtro,
                data_fim=data_fim_filtro,
                limite=150,
            )
        except Exception as e:
            st.error(f"Erro ao buscar agendamentos: {e}")
            agendamentos = []

        if not agendamentos:
            st.info("💡 Nenhum compromisso de venda encontrado com os filtros selecionados.")
        else:
            for item in agendamentos:
                diff_dias = (item["data_prevista"] - hoje).days
                eh_aberto = item["status"] in ("pendente", "confirmado")

                # Identificação de prazo
                if item["status"] == "concluido":
                    prazo_badge_html = '<span class="agro-badge badge-verde">🟢 CONCLUÍDO</span>'
                elif item["status"] == "cancelado":
                    prazo_badge_html = '<span class="agro-badge badge-cinza">❌ CANCELADO</span>'
                elif diff_dias == 0:
                    prazo_badge_html = '<span class="agro-badge badge-vermelho">🔴 CARREGAMENTO HOJE</span>'
                elif diff_dias == 1:
                    prazo_badge_html = '<span class="agro-badge badge-ouro">🟠 AMANHÃ</span>'
                elif diff_dias > 1:
                    prazo_badge_html = f'<span class="agro-badge badge-azul">🔵 EM {diff_dias} DIAS</span>'
                else:
                    prazo_badge_html = f'<span class="agro-badge badge-vermelho">⚠️ ATRASADO ({abs(diff_dias)} DIAS)</span>'

                status_badge_class = {
                    "pendente": "badge-ouro",
                    "confirmado": "badge-azul",
                    "concluido": "badge-verde",
                    "cancelado": "badge-cinza",
                }.get(item["status"], "badge-cinza")

                with st.container(border=True):
                    col_detalhes, col_valores, col_acoes = st.columns([1.6, 1.2, 1.2], gap="medium")

                    with col_detalhes:
                        # Cabeçalho do pedido
                        link_wpp = _formatar_link_whatsapp(
                            item["cliente_telefone"], item["cliente_nome"], item["cultura_nome"]
                        )
                        cliente_html = f"<strong>{item['cliente_nome']}</strong>"
                        if link_wpp:
                            cliente_html += f' &nbsp; <a href="{link_wpp}" target="_blank" style="text-decoration: none; font-size: 0.85rem; color: #34D399; background: rgba(16, 185, 129, 0.15); padding: 2px 8px; border-radius: 6px;">💬 WhatsApp</a>'
                        elif item["cliente_telefone"]:
                            cliente_html += f" <span style='color: #94A3B8; font-size: 0.85rem;'>({item['cliente_telefone']})</span>"

                        st.markdown(
                            f"""
                            <div style="margin-bottom: 6px;">
                                <span style="font-size: 1.15rem; color: #F8FAFC;">{cliente_html}</span>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                                <span class="agro-badge {status_badge_class}">{item['status_rotulo']}</span>
                                {prazo_badge_html}
                            </div>
                            <div style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.5;">
                                📅 <strong>Data Prevista:</strong> {item['data_prevista'].strftime('%d/%m/%Y')}<br>
                                🌾 <strong>Produto:</strong> {item['icone']} {item['cultura_nome']}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Informações logísticas extras se existirem
                        extras = []
                        if item["motorista_placa"]:
                            extras.append(f"🚛 <strong>Motorista/Placa:</strong> {item['motorista_placa']}")
                        if item["local_entrega"]:
                            extras.append(f"📍 <strong>Local:</strong> {item['local_entrega']}")
                        if item["observacoes"]:
                            extras.append(f"📝 <em>{item['observacoes']}</em>")

                        if extras:
                            st.markdown(
                                f"""
                                <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 6px 10px; margin-top: 6px; font-size: 0.83rem; color: #94A3B8;">
                                    {"<br>".join(extras)}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    with col_valores:
                        saldo_restante = max(0.0, item["valor_total_estimado"] - item["valor_adiantamento"])
                        st.markdown(
                            f"""
                            <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 12px;">
                                <div style="font-size: 0.82rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Volume & Preço</div>
                                <div style="font-size: 1.15rem; color: #F8FAFC; font-weight: 800; margin: 2px 0;">
                                    {int(item['quantidade_sacas']):,} sacas
                                </div>
                                <div style="font-size: 0.85rem; color: #A7F3D0;">
                                    a R$ {item['preco_estimado_saca']:,.2f} / saca
                                </div>
                                <div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 6px 0; padding-top: 6px;">
                                    <span style="font-size: 0.82rem; color: #94A3B8;">Total Previsto:</span>
                                    <span style="font-size: 1.05rem; font-weight: 800; color: #FBBF24; display: block;">
                                        R$ {item['valor_total_estimado']:,.2f}
                                    </span>
                                </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if item["valor_adiantamento"] > 0:
                            st.markdown(
                                f"""
                                <div style="font-size: 0.8rem; color: #60A5FA;">
                                    💵 Sinal: R$ {item['valor_adiantamento']:,.2f}<br>
                                    <span style="color: #34D399; font-weight: 700;">Restante: R$ {saldo_restante:,.2f}</span>
                                </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown("</div>", unsafe_allow_html=True)

                    with col_acoes:
                        st.markdown("<div style='font-size: 0.82rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; margin-bottom: 6px;'>Ações Rápidas</div>", unsafe_allow_html=True)

                        if eh_aberto:
                            # Ação 1: Efetivar Carga (abre popover/expander para confirmar dados reais)
                            with st.popover("🚛 Efetivar Carga", use_container_width=True):
                                st.markdown(f"**Despachar Carga — {item['cliente_nome']}**")
                                st.caption(f"{item['icone']} {item['cultura_nome']}")

                                dt_real = st.date_input(
                                    "Data Efetiva de Carregamento:",
                                    value=item["data_prevista"],
                                    key=f"dt_efet_{item['id']}",
                                )
                                qtd_real = st.number_input(
                                    "Quantidade Real Carregada (Sacas):",
                                    min_value=1,
                                    max_value=100000,
                                    value=int(item["quantidade_sacas"]),
                                    step=1,
                                    key=f"qtd_efet_{item['id']}",
                                )
                                preco_real = st.number_input(
                                    "Preço Final por Saca (R$):",
                                    min_value=0.10,
                                    max_value=5000.0,
                                    value=float(item["preco_estimado_saca"]),
                                    step=0.50,
                                    key=f"prc_efet_{item['id']}",
                                )
                                tot_real = qtd_real * preco_real
                                st.info(f"Total a faturar: **R$ {tot_real:,.2f}**")

                                if st.button(
                                    "✅ Confirmar e Despachar Carga",
                                    key=f"btn_confirm_carga_{item['id']}",
                                    type="primary",
                                ):
                                    try:
                                        carga_criada_id = dados.efetivar_agendamento_como_carga(
                                            agendamento_id=item["id"],
                                            data_carga=dt_real,
                                            quantidade_sacas=qtd_real,
                                            valor_por_saca=preco_real,
                                        )
                                        st.success(f"Carga #{carga_criada_id} gerada com sucesso! Venda registrada.")
                                        st.rerun()
                                    except Exception as err:
                                        st.error(f"Erro ao gerar carga: {err}")

                            # Ação 2: Confirmar se estava pendente
                            if item["status"] == "pendente":
                                if st.button("🔵 Marcar Confirmado", key=f"btn_conf_{item['id']}", use_container_width=True):
                                    dados.atualizar_status_agendamento(item["id"], "confirmado")
                                    st.rerun()

                            # Ação 3: Cancelar
                            if st.button("❌ Cancelar Pedido", key=f"btn_canc_{item['id']}", use_container_width=True):
                                dados.atualizar_status_agendamento(item["id"], "cancelado")
                                st.rerun()

                        elif item["status"] == "concluido":
                            if item["carga_id"]:
                                st.markdown(
                                    f"""
                                    <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 8px; text-align: center;">
                                        <span style="color: #34D399; font-size: 0.85rem; font-weight: 700;">
                                            🟢 Vinculado à Carga #{item['carga_id']}
                                        </span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            # Permitir reabrir se necessário
                            if st.button("🔄 Reabrir Pedido", key=f"btn_reabrir_{item['id']}", use_container_width=True):
                                dados.atualizar_status_agendamento(item["id"], "pendente")
                                st.rerun()

                        elif item["status"] == "cancelado":
                            if st.button("🔄 Reativar Pedido", key=f"btn_reativar_{item['id']}", use_container_width=True):
                                dados.atualizar_status_agendamento(item["id"], "pendente")
                                st.rerun()

                        # Excluir agendamento com confirmação
                        with st.popover("🗑️ Excluir", use_container_width=True):
                            st.caption("Deseja apagar este agendamento do histórico?")
                            if st.button("Sim, apagar registro", key=f"btn_del_{item['id']}", type="primary"):
                                dados.excluir_agendamento(item["id"])
                                st.rerun()

    # -------------------------------------------------------------------------
    # ABA 2: AGENDAR NOVA VENDA
    # -------------------------------------------------------------------------
    with tab_novo:
        col_form, col_preview = st.columns([1.1, 1], gap="large")

        with col_form:
            with st.container(border=True):
                st.markdown("<h3 style='color: #34D399; margin-top: 0; font-size: 1.2rem;'>📝 Novo Compromisso de Venda</h3>", unsafe_allow_html=True)

                cliente_nome = st.text_input(
                    "👤 Nome do Comprador / Cliente *:",
                    placeholder="Ex: Ceasa Recife, Seu Zé, Comercial Esperança...",
                    help="Informe o nome ou apelido da pessoa/empresa compradora",
                )

                cliente_telefone = st.text_input(
                    "📱 Telefone / WhatsApp do Comprador (Opcional):",
                    placeholder="Ex: (81) 98888-7777 ou 81988887777",
                    help="Permite abrir conversa no WhatsApp com 1 clique direto da agenda",
                )

                produto_rotulo = st.selectbox(
                    "🌾 Produto / Cultura:",
                    options=list(opcoes_safras.keys()),
                    help="Escolha o produto que está sendo negociado",
                )
                safra_selecionada = opcoes_safras[produto_rotulo]

                # Saldo disponível em estoque para essa cultura
                saldo_disponivel = 0.0
                try:
                    resumo_est = dados.obter_resumo_estoque(safra_id=safra_selecionada["id"])
                    if resumo_est:
                        saldo_disponivel = resumo_est[0]["saldo_disponivel"]
                        if saldo_disponivel > 0:
                            st.caption(f"📦 **Estoque disponível no galpão:** :green[{int(saldo_disponivel)} sacas]")
                        else:
                            st.caption("📦 **Estoque disponível no galpão:** :orange[0 sacas registradas]")
                except Exception:
                    pass

                data_prevista = st.date_input(
                    "📅 Data Prevista para Carregamento / Entrega:",
                    value=date.today(),
                    help="Dia combinado para o carregamento do caminhão",
                )

                col_qtd, col_prc = st.columns(2)
                with col_qtd:
                    qtd_sacas = st.number_input(
                        "📦 Quantidade Prevista (Sacas):",
                        min_value=1,
                        max_value=100000,
                        value=50,
                        step=1,
                    )
                with col_prc:
                    preco_saca = st.number_input(
                        "🏷️ Preço Combinado por Saca (R$):",
                        min_value=0.50,
                        max_value=5000.0,
                        value=40.0,
                        step=0.50,
                    )

                status_escolhido = st.radio(
                    "Situação do Pedido:",
                    ["🟡 Pendente (A Confirmar)", "🔵 Confirmado"],
                    index=0,
                    horizontal=True,
                )
                status_db = "pendente" if "Pendente" in status_escolhido else "confirmado"

                with st.expander("🚚 Detalhes de Logística, Motorista & Sinal (Opcional)", expanded=False):
                    valor_sinal = st.number_input(
                        "💵 Sinal / Adiantamento Recebido (R$):",
                        min_value=0.0,
                        max_value=5000000.0,
                        value=0.0,
                        step=50.0,
                        help="Valor já adiantado pelo comprador como garantia",
                    )
                    motorista_placa = st.text_input(
                        "🚛 Motorista / Placa do Caminhão:",
                        placeholder="Ex: João - Placa ABC1D23",
                    )
                    local_entrega = st.text_input(
                        "📍 Local de Entrega / Destino:",
                        placeholder="Ex: Carregamento no galpão da fazenda / Entrega Ceasa Box 12",
                    )
                    observacoes = st.text_area(
                        "📝 Observações / Condições Comerciais:",
                        placeholder="Ex: Sacaria limpa padrão 60kg, pagamento do restante à vista na pesagem.",
                    )

                btn_salvar_agendamento = st.button("💾 Gravar Agendamento de Venda", type="primary")

        with col_preview:
            total_estimado = qtd_sacas * preco_saca
            saldo_a_receber = max(0.0, total_estimado - valor_sinal)

            st.markdown(
                f"""
                <div class="agro-card-gold">
                    <span class="agro-badge badge-ouro">⚡ PREVISÃO DE FATURAMENTO</span>
                    <h1 style="color: #FBBF24; margin: 0.6rem 0; font-size: 2.8rem; font-weight: 800;">
                        R$ {total_estimado:,.2f}
                    </h1>
                    <div style="background: rgba(0,0,0,0.25); border-radius: 10px; padding: 0.6rem; display: inline-block; margin-top: 0.3rem;">
                        <span style="color: #CBD5E1; font-size: 1.05rem;">
                            <strong>{produto_rotulo}</strong>: <strong>{qtd_sacas}</strong> sacas × <strong>R$ {preco_saca:,.2f}</strong>/sc
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Cartão de conferência com estoque
            if saldo_disponivel < qtd_sacas:
                st.warning(
                    f"⚠️ **Atenção ao Estoque:** O pedido prevê **{qtd_sacas} sacas**, mas o galpão tem atualmente **{int(saldo_disponivel)} sacas**. "
                    "Certifique-se de colher ou adquirir o complemento até a data do carregamento!"
                )
            else:
                st.success(
                    f"✅ **Estoque suficiente:** O galpão tem **{int(saldo_disponivel)} sacas**, o que atende tranquilamente este pedido."
                )

            # Resumo do adiantamento
            if valor_sinal > 0:
                st.markdown(
                    f"""
                    <div class="agro-card" style="border: 1px solid rgba(59, 130, 246, 0.4); text-align: center;">
                        <span class="agro-badge badge-azul">💵 CONTROLE DO SINAL</span>
                        <div style="margin-top: 8px; font-size: 1.05rem; color: #F8FAFC;">
                            Sinal Recebido: <strong style="color: #60A5FA;">R$ {valor_sinal:,.2f}</strong>
                        </div>
                        <div style="font-size: 1.15rem; color: #34D399; font-weight: 800; margin-top: 4px;">
                            Saldo Restante a Receber: R$ {saldo_a_receber:,.2f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if btn_salvar_agendamento:
            if not cliente_nome.strip():
                st.error("Por favor, preencha o nome do comprador.")
            else:
                try:
                    agendamento_id = dados.salvar_agendamento(
                        safra_id=safra_selecionada["id"],
                        cliente_nome=cliente_nome,
                        data_prevista=data_prevista,
                        quantidade_sacas=qtd_sacas,
                        preco_estimado_saca=preco_saca,
                        status=status_db,
                        cliente_telefone=cliente_telefone,
                        local_entrega=local_entrega,
                        motorista_placa=motorista_placa,
                        valor_adiantamento=valor_sinal,
                        observacoes=observacoes,
                    )
                    st.success(f"🎉 Agendamento de venda registrado com sucesso! (Código #{agendamento_id})")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar agendamento: {err}")
