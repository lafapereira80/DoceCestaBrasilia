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
# CSS PREMIUM E RESPONSIVIDADE
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}

h1 {
    font-size: 28px !important;
    font-weight: 800 !important;
    color: #4a2e1b;
    margin-bottom: 2px !important;
    letter-spacing: -0.5px;
}

h2, h3, h4 {
    color: #5a3b28 !important;
    font-weight: 800 !important;
}

.block-container p, 
.block-container label {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINERS DAS CATEGORIAS (CARDS PREMIUM)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #d2bfae !important;
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08);
}

.categoria-title {
    font-size: 16px !important;
    font-weight: 800 !important;
    color: #5a3b28 !important;
    margin-bottom: 15px !important;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #f3ece6;
    padding-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* =========================================
   CHECKBOXES MODERNOS (ESTILO PÍLULA)
========================================== */
div[data-testid="stCheckbox"] {
    margin-bottom: 4px !important;
    background: #faf7f3;
    padding: 6px 12px;
    border-radius: 10px;
    border: 1px solid #e8ddd3;
    transition: all 0.2s ease;
}

div[data-testid="stCheckbox"]:hover {
    border-color: #d2bfae;
    background: #fdfcfb;
    transform: translateX(2px);
}

/* =========================================
   ESTILIZAÇÃO DE BOTÕES DE AÇÃO
========================================== */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 14px !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    min-height: 42px !important;
    transition: all 0.2s ease;
}

div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button:hover {
    transform: scale(1.02);
}

/* =========================================
   RESPONSIVIDADE MOBILE (LADO A LADO)
========================================== */
@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 14px 16px !important; }
    
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
        margin-top: 15px !important;
        justify-content: space-between;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {
        flex: 1 1 0% !important; 
        min-width: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) button {
        width: 100% !important;
        padding: 8px 0px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# VERIFICA CESTA SELECIONADA
# =====================================================

if "cesta_produtos" not in st.session_state or not st.session_state["cesta_produtos"]:
    st.warning("⚠️ Nenhuma cesta selecionada para configuração.")
    if st.button("⬅ Voltar para Cestas"):
        st.switch_page("pages/04_Cestas.py")
    st.stop()

cesta_id = st.session_state["cesta_produtos"]


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("📦 Composição da Cesta")
    st.caption("Selecione todos os produtos que fazem parte do pacote oficial desta cesta.")


# =====================================================
# CARREGA DADOS (FILTRANDO A CATEGORIA ADICIONAIS)
# =====================================================

try:
    categorias_brutas = listar_categorias()
    
    # REQUISITO: Filtra e remove a categoria "Adicionais" (ela vai em todas as cestas e não precisa ser selecionada aqui)
    categorias = [
        cat for cat in categorias_brutas 
        if "adicional" not in str(cat.get("nome", "")).strip().lower()
    ]

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
        produto.get("categoria_id")
    )

    # Se o produto pertencer a uma categoria válida (que não seja adicionais)
    if nome_categoria in produtos_por_categoria:
        produtos_por_categoria[nome_categoria].append(produto)


# Remove categorias sem produtos
produtos_por_categoria = {
    categoria: lista
    for categoria, lista in produtos_por_categoria.items()
    if lista
}


# Ordenação dinâmica das categorias
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
# SELEÇÃO DINÂMICA DOS PRODUTOS (CARDS PREMIUM 3 COLUNAS)
# =====================================================

selecionados = []
st.write("")

if not categorias_ordenadas:
    st.info("Nenhuma categoria de produtos cadastrada (a categoria Adicionais foi ocultada desta tela).")
else:
    for categoria in categorias_ordenadas:
        produtos_lista = produtos_por_categoria[categoria]

        with st.container(border=True):
            st.markdown(
                f'<div class="categoria-title">📁 {categoria}</div>',
                unsafe_allow_html=True
            )

            # Usando 3 colunas para aproveitar melhor o espaço horizontal
            col1, col2, col3 = st.columns(3)

            for index, produto in enumerate(produtos_lista):
                marcado = produto["id"] in produtos_marcados

                # Distribuição balanceada dos produtos entre as 3 colunas
                if index % 3 == 0:
                    coluna_atual = col1
                elif index % 3 == 1:
                    coluna_atual = col2
                else:
                    coluna_atual = col3

                with coluna_atual:
                    escolhido = st.checkbox(
                        produto["nome"],
                        value=marcado,
                        key=f"produto_{produto['id']}"
                    )

                    if escolhido:
                        selecionados.append(produto["id"])


# =====================================================
# BOTÕES DE AÇÃO (RODAPÉ)
# =====================================================

st.write("")
st.divider()

col_b1, col_b2, col_b3 = st.columns([1.5, 1.5, 1])

with col_b1:
    if st.button("💾 Salvar Composição da Cesta", use_container_width=True, type="primary"):
        with st.spinner("Atualizando itens da cesta..."):
            try:
                salvar_produtos_da_cesta(
                    cesta_id,
                    selecionados
                )
                st.toast("✅ Produtos vinculados com sucesso!")
                st.rerun()
            except Exception as erro:
                st.error(f"Erro ao salvar configuração: {erro}")

with col_b2:
    if st.button("⬅ Voltar ao Catálogo de Cestas", use_container_width=True):
        st.session_state.pop("cesta_produtos", None)
        st.switch_page("pages/04_Cestas.py")
