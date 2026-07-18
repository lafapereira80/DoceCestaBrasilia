import streamlit as st

from config.supabase import supabase

from services.produto_service import (
    listar_produtos,
    cadastrar_produto
)

st.set_page_config(
    page_title="Produtos",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Cadastro de Produtos")

st.divider()

# =====================================================
# CARREGA AS CATEGORIAS
# =====================================================

try:

    resposta = (
        supabase
        .table("categorias")
        .select("*")
        .order("nome")
        .execute()
    )

    categorias = resposta.data

except Exception as erro:

    st.error(erro)

    st.stop()

if not categorias:

    st.warning(
        "Nenhuma categoria cadastrada."
    )

    st.stop()
