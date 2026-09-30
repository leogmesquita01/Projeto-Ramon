import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app.servicos.dados import (
    atualizar_status_agendamento,
    efetivar_agendamento_como_carga,
    excluir_agendamento,
    listar_agendamentos,
    listar_safras_ativas,
    obter_resumo_agenda,
    salvar_agendamento,
)


def testar_fluxo_agendamentos():
    print("--- Iniciando Teste do Módulo Agenda de Vendas ---")

    safras = listar_safras_ativas()
    assert len(safras) > 0, "Deve haver ao menos uma cultura/safra cadastrada."
    safra = safras[0]
    safra_id = safra["id"]
    print(f"Safra de teste selecionada: {safra['rotulo']} (ID {safra_id})")

    # 1. Salvar agendamento
    data_prevista = date.today() + timedelta(days=3)
    agendamento_id = salvar_agendamento(
        safra_id=safra_id,
        cliente_nome="Cliente Teste Automatizado",
        cliente_telefone="81999998888",
        data_prevista=data_prevista,
        quantidade_sacas=120,
        preco_estimado_saca=45.50,
        status="pendente",
        local_entrega="Ceasa Box 10",
        motorista_placa="TST1A23",
        valor_adiantamento=500.0,
        observacoes="Entrega teste automatizado",
    )
    print(f"Agendamento criado com ID: {agendamento_id}")
    assert agendamento_id > 0

    # 2. Listar agendamentos e verificar campos
    itens = listar_agendamentos(safra_id=safra_id)
    criado = next((x for x in itens if x["id"] == agendamento_id), None)
    assert criado is not None, "O agendamento criado deve constar na listagem."
    assert criado["cliente_nome"] == "Cliente Teste Automatizado"
    assert criado["quantidade_sacas"] == 120
    assert criado["preco_estimado_saca"] == 45.50
    assert criado["valor_total_estimado"] == round(120 * 45.50, 2)
    assert criado["status"] == "pendente"
    assert criado["valor_adiantamento"] == 500.0
    print("✅ Criação e listagem validadas com sucesso.")

    # 3. Atualizar status
    atualizar_status_agendamento(agendamento_id, "confirmado")
    itens_atualizados = listar_agendamentos(safra_id=safra_id)
    criado_atualizado = next(x for x in itens_atualizados if x["id"] == agendamento_id)
    assert criado_atualizado["status"] == "confirmado"
    print("✅ Atualização de status para 'confirmado' validada.")

    # 4. Resumo da agenda
    resumo = obter_resumo_agenda()
    assert resumo["sacas_abertas"] >= 120
    assert resumo["faturamento_previsto"] >= round(120 * 45.50, 2)
    print(f"Resumo da agenda: {resumo}")
    print("✅ Resumo de métricas validado com sucesso.")

    # 5. Efetivar agendamento como carga
    carga_id = efetivar_agendamento_como_carga(
        agendamento_id=agendamento_id,
        data_carga=data_prevista,
        quantidade_sacas=120,
        valor_por_saca=45.50,
    )
    print(f"Carga gerada com ID: {carga_id}")
    assert carga_id > 0

    itens_concluidos = listar_agendamentos(safra_id=safra_id)
    criado_concluido = next(x for x in itens_concluidos if x["id"] == agendamento_id)
    assert criado_concluido["status"] == "concluido"
    assert criado_concluido["carga_id"] == carga_id
    print("✅ Efetivação como Carga vinculada validada.")

    # 6. Limpeza do agendamento e carga de teste
    excluir_agendamento(agendamento_id)
    from app.database.conexao import obter_conexao
    conn = obter_conexao()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM cargas WHERE id = %s;", (carga_id,))
        cur.execute("DELETE FROM precos WHERE valor_por_saca = 45.50;")
        conn.commit()
    conn.close()

    itens_finais = listar_agendamentos(safra_id=safra_id)
    assert not any(x["id"] == agendamento_id for x in itens_finais)
    print("✅ Exclusão e limpeza validadas com sucesso.")

    print("\n🎉 TODOS OS TESTES DA AGENDA DE VENDAS PASSARAM COM 100% DE SUCESSO!")


if __name__ == "__main__":
    testar_fluxo_agendamentos()
