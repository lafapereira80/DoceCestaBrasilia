import streamlit as st

from services.produto_service import (
    listar_categorias,
    listar_produtos,
    cadastrar_produto,
    excluir_produto,
    alterar_status
)

st.set_page_config(
    page_title="Produtos",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Cadastro de Produtos")

st.divider()

# =====================================================
# CARREGA CATEGORIAS
# =====================================================

try:

    categorias = listar_categorias()

except Exception as erro:

    st.error(f"Erro ao carregar categorias: {erro}")

    st.stop()

if not categorias:

    st.warning("Nenhuma categoria cadastrada.")

    st.stop()

# =====================================================
# NOVO PRODUTO
# =====================================================

st.subheader("➕ Novo Produto")

with st.form("novo_produto"):

    categoria = st.selectbox(
        "Categoria",
        categorias,
        format_func=lambda c: c["nome"]
    )

    nome = st.text_input(
        "Nome do Produto"
    )

    preco = st.number_input(
        "Preço",
        min_value=0.0,
        step=1.0,
        value=0.0
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
                nome.strip(),
                preco
            )

            st.success(
                "Produto cadastrado com sucesso!"
            )

            st.rerun()

        except Exception as erro:

            st.error(erro)

st.divider()

# =====================================================
# LISTA
# =====================================================

st.subheader("📋 Produtos")

try:

    produtos = listar_produtos()

except Exception as erro:

    st.error(erro)

    st.stop()

categorias_dict = {}

for categoria in categorias:

    categorias_dict[categoria["id"]] = categoria["nome"]

produtos_por_categoria = {}

for categoria in categorias:

    produtos_por_categoria[categoria["nome"]] = []

for produto in produtos:

    nome_categoria = categorias_dict.get(
        produto["categoria_id"],
        "Sem Categoria"
    )

    if nome_categoria not in produtos_por_categoria:

        produtos_por_categoria[nome_categoria] = []

    produtos_por_categoria[nome_categoria].append(produto)

