import html
from datetime import datetime

import streamlit as st

from services.usuario_service import autenticar_usuario
from utils.menu import configurar_pagina, menu_lateral

st.set_page_config(page_title="Painel Administrativo", page_icon="⚙️", layout="wide")
configurar_pagina()
menu_lateral()

st.markdown("""
<style>
:root {
    --ink: #0F172A;
    --muted: #64748B;
    --border: #E2E8F0;
    --bg-soft: #F8FAFC;
    --accent: #0F172A;
}

.app-greeting { font-size: clamp(28px, 4vw, 36px); font-weight: 800; color: var(--ink); margin-top: 10px; margin-bottom: 5px; letter-spacing: -1px; }
.app-sub { font-size: 16px; color: var(--muted); margin-bottom: 30px; font-weight: 500; }

/* --- Título de cada seção (estava sendo usado mas nunca definido) --- */
.app-section-title {
    font-size: 15px; font-weight: 800; color: var(--ink);
    margin-bottom: 14px; letter-spacing: -.2px;
    display: flex; align-items: center; gap: 8px;
}

/* --- Login --- */
.login-header { text-align: center; margin-top: 10vh; margin-bottom: 30px; }
.login-logo { font-size: 60px; margin-bottom: 15px; }
.login-title { font-size: 32px; font-weight: 800; color: var(--ink); margin-bottom: 5px; letter-spacing: -1px; }
.login-subtitle { font-size: 15px; color: var(--muted); font-weight: 500; }
div[data-testid="stForm"] { background: #FFFFFF; border: 1px solid var(--border); border-radius: 24px; padding: 35px 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
div[data-testid="stFormSubmitButton"] button { border-radius: 14px !important; font-weight: 800 !important; height: 50px !important; background: var(--ink) !important; color: white !important; border: none !important; transition: all .2s ease !important; }
div[data-testid="stFormSubmitButton"] button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.2) !important; }

/* --- Cabeçalho com avatar --- */
.header-row { display: flex; align-items: center; gap: 16px; margin-top: 10px; margin-bottom: 6px; }
.avatar-circle {
    width: 52px; height: 52px; border-radius: 16px; background: var(--ink); color: #fff;
    display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px;
    flex-shrink: 0;
}

/* --- Cards de seção --- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important; border-color: var(--border) !important;
    transition: box-shadow .2s ease, transform .2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 22px rgba(15, 23, 42, .06);
}

/* --- Links de módulo --- */
a[data-testid="stPageLink"] {
    border-radius: 12px !important; padding: 10px 12px !important; margin-bottom: 2px !important;
    transition: all .15s ease !important; font-weight: 600 !important;
}
a[data-testid="stPageLink"]:hover {
    background: var(--bg-soft) !important; transform: translateX(3px);
}

.rodape { text-align: center; color: #94A3B8; font-size: 12px; margin-top: 24px; }
</style>
""", unsafe_allow_html=True)

if "usuario" not in st.session_state or not st.session_state["usuario"]:
    st.markdown("""
    <div class="login-header">
        <div class="login-logo">🔒</div>
        <div class="login-title">Acesso Restrito</div>
        <div class="login-subtitle">Área Exclusiva para Colaboradores</div>
    </div>
    """, unsafe_allow_html=True)

    col_esp1, col_login, col_esp2 = st.columns([1, 1.5, 1])
    with col_login:
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário", placeholder="Seu login de acesso")
            senha_input = st.text_input("Senha", type="password", placeholder="Sua senha secreta")
            st.write("")
            submit_login = st.form_submit_button("Acessar Painel", use_container_width=True)

            if submit_login:
                if usuario_input and senha_input:
                    with st.spinner("Autenticando..."):
                        try:
                            usuario_autenticado = autenticar_usuario(usuario_input.strip(), senha_input.strip())
                            if usuario_autenticado:
                                st.session_state["usuario"] = usuario_autenticado
                                st.rerun()
                            else:
                                st.error("❌ Usuário ou senha incorretos.")
                        except Exception as e:
                            st.error("⚠️ Erro de conexão com o banco de dados. Tente novamente.")
                else:
                    st.warning("⚠️ Preencha usuário e senha para continuar.")
    st.stop()

from utils.permissao import administrador_operador
administrador_operador()
usuario = st.session_state.get("usuario", {})

login_seguro = html.escape(str(usuario.get('login', 'Admin')))
inicial = login_seguro[0].upper() if login_seguro else "A"

hora_atual = datetime.now().hour
if hora_atual < 12:
    saudacao = "Bom dia"
elif hora_atual < 18:
    saudacao = "Boa tarde"
else:
    saudacao = "Boa noite"

# Cabeçalho com avatar
st.markdown(f"""
    <div class="header-row">
        <div class="avatar-circle">{inicial}</div>
        <div>
            <div class="app-greeting">{saudacao}, {login_seguro} 👋</div>
            <div class="app-sub" style="margin-bottom:0;">O que vamos gerenciar hoje? Selecione um módulo abaixo.</div>
        </div>
    </div>
""", unsafe_allow_html=True)
st.write("")

# --- 📦 OPERAÇÃO & VENDAS ---
with st.container(border=True):
    st.markdown('<div class="app-section-title">📦 Operação & Vendas</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="📋")
        st.page_link("pages/18_Corporativo.py", label="Vendas B2B", icon="🏢")
        st.page_link("pages/08_Entregas.py", label="Rotas de Entrega", icon="🛵")
    with c2:
        st.page_link("pages/19_Pedido_Manual.py", label="Venda Varejo (PDV)", icon="🛍️")
        st.page_link("pages/16_Previsao.py", label="Previsão de Produção", icon="📈")

# --- 📊 GESTÃO & FINANCEIRO ---
with st.container(border=True):
    st.markdown('<div class="app-section-title">📊 Gestão & Financeiro</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.page_link("pages/03_Clientes.py", label="Base de Clientes", icon="👥")
    with c4:
        st.page_link("pages/06_Financeiro.py", label="Painel Financeiro", icon="💰")

# --- 🍓 CATÁLOGO DA LOJA ---
with st.container(border=True):
    st.markdown('<div class="app-section-title">🍓 Catálogo da Loja</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        st.page_link("pages/04_Cestas.py", label="Cestas e Kits", icon="🧺")
        st.page_link("pages/15_Categorias.py", label="Categorias", icon="🏷️")
    with c6:
        st.page_link("pages/05_Produtos.py", label="Produtos e Insumos", icon="🍓")
        st.page_link("pages/17_Secoes_Vitrine.py", label="Seções da Vitrine", icon="🖥️")

# --- ⚙️ CONFIGURAÇÕES ---
with st.container(border=True):
    st.markdown('<div class="app-section-title">⚙️ Configurações</div>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)
    with c7:
        st.page_link("pages/07_Usuarios.py", label="Gerenciar Usuários", icon="🔑")
    with c8:
        st.page_link("app.py", label="Ver Vitrine da Loja", icon="🌐")

st.write("")
st.markdown('<div class="rodape">Doce Cesta Brasília © App Nativo Web</div>', unsafe_allow_html=True)
