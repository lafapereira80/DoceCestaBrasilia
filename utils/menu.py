import streamlit as st

# =====================================================
# CONFIGURA VISUAL DO STREAMLIT (DESIGNER PREMIUM)
# =====================================================

def configurar_pagina():
    st.markdown(
        """
        <style>
        /* =========================================
           REMOÇÃO DE ELEMENTOS PADRÃO
        ========================================== */
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent !important; z-index: 99999 !important; pointer-events: none !important; }

        /* =========================================
           BOTÕES DE MENU (SANDUÍCHE) MOBILE
        ========================================== */
        [data-testid="collapsedControl"] {
            top: 10px !important; left: 10px !important;
            background-color: #ffffff !important; border: 1px solid #dfcdbb !important;
            border-radius: 8px !important; box-shadow: 0 2px 8px rgba(90, 59, 40, 0.1) !important;
            padding: 4px 10px !important; z-index: 100000 !important;
        }
        [data-testid="stSidebarCollapseButton"] button span, [data-testid="collapsedControl"] button span, button[aria-label="Close sidebar"] span, button[aria-label="Open sidebar"] span { display: none !important; }
        [data-testid="collapsedControl"] button::after { content: "☰" !important; font-size: 22px !important; font-weight: 800 !important; color: #5a3b28 !important; }
        button[aria-label="Close sidebar"]::after { content: "✕" !important; font-size: 18px !important; font-weight: 700 !important; color: #5a3b28 !important; }
        [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }

        /* =========================================
           SIDEBAR - FUNDO E CARTÃO DO USUÁRIO
        ========================================== */
        section[data-testid="stSidebar"] {
            background-color: #faf7f3 !important;
            border-right: 1px solid #e8ddd3 !important;
        }
        
        .sidebar-brand {
            font-size: 18px !important; font-weight: 800 !important; color: #5a3b28 !important;
            margin-top: 15px !important; margin-bottom: 12px !important; text-align: center;
        }
        
        .user-card {
            background: #ffffff; border: 1px solid #dfcdbb; border-radius: 10px;
            padding: 10px 10px !important; margin-bottom: 10px !important;
            box-shadow: 0 2px 4px rgba(90,59,40,0.03); display: flex; flex-direction: column; align-items: center;
        }
        
        .user-name { font-weight: 800; color: #333; font-size: 14px !important; margin-bottom: 4px; }
        
        .user-role {
            background-color: #f3ece6; color: #775a46; font-size: 10px !important;
            font-weight: 800; padding: 3px 8px; border-radius: 10px; text-transform: uppercase; letter-spacing: 0.5px;
        }

        /* =======================================================
           🔥 A MÁGICA DO ESPAÇAMENTO (MARGENS NEGATIVAS) 🔥
        ======================================================= */
        
        /* 1. Esmaga o Gap nativo do Streamlit */
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0 !important; 
        }

        /* 2. Puxa os links para cima e para baixo para colar um no outro */
        div[data-testid="stPageLink"] { 
            margin-top: -12px !important; 
            padding: 0 !important;
            z-index: 10;
        }

        /* 3. Estiliza o botão do link: gordinho por dentro, colado por fora */
        div[data-testid="stPageLink"] a {
            border-radius: 8px !important;
            padding: 10px 14px !important;  
            color: #5a3b28 !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            background-color: transparent !important;
            border: none !important;
            transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }

        /* Efeito de destaque Magnético */
        div[data-testid="stPageLink"] a:hover {
            background-color: #e8ddd3 !important;
            color: #222 !important;
            transform: translateX(4px);
        }

        /* Linhas Divisórias (hr) compactas */
        section[data-testid="stSidebar"] hr {
            margin-top: -4px !important;
            margin-bottom: 10px !important;
            border-bottom: 1px solid #dfcdbb !important;
        }

        /* Botão de Sair Compacto */
        div[data-testid="stSidebar"] button {
            margin-top: -6px !important;
            border-radius: 8px !important;
            font-size: 13px !important; font-weight: 700 !important;
            border: 1px solid #dfcdbb !important; background-color: #ffffff !important;
            color: #c5221f !important; min-height: 40px !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stSidebar"] button:hover {
            background-color: #fce8e6 !important; border-color: #f5c6cb !important;
            box-shadow: 0 2px 4px rgba(197, 34, 31, 0.1) !important;
        }

        /* =========================================
           CELULAR - AJUSTE FINO EXTREMO
        ========================================== */
        @media (max-width: 768px) {
            /* Puxa com mais força no celular porque o Streamlit injeta mais espaço */
            div[data-testid="stPageLink"] { margin-top: -16px !important; }
            
            /* Área de toque maior para o dedo */
            div[data-testid="stPageLink"] a { padding: 12px 14px !important; font-size: 15px !important; }
            
            section[data-testid="stSidebar"] hr { margin-top: -8px !important; margin-bottom: 12px !important; }
            div[data-testid="stSidebar"] button { margin-top: -8px !important; min-height: 46px !important; font-size: 15px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# MENU LATERAL PERSONALIZADO E BLOQUEIO DE ACESSO
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

        # O Entregador só vê o menu inicial. Os demais veem o sistema completo.
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
            
        if perfil == "Entregador":
            # Aqui entrará a tela exclusiva de "Minhas Entregas" no futuro
            pass

        st.divider()

        if st.button("🚪 Sair da Conta", use_container_width=True):
            # Envia uma "permissão de logout" para a tela Admin executar de forma segura
            st.session_state["fazer_logout"] = True
            st.switch_page("pages/99_Admin.py")
