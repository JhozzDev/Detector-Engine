from fastapi import FastAPI
import pandas as pd
from datetime import datetime, timedelta
from core.rule import Rule
from core.engine import RuleEngine
import joblib


app = FastAPI()

df = pd.read_csv("data/temperaturas.csv")
model = joblib.load("models/model_fallas.pkl")
scaler = joblib.load("models/scaler.pkl")

X = df[["temperaturas"]]
X_scaled = scaler.transform(X)
df["ml_result"] = model.predict(X_scaled)
df["estado_ml"] = df["ml_result"].map({
    1: "Normal",
    -1: "Anomalía detectada por ML"
})

def ml_anomaly_rule(df):
    return df["ml_result"].iloc[-1] == -1

def over_heat(df):
    return df["ml_result"].iloc[-1] >= 89

def over_pressure(df):
    return df["pressure"].iloc[-1] >= 100

def low_humidity(df):
    return df["humidity"].iloc[-1] < 60

rules = [
    Rule(name="ML temp anomaly", sensors=["temperature"], condition=ml_anomaly_rule, duration=1, severity="Critic"),
    Rule(name="Over heat", sensors=["temperature"], condition=over_heat, duration=1, severity="Critic"),
    Rule(name="Over pressure", sensors=["pressure"], condition=over_pressure, duration=1, severity="Critic"),
    Rule(name="Low humidity", sensors=["humidity"], condition=low_humidity, duration=1, severity="Critic")]

engine = RuleEngine(rules)

@app.get("/home")
def home():
    return {"Greeting": "Hi"}


@app.post("/process")
def process_data(data:dict):
    
    df = pd.DataFrame([data])
    X = scaler.transform([[data["temperature"]]])
    pred = model.predict(X)[0]
    df["ml_result"] = pred

    events = engine.process(df)

    return {
        "prediction": int(pred),
        "events": [
            {
                "rule": e.rule_name,
                "severity": e.severity,
                "timestamp": str(e.timestamp)
            } for e in events
        ]
    }
