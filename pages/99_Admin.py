import streamlit as st
import base64
import time
from pathlib import Path
from streamlit_cookies_controller import CookieController

from services.usuario_service import autenticar_usuario
from utils.menu import configurar_pagina

# Inicializa o controlador de cookies
controller = CookieController()

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
# CSS ULTRA COMPACTO E ISOLADO
# =====================================================

st.markdown(
"""
<style>
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
#MainMenu { display: none !important; }
header { display: none !important; }
footer { display: none !important; }
.block-container { max-width: 650px !important; padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
div[data-testid="stVerticalBlock"] { gap: 0.8rem !important; }
.admin-logo-banner { display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 8px; }
.admin-logo-img { width: 100px; height: auto; object-fit: contain; }
.titulo { text-align: center; font-size: 24px; font-weight: 700; color: #5a3b28; margin-top: 4px; }
.subtitulo { text-align: center; font-size: 14px; color: #775a46; margin-bottom: 12px; }
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 12px !important; padding: 16px 20px !important; margin-bottom: 8px !important; box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04); }
.card-title { font-size: 15px !important; font-weight: 700 !important; color: #5a3b28 !important; margin-bottom: 10px !important; text-align: center; }
div[data-baseweb="input"] { border-radius: 8px !important; }
input { font-size: 13px !important; }
.stButton button { background: #5a3b28 !important; color: white !important; border-radius: 8px !important; height: 38px !important; font-size: 13px !important; font-weight: 700 !important; border: none !important; transition: all 0.2s ease !important; }
.stButton button:hover { background: #42291d !important; color: white !important; }
div[data-testid="stPageLink"] { margin-bottom: 6px !important; }
div[data-testid="stPageLink"] a { border-radius: 10px !important; background-color: #faf7f3 !important; border: 1px solid #dfcdbb !important; color: #5a3b28 !important; font-weight: 700 !important; font-size: 13px !important; padding: 10px !important; text-align: center !important; justify-content: center !important; transition: all 0.2s ease !important; display: flex !important; box-sizing: border-box !important; }
div[data-testid="stPageLink"] a:hover { background-color: #f3ece6 !important; border-color: #5a3b28 !important; }
.rodape { text-align: center; font-size: 12px; color: #888; margin-top: 15px; }
@media (max-width: 640px) { .admin-logo-img { width: 50px !important; } .titulo { font-size: 20px !important; } .subtitulo { font-size: 12px !important; } }
</style>
""",
unsafe_allow_html=True
)

logo_path = Path("assets/logo.webp")
logo_html = ""
if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    logo_html = f'<img src="data:image/webp;base64,{encoded_logo}" class="admin-logo-img" alt="Logo">'

st.markdown(f'<div class="admin-logo-banner">{logo_html}</div>', unsafe_allow_html=True)
st.markdown("<div class='titulo'>Painel Administrativo</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Doce Cesta Brasília</div>", unsafe_allow_html=True)


# =====================================================
# CONTROLE DE LOGIN E CAPTURA DO COOKIE NA RAIZ
# =====================================================

if not st.session_state.get("usuario"):
    if not st.session_state.get("aguardou_cookie_login"):
        st.session_state["aguardou_cookie_login"] = True
        time.sleep(0.5)
        st.rerun()
        
    cookie_user = None
    try:
        # Tenta ler o cookie de forma segura
        cookie_user = controller.get("doce_cesta_admin")
    except Exception:
        pass
        
    if cookie_user:
        st.session_state["usuario"] = cookie_user
        st.session_state.pop("aguardou_cookie_login", None)
    else:
        st.session_state["usuario"] = None


# =====================================================
# TELA DE LOGIN
# =====================================================

if not st.session_state.get("usuario"):
    with st.container(border=True):
        st.markdown("<div class='card-title'>🔐 Acesso Administrativo</div>", unsafe_allow_html=True)

        login = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

        st.write("")

        entrar = st.button("Entrar no Sistema", use_container_width=True)

        if entrar:
            usuario = autenticar_usuario(login, senha)

            if usuario:
                st.session_state["usuario"] = usuario
                
                try:
                    # Manda o navegador salvar o Cookie
                    controller.set("doce_cesta_admin", usuario, max_age=2592000)
                except Exception:
                    pass
                
                # O SEGREDO: Dá quase 1 segundo para garantir a gravação na web antes de recarregar
                time.sleep(0.8)
                
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
            st.session_state["usuario"] = None
            try:
                controller.remove("doce_cesta_admin")
            except Exception:
                pass
            time.sleep(0.5) # Dá tempo de apagar o cookie
            st.rerun()

st.subheader("📂 Módulos do Sistema")
st.caption("Selecione o módulo que deseja acessar.")

col1, col2, col3 = st.columns(3)
with col1: st.page_link("pages/02_Pedidos.py", label="📋 Pedidos", use_container_width=True)
with col2: st.page_link("pages/03_Clientes.py", label="👥 Clientes", use_container_width=True)
with col3: st.page_link("pages/04_Cestas.py", label="🎁 Cestas", use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1: st.page_link("pages/05_Produtos.py", label="🛒 Produtos", use_container_width=True)
with col2:
    if usuario["perfil"] in ["Administrador", "Operador"]: st.page_link("pages/15_Categorias.py", label="📂 Categorias", use_container_width=True)
    else: st.info("Sem acesso")
with col3:
    if usuario["perfil"] == "Administrador": st.page_link("pages/06_Financeiro.py", label="💰 Financeiro", use_container_width=True)
    else: st.info("Sem acesso")

col1, col2, col3 = st.columns(3)
with col1:
    if usuario["perfil"] == "Administrador": st.page_link("pages/07_Usuarios.py", label="👤 Usuários", use_container_width=True)
    else: st.info("Sem acesso")

if usuario["perfil"] != "Administrador":
    st.warning("⚠️ Perfil Operador: acesso limitado aos módulos operacionais.")

st.divider()
st.markdown('<div class="rodape">Doce Cesta Brasília<br>Sistema Administrativo © 2026</div>', unsafe_allow_html=True)
