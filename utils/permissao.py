import streamlit as st
import time
from streamlit_cookies_controller import CookieController

# =====================================================
# VERIFICA LOGIN (COM SINCRONIZAÇÃO DE TEMPO)
# =====================================================

def verificar_login():
    # 1. Se o usuário já está na memória temporária, segue a vida normal
    if "usuario" in st.session_state and st.session_state.usuario:
        return True
        
    # 2. Se a memória caiu, precisamos checar o cookie.
    # O SEGREDO: O JavaScript do navegador demora uma fração de segundo para enviar o cookie.
    if "aguardou_cookie" not in st.session_state:
        st.session_state.aguardou_cookie = True
        time.sleep(0.5) # Pausa de meio segundo para o navegador responder
        st.rerun()      # Reinicia o script rapidamente para capturar a resposta
        
    # 3. Agora sim, com a resposta do navegador pronta, tentamos ler
    controller = CookieController()
    cookie_usuario = controller.get("doce_cesta_admin")
    
    if cookie_usuario:
        # Recuperou o login com sucesso! Restaura a memória
        st.session_state.usuario = cookie_usuario
        # Limpa a trava de espera para a próxima vez que a sessão cair
        del st.session_state.aguardou_cookie 
        return True
    
    # 4. Se realmente não tem cookie (ou ele venceu), expulsa para o login
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
