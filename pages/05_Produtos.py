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

    st.warning(
        "Nenhuma categoria cadastrada."
    )

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

# =====================================================
# LISTA DE PRODUTOS
# =====================================================

st.subheader("📋 Produtos Cadastrados")

try:

    produtos = listar_produtos()

except Exception as erro:

    st.error(erro)

    st.stop()

if not produtos:

    st.info("Nenhum produto cadastrado.")

else:

    # Agrupa os produtos por categoria
    categorias_dict = {
        categoria["id"]: categoria["nome"]
        for categoria in categorias
    }

    produtos_por_categoria = {}

    for produto in produtos:

        nome_categoria = categorias_dict.get(
            produto["categoria_id"],
            "Sem Categoria"
        )

        if nome_categoria not in produtos_por_categoria:

            produtos_por_categoria[nome_categoria] = []

        produtos_por_categoria[nome_categoria].append(produto)

    # Exibe os produtos agrupados
    for nome_categoria in sorted(produtos_por_categoria.keys()):

        st.markdown(f"### {nome_categoria}")

        for produto in produtos_por_categoria[nome_categoria]:

    col1, col2, col3, col4, col5 = st.columns([5, 2, 2, 1, 1])

    with col1:

        st.write(f"**{produto['nome']}**")

    with col2:

        st.write(
            f"R$ {float(produto['preco']):.2f}"
        )

    with col3:

        if produto["ativo"]:

            st.success("Ativo")

        else:

            st.error("Inativo")

    with col4:

        if st.button(
            "✏️",
            key=f"editar_{produto['id']}"
        ):

            st.session_state["produto_editar"] = produto["id"]

            st.switch_page(
                "pages/10_Editar_Produto.py"
            )

    with col5:

        if st.button(
            "🗑️",
            key=f"excluir_{produto['id']}"
        ):

            excluir_produto(produto["id"])

            st.success("Produto excluído!")

            st.rerun()

st.divider()
