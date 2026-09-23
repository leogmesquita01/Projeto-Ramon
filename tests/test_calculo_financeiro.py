import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.servicos.calculo_financeiro import (
    obter_historico_precos_cultura,
    obter_resumo_financeiro_safra,
)


def testar_calculo_financeiro():
    print("--- Testando Serviço de Cálculo Financeiro ---")

    resumo_financeiro = obter_resumo_financeiro_safra(1)
    print(f"Resumo Financeiro Safra 1: {resumo_financeiro}")

    assert resumo_financeiro["safra_id"] == 1
    assert resumo_financeiro["receita_bruta"] == 2000.0
    assert resumo_financeiro["custos_operacionais"] == 100.0
    assert resumo_financeiro["custos_mao_de_obra"] == 80.0
    assert resumo_financeiro["custo_total"] == 180.0
    assert resumo_financeiro["lucro_liquido"] == 1820.0
    assert resumo_financeiro["margem_lucro_pct"] == 91.0

    historico_precos = obter_historico_precos_cultura(1)
    print(f"Histórico de Preços da Cultura 1: {historico_precos}")

    assert len(historico_precos) > 0
    assert historico_precos[0]["valor_por_saca"] == 40.0

    print("✅ Todos os testes de calculo_financeiro.py passaram com sucesso!")


if __name__ == "__main__":
    testar_calculo_financeiro()
