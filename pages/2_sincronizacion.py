import streamlit as st
import pandas as pd
import time
import plotly.express as px
from io import BytesIO, StringIO
import plotly.graph_objects as go

st.title("Simulador de mecanismos de sincronizacion")

#mecanismos soportados: mutex locks, semaforos

#1. seleccion modo de sincronizacion
st.subheader("***Selecciona el modo de sincronizacion:***")
modo = st.selectbox("", ["mutex locks", "semaforos"])

# 2. carga dinamica de procesos de archivos
st.subheader("Cargar archivo de procesos de sincronizacion (.txt): ")
procesos_files= st.file_uploader(
    "Selecciona los archivos de procesos, acciones y recursos", 
    type="txt",
    accept_multiple_files=True
)

#archivos:
#procesos: PID,BT,AT,Priority
#recursos: NombreRecurso,Contador
#PID,ACCION,RECURSO,CICLO


#ejecutar la simulacion visualmente de manera dinamica

#visualizar horizontalmente  procesos, estados y acciones en una linea de tiempo grafica con scroll horizontal

#visualizacion dinamica del scheduling 
# """
# 1. linea del tiempo con bloques que representan las diferentes acciones detalladas 
# en el archivo de acciones y reflejando los diferentes estados en los que el proceso puede estar
# los estados son ACCESED o WAITING, dependiendo de si el recurso esta disponible o no
# numero de ciclo visible en todo momento. (asumiento que los tiempos de acceso a los recursos tanto read
# como write se miden en ciclos y cada operacion dura a lo maximo 1 ciclo)
# scroll horizontal dinamico cuando la cantidad de eventos exceda el espacio visual disponible
# diferenciacion visual entre accesos existosos y esperas

# Esta función simula el acceso a recursos críticos utilizando "mutex locks",
# solo un proceso puede acceder al recurso en un ciclo dado
# """

def MutexLocks(procesos_df, recursos_df, acciones_df):
    st.subheader("Simulacion con Mutex Locks")

    # Estado de los recursos: True = libre
    # diccionario para llevar el estado (libre/ocupado) de cada recurso
    recurso_estado = {row["nombreRecurso"]: True for _, row in recursos_df.iterrows()}
    # lista de acciones con que se graficara
    timeline = []

    # combinar acciones con atributos de procesos para filtrar por tiempo de llegada AT y BT
    acciones_df = acciones_df.merge(procesos_df[["PID", "AT", "BT"]], left_on="pid", right_on="PID", how="left")

    # filtrar las acciones que ocurren antes qhe e l proceso haya llegado
    acciones_df = acciones_df[acciones_df["ciclo"] >= acciones_df["AT"]]

    #limitar acciones por cada proceso segun su Burst Time
    acciones_df["accion_idx"] = acciones_df.groupby("pid").cumcount()
    acciones_df = acciones_df[acciones_df["accion_idx"] < acciones_df["BT"]]
    acciones_df = acciones_df.drop(columns=["accion_idx"])  

    acciones_realizadas = {pid: 0 for pid in procesos_df["PID"]}
    bt_map = dict(zip(procesos_df["PID"], procesos_df["BT"]))
    max_ciclo = acciones_df["ciclo"].max()

    #buffer de acciones que se tienen que volver a reintentar
    cola_espera = []
   
    for ciclo in range(max_ciclo + 10): 

        #obtener las acciones planeadas del ciclo
        acciones_en_ciclo = acciones_df[acciones_df["ciclo"] == ciclo].to_dict("records")
        #agregar acciones que estaban esperando
        acciones_en_ciclo += cola_espera
        cola_espera = []

        for accion in acciones_en_ciclo:
            pid = accion["pid"]
            recurso = accion["recurso"]
            tipo = accion["accion"]
            at = accion["AT"]

            #verificacion del tiempo de llgada, si no ha llegado se reprograma
            if ciclo < at:
                accion["ciclo"] = ciclo + 1
                cola_espera.append(accion)
                continue
            
            #verificar si el recurso esta disponible
            if recurso_estado[recurso]:
                estado = "ACCESSED"
                recurso_estado[recurso] = False
            else:
                #se reprograma la accion y se pone en waiting
                estado = "WAITING"
                accion["ciclo"] = ciclo + 1
                cola_espera.append(accion)

            #calcula las acciones que le quedan por ejecutar al proceso
            restantes = max(bt_map[pid] - acciones_realizadas[pid] - 1, 0)
            #registro en la linea del timepo del proceso en este ciclo
            timeline.append({
                "PID": pid,
                "Recurso": recurso,
                "Accion": tipo,
                "Estado": estado,
                "Inicio": ciclo,
                "Fin": ciclo + 1,
                "Restantes": restantes
            })

        # liberar todos los recursos usados en este ciclo
        for r in recurso_estado:
            recurso_estado[r] = True

        #salir si ya no hay acciones pendientes
        if ciclo > max_ciclo and len(cola_espera) == 0:
            break

    timeline_df = pd.DataFrame(timeline)
    st.write("Datos de simulacion:")
    st.dataframe(timeline_df)

    #graficar
    colores = {"ACCESSED": "green", "WAITING": "red"}
    placeholder = st.empty()

    ciclos_totales = timeline_df["Fin"].max()

    for ciclo_actual in range(ciclos_totales + 1):
        df_filtrado = timeline_df[timeline_df["Inicio"] <= ciclo_actual]

        fig = go.Figure()
        for _, row in df_filtrado.iterrows():
            fig.add_trace(go.Bar(
                x=[row["Fin"] - row["Inicio"]],
                y=[row["PID"]],
                base=[row["Inicio"]],
                orientation='h',
                marker_color=colores[row["Estado"]],
                hovertext=f'{row["Accion"]} en {row["Recurso"]} ({row["Estado"]}) ciclo {row["Inicio"]}',
                showlegend=False
            ))
        fig.add_trace(go.Bar(
            x=[0],
            y=["Leyenda"],
            orientation='h',
            marker_color='green',
            name='ACCESSED',
            showlegend=True
        ))
        fig.add_trace(go.Bar(
            x=[0],
            y=["Leyenda"],
            orientation='h',
            marker_color='red',
            name='WAITING',
            showlegend=True
        ))

        fig.update_layout(
            title=f"Ciclo {ciclo_actual}",
            xaxis=dict(title="Ciclo", tickmode="linear", dtick=1),
            yaxis=dict(title="Proceso", autorange="reversed"),
            height=400
        )

        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(1.5)


# Simula el acceso a recursos con semaforos contadores. Los recursos tienen un "contador"
# que representa cuantos procesos pueden acceder simultaneamente al mismo recurso
def semaforos(procesos_df, recursos_df, acciones_df):
    st.subheader("Simulacion con Semaforos")

    # mapeo de semaforos el recurso que se toma ese el contador disponible
    recurso_contador = {row["nombreRecurso"]: row["contador"] for _, row in recursos_df.iterrows()}
    uso_en_ciclo = {r: 0 for r in recurso_contador}

    timeline = []

    #ordenar por ciclo
    acciones_df = acciones_df.sort_values(by="ciclo")

    # Combinar datos para filtrar según AT y BT
    acciones_df = acciones_df.merge(procesos_df[["PID", "AT", "BT"]], left_on="pid", right_on="PID", how="left")

    # filtrado por AT y BT
    #limitar acciones por cada proceso segun su Burst Time
    acciones_df = acciones_df[acciones_df["ciclo"] >= acciones_df["AT"]]
    acciones_df["accion_idx"] = acciones_df.groupby("pid").cumcount()
    acciones_df = acciones_df[acciones_df["accion_idx"] < acciones_df["BT"]]
    acciones_df = acciones_df.drop(columns=["accion_idx"])

    #contador de cantidad todal de acciones 
    acciones_realizadas = {pid: 0 for pid in procesos_df["PID"]}
    bt_map = dict(zip(procesos_df["PID"], procesos_df["BT"]))
    max_ciclo = acciones_df["ciclo"].max()

    #buffer de acciones que se tienen que volver a reintentar
    cola_espera = []

    # por cada ciclo 
    for ciclo in range(max_ciclo + 10):
        #obtener las acciones planeadas del ciclo
        acciones_en_ciclo = acciones_df[acciones_df["ciclo"] == ciclo].to_dict("records")
        #agregar acciones que estaban esperando en ciclos pasados porque no se ejecutaron
        acciones_en_ciclo += cola_espera
        cola_espera = []
        #reiniciar un registro para saber cuantas veces fue usado cada recurso en este ciclo
        #es para liberarlos
        uso_en_ciclo = {r: 0 for r in recurso_contador}

        for accion in acciones_en_ciclo:
            pid = accion["pid"]
            recurso = accion["recurso"]
            tipo = accion["accion"]
            at = accion["AT"]

            #verificacion del tiempo de llgada, si no ha llegado se reprograma
            if ciclo < at:
                accion["ciclo"] = ciclo + 1
                cola_espera.append(accion)
                continue
            
            #verificar si el recurso esta disponible
            if recurso_contador[recurso] > 0:
                estado = "ACCESSED"
                recurso_contador[recurso] -= 1
                uso_en_ciclo[recurso] += 1
            else:
                #se reprograma la accion y se pone en waiting
                estado = "WAITING"
                accion["ciclo"] = ciclo + 1
                cola_espera.append(accion)

            #calcula las acciones que le quedan por ejecutar al proceso
            restantes = max(bt_map[pid] - acciones_realizadas[pid] - 1, 0)
            
            #registro en la linea del timepo del proceso en este ciclo
            timeline.append({
                "PID": pid,
                "Recurso": recurso,
                "Accion": tipo,
                "Estado": estado,
                "Inicio": ciclo,
                "Fin": ciclo + 1,
                "Restantes": restantes
            })

            #incrementar contador de acciones
            acciones_realizadas[pid] += 1

        #liberar recursos usados
        for r in uso_en_ciclo:
            recurso_contador[r] += uso_en_ciclo[r]

        #salir si ya no hay acciones pendientes
        if ciclo > max_ciclo and len(cola_espera) == 0:
            break

    # convertir el timeline en un dataframe
    timeline_df = pd.DataFrame(timeline)
    st.write("Datos de simulacion:")
    st.dataframe(timeline_df)

    #graficar
    colores = {"ACCESSED": "green", "WAITING": "orange"}
    placeholder = st.empty()

    ciclos_totales = timeline_df["Fin"].max()

    for ciclo_actual in range(ciclos_totales + 1):
        df_filtrado = timeline_df[timeline_df["Inicio"] <= ciclo_actual]

        fig = go.Figure()
        for _, row in df_filtrado.iterrows():
            fig.add_trace(go.Bar(
                x=[row["Fin"] - row["Inicio"]],
                y=[row["PID"]],
                base=[row["Inicio"]],
                orientation='h',
                marker_color=colores[row["Estado"]],
                hovertext=f'{row["PID"]} - {row["Accion"]} en {row["Recurso"]} ({row["Estado"]})\nCiclo {row["Inicio"]}\nQuedan: {row["Restantes"]} acciones',
                showlegend=False
            ))
        fig.add_trace(go.Bar(
            x=[0],
            y=["Leyenda"],
            orientation='h',
            marker_color='green',
            name='ACCESSED',
            showlegend=True
        ))
        fig.add_trace(go.Bar(
            x=[0],
            y=["Leyenda"],
            orientation='h',
            marker_color='orange',
            name='WAITING',
            showlegend=True
        ))

        fig.update_layout(
            title=f"Ciclo {ciclo_actual} (Semáforos)",
            xaxis=dict(title="Ciclo", tickmode="linear", dtick=1),
            yaxis=dict(title="Proceso", autorange="reversed"),
            height=400
        )

        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(1.5)


#----------
#cargar archivos
if procesos_files:
    for archivo in procesos_files:
        # st.write(archivo)
        contenido = archivo.read().decode("utf-8")
        #consultar informacion cargada
        st.text_area("contenido del archivo: " + archivo.name, contenido, height=100)
        

        if archivo.name == "procesos.txt":
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

        elif archivo.name =="recursos.txt":
            data=[]
            for line in StringIO(contenido):
                if line.strip():
                    try:
                        nombreRecurso, contador = [x.strip() for x in line.split(",")]
                        data.append({"nombreRecurso": nombreRecurso, "contador": int(contador)})

                    except: 
                        st.error(f"error " + {line.strip()})

            if data: 
                recursos_df = pd.DataFrame(data)
                st.success("se cargaron correctamente los recursos")

        elif archivo.name =="acciones.txt":
            data = []
            for line in StringIO(contenido):
                if line.strip():
                    try:
                        pid, accion, recurso, ciclo =[x.strip() for x in line.split(",")]
                        data.append({"pid": pid, "accion": accion, "recurso":recurso, "ciclo":int(ciclo)})
                    except:
                        st.error(f"error" + {line.strip()})
            if data: 
                acciones_df = pd.DataFrame(data)
                st.success("se cargaron correctamente las acciones")

        
        else:
            st.warning("el archivo no tiene ninguno de los nombres correspondientes para ser cargado")

        
    if procesos_df is not None and recursos_df is not None and acciones_df is not None and st.button("simular"):
        # st.subheader("Simulacion")
        if modo =="mutex locks":
            MutexLocks(procesos_df, recursos_df, acciones_df)
        if modo == "semaforos":
            semaforos(procesos_df, recursos_df, acciones_df)
