# core/engine.py
from datetime import datetime
from typing import List
import pandas as pd
from core.rule import Rule
from core.event import Event


class RuleEngine:
    """
    Evalua las reglas sobre los datos y genera eventos
    """

    def __init__(self, rules: List[Rule]):
        self.rules = rules

        # Graba cuando una condicion comienza
        self.rule_start_times = {}

        # Reglas que ya emitieron un evento mientras la condicion sigue activa
        self.rule_fired = set()

    def process(self, data_window: pd.DataFrame) -> List[Event]:
        events = []

        for rule in self.rules:

            now = datetime.now()
            condition_met = rule.evaluate(data_window)

            if condition_met:

                if rule.name not in self.rule_start_times:
                    self.rule_start_times[rule.name] = now

                elapsed = (now - self.rule_start_times[rule.name]).total_seconds()

                # Emite el evento una sola vez mientras la condicion permanezca activa
                if elapsed >= rule.duration and rule.name not in self.rule_fired:
                    self.rule_fired.add(rule.name)
                    event = Event(
                        timestamp=now.strftime("%H:%M:%S"),
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=f"{rule.name}"
                    )
                    events.append(event)

            else:
                # La condicion se normalizo: reinicia el estado de la regla
                self.rule_start_times.pop(rule.name, None)
                self.rule_fired.discard(rule.name)

        return events
