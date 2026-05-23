import streamlit as st
import requests
import random
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import random

API_URL = "http://127.0.0.1:8000/process"
MAX_POINTS = 30

st.set_page_config(page_title="Dashboard", layout="wide")
st_autorefresh(interval=1000, key="refresh")

if "running" not in st.session_state:
    st.session_state.running = False

if "buffer" not in st.session_state:
    st.session_state.buffer = []

if "events" not in st.session_state:
    st.session_state.events = []

if "started_time" not in st.session_state:
    st.session_state.started_time = datetime.now()

st.title("Dashboard")
st.subheader("Motor de detección de fallas")

col1, col2 = st.columns(2)

with col1:
    if st.button("Iniciar"):
        st.session_state.running = True
        
with col2:
    if st.button("Detener"):
        st.session_state.running = False

chart_placeholder = st.empty()
st.divider()
st.subheader("Metricas")
metrics_placeholder = st.empty()

m1, m2, m3 = st.columns(3)
m4, m5, m6 = st.columns(3)

st.subheader("Eventos")
events_placeholder = st.empty()

def generar_datos():
    return {
        "temperature": random.randint(60, 100),
        "pressure": random.randint(50, 100),
        "humidity": random.randint(40, 100),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

if st.session_state.running:

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

    st.session_state.buffer.append(data)

    temp_series = [x["temperature"] for x in st.session_state.buffer[-MAX_POINTS:]]
    pressure_series = [x["pressure"] for x in st.session_state.buffer[-MAX_POINTS:]]
    humidity_series = [x["humidity"] for x in st.session_state.buffer[-MAX_POINTS:]]
    st.session_state.buffer = st.session_state.buffer[-MAX_POINTS:]

    df = pd.DataFrame(st.session_state.buffer)
    df.set_index("timestamp", inplace=True)

    with chart_placeholder:
         st.line_chart(df, color=["#FF000080", "#0000FF80", "#FBFF00E8"], height=700)

    with metrics_placeholder:
        m1.metric("Temp", data["temperature"], delta=delta_temp, border=True, chart_data=temp_series, chart_type="area")
        m2.metric("Pressure", data["pressure"], delta=delta_press, border=True, chart_data=pressure_series, chart_type="area")
        m3.metric("Humidity", data["humidity"], delta=delta_humi, border=True, chart_data=humidity_series, chart_type="area")
        m4.metric("Started Time", f"{minutes} min", border=True)
        m5.metric("Events", len(st.session_state.events), border=True)

    try:
        response = requests.post(API_URL, json=data, timeout=3)
        response.raise_for_status() 

        result = response.json()
        new_events = result.get("events", [])

        with events_placeholder: 
            if new_events:
                for event in new_events:
                    st.session_state.events.append(event)
                    st.warning(f"{event["rule"].upper()} | {event["severity"].upper()} | {event["timestamp"].upper()}")
        
    except Exception as e:
        st.session_state.events.append({
            "severity": "error",
            "rule": "API",
            "timestamp": str(e)
        })
        

else:
    with chart_placeholder:
        st.write("Click en iniciar")
