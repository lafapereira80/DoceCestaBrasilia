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

# =====================================================
# ORGANIZA PRODUTOS POR CATEGORIA
# =====================================================

categorias_dict = {
    categoria["id"]: categoria["nome"]
    for categoria in categorias
}

produtos_por_categoria = {}

for categoria in categorias:

    produtos_por_categoria[categoria["nome"]] = []

for produto in produtos:

    nome_categoria = categorias_dict.get(
        produto["categoria_id"],
        "Sem Categoria"
    )

    produtos_por_categoria.setdefault(
        nome_categoria,
        []
    ).append(produto)

# Produtos já vinculados à cesta

produtos_marcados = []

for item in produtos_da_cesta:

    produtos_marcados.append(item["produto_id"])

# =====================================================
# CHECKBOXES
# =====================================================

selecionados = []

ordem = [
    "Pães",
    "Bebidas",
    "Espalháveis",
    "Adicionais"
]

for categoria in ordem:

    if categoria not in produtos_por_categoria:
        continue

    st.subheader(f"📦 {categoria}")

    for produto in produtos_por_categoria[categoria]:

        marcado = produto["id"] in produtos_marcados

        escolhido = st.checkbox(

            produto["nome"],

            value=marcado,

            key=f"produto_{produto['id']}"

        )

        if escolhido:

            selecionados.append(produto["id"])

    st.divider()
