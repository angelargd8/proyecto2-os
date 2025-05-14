import streamlit as st
import pandas as pd
import time
import plotly.express as px
from io import BytesIO, StringIO

st.title("Simulador de algoritmos de calendarizacion ")


# 1. algoritmos soportados:
#-First in first out (FIFO)
#-Shortest job first (SJF)
#-Shortest remaining time (SRT)
#-Round Robin (RR)
#-Priority (PRIO)


st.subheader("***Seleccionar el algoritmo de calendarización:***")
# seleccion de algoritmo
algoritmo = st.selectbox("", 
                         ["First in first out", "Shortest job first", "Shortest remaining time", "Round Robin", "Priority"])

if algoritmo == "Round Robin":
    quantum = st.slider("Selecciona el Quantum", 1, 10, 2)
else:
    quantum = None

# 2. carga dinamica de procesos de archivos
st.subheader("Cargar archivo de procesos (.txt): ")
procesos_file = st.file_uploader("Selecciona un archivo de procesos", type="txt")

# 3. visualizacion del scheduling (requerimientos)
# - Linea del tiempo con bloques 
# - numero de ciclo
# - scroll horizontal
# - diferencia por nombre y color cada uno de los procesos
# - resumen de metricas de eficiencia de los algoritmos seleccionados



