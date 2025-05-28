# Proyecto 2 sistemas operativos


Este proyecto es un simulador visual e interactivo de los principales algoritmos de planificación (scheduling) y de sincronizacion usados en sistemas operativos. A través de una interfaz desarrollada con Streamlit y gráficos de Plotly, permite observar y comparar el comportamiento de distintos algoritmos al calendarizar múltiples procesos y para ver el funcionamiento de lock mutex y semaforos. 

# Cómo ejecutar?
en la terminal correr:
```http
  streamlit run main.py
```
# Formatos de archivos:
- todos los archivos tienen que ser de tipo .txt
en el de calendarizacion, solo se sube el archivo de procesos.txt
Mientras que en el de sincronizacion se deben de subir 3 archivos con los siguientes nombres:
```http
  acciones.txt
  procesos.txt
  recursos.txt
```
Contenido de cada archivo:

procesos.txt
```http
<PID>, <BT>, <AT>, <Priority>

ejemplo:
P1, 8, 0, 1 
```

recursos.txt
```http
<NOMBRE RECURSO>, <CONTADOR> 

ejemplo:
R1, 1
```

acciones.txt
```http
<PID>, <ACCION>, <RECURSO>, <CICLO>

ejemplo:
P1, READ, R1, 0
```

## Requisitos: 
- Python 3.8+
- librerias de: streamlit, plotly, pandas

## Algoritmos de planificación soportados

| Algoritmo                   | Descripción                                                                 |
|-----------------------------|------------------------------------------------------------------------------|
| **FIFO** (First In First Out)        | Ejecuta los procesos en orden de llegada, sin interrupciones.                  |
| **SJF** (Shortest Job First)         | Ejecuta primero el proceso con menor tiempo de ejecución (no-preemptivo).      |
| **SRT** (Shortest Remaining Time)    | Interrumpe si llega un proceso con menor tiempo restante (versión preemptiva).|
| **RR** (Round Robin)                | Cada proceso recibe un quantum de CPU. Se alternan de forma circular.          |
| **PRIO** (Priority Scheduling)       | Ejecuta primero el proceso con **mayor prioridad** (menor número).             |

# Sincronizacion

Por otra parte, tambien tiene un simulador de sincronización de procesos es un mecanismo fundamental en los sistemas operativos que permite coordinar la ejecución concurrente de múltiples procesos o hilos que comparten recursos. Su objetivo es evitar condiciones de carrera, accesos simultáneos no controlados y asegurar la consistencia de los datos compartidos. 
Este simulador visual tiene dos técnicas de sincronización:
Mutex Locks: Permiten que un solo proceso acceda a un recurso a la vez. Si otro proceso intenta usar el recurso, debe esperar hasta que se libere.
Semáforos: Generalizan los mutex permitiendo un número limitado de accesos concurrentes. Se utilizan contadores para controlar el acceso múltiple a los recursos.
Cada proceso tiene un tiempo de llegada (AT), una cantidad máxima de operaciones (BT) y ejecuta acciones definidas (READ/WRITE). La simulación muestra el estado de cada proceso en cada ciclo (ACCESSED o WAITING) con colores diferenciados, ofreciendo una representación dinámica de cómo se sincronizan los procesos al acceder a los recursos.

