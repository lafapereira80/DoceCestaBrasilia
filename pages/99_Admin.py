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
# CSS ULTRA COMPACTO E ISOLADO (COM CSS GRID)
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   REMOÇÃO DE ELEMENTOS PADRÃO (TELA LOGIN)
========================================== */
section[data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, header, footer {
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
    display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 8px;
}
.admin-logo-img { width: 100px; height: auto; object-fit: contain; }
.titulo { text-align: center; font-size: 24px; font-weight: 700; color: #5a3b28; margin-top: 4px; }
.subtitulo { text-align: center; font-size: 14px; color: #775a46; margin-bottom: 12px; }

/* =========================================
   CONTAINERS E CARDS COMPACTOS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 12px !important;
    padding: 16px 20px !important; margin-bottom: 8px !important; box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04);
}
.card-title { font-size: 15px !important; font-weight: 700 !important; color: #5a3b28 !important; margin-bottom: 10px !important; text-align: center; }

div[data-baseweb="input"] { border-radius: 8px !important; }
input { font-size: 13px !important; }

.stButton button {
    background: #5a3b28 !important; color: white !important; border-radius: 8px !important;
    height: 38px !important; font-size: 13px !important; font-weight: 700 !important; border: none !important; transition: all 0.2s ease !important;
}
.stButton button:hover { background: #42291d !important; color: white !important; }

/* =========================================
   ESTILO DOS LINKS DE MÓDULOS (PAGE LINKS)
========================================== */
div[data-testid="stPageLink"] a {
    border-radius: 10px !important; background-color: #faf7f3 !important; border: 1px solid #dfcdbb !important;
    color: #5a3b28 !important; font-weight: 700 !important; font-size: 13px !important; padding: 10px !important;
    text-align: center !important; justify-content: center !important; display: flex !important;
    box-sizing: border-box !important; height: 100%; transition: all 0.2s ease !important;
}
div[data-testid="stPageLink"] a:hover { background-color: #f3ece6 !important; border-color: #5a3b28 !important; }

/* =========================================
   O NOVO MOTOR CSS GRID INFALÍVEL (MENU)
========================================== */
/* 1. Oculta o marcador secreto que usamos no Python */
div[data-testid="stVerticalBlock"]:has(> div.element-container .menu-grid-start) > div.element-container:has(.menu-grid-start) {
    display: none !important;
}

/* 2. Força o container do Menu a virar uma Tabela Flexível (Grid) com 3 colunas (PC) */
div[data-testid="stVerticalBlock"]:has(> div.element-container .menu-grid-start) {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 8px !important;
}

/* =========================================
   ESTILO BOTÕES BLOQUEADOS (SEM ACESSO)
========================================== */
.btn-disabled {
    border-radius: 10px; background-color: #fcfcfc; border: 1px dashed #dcdcdc;
    color: #a0a0a0; font-weight: 700; font-size: 13px; padding: 10px; text-align: center;
    display: flex; justify-content: center; align-items: center; box-sizing: border-box; height: 100%; min-height: 42px; cursor: not-allowed;
}

/* =========================================
   RODAPÉ
========================================== */
.rodape { text-align: center; font-size: 12px; color: #888; margin-top: 15px; }

/* =========================================
   MEDIA QUERY: CELULAR (FORÇA 2 POR LINHA)
========================================== */
@media (max-width: 768px) {
    .admin-logo-img { width: 65px !important; }
    .titulo { font-size: 20px !important; }
    .subtitulo { font-size: 12px !important; }

    /* Força exatamente 2 colunas no celular (Grid Mágico) */
    div[data-testid="stVerticalBlock"]:has(> div.element-container .menu-grid-start) {
        grid-template-columns: repeat(2, 1fr) !important;
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

with st.container(border=True):
    col_u1, col_u2 = st.columns([3.5, 1])
    with col_u1:
        st.markdown(f"👤 **{usuario['login']}** | Perfil: **{usuario['perfil']}**")
    with col_u2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario = None
            st.rerun()


# =====================================================
# MENU DE MÓDULOS (NOVO SISTEMA CSS GRID)
# =====================================================

st.subheader("📂 Módulos do Sistema")
st.caption("Selecione o módulo que deseja acessar.")

# Agrupando todos os links em um único container vertical (Sem st.columns!)
with st.container():
    # Marcador secreto para o CSS Grid capturar este bloco e formatá-lo
    st.markdown('<div class="menu-grid-start"></div>', unsafe_allow_html=True)
    
    st.page_link("pages/02_Pedidos.py", label="📋 Pedidos")
    st.page_link("pages/03_Clientes.py", label="👥 Clientes")
    st.page_link("pages/04_Cestas.py", label="🎁 Cestas")
    st.page_link("pages/05_Produtos.py", label="🛒 Produtos")
    
    if usuario["perfil"] in ["Administrador", "Operador"]:
        st.page_link("pages/15_Categorias.py", label="📂 Categorias")
    else:
        st.markdown('<div class="btn-disabled">🚫 Categorias</div>', unsafe_allow_html=True)
        
    if usuario["perfil"] == "Administrador":
        st.page_link("pages/06_Financeiro.py", label="💰 Financeiro")
        st.page_link("pages/07_Usuarios.py", label="👤 Usuários")
    else:
        st.markdown('<div class="btn-disabled">🚫 Financeiro</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-disabled">🚫 Usuários</div>', unsafe_allow_html=True)


# =====================================================
# AVISO DE PERFIL E RODAPÉ
# =====================================================

if usuario["perfil"] != "Administrador":
    st.warning("⚠️ Perfil Operador: acesso limitado aos módulos operacionais.")

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
