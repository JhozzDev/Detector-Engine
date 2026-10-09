# Motor de detección de fallas

Motor configurable para la **detección temprana de comportamiento inusual** en sistemas monitoreados. Combina un **motor de reglas flexibles** con un **modelo de machine learning** (Isolation Forest) y expone los resultados a través de una **API** y un **dashboard en tiempo real**.

<img width="1600" height="900" alt="Motor de detección de fallas" src="https://github.com/user-attachments/assets/424bb8e6-216c-4ea1-b69e-47109768c0d7" />

---

## Características

- **Reglas configurables**: nombre, sensores, condición, duración y severidad.
- **Ventanas deslizantes de datos** para evaluar el comportamiento reciente.
- **Generación de eventos/alerts** con severidad y timestamp, sin duplicados mientras la condición permanezca activa.
- **Detección de anomalías** con Isolation Forest vía scikit-learn.
- **Dashboard en localhost** con gráfico, métricas y eventos en tiempo real (Streamlit).
- **Arquitectura desacoplada**: el dashboard consume la API, lo que facilita escalar y sustituir piezas.

---

## Arquitectura

```
┌─────────────────────┐        POST /process        ┌──────────────────────────┐
│  dashboard.py       │  ─────────────────────────▶ │  api/api.py              │
│  (Streamlit)        │                             │  (FastAPI)               │
│                     │  ◀───────────────────────── │                          │
│  · gráfico          │   { prediction, events }    │  · escala temperatura    │
│  · métricas         │                             │  · Isolation Forest      │
│  · eventos          │                             │  · RuleEngine            │
└─────────────────────┘                             └───────────┬──────────────┘
                                                                 │
                                                     ┌───────────▼──────────────┐
                                                     │  core/                    │
                                                     │  · rule.py    (Rule)      │
                                                     │  · event.py   (Event)     │
                                                     │  · engine.py  (RuleEngine)│
                                                     └───────────────────────────┘

models/machine_model.py ──entrena──▶ models/*.pkl
data/temperaturas.csv  ──(datos)──▶
```

---

## Estructura del proyecto

```
.
├── api/
│   └── api.py              # API FastAPI: /home y /process
├── core/
│   ├── engine.py           # RuleEngine: evalúa reglas y emite eventos
│   ├── rule.py             # Rule: definición de una regla
│   └── event.py            # Event: evento generado
├── models/
│   └── machine_model.py    # Entrenamiento del modelo (Isolation Forest)
├── data/
│   └── temperaturas.csv    # Datos de ejemplo (~1013 registros)
├── docs/
│   └── escenario.md        # Descripción de un escenario de falla
├── tests/
│   └── test_engine.py      # Pruebas del motor de reglas
├── dashboard.py            # Dashboard Streamlit
├── requirements.txt
└── README.md
```

> Los archivos `models/*.pkl` y las carpetas `__pycache__/` están ignorados por Git. El modelo se puede regenerar con `models/machine_model.py`.

---

## Requisitos

- **Python 3.10+** (probado con 3.12)
- `pip`

Dependencias principales: `pandas`, `numpy`, `scikit-learn`, `joblib`, `streamlit`, `fastapi`, `uvicorn`, `requests`, `pytest`.

---

## Instalación

```bash
git clone https://github.com/JhozzDev/Detector-Engine.git
cd Detector-Engine

# Entorno virtual (opcional pero recomendado)
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Uso

La aplicación tiene **dos procesos**: la API (backend) y el dashboard (frontend).

### 1. Iniciar la API

```bash
python -m uvicorn api.api:app --host 127.0.0.1 --port 8010
```

La API queda en `http://127.0.0.1:8010`.

### 2. Iniciar el dashboard

En otra terminal:

```bash
streamlit run dashboard.py
```

Abre `http://localhost:8501`, pulsa **Iniciar** y verás el gráfico, las métricas y los eventos en tiempo real.

> El dashboard apunta por defecto a `http://127.0.0.1:8010/process`. Si cambias el puerto de la API, frente a un puerto ya ocupado (como el 8000 que usa PostgreSQL), puedes sobrescribirlo con:

```bash
# Windows (PowerShell)
$env:API_URL="http://127.0.0.1:8000/process"; streamlit run dashboard.py

# Linux / macOS
API_URL="http://127.0.0.1:8000/process" streamlit run dashboard.py
```

---

## Reglas y umbrales

Las reglas se definen en `api/api.py` y se evalúan sobre la ventana de datos. Umbrales actuales:

| Regla | Sensor | Condición | Duración | Severidad |
|-------|--------|-----------|----------|-----------|
| ML temp anomaly | temperatura | predicha como anomalía (`-1`) | 1 s | Critic |
| Over heat | temperatura | `>= 89` | 1 s | Critic |
| Over pressure | presión | `>= 90` | 1 s | Critic |
| Low humidity | humedad | `< 60` | 1 s | Critic |

Cada regla define:

```python
Rule(
    name="Over heat",
    sensors=["temperature"],
    condition=over_heat,     # Callable[[pd.DataFrame], bool]
    duration=1,              # segundos que debe sostenerse la condición
    severity="Critic",
)
```

---

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/home` | Comprobación de estado |
| `POST` | `/process` | Procesa una muestra o una ventana y devuelve los eventos |

**Ejemplo `POST /process`**

```bash
curl -X POST http://127.0.0.1:8010/process \
  -H "Content-Type: application/json" \
  -d '{"temperature": 95, "pressure": 92, "humidity": 50, "timestamp": "14:20:00"}'
```

Respuesta:

```json
{
  "prediction": -1,
  "events": [
    { "rule": "Over heat", "severity": "Critic", "timestamp": "14:20:00" }
  ]
}
```

El campo `prediction` es `1` (normal) o `-1` (anomalía) según el modelo. Opcionalmente se puede enviar `history` (lista de muestras) para evaluar una ventana deslizante real.

---

## Modelo de machine learning

`models/machine_model.py` entrena un pipeline sencillo sobre `data/temperaturas.csv`:

1. Selecciona la columna de temperatura y limpia valores inválidos.
2. Normaliza con `StandardScaler`.
- Entrena `IsolationForest` (`n_estimators=1000`, `contamination=0.05`).
- Guarda el modelo y el escalador en `models/`.

Para reentrenar:

```bash
python models/machine_model.py
```

---

## Tests

```bash
python -m pytest tests/ -q
```

Las pruebas cubren el motor de reglas: que no emita antes de cumplir la duración, que emita al cumplirla, que **no duplique** eventos mientras la condición sigue activa y que reinicie su estado al normalizarse.

---

## Casos de uso

1. Maquinaria industrial.
2. Sensores en tiempo real.
3. Plantas de generación eléctrica.
4. Análisis preventivo.
5. Monitoreo en general.

---

## Tecnologías

| Tecnología | Rol |
|------------|-----|
| **scikit-learn** | Detección de anomalías (Isolation Forest) |
| **pandas / numpy** | Manejo de datos y series |
| **Streamlit** | Dashboard en localhost en tiempo real |
| **FastAPI** | API desacoplada del dashboard |
| **uvicorn** | Servidor ASGI |
| **joblib** | Serialización del modelo |
| **pytest** | Pruebas automatizadas |
