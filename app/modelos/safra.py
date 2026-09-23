from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Safra:
    id: Optional[int]
    cultura_id: int
    data_inicio: date
    data_fim: Optional[date] = None
    status: str = "em_andamento"
