import streamlit as st
from config.supabase import supabase

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
    page_title="Clientes",
    page_icon="👥",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()


# =====================================================
# CSS COMPACTO E ESTILIZADO
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

p, div, span, label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINERS DOS CLIENTES (CARDS LINHA)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 6px 12px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.08);
}

/* =========================================
   ELEMENTOS DE TEXTO & BADGES
========================================== */
.cliente-nome {
    font-weight: 700;
    color: #333;
    font-size: 14px !important;
}

.badge-pedidos {
    display: inline-block;
    background-color: #f3ece6;
    color: #5a3b28;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px !important;
    border: 1px solid #dfcdbb;
}

.cabecalho-tabela {
    font-weight: 700;
    color: #775a46;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

/* Ajustes de botões */
.stButton button {
    font-size: 13px !important;
    padding: 2px 8px !important;
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

st.title("👥 Clientes")
st.caption("Clientes que já concluíram pelo menos um pedido.")
st.divider()


# =====================================================
# BUSCA PEDIDOS ENTREGUES
# =====================================================

try:
    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("status", "Entregue")
        .order("cliente_nome")
        .execute()
    )
    pedidos = resposta.data or []

except Exception as erro:
    st.error(f"Erro ao carregar clientes: {erro}")
    st.stop()


# =====================================================
# SEM CLIENTES
# =====================================================

if not pedidos:
    st.info("Nenhum cliente encontrado com pedidos entregues.")
    st.stop()


# =====================================================
# AGRUPA POR CPF
# =====================================================

clientes_dict = {}

for pedido in pedidos:
    cpf = pedido.get("cliente_cpf") or "Sem CPF"

    if cpf not in clientes_dict:
        clientes_dict[cpf] = {
            "nome": pedido.get("cliente_nome", "-"),
            "cpf": cpf,
            "telefone": pedido.get("cliente_telefone", "-"),
            "quantidade": 0
        }

    clientes_dict[cpf]["quantidade"] += 1

lista_clientes = list(clientes_dict.values())


# =====================================================
# BUSCA / PESQUISA
# =====================================================

pesquisa = st.text_input("🔍 Pesquisar", placeholder="Digite o nome, CPF ou telefone do cliente...")

if pesquisa.strip():
    termo = pesquisa.lower().strip()
    lista_clientes = [
        c for c in lista_clientes
        if termo in c["nome"].lower() or termo in c["cpf"].lower() or termo in c["telefone"].lower()
    ]


# =====================================================
# LISTAGEM
# =====================================================

st.subheader(f"📋 Lista de Clientes ({len(lista_clientes)})")

if not lista_clientes:
    st.warning("Nenhum cliente atende aos critérios da pesquisa.")
else:
    # Cabeçalho da Tabela
    col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([3.5, 2.2, 2.3, 1.2, 0.8])
    with col_h1:
        st.markdown('<div class="cabecalho-tabela">Nome</div>', unsafe_allow_html=True)
    with col_h2:
        st.markdown('<div class="cabecalho-tabela">CPF</div>', unsafe_allow_html=True)
    with col_h3:
        st.markdown('<div class="cabecalho-tabela">Telefone</div>', unsafe_allow_html=True)
    with col_h4:
        st.markdown('<div class="cabecalho-tabela">Pedidos</div>', unsafe_allow_html=True)
    with col_h5:
        st.markdown('<div class="cabecalho-tabela">Ação</div>', unsafe_allow_html=True)

    # Linhas da Tabela (Cards Compactos)
    for cliente in lista_clientes:
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([3.5, 2.2, 2.3, 1.2, 0.8])

            with col1:
                nome_formatado = " ".join(str(cliente["nome"]).split())
                st.markdown(f'<div class="cliente-nome">{nome_formatado}</div>', unsafe_allow_html=True)

            with col2:
                st.write(cliente["cpf"])

            with col3:
                st.write(f"📱 {cliente['telefone']}")

            with col4:
                qtd = cliente["quantidade"]
                st.markdown(f'<span class="badge-pedidos">📦 {qtd}</span>', unsafe_allow_html=True)

            with col5:
                if st.button("📖", key=f"hist_{cliente['cpf']}", help="Ver histórico do cliente", use_container_width=True):
                    st.session_state["cliente_cpf"] = cliente["cpf"]
                    st.switch_page("pages/13_Historico_Cliente.py")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption(f"Total de clientes cadastrados: {len(clientes_dict)}")
