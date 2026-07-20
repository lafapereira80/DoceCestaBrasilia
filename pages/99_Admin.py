import streamlit as st
from pathlib import Path

from services.usuario_service import autenticar_usuario


st.set_page_config(
    page_title="Administrador",
    page_icon="🔒",
    layout="wide"
)



# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>

#MainMenu{
display:none;
}

footer{
display:none;
}

header{
display:none;
}


section[data-testid="stSidebar"]{

background:#faf7f2;

}


</style>
""",
unsafe_allow_html=True
)



# =====================================================
# LOGIN
# =====================================================


if "usuario" not in st.session_state:

    st.session_state.usuario = None



if st.session_state.usuario is None:


    logo = Path(
        "assets/logo.webp"
    )


    c1,c2,c3 = st.columns(
        [2,1,2]
    )


    with c2:

        if logo.exists():

            st.image(
                str(logo),
                width=130
            )



    st.title(
        "🔒 Área Administrativa"
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



usuario = st.session_state.usuario



# =====================================================
# MENU LATERAL
# =====================================================


with st.sidebar:


    st.success(
        f"👤 {usuario['login']}"
    )


    st.caption(
        usuario["perfil"]
    )


    st.divider()



    st.page_link(
        "pages/02_Pedidos.py",
        label="Pedidos",
        icon="📋"
    )


    st.page_link(
        "pages/03_Clientes.py",
        label="Clientes",
        icon="👥"
    )



    if usuario["perfil"] == "Administrador":


        st.page_link(
            "pages/04_Cestas.py",
            label="Cestas",
            icon="🎁"
        )


        st.page_link(
            "pages/05_Produtos.py",
            label="Produtos",
            icon="🛒"
        )


        st.page_link(
            "pages/06_Financeiro.py",
            label="Financeiro",
            icon="💰"
        )


        st.page_link(
            "pages/07_Usuarios.py",
            label="Usuários",
            icon="👤"
        )


    st.divider()


    if st.button(
        "Sair"
    ):

        st.session_state.usuario = None

        st.rerun()



# =====================================================
# HOME ADMIN
# =====================================================


st.title(
    "Painel Administrativo"
)


st.write(
    f"Bem-vindo, {usuario['login']}."
)
