import streamlit as st
from pathlib import Path


from services.usuario_service import (
    autenticar_usuario
)


from utils.menu import (
    configurar_pagina
)



# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(

    page_title="Área Administrativa",

    page_icon="🔒",

    layout="centered",

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

/* ================================
   REMOVE ELEMENTOS STREAMLIT
================================ */

section[data-testid="stSidebar"]{
    display:none;
}


[data-testid="collapsedControl"]{
    display:none !important;
}


#MainMenu{
    display:none;
}


header{
    display:none;
}


footer{
    display:none;
}



/* ================================
   PÁGINA
================================ */


.block-container{

    max-width:850px;

    padding-top:30px;

}



/* ================================
   LOGO
================================ */


.logo-area{

    text-align:center;

}



/* ================================
   TÍTULOS
================================ */


.titulo{

    text-align:center;

    font-size:32px;

    font-weight:bold;

    color:#8B5A2B;

}



.subtitulo{

    text-align:center;

    font-size:18px;

    color:#777;

    margin-bottom:30px;

}



/* ================================
   LOGIN
================================ */


.login-box{

    background:#fffaf5;

    padding:30px;

    border-radius:18px;

    border:1px solid #ead8c7;

}



/* ================================
   CAMPOS
================================ */


input{

    height:42px !important;

    border-radius:10px !important;

}



/* ================================
   BOTÕES
================================ */


.stButton button{


    background:#8B5A2B;

    color:white;

    border-radius:12px;

    height:45px;

    font-size:15px;

    font-weight:bold;

}



.stButton button:hover{


    background:#6f451f;


}



/* ================================
   CARDS
================================ */


div[data-testid="stPageLink"]{


    background:#fffaf5;

    border-radius:15px;

    padding:15px;

    border:1px solid #ead8c7;


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


    st.markdown(
        "<div class='logo-area'>",
        unsafe_allow_html=True
    )


    st.image(

        str(logo),

        width=150

    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )




st.markdown(

"""
<div class="titulo">
Painel Administrativo
</div>

<div class="subtitulo">
Doce Cesta Brasília
</div>

""",

unsafe_allow_html=True

)




# =====================================================
# CONTROLE LOGIN
# =====================================================

if "usuario" not in st.session_state:


    st.session_state.usuario = None




# =====================================================
# LOGIN
# =====================================================


if st.session_state.usuario is None:



    st.markdown(

        "<div class='login-box'>",

        unsafe_allow_html=True

    )


    st.subheader(
        "🔐 Acesso Administrativo"
    )



    login = st.text_input(

        "Usuário",

        placeholder="Digite seu usuário"

    )



    senha = st.text_input(

        "Senha",

        type="password",

        placeholder="Digite sua senha"

    )



    entrar = st.button(

        "ENTRAR",

        use_container_width=True

    )



    st.markdown(

        "</div>",

        unsafe_allow_html=True

    )



    if entrar:



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





st.success(

    f"👤 {usuario['login']} | Perfil: {usuario['perfil']}"

)





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





if usuario["perfil"] != "Administrador":


    st.info(

        "Perfil Operador: acesso somente aos módulos operacionais."

    )





st.divider()



st.caption(

    "Doce Cesta Brasília - Sistema Administrativo"

)
