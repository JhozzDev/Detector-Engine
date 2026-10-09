import time
import pandas as pd

from core.engine import RuleEngine
from core.rule import Rule


def temperature_condition(df: pd.DataFrame):
    return df["temperature"].iloc[-1] > 80


rule = Rule(
    name="OverHeat",
    sensors=["temperature"],
    condition=temperature_condition,
    duration=2,
    severity="HIGH"
)

regla = Rule(
    name="Overheat",
    sensors=["temperature"],
    condition=temperature_condition,
    duration=1,
    severity="HIGH"
)


def test_dont_Throw():

    engine = RuleEngine([rule])

    buffer = []
    buffer.append({"temperature": 85})
    df = pd.DataFrame(buffer)

    events = engine.process(df)

    assert len(events) == 0


def test_Throw():

    engine = RuleEngine([regla])

    buffer = []

    buffer.append({"temperature": 85})
    df = pd.DataFrame(buffer)

    engine.process(df)
    time.sleep(1)

    eventos = engine.process(df)

    assert len(eventos) == 1
    assert eventos[0].rule_name == "Overheat"


def test_event_only_once():

    engine = RuleEngine([regla])
    df = pd.DataFrame([{"temperature": 85}])

    engine.process(df)
    time.sleep(1)

    assert len(engine.process(df)) == 1
    # No vuelve a emitir mientras la condicion siga activa
    assert len(engine.process(df)) == 0


def test_state_resets_when_normal():

    engine = RuleEngine([regla])
    hot = pd.DataFrame([{"temperature": 85}])
    cold = pd.DataFrame([{"temperature": 20}])

    engine.process(hot)
    time.sleep(1)
    assert len(engine.process(hot)) == 1

    # Al normalizarse la condicion se reinicia el estado
    engine.process(cold)
    assert len(engine.process(hot)) == 0
