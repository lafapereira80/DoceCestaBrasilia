import streamlit as st


# =====================================================
# CONFIGURA VISUAL DO STREAMLIT
# =====================================================

def configurar_pagina():
    st.markdown(
        """
        <style>
        /* =========================================
           REMOÇÃO LIMPA DE ELEMENTOS PADRÃO
        ========================================== */
        #MainMenu { display: none !important; }
        header { display: none !important; }
        footer { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }

        /* Remove o botão de recolher sem vazar o texto dos ícones */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* =========================================
           ESTILIZAÇÃO DA SIDEBAR (LAYOUT MODERNO)
        ========================================== */
        section[data-testid="stSidebar"] {
            background-color: #faf7f3 !important;
            border-right: 1px solid #e8ddd3 !important;
        }

        /* Título da Marca */
        .sidebar-brand {
            font-size: 18px !important;
            font-weight: 700 !important;
            color: #5a3b28 !important;
            margin-bottom: 12px;
            text-align: center;
        }

        /* Card do Usuário */
        .user-card {
            background: #ffffff;
            border: 1px solid #dfcdbb;
            border-radius: 12px;
            padding: 10px 12px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }

        .user-name {
            font-weight: 700;
            color: #333;
            font-size: 13px !important;
        }

        .user-role {
            display: inline-block;
            background-color: #f3ece6;
            color: #775a46;
            font-size: 11px !important;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 6px;
            margin-top: 4px;
        }

        /* Estilização dos Links da Sidebar */
        div[data-testid="stPageLink"] a {
            border-radius: 8px !important;
            padding: 6px 10px !important;
            transition: all 0.2s ease !important;
            color: #5a3b28 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            margin-bottom: 3px !important;
        }

        div[data-testid="stPageLink"] a:hover {
            background-color: #f3ece6 !important;
            color: #333 !important;
        }

        /* Botão Sair na Sidebar */
        div[data-testid="stSidebar"] button {
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            border: 1px solid #dfcdbb !important;
            background-color: #ffffff !important;
            color: #c5221f !important;
        }

        div[data-testid="stSidebar"] button:hover {
            background-color: #fce8e6 !important;
            border-color: #f5c6cb !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# MENU LATERAL PERSONALIZADO
# =====================================================

def menu_lateral():
    usuario = st.session_state.get("usuario")

    if not usuario:
        return

    perfil = usuario.get("perfil", "Operador")

    with st.sidebar:
        # Marca e Título
        st.markdown('<div class="sidebar-brand">🎁 Doce Cesta Brasília</div>', unsafe_allow_html=True)

        # Card de Perfil do Usuário
        st.markdown(
            f"""
            <div class="user-card">
                <div class="user-name">👤 {usuario.get('login', 'Usuário')}</div>
                <div class="user-role">{perfil}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # =====================================================
        # NAVEGAÇÃO PRINCIPAL (ADMIN / PAINEL)
        # =====================================================

        st.page_link(
            "pages/99_Admin.py",
            label="🏠 Administração"
        )

        # =====================================================
        # OPERACIONAL (ADMINISTRADOR + OPERADOR)
        # =====================================================

        if perfil in ["Administrador", "Operador"]:
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
            "🚪 Sair da Conta",
            use_container_width=True
        ):
            st.session_state.usuario = None
            st.rerun()
