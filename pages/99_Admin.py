import streamlit as st
import base64
from pathlib import Path

from services.usuario_service import (
    autenticar_usuario
)

from utils.menu import (
    configurar_pagina
)


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Área Administrativa",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

configurar_pagina()


# =====================================================
# CSS ULTRA COMPACTO E ISOLADO (COM LOGO RESPONSIVA)
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   REMOÇÃO DE ELEMENTOS PADRÃO (TELA LOGIN)
========================================== */
section[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

#MainMenu {
    display: none !important;
}

header {
    display: none !important;
}

footer {
    display: none !important;
}

/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    max-width: 650px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.8rem !important;
}

/* =========================================
   LOGO RESPONSIVA UNIFICADA
========================================== */
.admin-logo-banner {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-bottom: 8px;
}

.admin-logo-img {
    width: 100px;
    height: auto;
    object-fit: contain;
}

.titulo {
    text-align: center;
    font-size: 24px;
    font-weight: 700;
    color: #5a3b28;
    margin-top: 4px;
}

.subtitulo {
    text-align: center;
    font-size: 14px;
    color: #775a46;
    margin-bottom: 12px;
}

/* =========================================
   CONTAINERS E CARDS COMPACTOS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04);
}

.card-title {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-bottom: 10px !important;
    text-align: center;
}

/* Customização dos Inputs */
div[data-baseweb="input"] {
    border-radius: 8px !important;
}

input {
    font-size: 13px !important;
}

/* Botões do Sistema */
.stButton button {
    background: #5a3b28 !important;
    color: white !important;
    border-radius: 8px !important;
    height: 38px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    background: #42291d !important;
    color: white !important;
}

/* Links dos Módulos com Espaçamento Correto */
div[data-testid="stPageLink"] {
    margin-bottom: 6px !important;
}

div[data-testid="stPageLink"] a {
    border-radius: 10px !important;
    background-color: #faf7f3 !important;
    border: 1px solid #dfcdbb !important;
    color: #5a3b28 !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px !important;
    text-align: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    box-sizing: border-box !important;
}

div[data-testid="stPageLink"] a:hover {
    background-color: #f3ece6 !important;
    border-color: #5a3b28 !important;
}

.rodape {
    text-align: center;
    font-size: 12px;
    color: #888;
    margin-top: 15px;
}

/* =========================================
   MEDIA QUERY EXCLUSIVA PARA CELULAR
========================================== */
@media (max-width: 640px) {
    .admin-logo-img {
        width: 50px !important;
    }

    .titulo {
        font-size: 20px !important;
    }

    .subtitulo {
        font-size: 12px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# LOGO E CABEÇALHO UNIFICADO
# =====================================================

logo_path = Path("assets/logo.webp")
logo_html = ""

if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    logo_html = f'<img src="data:image/webp;base64,{encoded_logo}" class="admin-logo-img" alt="Logo">'

st.markdown(
    f"""
    <div class="admin-logo-banner">
        {logo_html}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='titulo'>Painel Administrativo</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Doce Cesta Brasília</div>", unsafe_allow_html=True)


# =====================================================
# CONTROLE DE LOGIN
# =====================================================

if "usuario" not in st.session_state:
    st.session_state.usuario = None


# =====================================================
# TELA DE LOGIN (LOGOUT / NÃO AUTENTICADO)
# =====================================================

if st.session_state.usuario is None:
    with st.container(border=True):
        st.markdown("<div class='card-title'>🔐 Acesso Administrativo</div>", unsafe_allow_html=True)

        login = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

        st.write("")

        entrar = st.button("Entrar no Sistema", use_container_width=True)

        if entrar:
            usuario = autenticar_usuario(login, senha)

            if usuario:
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    st.stop()


# =====================================================
# TELA PRINCIPAL (USUÁRIO AUTENTICADO)
# =====================================================

usuario = st.session_state.usuario

# Card de Boas-Vindas
with st.container(border=True):
    col_u1, col_u2 = st.columns([3.5, 1])

    with col_u1:
        st.markdown(f"👤 **{usuario['login']}** | Perfil: **{usuario['perfil']}**")

    with col_u2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario = None
            st.rerun()


# =====================================================
# MENU DE MÓDULOS (GRID SEPARADO)
# =====================================================

st.subheader("📂 Módulos do Sistema")
st.caption("Selecione o módulo que deseja acessar.")

# Linha 1
col1, col2, col3 = st.columns(3)

with col1:
    st.page_link(
        "pages/02_Pedidos.py",
        label="📋 Pedidos",
        use_container_width=True
    )

with col2:
    st.page_link(
        "pages/03_Clientes.py",
        label="👥 Clientes",
        use_container_width=True
    )

with col3:
    st.page_link(
        "pages/04_Cestas.py",
        label="🎁 Cestas",
        use_container_width=True
    )

# Linha 2
col1, col2, col3 = st.columns(3)

with col1:
    st.page_link(
        "pages/05_Produtos.py",
        label="🛒 Produtos",
        use_container_width=True
    )

with col2:
    if usuario["perfil"] in ["Administrador", "Operador"]:
        st.page_link(
            "pages/15_Categorias.py",
            label="📂 Categorias",
            use_container_width=True
        )
    else:
        st.info("Sem acesso")

with col3:
    if usuario["perfil"] == "Administrador":
        st.page_link(
            "pages/06_Financeiro.py",
            label="💰 Financeiro",
            use_container_width=True
        )
    else:
        st.info("Sem acesso")

# Linha 3
col1, col2, col3 = st.columns(3)

with col1:
    if usuario["perfil"] == "Administrador":
        st.page_link(
            "pages/07_Usuarios.py",
            label="👤 Usuários",
            use_container_width=True
        )
    else:
        st.info("Sem acesso")


# =====================================================
# AVISO DE PERFIL
# =====================================================

if usuario["perfil"] != "Administrador":
    st.warning("⚠️ Perfil Operador: acesso limitado aos módulos operacionais.")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()

st.markdown(
    """
    <div class="rodape">
    Doce Cesta Brasília<br>
    Sistema Administrativo © 2026
    </div>
    """,
    unsafe_allow_html=True
)
