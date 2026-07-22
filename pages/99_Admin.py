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


section[data-testid="stSidebar"]{

    display:none !important;

}


[data-testid="collapsedControl"]{

    display:none !important;

}


#MainMenu{

    display:none !important;

}


header{

    display:none !important;

}


footer{

    display:none !important;

}



.block-container{

    max-width:700px;

    padding-top:20px;

    padding-bottom:40px;

}



.titulo{

    text-align:center;

    font-size:28px;

    font-weight:bold;

    color:#8B5A2B;

    margin-top:15px;

}



.subtitulo{

    text-align:center;

    font-size:16px;

    color:#777;

    margin-bottom:30px;

}



.login-area{

    background:transparent;

    border:none;

    padding:0;

}



div[data-baseweb="input"]{

    border-radius:10px;

}



input{

    font-size:15px !important;

}



.stButton button{

    background:#8B5A2B;

    color:white;

    border-radius:10px;

    height:45px;

    font-size:16px;

    font-weight:bold;

    width:100%;

}



.stButton button:hover{

    background:#6f451f;

}



div[data-testid="stPageLink"] button{

    border-radius:12px;

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

        [1,1,1]

    )


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



# =====================================================
# CONTROLE DE LOGIN
# =====================================================


if "usuario" not in st.session_state:


    st.session_state.usuario = None



# =====================================================
# LOGIN
# =====================================================


if st.session_state.usuario is None:


    st.markdown(

        "<div class='login-area'>",

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



st.divider()



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
# MENU PRINCIPAL
# =====================================================


st.subheader(

    "📂 Módulos do Sistema"

)


st.caption(

    "Selecione o módulo que deseja acessar."

)



# =====================================================
# LINHA 1
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
# LINHA 2
# =====================================================


col1,col2,col3 = st.columns(3)



with col1:


    st.page_link(

        "pages/05_Produtos.py",

        label="🛒 Produtos",

        use_container_width=True

    )



with col2:


    if usuario["perfil"] in [

        "Administrador",

        "Operador"

    ]:


        st.page_link(

            "pages/15_Categorias.py",

            label="📂 Categorias",

            use_container_width=True

        )


    else:


        st.info(

            "Sem acesso"

        )



with col3:


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



# =====================================================
# LINHA 3
# =====================================================


col1,col2,col3 = st.columns(3)



with col1:


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


    st.warning(

        "⚠️ Perfil Operador: acesso limitado aos módulos operacionais."

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
