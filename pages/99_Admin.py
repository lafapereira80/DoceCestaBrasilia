import streamlit as st
from pathlib import Path


from services.usuario_service import (
    autenticar_usuario
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
# CSS GERAL
# =====================================================

st.markdown(
"""
<style>

/* =====================================
   REMOVE ELEMENTOS DO STREAMLIT
===================================== */


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



/* =====================================
   ÁREA PRINCIPAL
===================================== */


.block-container{


    max-width:600px;

    padding-top:25px;

    padding-bottom:30px;


}



/* =====================================
   TÍTULOS
===================================== */


.titulo{


    text-align:center;

    color:#8B5A2B;

    font-size:30px;

    font-weight:bold;

    margin-top:10px;


}



.subtitulo{


    text-align:center;

    color:#777;

    font-size:16px;

    margin-bottom:30px;


}



/* =====================================
   CAMPOS
===================================== */


input{


    border-radius:10px !important;


}



div[data-baseweb="input"]{


    border-radius:10px !important;


}



/* =====================================
   BOTÕES
===================================== */


.stButton button{


    background:#8B5A2B;

    color:white;

    border-radius:12px;

    height:45px;

    font-weight:bold;

    width:100%;


}



.stButton button:hover{


    background:#6f451f;


}



/* =====================================
   LINKS DO PAINEL
===================================== */


div[data-testid="stPageLink"]{


    background:#fffaf5;

    border-radius:12px;

    padding:10px;

    border:1px solid #ead8c7;


}


</style>
""",
unsafe_allow_html=True
)





# =====================================================
# LOGO CENTRALIZADA
# =====================================================


logo = Path(

    "assets/logo.webp"

)



if logo.exists():


    col1,col2,col3 = st.columns(

        [1,2,1]

    )


    with col2:


        st.image(

            str(logo),

            width=150

        )





# =====================================================
# CABEÇALHO
# =====================================================


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
# CONTROLE DE SESSÃO
# =====================================================


if "usuario" not in st.session_state:


    st.session_state.usuario = None
# =====================================================
# TELA DE LOGIN
# =====================================================


if st.session_state.usuario is None:



    st.markdown(
        "<h3 style='text-align:center;'>🔐 Acesso Administrativo</h3>",
        unsafe_allow_html=True
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



    st.write("")



    entrar = st.button(

        "ENTRAR",

        use_container_width=True

    )



    if entrar:



        if not login or not senha:


            st.warning(

                "Informe usuário e senha."

            )

            st.stop()




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





col1,col2 = st.columns(

    [3,1]

)



with col1:


    st.caption(

        "Usuário autenticado no sistema."

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
# PAINEL DE MÓDULOS
# =====================================================


st.markdown(

"""
<h3 style="text-align:center;">
📂 Módulos do Sistema
</h3>
""",

unsafe_allow_html=True

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
# TERCEIRA LINHA
# =====================================================


col1,col2,col3 = st.columns(3)



with col1:


    st.page_link(

        "pages/12_Produtos_da_Cesta.py",

        label="📦 Produtos da Cesta",

        use_container_width=True

    )



with col2:


    st.page_link(

        "pages/14_Configurar_Cesta.py",

        label="⚙️ Configurar Cesta",

        use_container_width=True

    )



with col3:


    if usuario["perfil"] == "Administrador":


        st.page_link(

            "pages/08_Admin.py",

            label="🔧 Configurações",

            use_container_width=True

        )





# =====================================================
# AVISO DE PERFIL
# =====================================================


if usuario["perfil"] != "Administrador":


    st.info(

        "Perfil Operador: acesso limitado aos módulos operacionais."

    )





# =====================================================
# RODAPÉ
# =====================================================


st.divider()



st.markdown(

"""
<div style="
text-align:center;
font-size:12px;
color:#777;
padding:10px;
">

© 2026 Doce Cesta Brasília<br>
Sistema Administrativo

</div>
""",

unsafe_allow_html=True

)
