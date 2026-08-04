import streamlit as st
import time
import html

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
# CONFIGURAÇÃO DA PÁGINA
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
    max-width: 1150px;
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
   CARDS DE RESUMO
========================================== */
.resumo-card {
    background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%);
    border: 1px solid #dfcdbb;
    border-radius: 12px;
    padding: 12px 15px;
    text-align: center;
}
.resumo-cat { font-size: 13px; font-weight: 800; color: #5a3b28; text-transform: uppercase; margin-bottom: 4px; }
.resumo-info { font-size: 12px; color: #666; font-weight: 600; }

/* =========================================
   RESPONSIVIDADE — TABLET (≤ 1024px)
========================================== */
@media (max-width: 1024px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}

/* =========================================
   RESPONSIVIDADE MOBILE (LADO A LADO)
========================================== */
@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 14px 16px !important; }
    
    /* Força os botões da base a ficarem na horizontal no mobile */
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
# TÍTULO E CABEÇALHO
# =====================================================

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("⚙️ Configurações Avançadas")
    st.caption("Defina os produtos, os grupos e os limites de escolhas (mínimo e máximo) para o formulário da cesta.")


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
    st.warning("⚠️ Nenhuma cesta cadastrada. Cadastre uma cesta primeiro.")
    st.stop()

if not categorias:
    st.warning("⚠️ Nenhuma categoria cadastrada.")
    st.stop()


# =====================================================
# IDENTIFICAÇÃO DA CESTA (VIA SESSION STATE OU SELECT)
# =====================================================

cesta_alvo_id = st.session_state.get("cesta_configurar", None)

indice_cesta = 0
if cesta_alvo_id:
    for i, c in enumerate(cestas):
        if c["id"] == cesta_alvo_id:
            indice_cesta = i
            break

st.write("")
cesta = st.selectbox(
    "🎁 Selecione a Cesta que deseja configurar:",
    cestas,
    index=indice_cesta,
    format_func=lambda x: x["nome"]
)

if not cesta:
    st.stop()

cesta_id = cesta["id"]


# =====================================================
# MAPA DE CATEGORIAS E REMOÇÃO DE "ADICIONAIS"
# =====================================================

categorias_dict = {
    categoria["id"]: categoria
    for categoria in categorias
}

produtos_configuraveis = []

for produto in produtos:
    categoria = categorias_dict.get(produto["categoria_id"])
    if not categoria:
        continue

    # A categoria "Adicionais" tem um fluxo próprio e não entra nas regras da cesta
    if categoria["nome"].strip().lower() == "adicionais":
        continue

    # Ignora produtos inativos
    if "ativo" in produto and not produto["ativo"]:
        continue

    produtos_configuraveis.append(produto)

if not produtos_configuraveis:
    st.warning("Nenhum produto disponível para configuração.")
    st.stop()


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
# EXIBIÇÃO DINÂMICA DAS CATEGORIAS (CARDS)
# =====================================================

st.write("")
st.subheader("📦 Regras e Opções da Cesta")
st.info("💡 Marque os itens disponíveis e defina quantos produtos o cliente precisará escolher nesta categoria.")

configuracoes = []
ordem = 1

for categoria_id, dados_categoria in produtos_por_categoria.items():
    categoria_nome = dados_categoria["nome"]
    lista_produtos = dados_categoria["produtos"]

    with st.container(border=True):
        st.markdown(f'<div class="categoria-title">📁 {html.escape(str(categoria_nome))}</div>', unsafe_allow_html=True)

        col_min, col_max = st.columns(2)
        
        # O banco salva a configuração anterior? O código original não pré-carregava min/max. 
        # Mantive o comportamento padrão original, onde o usuário recria as regras (value=1).
        with col_min:
            minimo = st.number_input(
                "Mínimo de Escolhas",
                min_value=0,
                max_value=50,
                value=1,
                key=f"min_{cesta_id}_{categoria_id}",
                help="Quantidade mínima obrigatória de itens que devem ser escolhidos."
            )

        with col_max:
            maximo = st.number_input(
                "Máximo de Escolhas",
                min_value=1,
                max_value=50,
                value=1,
                key=f"max_{cesta_id}_{categoria_id}",
                help="Limite máximo de itens permitidos nesta categoria."
            )

        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px dashed #dfcdbb;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 13px; font-weight: 800; color: #775a46; margin-bottom: 10px; text-transform: uppercase;'>Itens Disponíveis:</div>", unsafe_allow_html=True)

        selecionados = []
        
        # Exibição em 3 colunas para aproveitar espaço no Desktop
        col_p1, col_p2, col_p3 = st.columns(3)

        for indice, produto in enumerate(lista_produtos):
            if indice % 3 == 0: coluna_atual = col_p1
            elif indice % 3 == 1: coluna_atual = col_p2
            else: coluna_atual = col_p3

            with coluna_atual:
                marcado = produto["id"] in produtos_marcados
                selecionado = st.checkbox(
                    produto["nome"],
                    value=marcado,
                    key=f"produto_{cesta_id}_{produto['id']}"
                )

                if selecionado:
                    selecionados.append(produto["id"])

        # Lógica original de proteção de limites
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
# RESUMO DA CONFIGURAÇÃO (CARDS COMPACTOS)
# =====================================================

st.write("")
st.subheader("📋 Resumo da Estrutura")

if configuracoes:
    col_res = st.columns(min(len(configuracoes), 3))
    for idx, item in enumerate(configuracoes):
        with col_res[idx % len(col_res)]:
            st.markdown(
                f"""
                <div class="resumo-card">
                    <div class="resumo-cat">📦 {html.escape(str(item['categoria']))}</div>
                    <div class="resumo-info">Produtos Selecionados: <strong>{len(item['produtos'])}</strong></div>
                    <div class="resumo-info">Regra: <strong>{item['min_escolhas']} a {item['max_escolhas']} itens</strong></div>
                </div>
                """, unsafe_allow_html=True
            )
else:
    st.info("Nenhuma categoria configurada para esta cesta no momento.")


# =====================================================
# BOTÕES DE AÇÃO (RODAPÉ)
# =====================================================

st.write("")
st.divider()

col_b1, col_b2, col_b3 = st.columns([1.5, 1.5, 1])

with col_b1:
    if st.button("💾 Salvar Configurações", use_container_width=True, type="primary"):
        if not configuracoes:
            st.error("Selecione pelo menos um produto para configurar a cesta.")
            st.stop()

        with st.spinner("Salvando estrutura da cesta..."):
            try:
                salvar_configuracao_cesta(
                    cesta_id,
                    configuracoes
                )
                st.toast("✅ Configuração salva com sucesso!")
                st.session_state.pop("cesta_configurar", None)
                time.sleep(1)
                st.switch_page("pages/04_Cestas.py")

            except Exception as erro:
                st.error(f"Erro ao salvar configuração: {erro}")

with col_b2:
    if st.button("⬅ Voltar ao Catálogo", use_container_width=True):
        st.session_state.pop("cesta_configurar", None)
        st.switch_page("pages/04_Cestas.py")
