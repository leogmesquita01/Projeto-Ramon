from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Carga:
    id: Optional[int]
    safra_id: int
    data: date
    quantidade_sacas: int
    preco_id: Optional[int] = None
    valor_total: Optional[float] = None
