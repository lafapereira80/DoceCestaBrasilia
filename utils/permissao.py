import streamlit as st
from streamlit_cookies_controller import CookieController

# =====================================================
# VERIFICA LOGIN (COM PERSISTÊNCIA VIA COOKIE)
# =====================================================

def verificar_login():
    # 1. Verifica se a sessão atual já tem o usuário
    if "usuario" not in st.session_state or st.session_state.usuario is None:
        
        # 2. Se não tem (a sessão caiu), tenta buscar do cookie
        controller = CookieController()
        cookie_usuario = controller.get("doce_cesta_admin")
        
        if cookie_usuario:
            # Reconecta o usuário silenciosamente
            st.session_state.usuario = cookie_usuario
        else:
            # 3. Se não tem cookie, expulsa para a tela de login ao invés de quebrar a página
            st.switch_page("pages/99_Admin.py")


# =====================================================
# USUÁRIO ATUAL
# =====================================================

def usuario_atual():
    verificar_login()
    return st.session_state.usuario


# =====================================================
# EXIGIR PERFIL
# =====================================================

def exigir_perfil(perfis_permitidos):
    usuario = usuario_atual()
    perfil = usuario.get("perfil")

    if perfil not in perfis_permitidos:
        st.error("Você não possui permissão para acessar este módulo.")
        st.stop()


# =====================================================
# SOMENTE ADMINISTRADOR
# =====================================================

def administrador():
    exigir_perfil(["Administrador"])


# =====================================================
# ADMINISTRADOR OU OPERADOR
# =====================================================

def administrador_operador():
    exigir_perfil(["Administrador", "Operador"])
