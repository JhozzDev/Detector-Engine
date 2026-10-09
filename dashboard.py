import streamlit as st
import requests
import random
import os
import pandas as pd
from datetime import datetime

# Configuración 
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8010/process")
MAX_POINTS = 30
MAX_EVENTS = 100

# Header
st.set_page_config(page_title="Dashboard", layout="wide")

# Sesiones 
if "running" not in st.session_state:
    st.session_state.running = False

if "buffer" not in st.session_state:
    st.session_state.buffer = []

if "events" not in st.session_state:
    st.session_state.events = []

if "started_time" not in st.session_state:
    st.session_state.started_time = datetime.now()


# Generador de datos
def generar_datos():
    return {
        "temperature": random.randint(60, 100),
        "pressure": random.randint(50, 100),
        "humidity": random.randint(40, 100),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }


# UI
st.title("Dashboard")
st.subheader("Motor de detección de fallas")

col1, col2 = st.columns(2)

# Uso de botones
with col1:
    if st.button("Iniciar"):
        st.session_state.running = True
        st.session_state.started_time = datetime.now()

with col2:
    if st.button("Detener"):
        st.session_state.running = False


# Bloque en tiempo real: solo este fragmento se re-ejecuta cada segundo,
# por lo que el resto de la pagina no parpadea ni pierde las metricas.
@st.fragment(run_every=(1.0 if st.session_state.running else None))
def render_realtime():

    if not st.session_state.running:
        st.info("Click en iniciar")
        return

    current_time = datetime.now()
    minutes = int((current_time - st.session_state.started_time).total_seconds() / 60)

    data = generar_datos()

    delta_temp = (
        data["temperature"] - st.session_state.buffer[-1]["temperature"]
        if len(st.session_state.buffer) > 0
        else 0
    )

    delta_humi = (
        data["humidity"] - st.session_state.buffer[-1]["humidity"]
        if len(st.session_state.buffer) > 0
        else 0
    )

    delta_press = (
        data["pressure"] - st.session_state.buffer[-1]["pressure"]
        if len(st.session_state.buffer) > 0
        else 0
    )

    # Guardar datos
    st.session_state.buffer.append(data)
    st.session_state.buffer = st.session_state.buffer[-MAX_POINTS:]

    temp_series = [x["temperature"] for x in st.session_state.buffer]
    pressure_series = [x["pressure"] for x in st.session_state.buffer]
    humidity_series = [x["humidity"] for x in st.session_state.buffer]

    # Gráfico
    df = pd.DataFrame(st.session_state.buffer)
    df.set_index("timestamp", inplace=True)

    st.line_chart(df, color=["#FF000080", "#0000FF80", "#FBFF00E8"], height=700)

    st.divider()
    st.subheader("Metricas")

    m1, m2, m3 = st.columns(3)
    m4, m5, m6 = st.columns(3)

    m1.metric("Temp", data["temperature"], delta=delta_temp, border=True, chart_data=temp_series, chart_type="area")
    m2.metric("Pressure", data["pressure"], delta=delta_press, border=True, chart_data=pressure_series, chart_type="area")
    m3.metric("Humidity", data["humidity"], delta=delta_humi, border=True, chart_data=humidity_series, chart_type="area")
    m4.metric("Started Time", f"{minutes} min", border=True)
    m5.metric("Events", len(st.session_state.events), border=True)

    st.subheader("Eventos")

    # LLamada Api - se envia el buffer como ventana deslizante
    try:
        payload = {**data, "history": st.session_state.buffer[-MAX_POINTS:]}
        response = requests.post(API_URL, json=payload, timeout=5)

        # Pasa error si peticion falla
        response.raise_for_status()

        # Traspasar json
        result = response.json()
        new_events = result.get("events", [])

        for event in new_events:
            st.session_state.events.append(event)

        # Limitar el historial de eventos en memoria
        st.session_state.events = st.session_state.events[-MAX_EVENTS:]

    # Excepcion
    except Exception as e:
        st.session_state.events.append({
            "severity": "error",
            "rule": "API",
            "timestamp": str(e)
        })

    # Mostrar los eventos mas recientes
    if st.session_state.events:
        for event in st.session_state.events[-10:]:
            st.warning(f"{event['rule'].upper()} | {event['severity'].upper()} | {event['timestamp'].upper()}")


render_realtime()
