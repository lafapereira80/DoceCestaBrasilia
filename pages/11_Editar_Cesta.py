import streamlit as st

from services.cesta_service import (
    buscar_cesta,
    atualizar_cesta
)

st.set_page_config(
    page_title="Editar Cesta",
    page_icon="✏️",
    layout="wide"
)

# =====================================================
# VERIFICA SE EXISTE CESTA SELECIONADA
# =====================================================

if "cesta_editar" not in st.session_state:

    st.error("Nenhuma cesta selecionada.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/04_Cestas.py")

    st.stop()

cesta_id = st.session_state["cesta_editar"]

# =====================================================
# CARREGA DADOS
# =====================================================

try:

    cesta = buscar_cesta(cesta_id)

except Exception as erro:

    st.error(erro)

    st.stop()

st.title("✏️ Editar Cesta")

st.divider()
