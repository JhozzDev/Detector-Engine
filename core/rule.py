# core/rule.py

from dataclasses import dataclass
from typing import Callable, List
import pandas as pd

@dataclass
class Rule:
    """
    Representa las reglas de cada falla

    Define:
    - Sensor involucrado
    - Condicion
    - Cuanto tiempo duro
    - El Grado de la falla
    """
    name: str
    sensors: List[str]
    condition: Callable[[pd.DataFrame], bool]
    duration: int
    severity: str

    def evaluate(self, data_window: pd.DataFrame) -> bool:
        """
        Evalua las condiciones dadas por la ventana deslizante
        """
        return self.condition(data_window) 
