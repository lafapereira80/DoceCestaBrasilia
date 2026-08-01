import streamlit as st

def configurar_pagina():
    """Design Mobile-First estilo App Nativo (iOS / Nubank)"""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Dancing+Script:wght@700&display=swap');
        
        /* Fontes e Fundo Global do App */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
        .stApp { background-color: #F8FAFC !important; }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployMenu {display: none;}
        [data-testid="stSidebarNav"] {display: none !important;}
        
        /* ----------------------------------------------------
           AJUSTES DA BARRA LATERAL (SIDEBAR)
        ---------------------------------------------------- */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
        [data-testid="stSidebar"] .block-container { padding-top: 1.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important;}

        /* Links da Barra Lateral (Clean & Flat) */
        section[data-testid="stSidebar"] div[data-testid="stPageLink"] { margin-bottom: 4px !important; }
        section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
            background: transparent !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            font-weight: 600 !important;
            color: #475569 !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
            background-color: #F1F5F9 !important;
            color: #C5721F !important;
            transform: translateX(4px) !important;
        }

        /* ----------------------------------------------------
           AJUSTES DOS BOTÕES NA PÁGINA PRINCIPAL (ADMIN)
        ---------------------------------------------------- */
        /* Cartões de Seção (Grupos) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 24px !important;
            padding: 24px 20px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02) !important;
            margin-bottom: 24px !important;
        }

        /* Botões "App Style" nas páginas */
        .stApp a[data-testid="stPageLink"] {
            background: #F8FAFC !important;
            border: 1px solid #F1F5F9 !important;
            border-radius: 16px !important;
            padding: 16px 20px !important;
            color: #1E293B !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            display: flex !important;
            align-items: center !important;
            transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.01) !important;
            margin-bottom: 12px !important;
            width: 100% !important;
        }
        .stApp a[data-testid="stPageLink"]:hover {
            background: #FFFFFF !important;
            border-color: #C5721F !important;
            color: #C5721F !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(197, 114, 31, 0.12) !important;
        }

        /* Títulos de Seção */
        .app-section-title {
            font-size: 14px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94A3B8;
            margin-bottom: 16px;
            padding-left: 4px;
        }

        /* Oculta label do Page Link nativo que fica feio */
        div[data-testid="stPageLink"] p { margin: 0 !important; }

        @media (max-width: 640px) {
            .block-container { padding: 1rem 0.8rem !important; }
            div[data-testid="stVerticalBlockBorderWrapper"] { padding: 20px 16px !important; border-radius: 20px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def menu_lateral():
    usuario = st.session_state.get("usuario")

    with st.sidebar:
        # BRANDING TIPO "CARTÃO BLACK"
        html_branding = """
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-radius: 20px; padding: 24px 16px; text-align: center; margin-bottom: 24px; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);">
            <div style="font-size: 32px; margin-bottom: 5px;">🧺</div>
            <h2 style="font-family: 'Dancing Script', cursive !important; font-size: 32px; font-weight: 700; color: #FFFFFF; margin: 0; line-height: 1;">Doce Cesta</h2>
            <div style="color: #C5721F; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-top: 8px;">App de Gestão</div>
        </div>
        """
        st.markdown(html_branding, unsafe_allow_html=True)

        if usuario:
            perfil = usuario.get("perfil", "Usuário")
            login = usuario.get("login", "Admin")
            
            # CRACHÁ ESTILO "APPLE ID"
            html_cracha = f"""
            <div style="background: #F8FAFC; border: 1px solid #F1F5F9; padding: 12px; border-radius: 16px; margin-bottom: 24px; display: flex; align-items: center; gap: 12px;">
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">🧑‍💻</div>
                <div>
                    <div style="color: #1E293B; font-size: 14px; font-weight: 700; line-height: 1.2;">{login}</div>
                    <div style="color: #64748B; font-size: 11px; font-weight: 600; margin-top: 2px;">{perfil}</div>
                </div>
            </div>
            """
            st.markdown(html_cracha, unsafe_allow_html=True)

            if perfil in ["Administrador", "Operador"]:
                st.markdown('<div style="font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px; margin-top: 10px; padding-left: 8px;">OPERAÇÃO & VENDAS</div>', unsafe_allow_html=True)
                st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="📋")
                st.page_link("pages/19_Pedido_Manual.py", label="Venda Varejo (PDV)", icon="🛍️")
                st.page_link("pages/18_Corporativo.py", label="Vendas B2B", icon="🏢")
                st.page_link("pages/16_Previsao.py", label="Previsão de Produção", icon="📈")
                st.page_link("pages/08_Entregas.py", label="Rotas de Entrega", icon="🛵")
                
                st.markdown('<div style="font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px; margin-top: 24px; padding-left: 8px;">GESTÃO & FINANCEIRO</div>', unsafe_allow_html=True)
                st.page_link("pages/03_Clientes.py", label="Base de Clientes", icon="👥")
                st.page_link("pages/06_Financeiro.py", label="Painel Financeiro", icon="💰")
                
                st.markdown('<div style="font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px; margin-top: 24px; padding-left: 8px;">CATÁLOGO DA LOJA</div>', unsafe_allow_html=True)
                st.page_link("pages/04_Cestas.py", label="Cestas e Kits", icon="🧺")
                st.page_link("pages/05_Produtos.py", label="Produtos e Insumos", icon="🍓")
                st.page_link("pages/15_Categorias.py", label="Categorias", icon="🏷️")
                st.page_link("pages/17_Secoes_Vitrine.py", label="Seções da Vitrine", icon="🖥️")

                st.markdown('<div style="font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px; margin-top: 24px; padding-left: 8px;">CONFIGURAÇÕES</div>', unsafe_allow_html=True)
                st.page_link("pages/07_Usuarios.py", label="Gerenciar Usuários", icon="🔑")
                st.page_link("app.py", label="Ver Vitrine da Loja", icon="🌐")

            elif perfil == "Entregador":
                st.markdown('<div style="font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px; margin-top: 10px; padding-left: 8px;">ENTREGADOR</div>', unsafe_allow_html=True)
                st.page_link("pages/08_Entregas.py", label="Minha Rota", icon="🗺️")

            st.write("")
            st.divider()
            
            if st.button("🚪 Sair da Conta", use_container_width=True):
                st.session_state.clear()
                st.switch_page("app.py")
        else:
            st.info("Faça login para acessar o painel restrito.")
            st.page_link("app.py", label="Voltar para a Loja", icon="🏠")
