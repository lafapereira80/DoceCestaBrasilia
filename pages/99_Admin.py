import streamlit as st
from pathlib import Path


from services.usuario_service import (
    autenticar_usuario
)


from utils.menu import (
    configurar_pagina,
    menu_lateral
)



# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(

    page_title="Área Administrativa",

    page_icon="🔒",

    layout="wide",

    initial_sidebar_state="collapsed"

)



# =====================================================
# CONFIGURAÇÃO GERAL
# =====================================================

configurar_pagina()



# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>

/* REMOVE SIDEBAR */
section[data-testid="stSidebar"]{
    display:none;
}


/* REMOVE BOTÃO SHOW/HIDE */
[data-testid="collapsedControl"]{
    display:none;
}


/* REMOVE MENU SUPERIOR */
#MainMenu{
    visibility:hidden;
}


header{
    visibility:hidden;
}


footer{
    visibility:hidden;
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


    col1,col2,col3 = st.columns(
        [2,1,2]
    )


    with col2:


        st.image(

            str(logo),

            width=130

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
# INFORMAÇÕES USUÁRIO
# =====================================================

col1,col2 = st.columns([4,1])


with col1:


    st.success(

        f"👤 {usuario['login']} | Perfil: {usuario['perfil']}"

    )



with col2:


    if st.button(

        "🚪 Sair",

        use_container_width=True

    ):


        st.session_state.usuario = None

        st.rerun()



st.divider()



# =====================================================
# MÓDULOS
# =====================================================

st.subheader(

    "📂 Módulos do Sistema"

)



# =====================================================
# PRIMEIRA LINHA
# =====================================================

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


    st.page_link(

        "pages/04_Cestas.py",

        label="🎁 Cestas",

        use_container_width=True

    )



# =====================================================
# SEGUNDA LINHA
# =====================================================

col1,col2,col3 = st.columns(3)



with col1:


    st.page_link(

        "pages/05_Produtos.py",

        label="🛒 Produtos",

        use_container_width=True

    )



with col2:


    if usuario["perfil"] == "Administrador":


        st.page_link(

            "pages/06_Financeiro.py",

            label="💰 Financeiro",

            use_container_width=True

        )



with col3:


    if usuario["perfil"] == "Administrador":


        st.page_link(

            "pages/07_Usuarios.py",

            label="👤 Usuários",

            use_container_width=True

        )



# =====================================================
# AVISO OPERADOR
# =====================================================

if usuario["perfil"] != "Administrador":


    st.info(

        "Perfil Operador: acesso aos módulos operacionais."

    )



st.divider()



st.caption(

    "Doce Cesta Brasília - Sistema Administrativo"

)
