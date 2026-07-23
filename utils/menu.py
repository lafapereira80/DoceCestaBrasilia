import streamlit as st


# =====================================================
# CONFIGURA VISUAL DO STREAMLIT
# =====================================================

def configurar_pagina():
    st.markdown(
        """
        <style>
        /* =========================================
           REMOÇÃO DE ELEMENTOS PADRÃO (MENU E FOOTER)
        ========================================== */
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }

        /* Deixa o header transparente para mostrar a seta no topo */
        header[data-testid="stHeader"] {
            background: transparent !important;
            z-index: 99999 !important;
        }

        /* =========================================
           CORREÇÃO DOS BOTAOES ABRIR/FECHAR SIDEBAR
        ========================================== */
        /* Oculta os textos de ícones vazados nativos */
        [data-testid="stSidebarCollapseButton"] button span,
        [data-testid="collapsedControl"] button span,
        button[aria-label="Close sidebar"] span,
        button[aria-label="Open sidebar"] span {
            display: none !important;
        }

        /* Ícone bonito para fechar no menu */
        [data-testid="stSidebarCollapseButton"] button::after,
        button[aria-label="Close sidebar"]::after {
            content: "✕" !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            color: #5a3b28 !important;
        }

        /* Ícone bonito para abrir na tela principal */
        [data-testid="collapsedControl"] button::after,
        button[aria-label="Open sidebar"]::after {
            content: "☰" !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #5a3b28 !important;
        }

        /* Ajusta área clicável */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        /* =========================================
           ESTILIZAÇÃO DA SIDEBAR (LAYOUT MODERNO)
        ========================================== */
        section[data-testid="stSidebar"] {
            background-color: #faf7f3 !important;
            border-right: 1px solid #e8ddd3 !important;
        }

        .sidebar-brand {
            font-size: 18px !important;
            font-weight: 700 !important;
            color: #5a3b28 !important;
            margin-bottom: 12px;
            text-align: center;
        }

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
        st.markdown('<div class="sidebar-brand">🎁 Doce Cesta Brasília</div>', unsafe_allow_html=True)

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

        st.page_link(
            "pages/99_Admin.py",
            label="🏠 Administração"
        )

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

        if st.button(
            "🚪 Sair da Conta",
            use_container_width=True
        ):
            st.session_state.usuario = None
            st.rerun()
