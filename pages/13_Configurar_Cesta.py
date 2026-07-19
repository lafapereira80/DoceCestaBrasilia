import streamlit as st

from services.configuracao_cesta_service import (
    buscar_configuracoes_da_cesta,
    salvar_configuracoes
)

st.set_page_config(
    page_title="Configuração da Cesta",
    page_icon="⚙️",
    layout="wide"
)

# =====================================================
# VERIFICA SE EXISTE CESTA SELECIONADA
# =====================================================

if "cesta_produtos" not in st.session_state:

    st.error("Nenhuma cesta selecionada.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/04_Cestas.py")

    st.stop()

cesta_id = st.session_state["cesta_produtos"]

st.title("⚙️ Configuração da Cesta")

st.divider()

# =====================================================
# CARREGA CONFIGURAÇÕES
# =====================================================

configuracoes = buscar_configuracoes_da_cesta(cesta_id)

config = {}

for item in configuracoes:

    config[item["categoria"]] = item["quantidade"]
