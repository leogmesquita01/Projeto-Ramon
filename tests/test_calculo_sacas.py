import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.servicos.calculo_sacas import (
    obter_resumo_sacas_safra,
    obter_total_sacas_por_cultura,
)


def testar_calculo_sacas():
    print("--- Testando Serviço de Cálculo de Sacas ---")

    resumo_safra_1 = obter_resumo_sacas_safra(1)
    print(f"Resumo da Safra 1: {resumo_safra_1}")

    assert resumo_safra_1["safra_id"] == 1
    assert resumo_safra_1["total_sacas"] == 50.0
    assert resumo_safra_1["total_cargas"] == 1
    assert resumo_safra_1["media_sacas_por_carga"] == 50.0

    totais_cultura = obter_total_sacas_por_cultura()
    print(f"Totais por Cultura: {totais_cultura}")

    assert len(totais_cultura) > 0
    assert totais_cultura[0]["cultura"] == "Milho"
    assert totais_cultura[0]["total_sacas"] == 50.0

    print("✅ Todos os testes de calculo_sacas.py passaram com sucesso!")


if __name__ == "__main__":
    testar_calculo_sacas()
