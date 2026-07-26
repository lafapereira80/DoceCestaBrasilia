import streamlit as st

# =====================================================
# VERIFICA LOGIN (Sincronização Assíncrona Inteligente)
# =====================================================

def verificar_login():
    # 1. Se o usuário já está na memória temporária, segue a vida normal
    if st.session_state.get("usuario"):
        return True
        
    # 2. Chama a biblioteca de cookies
    cookie_usuario = None
    try:
        from streamlit_cookies_controller import CookieController
        controller = CookieController(key="auth_guard")
        cookie_usuario = controller.get("doce_cesta_admin")
    except Exception:
        pass
        
    # 3. Se o navegador já enviou o cookie, restaura a sessão e continua
    if cookie_usuario:
        st.session_state["usuario"] = cookie_usuario
        st.session_state.pop("esperando_cookie", None)
        return True
        
    # 4. O SEGREDO: Na 1ª leitura, o navegador ainda está processando.
    # Nós usamos o st.stop() para PARAR o Python e deixar o navegador trabalhar.
    # Assim que o navegador achar o cookie, ele força o sistema a continuar sozinho.
    if not st.session_state.get("esperando_cookie"):
        st.session_state["esperando_cookie"] = True
        st.markdown("<h4 style='text-align:center; color:#5a3b28; margin-top: 40px;'>🔄 Sincronizando conexão segura...</h4>", unsafe_allow_html=True)
        st.stop() # Trava a tela para impedir o redirecionamento apressado
        
    # 5. Se o sistema chegou aqui, o navegador respondeu que o cookie NÃO EXISTE.
    # O usuário está realmente deslogado.
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
