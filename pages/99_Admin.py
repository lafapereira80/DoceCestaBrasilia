import streamlit as st
from pathlib import Path

from services.usuario_service import autenticar_usuario

from utils.menu import configurar_pagina, menu_lateral



st.set_page_config(
    page_title="Administrador",
    page_icon="🔒",
    layout="wide"
)



# =====================================================
# CONFIGURAÇÃO VISUAL
# =====================================================

configurar_pagina()



# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>

.titulo{

text-align:center;

font-size:32px;

font-weight:bold;

color:#8B5A2B;

}


.subtitulo{

text-align:center;

color:#777;

}

</style>
""",
unsafe_allow_html=True
)



# =====================================================
# LOGO
# =====================================================

logo = Path(
    "assets/logo.webp"
)


if logo.exists():

    col1,col2,col3 = st.columns([2,1,2])


    with col2:

        st.image(
            str(logo),
            width=140
        )



st.markdown(

"<div class='titulo'>Painel Administrativo</div>",

unsafe_allow_html=True

)


st.markdown(

"<div class='subtitulo'>Doce Cesta Brasília</div>",

unsafe_allow_html=True

)



st.divider()



# =====================================================
# CONTROLE LOGIN
# =====================================================

if "usuario" not in st.session_state:

    st.session_state.usuario = None



# =====================================================
# LOGIN
# =====================================================

if st.session_state.usuario is None:


    st.subheader(
        "🔐 Login"
    )


    login = st.text_input(
        "Usuário"
    )


    senha = st.text_input(
        "Senha",
        type="password"
    )



    if st.button(

        "Entrar",

        use_container_width=True

    ):


        usuario = autenticar_usuario(

            login,

            senha

        )


        if usuario:


            st.session_state.usuario = usuario

            st.rerun()


        else:

            st.error(
                "Usuário ou senha inválidos."
            )


    st.stop()



# =====================================================
# USUÁRIO LOGADO
# =====================================================

usuario = st.session_state.usuario



# =====================================================
# MENU NOVO
# =====================================================

menu_lateral()



# =====================================================
# PAINEL CENTRAL
# =====================================================


st.subheader(
    "📂 Módulos do Sistema"
)



col1,col2,col3 = st.columns(3)



with col1:

    st.page_link(

        "pages/02_Pedidos.py",

        label="📋 Pedidos",

        use_container_width=True

    )



with col2:

    st.page_link(

        "pages/03_Clientes.py",

        label="👥 Clientes",

        use_container_width=True

    )



with col3:

    if usuario["perfil"] == "Administrador":

        st.page_link(

            "pages/06_Financeiro.py",

            label="💰 Financeiro",

            use_container_width=True

        )



col1,col2,col3 = st.columns(3)



if usuario["perfil"] == "Administrador":


    with col1:

        st.page_link(

            "pages/04_Cestas.py",

            label="🎁 Cestas",

            use_container_width=True

        )



    with col2:

        st.page_link(

            "pages/05_Produtos.py",

            label="🛒 Produtos",

            use_container_width=True

        )



    with col3:

        st.page_link(

            "pages/07_Usuarios.py",

            label="👤 Usuários",

            use_container_width=True

        )



st.divider()



st.caption(
    "Doce Cesta Brasília - Sistema Administrativo"
)
