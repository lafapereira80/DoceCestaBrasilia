import streamlit as st

from services.cesta_service import (
    listar_cestas
)

from services.produto_service import (
    listar_produtos,
    listar_categorias
)

from services.cesta_produto_service import (
    listar_produtos_da_cesta
)

from services.configuracao_cesta_service import (
    salvar_configuracao_cesta
)

from utils.menu import (
    configurar_pagina,
    menu_lateral
)

from utils.permissao import (
    administrador_operador
)


# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Configurar Cesta",
    page_icon="⚙️",
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
    max-width: 1100px;
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
}

/* Customização dos checkboxes */
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
# TÍTULO E CABEÇALHO
# =====================================================

st.title("⚙️ Configurar Cesta")
st.caption("Configure os produtos e limites de escolha para cada cesta.")
st.divider()


# =====================================================
# CARREGAMENTO DOS DADOS
# =====================================================

try:
    cestas = listar_cestas()
    produtos = listar_produtos()
    categorias = listar_categorias()
except Exception as erro:
    st.error(f"Erro ao carregar dados: {erro}")
    st.stop()

if not cestas:
    st.warning("Nenhuma cesta cadastrada.")
    st.stop()

if not categorias:
    st.warning("Nenhuma categoria cadastrada.")
    st.stop()


# =====================================================
# MAPA DE CATEGORIAS
# =====================================================

categorias_dict = {
    categoria["id"]: categoria
    for categoria in categorias
}


# =====================================================
# REMOVE CATEGORIA ADICIONAIS
# =====================================================

produtos_configuraveis = []

for produto in produtos:
    categoria = categorias_dict.get(produto["categoria_id"])
    if not categoria:
        continue

    if categoria["nome"].strip().lower() == "adicionais":
        continue

    produtos_configuraveis.append(produto)

if not produtos_configuraveis:
    st.warning("Nenhum produto disponível para configuração.")
    st.stop()


# =====================================================
# SELEÇÃO DA CESTA
# =====================================================

cesta = st.selectbox(
    "🎁 Selecione a cesta para configurar",
    cestas,
    format_func=lambda x: x["nome"]
)

if not cesta:
    st.stop()

cesta_id = cesta["id"]

st.divider()


# =====================================================
# PRODUTOS JÁ CONFIGURADOS NA CESTA
# =====================================================

try:
    produtos_configurados = listar_produtos_da_cesta(cesta_id)
except Exception:
    produtos_configurados = []

produtos_marcados = [
    item["produto_id"]
    for item in produtos_configurados
]


# =====================================================
# AGRUPAR PRODUTOS POR CATEGORIA
# =====================================================

produtos_por_categoria = {}

for produto in produtos_configuraveis:
    categoria = categorias_dict.get(produto["categoria_id"])
    if not categoria:
        continue

    categoria_id = categoria["id"]
    categoria_nome = categoria["nome"]

    if categoria_id not in produtos_por_categoria:
        produtos_por_categoria[categoria_id] = {
            "nome": categoria_nome,
            "produtos": []
        }

    produtos_por_categoria[categoria_id]["produtos"].append(produto)

if not produtos_por_categoria:
    st.warning("Nenhuma categoria possui produtos disponíveis.")
    st.stop()


# =====================================================
# CONFIGURAÇÃO DAS CATEGORIAS
# =====================================================

st.subheader("📦 Produtos disponíveis")
st.info("Selecione os produtos e defina os limites mínimos e máximos de escolha para esta cesta.")

configuracoes = []
ordem = 1


# =====================================================
# EXIBIÇÃO DINÂMICA DAS CATEGORIAS
# =====================================================

for categoria_id, dados_categoria in produtos_por_categoria.items():
    categoria_nome = dados_categoria["nome"]
    lista_produtos = dados_categoria["produtos"]

    with st.container(border=True):
        st.markdown(f'<div class="categoria-title">📦 {categoria_nome}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            minimo = st.number_input(
                "Mínimo de escolhas",
                min_value=0,
                max_value=50,
                value=1,
                key=f"min_{cesta_id}_{categoria_id}"
            )

        with col2:
            maximo = st.number_input(
                "Máximo de escolhas",
                min_value=1,
                max_value=50,
                value=1,
                key=f"max_{cesta_id}_{categoria_id}"
            )

        st.divider()

        selecionados = []
        col_p1, col_p2 = st.columns(2)

        for indice, produto in enumerate(lista_produtos):
            coluna = col_p1 if indice % 2 == 0 else col_p2

            with coluna:
                marcado = produto["id"] in produtos_marcados
                selecionado = st.checkbox(
                    produto["nome"],
                    value=marcado,
                    key=f"produto_{cesta_id}_{produto['id']}"
                )

                if selecionado:
                    selecionados.append(produto["id"])

        if selecionados:
            if maximo > len(selecionados):
                maximo = len(selecionados)

            if minimo > maximo:
                minimo = maximo

            configuracoes.append({
                "categoria_id": categoria_id,
                "categoria": categoria_nome,
                "produtos": selecionados,
                "min_escolhas": minimo,
                "max_escolhas": maximo,
                "ordem": ordem
            })

            ordem += 1


# =====================================================
# RESUMO DA CONFIGURAÇÃO (SIDES BY SIDE COMPACTO)
# =====================================================

st.divider()
st.subheader("📋 Resumo da configuração")

if configuracoes:
    col_res = st.columns(min(len(configuracoes), 3))
    for idx, item in enumerate(configuracoes):
        with col_res[idx % len(col_res)]:
            with st.container(border=True):
                st.markdown(f"**📦 {item['categoria']}**")
                st.caption(f"Produtos: **{len(item['produtos'])}**")
                st.caption(f"Escolhas: **{item['min_escolhas']} até {item['max_escolhas']} itens**")
else:
    st.info("Nenhum produto selecionado nas categorias acima.")


# =====================================================
# BOTÕES DE AÇÃO
# =====================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    salvar = st.button("💾 Salvar Configuração", use_container_width=True, type="primary")

with col2:
    voltar = st.button("⬅ Voltar", use_container_width=True)


# =====================================================
# VOLTAR
# =====================================================

if voltar:
    st.session_state.pop("cesta_configurar", None)
    st.switch_page("pages/04_Cestas.py")


# =====================================================
# SALVAR CONFIGURAÇÃO
# =====================================================

if salvar:
    if not configuracoes:
        st.error("Selecione pelo menos um produto.")
        st.stop()

    try:
        salvar_configuracao_cesta(
            cesta_id,
            configuracoes
        )

        st.success("Configuração da cesta salva com sucesso!")
        st.session_state.pop("cesta_configurar", None)
        st.switch_page("pages/04_Cestas.py")

    except Exception as erro:
        st.error(f"Erro ao salvar configuração: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("Doce Cesta Brasília - Configuração de Cestas")
