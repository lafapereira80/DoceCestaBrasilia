import streamlit as st

# =====================================================
# CONFIGURA VISUAL DO STREAMLIT (DESIGNER PREMIUM)
# =====================================================

def configurar_pagina():
    st.markdown(
        """
        <style>
        /* =========================================
           REMOÇÃO DE ELEMENTOS PADRÃO E CABEÇALHO
        ========================================== */
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent !important; z-index: 99999 !important; pointer-events: none !important; }

        /* =========================================
           BOTÕES DE ABRIR/FECHAR SIDEBAR
        ========================================== */
        [data-testid="stSidebarCollapseButton"] button span, [data-testid="collapsedControl"] button span, button[aria-label="Close sidebar"] span, button[aria-label="Open sidebar"] span { display: none !important; }
        [data-testid="stSidebarCollapseButton"] button::after, button[aria-label="Close sidebar"]::after { content: "✕" !important; font-size: 18px !important; font-weight: 700 !important; color: #5a3b28 !important; }
        [data-testid="collapsedControl"] button::after, button[aria-label="Open sidebar"]::after { content: "☰" !important; font-size: 24px !important; font-weight: 800 !important; color: #5a3b28 !important; }
        [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }

        /* =========================================
           SIDEBAR - ESTRUTURA E ESPAÇAMENTOS (O SEGREDO DO COMPACTO)
        ========================================== */
        section[data-testid="stSidebar"] {
            background-color: #faf7f3 !important;
            border-right: 1px solid #e8ddd3 !important;
        }
        /* Mata o espaçamento exagerado padrão do Streamlit entre os itens */
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.15rem !important;
        }
        /* Mata a margem gigante do st.divider() */
        section[data-testid="stSidebar"] hr {
            margin: 0.6rem 0 !important;
            border-bottom: 1px solid #dfcdbb !important;
        }

        /* =========================================
           MARCA E CARTÃO DO USUÁRIO
        ========================================== */
        .sidebar-brand {
            font-size: 17px !important; font-weight: 800 !important; color: #5a3b28 !important;
            margin-bottom: 8px; text-align: center; letter-spacing: -0.5px;
        }
        .user-card {
            background: #ffffff; border: 1px solid #dfcdbb; border-radius: 8px;
            padding: 8px 10px; margin-bottom: 4px; box-shadow: 0 2px 4px rgba(90,59,40,0.04);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .user-name { font-weight: 800; color: #333; font-size: 13px !important; margin-bottom: 2px; text-align: center;}
        .user-role {
            display: inline-block; background-color: #f3ece6; color: #775a46;
            font-size: 10px !important; font-weight: 700; padding: 2px 8px;
            border-radius: 10px; text-transform: uppercase; letter-spacing: 0.5px;
        }

        /* =========================================
           ITENS DO MENU (LINKS COMPACTOS E ANIMADOS)
        ========================================== */
        div[data-testid="stPageLink"] { padding: 0 !important; }
        div[data-testid="stPageLink"] a {
            border-radius: 6px !important;
            padding: 6px 12px !important;
            margin: 0 !important;
            color: #5a3b28 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            border: none !important;
            background-color: transparent !important;
            transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        /* Efeito "Surpresa": Fundo suave e leve deslize para a direita ao passar o mouse */
        div[data-testid="stPageLink"] a:hover {
            background-color: #efe8e1 !important;
            color: #222 !important;
            transform: translateX(4px);
        }

        /* =========================================
           BOTÃO DE SAIR
        ========================================== */
        div[data-testid="stSidebar"] button {
            border-radius: 6px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            border: 1px solid #dfcdbb !important;
            background-color: #ffffff !important;
            color: #c5221f !important;
            padding: 4px 8px !important;
            min-height: 32px !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stSidebar"] button:hover {
            background-color: #fce8e6 !important;
            border-color: #f5c6cb !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(197, 34, 31, 0.1) !important;
        }

        /* =========================================
           RESPONSIVIDADE (CELULARES)
        ========================================== */
        @media (max-width: 768px) {
            [data-testid="collapsedControl"] {
                top: 8px !important; left: 8px !important; background-color: #ffffff !important;
                border: 2px solid #dfcdbb !important; border-radius: 8px !important;
                box-shadow: 0 4px 10px rgba(90, 59, 40, 0.15) !important; padding: 4px 10px !important;
            }
            .sidebar-brand { font-size: 20px !important; margin-top: 10px !important; margin-bottom: 15px !important; }
            section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] { gap: 0.25rem !important; }
            section[data-testid="stSidebar"] hr { margin: 0.8rem 0 !important; }
            /* No celular o toque precisa ser um pouco maior para o dedo, mas mantém a elegância */
            div[data-testid="stPageLink"] a { padding: 10px 14px !important; font-size: 15px !important; border-radius: 8px !important; }
            div[data-testid="stSidebar"] button { min-height: 40px !important; font-size: 14px !important; margin-top: 5px !important; }
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

        # Exibição completa para Administradores e Operadores
        if perfil in ["Administrador", "Operador"]:
            st.page_link("pages/02_Pedidos.py", label="📦 Pedidos")
            st.page_link("pages/03_Clientes.py", label="👥 Clientes")
            st.page_link("pages/04_Cestas.py", label="🧺 Cestas")
            st.page_link("pages/05_Produtos.py", label="🍫 Produtos")
            st.page_link("pages/15_Categorias.py", label="📂 Categorias")

        # Exibição estrita para Administradores
        if perfil == "Administrador":
            st.divider()
            st.page_link("pages/06_Financeiro.py", label="💰 Financeiro")
            st.page_link("pages/07_Usuarios.py", label="👤 Usuários")

        st.divider()

        if st.button("🚪 Sair da Conta", use_container_width=True):
            # Envia uma "permissão de logout" para a tela Admin executar de forma segura
            st.session_state["fazer_logout"] = True
            st.switch_page("pages/99_Admin.py")
