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


/* REMOVE SIDEBAR */

section[data-testid="stSidebar"]{

    display:none;

}



/* REMOVE BOTÃO SHOW/HIDE */

[data-testid="collapsedControl"]{

    display:none !important;

}



/* REMOVE MENU SUPERIOR */

#MainMenu{

    display:none;

}



header{

    display:none;

}



footer{

    display:none;

}



/* CONTAINER PRINCIPAL */

.block-container{

    max-width:900px;

    padding-top:20px;

    padding-bottom:30px;

}



/* LOGO */

.logo-container{

    display:flex;

    justify-content:center;

    align-items:center;

    margin-bottom:10px;

}



/* TITULOS */

.titulo{

    text-align:center;

    font-size:28px;

    font-weight:bold;

    color:#8B5A2B;

}



.subtitulo{

    text-align:center;

    font-size:16px;

    color:#777;

    margin-bottom:25px;

}



/* LOGIN BOX */

.login-box{

    background:#fffaf5;

    padding:25px;

    border-radius:15px;

    border:1px solid #ead8c7;

}



/* BOTÕES */

.stButton button{

    background:#8B5A2B;

    color:white;

    border-radius:10px;

    height:45px;

    font-size:15px;

    font-weight:bold;

}



.stButton button:hover{

    background:#6f451f;

}



/* CARDS */

.card{

    background:#fffaf5;

    padding:20px;

    border-radius:15px;

    border:1px solid #ead8c7;

    text-align:center;

    font-size:18px;

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

        "<div class='logo-container'>",

        unsafe_allow_html=True

    )


    st.image(

        str(logo),

        width=140

    )


    st.markdown(

        "</div>",

        unsafe_allow_html=True

    )



st.markdown(

"<div class='titulo'>Painel Administrativo</div>",

unsafe_allow_html=True

)



st.markdown(

"<div class='subtitulo'>Doce Cesta Brasília</div>",

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

        "Entrar",

        use_container_width=True

    )



    if entrar:


        if not login or not senha:


            st.warning(

                "Informe usuário e senha."

            )


        else:



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



    st.markdown(

        "</div>",

        unsafe_allow_html=True

    )


    st.stop()





# =====================================================
# USUÁRIO LOGADO
# =====================================================


usuario = st.session_state.usuario




# =====================================================
# CABEÇALHO USUÁRIO
# =====================================================


col1,col2 = st.columns(

    [4,1]

)



with col1:


    st.success(

        f"👤 {usuario['login']} | Perfil: {usuario['perfil']}"

    )



with col2:


    sair = st.button(

        "🚪 Sair",

        use_container_width=True

    )



    if sair:


        st.session_state.usuario = None

        st.rerun()




st.divider()



# =====================================================
# TÍTULO DOS MÓDULOS
# =====================================================


st.markdown(

"### 📂 Módulos do Sistema",

)





# =====================================================
# PRIMEIRA LINHA DE MÓDULOS
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
# SEGUNDA LINHA DE MÓDULOS
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


    else:


        st.info(

            "Sem acesso"

        )




with col3:


    if usuario["perfil"] == "Administrador":


        st.page_link(

            "pages/07_Usuarios.py",

            label="👤 Usuários",

            use_container_width=True

        )


    else:


        st.info(

            "Sem acesso"

        )
        
# =====================================================
# AVISO DE PERFIL
# =====================================================


if usuario["perfil"] != "Administrador":


    st.info(

        """
        👷 Perfil Operador

        Você possui acesso somente aos módulos operacionais.
        """

    )



# =====================================================
# RODAPÉ
# =====================================================


st.divider()



st.markdown(

"""
<div class="rodape">

Doce Cesta Brasília<br>
Sistema Administrativo

</div>
""",

unsafe_allow_html=True

)
