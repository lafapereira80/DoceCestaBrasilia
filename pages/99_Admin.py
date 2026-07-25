import streamlit as st

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
    page_title="Painel Administrativo",
    page_icon="⚙️",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()


# =====================================================
# IDENTIFICA O USUÁRIO E O PERFIL (À PROVA DE FALHAS)
# =====================================================

usuario = st.session_state.get("usuario", {})

if isinstance(usuario, dict):
    perfil_usuario_bruto = usuario.get("perfil", "Operador")
    nome_usuario = usuario.get("nome", "Usuário")
else:
    perfil_usuario_bruto = getattr(usuario, "perfil", "Operador")
    nome_usuario = getattr(usuario, "nome", "Usuário")

# Padroniza o texto do perfil para evitar erros de maiúscula/minúscula
perfil_usuario = str(perfil_usuario_bruto).strip().title()


# =====================================================
# CSS RESPONSIVO (MOBILE FIRST)
# =====================================================

st.markdown(
"""
<style>
.block-container {
    max-width: 1000px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

header { visibility: hidden !important; height: 0px !important; }
#MainMenu { visibility: hidden !important; }

.admin-header { margin-bottom: 1.5rem; }
.admin-title { font-size: 28px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 0px !important; }
.admin-subtitle { font-size: 15px !important; color: #775a46; margin-top: 4px !important; }
.secao-titulo { font-size: 18px !important; font-weight: 700 !important; color: #c5721f !important; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; border-bottom: 2px solid #f0e6dc; padding-bottom: 4px; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 12px !important; padding: 14px 16px !important;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04); transition: all 0.2s ease; height: 100%;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #c5721f !important; box-shadow: 0 4px 10px rgba(197, 114, 31, 0.15); transform: translateY(-2px);
}
.link-desc { font-size: 12.5px; color: #775a46; margin-top: 4px; line-height: 1.4; }

@media (max-width: 768px) {
    .block-container { padding-top: 1rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
    .admin-title { font-size: 24px !important; }
    .secao-titulo { font-size: 16px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 12px !important; margin-bottom: 8px !important; }
}
</style>
""",
unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="admin-header">
        <h1 class="admin-title">⚙️ Painel Central</h1>
        <p class="admin-subtitle">Olá, <b>{nome_usuario}</b>! O que vamos gerenciar hoje?</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# SEÇÃO 1: OPERACIONAL E VENDAS
# =====================================================
st.markdown('<div class="secao-titulo">📦 Operacional e Vendas</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="🛍️")
        st.markdown('<div class="link-desc">Controle de novos pedidos, andamento, entregas e WhatsApp.</div>', unsafe_allow_html=True)
with col2:
    with st.container(border=True):
        st.page_link("pages/03_Clientes.py", label="Base de Clientes", icon="👥")
        st.markdown('<div class="link-desc">Histórico de compras, dados de contato e relacionamento.</div>', unsafe_allow_html=True)

# =====================================================
# SEÇÃO 2: CATÁLOGO E ESTOQUE
# =====================================================
st.markdown('<div class="secao-titulo">🍓 Catálogo e Estoque</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    with st.container(border=True):
        st.page_link("pages/07_Cestas.py", label="Cestas (Vitrine)", icon="🎁")
        st.markdown('<div class="link-desc">Crie cestas, ajuste preços, imagens e organize o site.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.page_link("pages/04_Categorias.py", label="Categorias", icon="📁")
        st.markdown('<div class="link-desc">Organize os produtos (Ex: Bebidas, Pães, Frios).</div>', unsafe_allow_html=True)
with col4:
    with st.container(border=True):
        st.page_link("pages/05_Produtos.py", label="Produtos Base", icon="🧀")
        st.markdown('<div class="link-desc">Itens que compõem as cestas e produtos avulsos.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.page_link("pages/08_Configurar_Cesta.py", label="Montagem das Cestas", icon="🧩")
        st.markdown('<div class="link-desc">Defina as regras de escolha (Ex: Escolha 1 bebida).</div>', unsafe_allow_html=True)

# =====================================================
# SEÇÃO 3: GESTÃO E CONFIGURAÇÕES (SÓ ADMINISTRADOR)
# =====================================================
if perfil_usuario == "Administrador":
    st.markdown('<div class="secao-titulo">🔒 Gestão e Configurações (Acesso Restrito)</div>', unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    with col5:
        with st.container(border=True):
            st.page_link("pages/06_Financeiro.py", label="Relatório Financeiro", icon="📈")
            st.markdown('<div class="link-desc">Faturamento mensal, ticket médio e fluxo de caixa.</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link("pages/16_Vitrine_Config.py", label="Editor do Site (CMS)", icon="🖥️")
            st.markdown('<div class="link-desc">Altere textos, títulos, links e a ordem do site público.</div>', unsafe_allow_html=True)
    with col6:
        with st.container(border=True):
            st.page_link("pages/10_Usuarios.py", label="Controle de Usuários", icon="🛡️")
            st.markdown('<div class="link-desc">Adicione ou remova acesso de operadores ao sistema.</div>', unsafe_allow_html=True)


# =====================================================
# RODAPÉ
# =====================================================
st.write("")
st.divider()
st.markdown(
    """
    <div style="text-align:center; font-size:12px; color:#888;">
    Doce Cesta Brasília - Sistema de Gestão Interna © 2026<br>
    <i>Logado como: <b>{}</b></i>
    </div>
    """.format(perfil_usuario_bruto),
    unsafe_allow_html=True
)
