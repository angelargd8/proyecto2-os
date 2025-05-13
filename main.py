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
        st.text_area("", "explicacion xd", height=150)
    with col2:
        st.markdown("**Simulacion de mecanismos de sincronizacion:**", unsafe_allow_html=True)
        st.text_area("", "explicacion2 xd", height=150)


