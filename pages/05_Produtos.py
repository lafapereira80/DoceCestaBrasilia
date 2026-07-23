import streamlit as st

from services.produto_service import (
    listar_produtos,
    cadastrar_produto,
    excluir_produto,
    listar_categorias,
    alterar_status_produto
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
    page_title="Produtos",
    page_icon="🛒",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CSS COMPACTO E ISOLADO
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
    max-width: 1100px;
}

h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-top: 10px !important;
    margin-bottom: 8px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINERS DOS PRODUTOS (CARDS LINHA)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.08);
}

/* =========================================
   DIVISOR DE CATEGORIAS
========================================== */
.categoria-header {
    background-color: #5a3b28;
    color: #ffffff;
    padding: 6px 14px;
    border-radius: 10px;
    margin-top: 18px;
    margin-bottom: 10px;
    font-weight: 700;
    font-size: 14px !important;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
}

/* =========================================
   ELEMENTOS DE TEXTO & BADGES
========================================== */
.produto-nome {
    font-weight: 700;
    color: #333;
    font-size: 14px !important;
}

.produto-preco {
    font-weight: 700;
    color: #2e7d32;
    font-size: 14px !important;
}

.badge-incluso {
    display: inline-block;
    background-color: #e8f0fe;
    color: #1a73e8;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

.badge-consulta {
    display: inline-block;
    background-color: #fef7e0;
    color: #b06000;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

.badge-ativo {
    display: inline-block;
    background-color: #e6f4ea;
    color: #137333;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

.badge-inativo {
    display: inline-block;
    background-color: #fce8e6;
    color: #c5221f;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

/* Botões de Ação na Tabela */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 13px !important;
    padding: 2px 6px !important;
    border-radius: 8px !important;
    min-height: 32px !important;
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

st.title("🛒 Gestão de Produtos")
st.caption("Gerenciamento de produtos por categoria dinâmica.")
st.divider()


# =====================================================
# CARREGAR CATEGORIAS
# =====================================================

try:
    categorias = listar_categorias()
except Exception as erro:
    st.error(f"Erro ao carregar categorias: {erro}")
    categorias = []


# =====================================================
# CADASTRO DE PRODUTO
# =====================================================

if usuario.get("perfil") == "Administrador":
    st.subheader("➕ Novo Produto")

    with st.container(border=True):
        col_f1, col_f2 = st.columns([1.5, 1])

        with col_f1:
            nome = st.text_input("Nome do Produto", placeholder="Ex: Nutella 350g")
            descricao = st.text_area("Descrição", height=70, placeholder="Descrição opcional do produto...")

        with col_f2:
            if categorias:
                categoria = st.selectbox("Categoria", categorias, format_func=lambda x: x["nome"])
            else:
                categoria = None
                st.warning("Nenhuma categoria cadastrada.")

            # Regra Dinâmica de Preço
            if categoria:
                categoria_possui_preco = categoria.get("possui_preco", False)
            else:
                categoria_possui_preco = False

            if categoria_possui_preco:
                tipo_preco = st.radio("Tipo de preço", ["Preço definido", "Preço sob consulta"], horizontal=True)

                if tipo_preco == "Preço sob consulta":
                    preco = None
                    st.info("O valor será definido no fechamento do pedido.")
                else:
                    preco = st.number_input("Preço (R$)", min_value=0.0, value=0.0, step=0.50, format="%.2f")
            else:
                tipo_preco = "Incluso na cesta"
                preco = None
                st.info("Este produto será incluso automaticamente na composição da cesta.")

            ativo = st.checkbox("Produto ativo", value=True)

        salvar = st.button("💾 Cadastrar Produto", use_container_width=True, type="primary")

else:
    salvar = False
    st.info("Modo consulta. Apenas Administradores podem cadastrar produtos.")


# =====================================================
# SALVAR PRODUTO
# =====================================================

if salvar:
    if not nome.strip():
        st.error("Informe o nome do produto.")
        st.stop()

    if not categoria:
        st.error("Selecione uma categoria.")
        st.stop()

    if categoria.get("possui_preco") and tipo_preco == "Preço definido" and preco <= 0:
        st.error("Informe o valor do produto.")
        st.stop()

    try:
        cadastrar_produto(
            categoria_id=categoria["id"],
            nome=nome.strip(),
            descricao=descricao.strip(),
            preco=preco,
            ativo=ativo,
            tipo_preco=tipo_preco
        )
        st.success("Produto cadastrado com sucesso!")
        st.rerun()

    except Exception as erro:
        st.error(f"Erro ao cadastrar produto: {erro}")


# =====================================================
# FUNÇÃO EXIBIR PRODUTO
# =====================================================

def exibir_produto(produto, categoria):
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([5, 2, 1.2, 1.8])

        # Nome / Descrição
        with col1:
            st.markdown(f'<div class="produto-nome">{produto.get("nome","-")}</div>', unsafe_allow_html=True)
            if produto.get("descricao"):
                st.caption(produto["descricao"])

        # Preço / Regra
        with col2:
            possui_preco = categoria.get("possui_preco", False)

            if possui_preco:
                tipo = str(produto.get("tipo_preco", "Preço definido")).strip()
                if tipo.lower() == "preço sob consulta":
                    st.markdown('<span class="badge-consulta">Sob consulta</span>', unsafe_allow_html=True)
                else:
                    valor = produto.get("preco")
                    if valor is not None:
                        valor_formatado = f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                        st.markdown(f'<div class="produto-preco">{valor_formatado}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="badge-consulta">Sob consulta</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-incluso">Incluso na Cesta</span>', unsafe_allow_html=True)

        # Status Badge
        with col3:
            if produto.get("ativo", True):
                st.markdown('<span class="badge-ativo">🟢 Ativo</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-inativo">🔴 Inativo</span>', unsafe_allow_html=True)

        # Ações
        with col4:
            b1, b2, b3 = st.columns(3)

            with b1:
                editar = st.button("✏️", key=f"editar_{produto['id']}", help="Editar produto", use_container_width=True)

            with b2:
                status = st.button("🔴" if produto.get("ativo", True) else "🟢", key=f"status_{produto['id']}", help="Alterar status", use_container_width=True)

            with b3:
                excluir = st.button("🗑️", key=f"excluir_{produto['id']}", help="Excluir produto", use_container_width=True)

    return editar, status, excluir


# =====================================================
# LISTAGEM DOS PRODUTOS
# =====================================================

st.divider()
st.subheader("📋 Produtos Cadastrados")

try:
    produtos = listar_produtos()
except Exception as erro:
    st.error(f"Erro ao carregar produtos: {erro}")
    produtos = []

if not produtos:
    st.info("Nenum produto cadastrado.")
    st.stop()


# Organiza Categorias
categorias_dict = {categoria["id"]: categoria for categoria in categorias}
produtos_agrupados = {}

for produto in produtos:
    categoria_id = produto.get("categoria_id")
    categoria = categorias_dict.get(categoria_id)

    if categoria:
        nome_categoria = categoria.get("nome", "Sem Categoria")
    else:
        nome_categoria = "Sem Categoria"

    if nome_categoria not in produtos_agrupados:
        produtos_agrupados[nome_categoria] = {
            "categoria": categoria,
            "produtos": []
        }

    produtos_agrupados[nome_categoria]["produtos"].append(produto)


# Ordena Categorias
categorias_ordenadas = sorted(
    produtos_agrupados.items(),
    key=lambda x: x[1]["categoria"].get("ordem", 999) if x[1]["categoria"] else 999
)


# Exibição dos Grupos
for categoria_nome, dados in categorias_ordenadas:
    categoria = dados["categoria"] or {}

    st.markdown(
        f'<div class="categoria-header">📂 {categoria_nome}</div>',
        unsafe_allow_html=True
    )

    for produto in dados["produtos"]:
        editar, status, excluir = exibir_produto(produto, categoria)

        if editar:
            st.session_state["produto_editar"] = produto["id"]
            st.switch_page("pages/10_Editar_Produto.py")

        if status:
            novo_status = not produto.get("ativo", True)
            try:
                alterar_status_produto(produto["id"], novo_status)
                st.rerun()
            except Exception as erro:
                st.error(f"Erro ao alterar status: {erro}")

        if excluir:
            try:
                excluir_produto(produto["id"])
                st.success("Produto excluído com sucesso.")
                st.rerun()
            except Exception as erro:
                st.error(f"Erro ao excluir produto: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("🛒 Cadastro de produtos - Doce Cesta Brasília")
