import streamlit as st


def configurar_pagina():

    st.markdown(
        """
        <style>

        #MainMenu {
            display:none;
        }

        footer {
            display:none;
        }

        header {
            display:none;
        }

        [data-testid="stSidebar"] {
            display:none;
        }

        </style>
        """,
        unsafe_allow_html=True
    )



def menu_lateral():


    usuario = st.session_state.get(
        "usuario"
    )


    if not usuario:

        return



    perfil = usuario.get(
        "perfil"
    )



    st.sidebar.title(
        "🍓 Doce Cesta Brasília"
    )


    st.sidebar.write(
        f"Usuário: {usuario['login']}"
    )


    st.sidebar.divider()



    st.sidebar.page_link(
        "pages/01_Inicio.py",
        label="🏠 Início"
    )


    if perfil in [
        "Administrador",
        "Operador"
    ]:


        st.sidebar.page_link(
            "pages/02_Pedidos.py",
            label="📦 Pedidos"
        )


        st.sidebar.page_link(
            "pages/03_Clientes.py",
            label="👥 Clientes"
        )


        st.sidebar.page_link(
            "pages/04_Cestas.py",
            label="🧺 Cestas"
        )


        st.sidebar.page_link(
            "pages/05_Produtos.py",
            label="🍫 Produtos"
        )



    if perfil == "Administrador":


        st.sidebar.page_link(
            "pages/06_Financeiro.py",
            label="💰 Financeiro"
        )


        st.sidebar.page_link(
            "pages/07_Usuarios.py",
            label="👤 Usuários"
        )


        st.sidebar.page_link(
            "pages/99_Admin.py",
            label="⚙️ Administração"
        )


    st.sidebar.divider()



    if st.sidebar.button(
        "🚪 Sair"
    ):

        st.session_state.usuario = None

        st.rerun()
