import streamlit as st

from services.produto_service import (
    listar_produtos,
    listar_categorias
)

from services.cesta_produto_service import (
    listar_produtos_da_cesta,
    salvar_produtos_da_cesta
)

from utils.menu import (
    configurar_pagina,
    menu_lateral
)

from utils.permissao import (
    administrador_operador
)


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Produtos da Cesta",
    page_icon="📦",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()


# =====================================================
# CSS ULTRA COMPACTO E ISOLADO
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1050px;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}

h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-top: 4px !important;
    margin-bottom: 6px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINERS DAS CATEGORIAS (CARDS COMPACTOS)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.categoria-title {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-bottom: 8px !important;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Ajustes direcionados para os checkboxes */
div[data-testid="stCheckbox"] {
    margin-bottom: 2px !important;
    background: #faf7f3;
    padding: 4px 10px;
    border-radius: 8px;
    border: 1px solid #f0e6dd;
    transition: all 0.2s ease;
}

div[data-testid="stCheckbox"]:hover {
    border-color: #dfcdbb;
    background: #f5eee6;
}

/* Botões da Página */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 13px !important;
    border-radius: 8px !important;
    min-height: 36px !important;
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# VERIFICA CESTA SELECIONADA
# =====================================================

if "cesta_produtos" not in st.session_state:
    st.error("Nenhuma cesta selecionada.")
    if st.button("⬅ Voltar"):
        st.switch_page("pages/04_Cestas.py")
    st.stop()

cesta_id = st.session_state["cesta_produtos"]


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

st.title("📦 Produtos da Cesta")
st.caption("Selecione os produtos que fazem parte da composição desta cesta.")
st.divider()


# =====================================================
# CARREGA DADOS
# =====================================================

try:
    categorias = listar_categorias()
    produtos = listar_produtos()
    produtos_da_cesta = listar_produtos_da_cesta(cesta_id)
except Exception as erro:
    st.error(f"Erro ao carregar dados: {erro}")
    st.stop()


# =====================================================
# ORGANIZA CATEGORIAS DINAMICAMENTE
# =====================================================

categorias_dict = {
    categoria["id"]: categoria["nome"]
    for categoria in categorias
}

produtos_por_categoria = {}

for categoria in categorias:
    produtos_por_categoria[categoria["nome"]] = []

for produto in produtos:
    # Ignora produtos inativos
    if "ativo" in produto and not produto["ativo"]:
        continue

    nome_categoria = categorias_dict.get(
        produto.get("categoria_id"),
        "Sem Categoria"
    )

    produtos_por_categoria.setdefault(
        nome_categoria,
        []
    ).append(produto)


# Remove categorias sem produtos
produtos_por_categoria = {
    categoria: lista
    for categoria, lista in produtos_por_categoria.items()
    if lista
}


# Ordenação dinâmica
categorias_ordenadas = sorted(
    produtos_por_categoria.keys(),
    key=lambda x: x.lower()
)


# =====================================================
# PRODUTOS VINCULADOS À CESTA
# =====================================================

produtos_marcados = [
    item["produto_id"]
    for item in produtos_da_cesta
]


# =====================================================
# SELEÇÃO DINÂMICA DOS PRODUTOS (CARDS COMPACTOS)
# =====================================================

selecionados = []

for categoria in categorias_ordenadas:
    produtos_lista = produtos_por_categoria[categoria]

    with st.container(border=True):
        st.markdown(
            f'<div class="categoria-title">📂 {categoria}</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        for index, produto in enumerate(produtos_lista):
            marcado = produto["id"] in produtos_marcados

            with col1 if index % 2 == 0 else col2:
                escolhido = st.checkbox(
                    produto["nome"],
                    value=marcado,
                    key=f"produto_{produto['id']}"
                )

                if escolhido:
                    selecionados.append(produto["id"])


# =====================================================
# BOTÕES DE AÇÃO
# =====================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 Salvar Produtos", use_container_width=True, type="primary"):
        try:
            salvar_produtos_da_cesta(
                cesta_id,
                selecionados
            )
            st.success("Produtos da cesta atualizados com sucesso!")
            st.rerun()
        except Exception as erro:
            st.error(f"Erro ao salvar: {erro}")

with col2:
    if st.button("⬅ Voltar ao Catálogo", use_container_width=True):
        st.session_state.pop("cesta_produtos", None)
        st.switch_page("pages/04_Cestas.py")
