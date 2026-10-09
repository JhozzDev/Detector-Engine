from fastapi import FastAPI
import pandas as pd
from core.rule import Rule
from core.engine import RuleEngine
import joblib


app = FastAPI()

# Cargar modelo
model = joblib.load("models/model_fallas.pkl")
scaler = joblib.load("models/scaler.pkl")

# Umbrales de las reglas
OVER_HEAT_TEMP = 89   # °C
OVER_PRESSURE = 90    # presion
LOW_HUMIDITY = 60     # % humedad


def ml_anomaly_rule(df):
    return df["ml_result"].iloc[-1] == -1


def over_heat(df):
    return df["temperature"].iloc[-1] >= OVER_HEAT_TEMP


def over_pressure(df):
    return df["pressure"].iloc[-1] >= OVER_PRESSURE


def low_humidity(df):
    return df["humidity"].iloc[-1] < LOW_HUMIDITY


rules = [
    Rule(name="ML temp anomaly", sensors=["temperature"], condition=ml_anomaly_rule, duration=1, severity="Critic"),
    Rule(name="Over heat", sensors=["temperature"], condition=over_heat, duration=1, severity="Critic"),
    Rule(name="Over pressure", sensors=["pressure"], condition=over_pressure, duration=1, severity="Critic"),
    Rule(name="Low humidity", sensors=["humidity"], condition=low_humidity, duration=1, severity="Critic")]

# Motor
engine = RuleEngine(rules)


@app.get("/home")
def home():
    return {"Greeting": "Hi"}


# Definir ruta
@app.post("/process")
def process_data(data: dict):

    # Si el cliente envia una ventana de datos se usa como ventana deslizante;
    # si no, se evalua unicamente el punto actual.
    history = data.get("history")
    if history:
        df = pd.DataFrame(history)
    else:
        df = pd.DataFrame([data])

    # Escalar la temperatura del ultimo punto y predecir
    last_temp = df["temperature"].iloc[-1]
    X = scaler.transform([[last_temp]])
    pred = int(model.predict(X)[0])
    df["ml_result"] = pred

    events = engine.process(df)

    # Returnar JSON
    return {
        "prediction": pred,
        "events": [
            {
                "rule": e.rule_name,
                "severity": e.severity,
                "timestamp": str(e.timestamp)
            } for e in events
        ]
    }
