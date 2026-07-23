import streamlit as st



# =====================================================
# CONFIGURA VISUAL DO STREAMLIT
# =====================================================

def configurar_pagina():

    st.markdown(
        """
        <style>

        #MainMenu {
            display:none;
        }


        header {
            display:none;
        }


        footer {
            display:none;
        }


        /* Esconde somente o menu automático */
        [data-testid="stSidebarNav"] {
            display:none;
        }


        /* Remove botão de recolher */
        [data-testid="collapsedControl"] {
            display:none;
        }


        </style>
        """,
        unsafe_allow_html=True
    )



# =====================================================
# MENU LATERAL PERSONALIZADO
# =====================================================

def menu_lateral():


    usuario = st.session_state.get(
        "usuario"
    )


    if not usuario:

        return



    perfil = usuario.get(
        "perfil"
    )



    with st.sidebar:


        st.title(
            "Doce Cesta Brasília"
        )


        st.success(
            f"Olá, {usuario['login']}"
        )


        st.caption(
            f"Perfil: {perfil}"
        )


        st.divider()



        # =====================================================
        # ADMINISTRAÇÃO
        # =====================================================

        st.page_link(

            "pages/99_Admin.py",

            label="🏠 Administração"

        )



        # =====================================================
        # OPERACIONAL
        # ADMINISTRADOR + OPERADOR
        # =====================================================

        if perfil in [

            "Administrador",
            "Operador"

        ]:


            st.page_link(

                "pages/02_Pedidos.py",

                label="📦 Pedidos"

            )


            st.page_link(

                "pages/03_Clientes.py",

                label="👥 Clientes"

            )


            st.page_link(

                "pages/04_Cestas.py",

                label="🧺 Cestas"

            )


            st.page_link(

                "pages/05_Produtos.py",

                label="🍫 Produtos"

            )


            st.page_link(

                "pages/15_Categorias.py",

                label="📂 Categorias"

            )



        # =====================================================
        # SOMENTE ADMINISTRADOR
        # =====================================================

        if perfil == "Administrador":


            st.divider()


            st.page_link(

                "pages/06_Financeiro.py",

                label="💰 Financeiro"

            )


            st.page_link(

                "pages/07_Usuarios.py",

                label="👤 Usuários"

            )



        st.divider()



        # =====================================================
        # SAIR
        # =====================================================

        if st.button(

            "🚪 Sair",

            use_container_width=True

        ):


            st.session_state.usuario = None

            st.rerun()
