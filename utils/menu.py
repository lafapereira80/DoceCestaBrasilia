import streamlit as st
import time

# =====================================================
# CONFIGURA VISUAL DO STREAMLIT (OTIMIZADO MOBILE)
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

        header[data-testid="stHeader"] {
            background: transparent !important;
            z-index: 99999 !important;
            pointer-events: none !important; 
        }

        /* =========================================
           CORREÇÃO DOS BOTAOES ABRIR/FECHAR SIDEBAR
        ========================================== */
        [data-testid="stSidebarCollapseButton"] button span,
        [data-testid="collapsedControl"] button span,
        button[aria-label="Close sidebar"] span,
        button[aria-label="Open sidebar"] span {
            display: none !important;
        }

        [data-testid="stSidebarCollapseButton"] button::after,
        button[aria-label="Close sidebar"]::after {
            content: "✕" !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            color: #5a3b28 !important;
        }

        [data-testid="collapsedControl"] button::after,
        button[aria-label="Open sidebar"]::after {
            content: "☰" !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            color: #5a3b28 !important;
        }

        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important; 
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
            padding: 8px 10px !important;
            transition: all 0.2s ease !important;
            color: #5a3b28 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            margin-bottom: 4px !important;
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

        /* =========================================
           RESPONSIVIDADE EXCLUSIVA PARA MOBILE
        ========================================== */
        @media (max-width: 768px) {
            [data-testid="collapsedControl"] {
                top: 12px !important;
                left: 12px !important;
                background-color: #ffffff !important;
                border: 2px solid #dfcdbb !important;
                border-radius: 8px !important;
                box-shadow: 0 4px 10px rgba(90, 59, 40, 0.15) !important;
                padding: 6px 12px !important;
                z-index: 100000 !important;
            }
            .sidebar-brand { font-size: 24px !important; margin-top: 20px !important; margin-bottom: 25px !important; }
            .user-name { font-size: 16px !important; }
            .user-role { font-size: 12px !important; padding: 4px 8px !important; }
            div[data-testid="stPageLink"] a { padding: 14px 16px !important; font-size: 16px !important; margin-bottom: 8px !important; }
            div[data-testid="stSidebar"] button { height: 54px !important; font-size: 16px !important; margin-top: 15px !important; }
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

        st.page_link("pages/99_Admin.py", label="🏠 Administração")

        if perfil in ["Administrador", "Operador"]:
            st.page_link("pages/02_Pedidos.py", label="📦 Pedidos")
            st.page_link("pages/03_Clientes.py", label="👥 Clientes")
            st.page_link("pages/04_Cestas.py", label="🧺 Cestas")
            st.page_link("pages/05_Produtos.py", label="🍫 Produtos")
            st.page_link("pages/15_Categorias.py", label="📂 Categorias")

        if perfil == "Administrador":
            st.divider()
            st.page_link("pages/06_Financeiro.py", label="💰 Financeiro")
            st.page_link("pages/07_Usuarios.py", label="👤 Usuários")

        st.divider()

        if st.button("🚪 Sair da Conta", use_container_width=True):
            # Remove a memória primeiro
            st.session_state.pop("usuario", None)
            
            # Tenta apagar o cookie do navegador
            try:
                from streamlit_cookies_controller import CookieController
                controller = CookieController(key="menu_remove")
                controller.remove("doce_cesta_admin")
            except Exception:
                pass
                
            time.sleep(0.5)
            st.switch_page("app.py")
