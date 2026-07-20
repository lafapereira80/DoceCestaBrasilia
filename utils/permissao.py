import streamlit as st



# =====================================================
# VERIFICA LOGIN
# =====================================================

def verificar_login():

    if (
        "usuario" not in st.session_state
        or st.session_state.usuario is None
    ):

        st.error(
            "Acesso não autorizado."
        )

        st.stop()



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


    perfil = usuario.get(
        "perfil"
    )


    if perfil not in perfis_permitidos:

        st.error(
            "Você não possui permissão para acessar este módulo."
        )

        st.stop()



# =====================================================
# SOMENTE ADMINISTRADOR
# =====================================================

def administrador():

    exigir_perfil(
        [
            "Administrador"
        ]
    )



# =====================================================
# ADMINISTRADOR OU OPERADOR
# =====================================================

def administrador_operador():

    exigir_perfil(
        [
            "Administrador",
            "Operador"
        ]
    )
