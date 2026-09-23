from dataclasses import dataclass
from typing import Optional


@dataclass
class Trabalhador:
    id: Optional[int]
    nome: str
    tipo_pagamento: str  # 'diaria' ou 'producao'
