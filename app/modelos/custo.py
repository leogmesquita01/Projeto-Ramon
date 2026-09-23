from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Custo:
    id: Optional[int]
    safra_id: int
    descricao: str
    valor: float
    data: date
