import streamlit as st

import plotly.express as px


if "page" not in st.session_state:
    st.session_state.page = "menu"

if st.session_state.page == "menu":
    st.title("Simulador de planificacion de procesos ")
    st.markdown("-----", unsafe_allow_html=True)

    st.subheader("Tipos de simulación:")

    st.markdown("<br>", unsafe_allow_html=True)



    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Algoritmos de Calendarización")
        with st.expander("¿Qué es la calendarización de procesos?"):
            st.markdown("""
La calendarización de procesos es una función clave del sistema operativo que decide el orden en que los procesos acceden al CPU.  
Su objetivo es maximizar el rendimiento del sistema, minimizar los tiempos de espera y asegurar un uso eficiente del procesador.

#### Algoritmos simulados:
- **First In First Out (FIFO):** Ejecuta los procesos en orden de llegada, sin interrupciones.  
- **Shortest Job First (SJF):** Ejecuta primero el proceso con menor tiempo de ejecución (no-preemptivo).  
- **Shortest Remaining Time (SRT):** Interrumpe si llega un proceso con menor tiempo restante (versión preemptiva).  
- **Round Robin:** Cada proceso recibe un quantum de CPU. Se alternan de forma circular.  
- **Priority Scheduling:** Ejecuta primero el proceso con mayor prioridad (menor número).
            """)

    with col2:
        st.markdown("### Mecanismos de Sincronización")
        with st.expander("¿Qué es la sincronización de procesos?"):
            st.markdown("""
La sincronización de procesos coordina la ejecución concurrente de procesos que comparten recursos, evitando condiciones de carrera y garantizando la consistencia de los datos.

#### Técnicas simuladas:
- **Mutex Locks:** Solo un proceso accede al recurso; los demás esperan.  
- **Semáforos:** Permiten múltiples accesos controlados con un contador.

Cada proceso tiene:
- Tiempo de llegada (**AT**)  
- Tiempo de ejecución (**BT**)  
- Acciones (**READ/WRITE**)

La simulación muestra estados como:
- **ACCESSED**
- **WAITING**

Todo esto se representa visualmente por ciclo, en una línea de tiempo dinámica.
            """)




