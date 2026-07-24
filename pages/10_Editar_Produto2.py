import streamlit as st

from services.produto_service import (
    listar_categorias,
    buscar_produto,
    atualizar_produto
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
    page_title="Editar Produto",
    page_icon="✏️",
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
    max-width: 1000px;
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

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINER CARD DO FORMULÁRIO
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
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
# VALIDA PRODUTO
# =====================================================

if "produto_editar" not in st.session_state:
    st.error("Nenhum produto selecionado.")
    if st.button("⬅ Voltar"):
        st.switch_page("pages/05_Produtos.py")
    st.stop()

produto_id = st.session_state["produto_editar"]


# =====================================================
# BUSCAR DADOS
# =====================================================

try:
    produto = buscar_produto(produto_id)
    categorias = listar_categorias()
except Exception as erro:
    st.error(f"Erro ao carregar produto: {erro}")
    st.stop()

if not produto:
    st.error("Produto não encontrado.")
    st.stop()


# =====================================================
# TÍTULO
# =====================================================

st.title("✏️ Editar Produto")
st.caption("Atualize as informações do produto.")
st.divider()


# =====================================================
# IDENTIFICA CATEGORIA ATUAL
# =====================================================

indice_categoria = 0

for i, categoria_item in enumerate(categorias):
    if categoria_item["id"] == produto["categoria_id"]:
        indice_categoria = i
        break


# =====================================================
# FORMULÁRIO DE EDIÇÃO (CARD COMPACTO SIDE-BY-SIDE)
# =====================================================

with st.container(border=True):
    col1, col2 = st.columns([1.3, 1])

    with col1:
        categoria = st.selectbox(
            "Categoria",
            categorias,
            index=indice_categoria,
            format_func=lambda c: c["nome"]
        )

        nome = st.text_input(
            "Nome do Produto",
            value=produto.get("nome", "")
        )

        descricao = st.text_area(
            "Descrição",
            value=produto.get("descricao", "") or "",
            height=90
        )

    with col2:
        # Regra de preço
        categoria_nome = categoria["nome"].strip().lower()

        if categoria_nome == "adicionais":
            tipo_atual = produto.get("tipo_preco", "Preço definido")

            tipo_preco = st.radio(
                "Tipo de preço",
                ["Preço definido", "Preço sob consulta"],
                index=(1 if tipo_atual == "Preço sob consulta" else 0),
                horizontal=True
            )

            if tipo_preco == "Preço sob consulta":
                preco = None
                st.info("Produto sem valor definido. O preço será informado no pedido.")
            else:
                preco = st.number_input(
                    "Preço (R$)",
                    min_value=0.0,
                    value=float(produto.get("preco", 0) or 0),
                    step=0.50,
                    format="%.2f"
                )
        else:
            tipo_preco = "Incluso na cesta"
            preco = None
            st.info("Produto incluso na composição da cesta. Não possui preço individual.")

        ativo = st.checkbox(
            "Produto ativo",
            value=produto.get("ativo", True)
        )

    st.write("")

    # Botões de Ação
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        salvar = st.button("💾 Salvar Alterações", use_container_width=True, type="primary")

    with col_b2:
        cancelar = st.button("❌ Cancelar", use_container_width=True)


# =====================================================
# CANCELAR
# =====================================================

if cancelar:
    st.session_state.pop("produto_editar", None)
    st.switch_page("pages/05_Produtos.py")


# =====================================================
# SALVAR ALTERAÇÕES
# =====================================================

if salvar:
    if not nome.strip():
        st.error("Informe o nome do produto.")
        st.stop()

    # Validação de Preço
    if (
        categoria_nome == "adicionais"
        and tipo_preco == "Preço definido"
        and preco <= 0
    ):
        st.error("Informe o valor do adicional.")
        st.stop()

    try:
        atualizar_produto(
            produto_id,
            categoria["id"],
            nome.strip(),
            descricao.strip(),
            preco,
            ativo,
            tipo_preco
        )

        st.success("Produto atualizado com sucesso!")
        st.session_state.pop("produto_editar", None)
        st.switch_page("pages/05_Produtos.py")

    except Exception as erro:
        st.error(f"Erro ao atualizar produto: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("✏️ Edição de produtos - Doce Cesta Brasília")
