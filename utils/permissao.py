import streamlit as st
import time

# =====================================================
# VERIFICA LOGIN (BLINDADO CONTRA RESET DE NAVEGAÇÃO)
# =====================================================

def verificar_login():
    # 1. SE JÁ ESTIVER LOGADO: SUCESSO IMEDIATO!
    # Passa direto sem acionar a biblioteca de cookies para não bugar a troca de páginas.
    if st.session_state.get("usuario"):
        return True
        
    # 2. Se a memória está vazia (F5 no navegador), tentamos ler o cookie
    cookie_usuario = None
    try:
        from streamlit_cookies_controller import CookieController
        controller = CookieController(key="auth_guard")
        cookie_usuario = controller.get("doce_cesta_admin")
    except Exception:
        pass
        
    # 3. Se achou o cookie, restaura a sessão e sucesso!
    if cookie_usuario:
        st.session_state["usuario"] = cookie_usuario
        st.session_state.pop("esperando_cookie", None)
        return True
        
    # 4. Dá 1 segundo para o navegador carregar o cookie na primeira vez
    if not st.session_state.get("esperando_cookie"):
        st.session_state["esperando_cookie"] = True
        time.sleep(1.0)
        st.rerun()
        
    # 5. Se já esperou e não tem cookie, expulsa pro login
    st.session_state.pop("esperando_cookie", None)
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
