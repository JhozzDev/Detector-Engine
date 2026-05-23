import pandas as pd 
import numpy as np

from sklearn.ensemble import IsolationForest 
from sklearn.preprocessing import StandardScaler 

import joblib 

df = pd.read_csv("data/temperaturas.csv")
features = ["temperaturas"]
X = df[features] 
X = X.dropna()
X = X[X["temperaturas"] > 0]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X) 


model = IsolationForest(

    n_estimators=1000,
    contamination=0.05, 
    random_state=42,
    bootstrap=True


) 

model.fit(X_scaled)
df["ml_result"] = model.predict(X_scaled) 

df["ml_result"] = df["ml_result"].map({
    1: "Normal",
    -1: "Anomalia Detectada por ML"
})

print(df)

joblib.dump(model, "models/model_fallas.pkl")
joblib.dump(scaler, "models/scaler.pkl")

def decision(d, ml):
    if d > 90 and d<70:
        return "Falla"
    elif ml == -1:
        return "Advertencia ML"
    else:
        return "Normal"

