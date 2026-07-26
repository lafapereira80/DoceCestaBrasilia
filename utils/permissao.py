import streamlit as st

# =====================================================
# VERIFICA LOGIN (SINCRONIZAÇÃO PERFEITA COM O NAVEGADOR)
# =====================================================

def verificar_login():
    # 1. Se o usuário já está na memória (navegação normal), passa direto!
    if st.session_state.get("usuario"):
        return True
        
    # 2. Se a memória está vazia (F5 ou aba fechada), acionamos a biblioteca
    try:
        from streamlit_cookies_controller import CookieController
        controller = CookieController()
    except Exception:
        st.switch_page("pages/99_Admin.py")

    # 3. Pede o cookie para o navegador
    cookie = controller.get("doce_cesta_admin")

    # 4. Se o navegador já respondeu com o cookie, restaura a vida!
    if cookie:
        st.session_state["usuario"] = cookie
        st.session_state.pop("ciclo_leitura", None)
        st.rerun()

    # 5. O PULO DO GATO: Na 1ª vez, a resposta SEMPRE vem vazia porque o JavaScript demora 1 milissegundo a mais.
    # Usamos o st.stop() para PARAR o Python e deixar o navegador trabalhar. 
    # Quando o navegador achar o cookie, ele mesmo gera o rerun automático!
    if not st.session_state.get("ciclo_leitura"):
        st.session_state["ciclo_leitura"] = True
        st.markdown("<h4 style='text-align:center; color:#5a3b28; margin-top: 40px;'>🔄 Restaurando conexão segura...</h4>", unsafe_allow_html=True)
        st.stop() # Pausa o Python e entrega a bola pro navegador

    # 6. Se o código chegou aqui (depois da pausa) e não achou nada, você está deslogado de verdade.
    st.session_state.pop("ciclo_leitura", None)
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
