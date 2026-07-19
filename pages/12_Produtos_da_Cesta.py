import streamlit as st

from services.produto_service import (
    listar_produtos,
    listar_categorias
)

from services.cesta_produto_service import (
    listar_produtos_da_cesta,
    salvar_produtos_da_cesta
)

st.set_page_config(
    page_title="Produtos da Cesta",
    page_icon="📦",
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

st.title("📦 Produtos da Cesta")

st.divider()

# =====================================================
# CARREGA DADOS
# =====================================================

categorias = listar_categorias()

produtos = listar_produtos()

produtos_da_cesta = listar_produtos_da_cesta(cesta_id)
