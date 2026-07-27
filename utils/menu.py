import streamlit as st

# =====================================================
# CONFIGURA VISUAL DO STREAMLIT (DESIGNER PREMIUM E SEGURO)
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
           BOTÕES DE MENU (SANDUÍCHE) MOBILE E DESKTOP
        ========================================== */
        [data-testid="collapsedControl"] {
            top: 12px !important; left: 12px !important;
            background-color: #ffffff !important; border: 1px solid #dfcdbb !important;
            border-radius: 10px !important; box-shadow: 0 4px 10px rgba(90, 59, 40, 0.08) !important;
            padding: 4px 12px !important; z-index: 100000 !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="collapsedControl"]:hover { box-shadow: 0 6px 14px rgba(90, 59, 40, 0.15) !important; transform: translateY(-1px); }
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
            font-size: 19px !important; font-weight: 800 !important; color: #5a3b28 !important;
            margin-top: 10px !important; margin-bottom: 15px !important; text-align: center;
        }
        
        .user-card {
            background: #ffffff; border: 1px solid #dfcdbb; border-radius: 12px;
            padding: 14px 10px !important; margin-bottom: 10px !important;
            box-shadow: 0 2px 6px rgba(90,59,40,0.04); display: flex; flex-direction: column; align-items: center;
        }
        
        .user-name { font-weight: 800; color: #333; font-size: 15px !important; margin-bottom: 4px; line-height: 1.2; text-align: center; }
        
        .user-role {
            background-color: #f3ece6; color: #775a46; font-size: 10px !important;
            font-weight: 800; padding: 4px 10px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.5px;
        }

        /* =======================================================
           🔥 O SEGREDO DO ESPAÇAMENTO PERFEITO 🔥
        ======================================================= */
        
        /* 1. Controla a distância global entre os blocos sem usar margem negativa */
        section[data-testid="stSidebar"] > div > div > div > div > div[data-testid="stVerticalBlock"] {
            gap: 0.35rem !important; 
        }

        /* 2. Zera margens externas apenas dos links */
        div[data-testid="stPageLink"] { 
            margin: 0 !important; 
            padding: 0 !important;
        }

        /* 3. Estiliza o botão do link com respiro interno agradável */
        div[data-testid="stPageLink"] a {
            border-radius: 8px !important;
            padding: 10px 14px !important;  
            color: #5a3b28 !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            background-color: transparent !important;
            border: none !important;
            transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            display: flex !important;
            align-items: center !important;
            text-decoration: none !important;
        }

        /* Efeito Magnético: Hover */
        div[data-testid="stPageLink"] a:hover {
            background-color: #e8ddd3 !important;
            color: #222 !important;
            transform: translateX(4px);
        }

        /* =========================================
           LINHAS DIVISÓRIAS E BOTÃO DE SAIR
        ========================================== */
        section[data-testid="stSidebar"] hr {
            margin: 10px 0 !important;
            border-bottom: 1px solid #dfcdbb !important;
        }

        div[data-testid="stSidebar"] button {
            border-radius: 8px !important;
            font-size: 14px !important; font-weight: 700 !important;
            border: 1px solid #dfcdbb !important; background-color: #ffffff !important;
            color: #c5221f !important; min-height: 44px !important;
            margin-top: 5px !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stSidebar"] button:hover {
            background-color: #fce8e6 !important; border-color: #f5c6cb !important;
            box-shadow: 0 4px 10px rgba(197, 34, 31, 0.1) !important;
            transform: translateY(-2px);
        }

        /* =========================================
           CELULAR - AJUSTE FINO (MOBILE)
        ========================================== */
        @media (max-width: 768px) {
            /* No celular, os links ficam ligeiramente mais "gordinhos" para facilitar o toque do dedo */
            div[data-testid="stPageLink"] a { 
                padding: 12px 14px !important; 
                font-size: 15px !important; 
            }
            
            section[data-testid="stSidebar"] hr { 
                margin: 12px 0 !important; 
            }
            
            div[data-testid="stSidebar"] button { 
                min-height: 48px !important; 
                font-size: 15px !important;
            }
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
    nome_formatado = str(usuario.get("login", "Usuário")).capitalize()

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🎁 Doce Cesta Brasília</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="user-card">
                <div class="user-name">👤 {nome_formatado}</div>
                <div class="user-role">{perfil}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # Todos têm acesso à Home
        st.page_link("pages/99_Admin.py", label="🏠 Administração")

        # Entregador, Operador e Admin têm acesso à Rota de Entregas
        if perfil in ["Administrador", "Operador", "Entregador"]:
            st.page_link("pages/08_Entregas.py", label="🛵 Rotas e Entregas")

        # Apenas Admin e Operador veem o módulo operacional e catálogo
        if perfil in ["Administrador", "Operador"]:
            st.page_link("pages/02_Pedidos.py", label="📦 Pedidos")
            st.page_link("pages/03_Clientes.py", label="👥 Clientes")
            st.page_link("pages/04_Cestas.py", label="🧺 Cestas")
            st.page_link("pages/05_Produtos.py", label="🍫 Produtos")
            st.page_link("pages/15_Categorias.py", label="📂 Categorias")

        # Apenas Administrador vê o módulo avançado
        if perfil == "Administrador":
            st.divider()
            st.page_link("pages/06_Financeiro.py", label="💰 Financeiro")
            st.page_link("pages/07_Usuarios.py", label="🔐 Usuários")

        st.divider()

        # Botão de Logout Seguro
        if st.button("🚪 Sair da Conta", use_container_width=True):
            st.session_state["fazer_logout"] = True
            st.switch_page("pages/99_Admin.py")
