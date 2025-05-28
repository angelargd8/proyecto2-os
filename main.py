import streamlit as st

import plotly.express as px


if "page" not in st.session_state:
    st.session_state.page = "menu"

if st.session_state.page == "menu":
    st.title("Simulador de planificacion de procesos ")
    st.markdown("-----", unsafe_allow_html=True)

    st.subheader("Tipos de simulacion:")

    st.markdown("<br>", unsafe_allow_html=True)



    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Simulacion de algoritmos de calendarizacion:**", unsafe_allow_html=True)
        st.text_area("", """La calendarización de procesos es una función clave del sistema operativo que decide el orden en el que los procesos acceden al CPU. Su objetivo es maximizar el rendimiento del sistema, minimizar los tiempos de espera y asegurar un uso eficiente del procesador.
Ya que en un sistema multitarea existen múltiples procesos compitiendo por el uso del CPU, el planificador (scheduler) debe aplicar un algoritmo de planificación para decidir cuál proceso ejecutar, cuándo y por cuánto tiempo.
Los algoritmos que se simula son:                     
First In First Out: Ejecuta los procesos en orden de llegada, sin interrupciones. 
Shortest Job First: Ejecuta primero el proceso con menor tiempo de ejecución (no-preemptivo). 
Shortest Remaining Time: Interrumpe si llega un proceso con menor tiempo restante (versión preemptiva).
Round Robin : Cada proceso recibe un quantum de CPU. Se alternan de forma circular. 
Priority Scheduling: Ejecuta primero el proceso con mayor prioridad (menor número).                 
""", height=650)
    with col2:
        st.markdown("**Simulacion de mecanismos de sincronizacion:**", unsafe_allow_html=True)
        st.text_area("", """La sincronización de procesos es un mecanismo fundamental en los sistemas operativos que permite coordinar la ejecución concurrente de múltiples procesos o hilos que comparten recursos. Su objetivo es evitar condiciones de carrera, accesos simultáneos no controlados y asegurar la consistencia de los datos compartidos.
Este simulador visual tiene dos técnicas de sincronización:
Mutex Locks: Permiten que un solo proceso acceda a un recurso a la vez. Si otro proceso intenta usar el recurso, debe esperar hasta que se libere.
Semáforos: Generalizan los mutex permitiendo un número limitado de accesos concurrentes. Se utilizan contadores para controlar el acceso múltiple a los recursos.
Cada proceso tiene un tiempo de llegada (AT), una cantidad máxima de operaciones (BT) y ejecuta acciones definidas (READ/WRITE). La simulación muestra el estado de cada proceso en cada ciclo (ACCESSED o WAITING) con colores diferenciados, ofreciendo una representación dinámica de cómo se sincronizan los procesos al acceder a los recursos.
        """, height=650)




