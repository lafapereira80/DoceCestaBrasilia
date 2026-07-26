import streamlit as st
import time
from streamlit_cookies_controller import CookieController

# =====================================================
# VERIFICA LOGIN (COM SINCRONIZAÇÃO SEGURA)
# =====================================================

def verificar_login():
    # 1. Se o usuário já está na memória temporária, segue a vida normal
    if st.session_state.get("usuario"):
        return True
        
    # 2. Sincronização do navegador (Pausa segura)
    if not st.session_state.get("aguardou_cookie"):
        st.session_state["aguardou_cookie"] = True
        time.sleep(0.5)
        st.rerun()
        
    # 3. Lê o cookie
    controller = CookieController()
    cookie_usuario = controller.get("doce_cesta_admin")
    
    if cookie_usuario:
        # Recuperou o login com sucesso! Restaura a memória
        st.session_state["usuario"] = cookie_usuario
        st.session_state.pop("aguardou_cookie", None) # Jeito 100% seguro de limpar a memória
        return True
    
    # 4. Sem cookie válido, remove a trava e expulsa para o login
    st.session_state.pop("aguardou_cookie", None) 
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
