import streamlit as st
import pandas as pd
import time
import plotly.express as px
from io import BytesIO, StringIO
from queue import Queue
from collections import deque 

# 1. algoritmos soportados:
#-First in first out (FIFO)
#-Shortest job first (SJF)
#-Shortest remaining time (SRT)
#-Round Robin (RR)
#-Priority (PRIO)


st.title("Simulador de algoritmos de calendarizacion ")

st.subheader("***Selecciona el algoritmo de calendarización:***")
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

def graficar(algoritmo,i, grafico_gantt, timeline):
    parcial_df = pd.DataFrame(timeline)

    if not timeline:
        return 

    fig = px.bar(
        parcial_df,
        x="Duracion",
        y="Proceso",
        color="Proceso",
        orientation="h",
        text="Proceso"
    )

    fig.update_traces(
        base=parcial_df["Inicio"],
        hovertemplate='<b>%{text}</b><br>Inicio: %{base}<br>Duración: %{x}'
    )

    fig.update_layout(
        title= f"Simulacion {algoritmo}",
        xaxis_title="Ciclos",
        yaxis_title="Procesos",
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tick0=0,
            range=[0, 10],
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        ),
        bargap=0.2,
        height=400,
        width=500
    )

    grafico_gantt.plotly_chart(fig, use_container_width=True, key=f"grafico_{i}")
    time.sleep(0.8)


#los procesos siguen una cola fifo
# """
# - Ordenar los procesos según el orden de llegada.
# - Ejecutar el primer proceso hasta que termine.
# - Pasar al siguiente proceso y repetir hasta que todos los procesos hayan terminado.
# """
def fifo(procesos_df):
    #ordenar por tiempo de llegada
    # procesos_df = procesos_df.sort_values("AT")
    procesos_ordenados = procesos_df.sort_values("AT")


    cola = Queue()

    #llenar la cola con los procesos
    for _, proceso in procesos_ordenados.iterrows():
        cola.put(proceso)

    grafico_gantt = st.empty()
    tiempo = 0 
    timeline = []

    i = 0 
    while not cola.empty():
        
        proceso = cola.get()
        #ejecucion uno por uno sin interupciones
        start = max(tiempo, proceso["AT"])
        end = start + proceso["BT"]

        timeline.append({
            "Proceso": proceso["PID"],
            "Inicio": start,
            "Fin": end,
            "Duracion": proceso["BT"]
        })

        #tiempos ejecutados en secuencia
        tiempo = end

        graficar("First in first out",i, grafico_gantt, timeline)

        i+=1


    espera_total = 0
    for i, row in procesos_ordenados.iterrows():
        espera_total += max(0, timeline[i]["Inicio"] - row["AT"])
    avg_waiting_time= espera_total/len(procesos_ordenados)

    st.success(f"tiempo de espera promedio: {avg_waiting_time:.2f} ciclos")

    st.session_state["waitinTime"]["First in first out"] = avg_waiting_time


#sfj, se pueden conocer los tiempos de ejecucion de cada proceso con anticipacion
#funciona si los procesos estan todos disponibles a la vez
#no llegan a la cola en diferentes momentos
#contrarrestra el favorecimiento de procesos CPU-bound y mejora tiempos de respuesta
# """
# - Ordenar los procesos por su tiempo de ejecución, de menor a mayor.
# - Ejecutar el proceso con el menor tiempo de ejecución hasta que termine.
# - Repetir el proceso con el siguiente más corto hasta que todos los procesos hayan terminado.
# """
def sjf(procesos_df):

    procesos_restantes = procesos_df.copy()
    tiempo = 0
    ejecutados =[]
    i=0
    grafico_gantt = st.empty()
    timeline = []



    while not procesos_restantes.empty:

        #filtrar los procesos que estan 
        disponibles = procesos_restantes[procesos_restantes["AT"] <= tiempo]

        if disponibles.empty:
            #se avanza un 1 si no hay disponibles
            tiempo += 1
            continue

        #elegir el de menor BT
        proceso = disponibles.sort_values("BT").iloc[0]
        start = max(tiempo, proceso["AT"])
        end = start + proceso["BT"]

        timeline.append({
            "Proceso": proceso["PID"],
            "Inicio": start,
            "Fin": end,
            "Duracion": proceso["BT"]
        })


        #quitar los restantes
        procesos_restantes = procesos_restantes[procesos_restantes["PID"] != proceso["PID"]]

        tiempo = end
        ejecutados.append(proceso)

        graficar("Shortest job first", i, grafico_gantt, timeline)

        i+=1


    #
    espera = 0
    for p in ejecutados:
        tiempo_inicio = [t["Inicio"] for t in timeline if t["Proceso"] == p["PID"]][0]
        espera += tiempo_inicio - p["AT"]

    avg_waiting_time = espera/len(ejecutados)

    st.success(f"tiempo de espera promedio: {avg_waiting_time:.2f} ciclos")

    st.session_state["waitinTime"]["Shortest job first"] = avg_waiting_time


# - Ordenar los procesos según su tiempo de ejecución.
# - Ejecutar el proceso con el menor tiempo restante.
# - Si llega un nuevo proceso con menor tiempo restante, se interrumpe el proceso actual y se ejecuta el nuevo.
# - Repetir hasta que todos los procesos hayan terminado.
def srt(procesos_df):
    
    grafico_gantt = st.empty()
    tiempo = 0 
    timeline = []
    i=0
    ejecucion_ciclos = [] 

    procesos = procesos_df.copy()
    #remaining time
    procesos["RT"] = procesos["BT"]

    ejecutando = None
    start_time = None

    while not procesos.empty or ejecutando is not None: 

        #filtrar los procesos que estan 
        disponibles = procesos[(procesos["AT"] <= tiempo) & (procesos["RT"] > 0)]

        if disponibles.empty and ejecutando is None:
            tiempo+=1
            continue

        if not disponibles.empty :
            #seleccionar el proceso con menor RT

            siguiente = disponibles.sort_values("RT").iloc[0]
            #si se cambia de proceso/se interrumpe
            if ejecutando is None or siguiente["PID"] != ejecutando["PID"]:
                #Gguardar el anterior si esta corriendo
                if ejecutando is not None:
                    timeline.append({
                        "Proceso": ejecutando["PID"],
                        "Inicio": start_time,
                        "Fin": tiempo,
                        "Duracion": tiempo - start_time
                    })
                ejecutando = siguiente
                start_time = tiempo

        ejecucion_ciclos.append(f"Tiempo {tiempo} → {ejecutando['PID']}")
        

        #ejecutar 1 ciclo
        idx = procesos[procesos["PID"] == ejecutando["PID"]].index[0]
        procesos.at[idx, "RT"]-= 1

        #si termino
        if procesos.at[idx, "RT"] == 0:
            timeline.append({
                "Proceso": ejecutando["PID"],
                "Inicio": start_time,
                "Fin": tiempo + 1,
                "Duracion": tiempo + 1 - start_time
            })
            
            procesos = procesos.drop(idx)
            ejecutando = None
            start_time = None

        graficar("Shortest remaining time", i, grafico_gantt, timeline)
        tiempo+=1
        i+=1

    # Mostrar orden 
    st.subheader("Orden de ejecución paso a paso:")
    st.code("\n".join(ejecucion_ciclos))

    #tiempo de espera
    espera_total = 0
    for _, proceso in procesos_df.iterrows():
        ejecuciones = [b for b in timeline if b["Proceso"] == proceso["PID"]]
        start = ejecuciones[0]["Inicio"]
        end = sum(b["Duracion"] for b in ejecuciones)
        espera = start - proceso["AT"]
        espera_total += espera

    avg_wait = espera_total / len(procesos_df)
    st.success(f"Tiempo de espera promedio (SRT): {avg_wait:.2f} ciclos")

    st.session_state["waitinTime"]["Shortest remaining time"] = avg_wait


# - Establecer un tiempo máximo de ejecución (quantum) para cada proceso.
# - Ejecutar el primer proceso durante el tiempo del quantum.
# - Si el proceso no ha terminado, se pone en cola y se pasa al siguiente.
# - Repetir este ciclo hasta que todos los procesos hayan terminado.
def rr(procesos_df, quantum):
    
    grafico_gantt = st.empty()
    tiempo = 0 
    timeline = []
    i=0
    ejecucion_ciclos=[]

    procesos = procesos_df.copy()
    #remaining time
    procesos["RT"] = procesos["BT"]
    procesos["EnCola"] = False
    cola = deque()

    ejecutando = None
    start_time = None
    

    while not procesos[procesos["RT"]> 0].empty or cola:
        #anadir procesos nuevos que hayan llegado
        for idx, proceso in procesos.iterrows():
            if proceso["AT"] <= tiempo and not proceso["EnCola"] and proceso["RT"] >0:
                cola.append(idx)
                procesos.at[idx, "EnCola"] = True

        if not cola:
            tiempo +=1
            continue

        idx = cola.popleft()
        proceso= procesos.loc[idx]

        #ejecutar el proceso por min quantum, tiempo restante
        start = tiempo
        duracion = min(quantum, proceso["RT"])
        tiempo+=duracion
        procesos.at[idx, "RT"] -= duracion
        #si no ha terminado puede devolver a entrada
        procesos.at[idx, "EnCola"] = False

        timeline.append({
            "Proceso": proceso["PID"],
            "Inicio": start,
            "Fin": tiempo,
            "Duracion": duracion
        })

        for t in range(start, tiempo):
            ejecucion_ciclos.append(f"Tiempo {t} → {proceso['PID']}")

        # Si aun no termina, volver a la cola
        if procesos.at[idx, "RT"] > 0:
            # Aniadir cualquier proceso nuevo que haya llegado 
            for jdx, nuevo in procesos.iterrows():
                if nuevo["AT"] > start and nuevo["AT"] <= tiempo and not nuevo["EnCola"] and nuevo["RT"] > 0:
                    cola.append(jdx)
                    procesos.at[jdx, "EnCola"] = True

            cola.append(idx)

        graficar("round robin", i, grafico_gantt, timeline)
        i+=1
        tiempo+=1

    # # Mostrar orden 
    # st.subheader("Orden de ejecución paso a paso:")
    # st.code("\n".join(ejecucion_ciclos))
    


    espera_total = 0
    for _, proceso in procesos_df.iterrows():
        ejecuciones = [b for b in timeline if b["Proceso"] == proceso["PID"]]

        # Tiempo de espera
        fin = ejecuciones[-1]["Fin"]
        espera = fin - proceso["AT"] - proceso["BT"]
        espera_total += espera

    avg_wait = espera_total / len(procesos_df)
    st.success(f"Tiempo de espera promedio (Round Robin): {avg_wait:.2f} ciclos")
    st.session_state["waitinTime"]["Round Robin"] = avg_wait


# - Asignar una prioridad a cada proceso.
# - Ordenar los procesos por prioridad (de mayor a menor).
# - Ejecutar el proceso de mayor prioridad hasta que termine.
# - Pasar al siguiente proceso con mayor prioridad y repetir hasta completar todos los procesos.
def prio(procesos_df):

    grafico_gantt = st.empty()
    tiempo = 0 
    timeline = []
    i=0
    ejecucion_ciclos = [] 

    procesos_restantes = procesos_df.copy()

    while not procesos_restantes.empty:

        #filtrar los procesos que estan 
        disponibles = procesos_restantes[procesos_restantes["AT"] <= tiempo]

        if disponibles.empty:
            #se avanza un 1 si no hay disponibles
            tiempo += 1
            continue
        
        #seleccionar el de mayor prioridad, mrnor valor numerico 
        proceso = disponibles.sort_values("Priority").iloc[0]
        start = tiempo
        duracion = proceso["BT"]
        tiempo +=duracion

        timeline.append({
            "Proceso": proceso["PID"],
            "Inicio": start,
            "Fin": tiempo,
            "Duracion": duracion
        })

        for t in range(start, tiempo):
            ejecucion_ciclos.append(f"Tiempo {t} → {proceso['PID']}")

        #quitar los restantes
        procesos_restantes = procesos_restantes[procesos_restantes["PID"] != proceso["PID"]]

        graficar("Priority", i, grafico_gantt, timeline)
        i += 1


    # # Mostrar orden
    # st.subheader("Orden de ejecución paso a paso:")
    # st.code("\n".join(ejecucion_ciclos))

    # Calcular tiempo de espera
    espera_total = 0
    for _, proceso in procesos_df.iterrows():
        ejecuciones = [b for b in timeline if b["Proceso"] == proceso["PID"]]
        comienzo = ejecuciones[0]["Inicio"]
        espera = comienzo - proceso["AT"]
        espera_total += espera

    avg_wait = espera_total / len(procesos_df)
    st.success(f"Tiempo de espera promedio (Priority): {avg_wait:.2f} ciclos")

    st.session_state["waitinTime"]["Priority"] = avg_wait

    
#---------------------
procesos_df = None

if procesos_file:
    contenido = procesos_file.read().decode("utf-8")
    st.text_area("Contenido del archivo:", contenido, height=100)

    #parsear los datos
    data =[]
    for line in StringIO(contenido):
        if line.strip():
            try:
                pid, bt, at, priority = [x.strip() for x in line.split(",")]

                data.append({"PID": pid, "BT": int(bt), "AT": int(at), "Priority": int(priority)})

            except:
                st.error(f"error: " + {line.strip()})

    if data: 
        procesos_df = pd.DataFrame(data)
        st.success("se cargaron correctamente los procesos")



if "waitinTime" not in st.session_state:
    st.session_state["waitinTime"] = {
        "First in first out": 0,
        "Shortest job first": 0,
        "Shortest remaining time": 0,
        "Round Robin": 0,
        "Priority": 0
    }

if procesos_df is not None and st.button("Simular"):
    st.subheader("Diagrama de gantt")

    if algoritmo == "First in first out":
        fifo(procesos_df)
    elif algoritmo=="Shortest job first":
        sjf(procesos_df)
        
    elif algoritmo == "Shortest remaining time":
        srt(procesos_df)
        
    elif algoritmo == "Round Robin":
        rr(procesos_df, quantum)
        
    elif algoritmo == "Priority":
        prio(procesos_df)
        

    st.subheader("Resumen de metricas de eficiencia de los algoritmos:")
    st.write(":blue[Tiempos de espera por algoritmo]:")
    st.dataframe(pd.DataFrame.from_dict(
        st.session_state["waitinTime"], 
        orient="index", 
        columns=["Tiempo de espera (ciclos de CPU)"]
    ))

