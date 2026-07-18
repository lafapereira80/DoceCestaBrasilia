import streamlit as st

from config.supabase import supabase

from services.produto_service import (
    listar_produtos,
    cadastrar_produto,
    excluir_produto
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

    st.warning("Nenhuma categoria cadastrada.")
    st.stop()

# =====================================================
# FORMULÁRIO
# =====================================================

st.subheader("➕ Novo Produto")

with st.form("form_produto"):

    categoria = st.selectbox(
        "Categoria",
        categorias,
        format_func=lambda x: x["nome"]
    )

    nome = st.text_input(
        "Nome do Produto"
    )

    preco = st.number_input(
        "Preço (R$)",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

    salvar = st.form_submit_button(
        "💾 Cadastrar Produto",
        use_container_width=True
    )

if salvar:

    if nome.strip() == "":

        st.error("Informe o nome do produto.")

    else:

        try:

            cadastrar_produto(
                categoria["id"],
                nome,
                preco
            )

            st.success(
                "Produto cadastrado com sucesso!"
            )

            st.rerun()

        except Exception as erro:

            st.error(erro)

st.divider()
