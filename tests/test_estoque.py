import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app.servicos.dados import (
    listar_safras_ativas,
    salvar_movimentacao_estoque,
    listar_movimentacoes_estoque,
    obter_resumo_estoque,
)


def testar_estoque():
    print("--- Testando Controle de Estoque ---")
    safras = listar_safras_ativas()
    assert len(safras) >= 9, f"Esperado pelo menos 9 culturas ativas, encontrou {len(safras)}"

    # Verifica resumo de estoque
    resumo = obter_resumo_estoque()
    assert len(resumo) >= 9, f"Esperado pelo menos 9 itens no resumo, encontrou {len(resumo)}"
    print(f"✅ Resumo de estoque retornou {len(resumo)} culturas corretamente.")

    # Testa busca de movimentações
    movs = listar_movimentacoes_estoque(limite=5)
    assert isinstance(movs, list)
    print(f"✅ Listagem de movimentações retornou {len(movs)} registros.")
    print("✅ Todos os testes de estoque passaram com sucesso!")


if __name__ == "__main__":
    testar_estoque()
