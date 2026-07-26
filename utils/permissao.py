import streamlit as st
import time

# =====================================================
# VERIFICA LOGIN (BLINDADO CONTRA ERROS DA API)
# =====================================================

def verificar_login():
    # 1. Se o usuário já está na memória temporária, segue a vida
    if st.session_state.get("usuario"):
        return True
        
    # 2. Sincronização segura do navegador (Pausa)
    if not st.session_state.get("aguardou_cookie"):
        st.session_state["aguardou_cookie"] = True
        time.sleep(0.4)
        st.rerun()
        
    # 3. Escudo anti-crash para ler o cookie
    cookie_usuario = None
    try:
        from streamlit_cookies_controller import CookieController
        # A key única evita que o Streamlit confunda os componentes e dê erro
        controller = CookieController(key="auth_guard")
        cookie_usuario = controller.get("doce_cesta_admin")
    except Exception:
        # Se a biblioteca der QUALQUER erro (como o StreamlitAPIException), ele ignora silenciosamente
        pass
    
    if cookie_usuario:
        # Recuperou o login com sucesso! Restaura a memória
        st.session_state["usuario"] = cookie_usuario
        st.session_state.pop("aguardou_cookie", None)
        return True
    
    # 4. Sem cookie válido, remove a trava e expulsa para o login
    st.session_state.pop("aguardou_cookie", None) 
    st.switch_page("pages/99_Admin.py")


# =====================================================
# USUÁRIO ATUAL
# =====================================================

def usuario_atual():
    verificar_login()
    return st.session_state.get("usuario")


# =====================================================
# EXIGIR PERFIL
# =====================================================

def exigir_perfil(perfis_permitidos):
    usuario = usuario_atual()
    
    if not usuario:
        st.stop()
        
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
