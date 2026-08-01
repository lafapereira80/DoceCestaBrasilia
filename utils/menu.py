import streamlit as st

def configurar_pagina():
    """Injeta os estilos globais de design e garante a persistência visual do menu e páginas"""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
        
        html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployMenu {display: none;}
        
        /* ESCONDE A LISTA DE ARQUIVOS PADRÃO DO STREAMLIT NO MENU LATERAL */
        [data-testid="stSidebarNav"] {display: none !important;}
        
        /* REMOVE O ESPAÇO EM BRANCO GRANDE NO TOPO DA BARRA LATERAL */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0rem !important;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 0.8rem !important;
        }

        /* ESTILIZAÇÃO DOS LINKS DA BARRA LATERAL (COM RELEVO E SOMBRA) */
        section[data-testid="stSidebar"] div[data-testid="stPageLink"] {
            background: linear-gradient(135deg, #ffffff 0%, #fcfbf8 100%) !important;
            border: 1px solid #e8ddd3 !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(90, 59, 40, 0.04) !important;
            transition: all 0.2s ease !important;
            margin-bottom: 8px !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stPageLink"]:hover {
            border-color: #c5721f !important;
            background: linear-gradient(135deg, #ffffff 0%, #fff7f0 100%) !important;
            transform: translateX(3px) !important;
            box-shadow: 0 6px 16px rgba(197, 114, 31, 0.12) !important;
        }
        section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
            padding: 10px 14px !important;
            font-weight: 700 !important;
            color: #4a2e1b !important;
        }
        section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
            text-decoration: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def menu_lateral():
    """Gera o menu lateral dinâmico baseado no perfil do usuário"""
    usuario = st.session_state.get("usuario")

    with st.sidebar:
        # ==========================================
        # BRANDING MINIMALISTA PREMIUM
        # ==========================================
        html_branding = """
<div style="text-align: center; margin-top: 0px; margin-bottom: 20px;">
    <div style="position: relative; z-index: 2; margin-bottom: -22px;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: linear-gradient(135deg, #c5721f 0%, #a65d14 100%); border-radius: 50%; border: 4px solid #f6f7f8; color: white; font-size: 20px; box-shadow: 0 4px 10px rgba(197, 114, 31, 0.25);">🧺</div>
    </div>
    <div style="background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 32px 15px 15px 15px; position: relative; z-index: 1; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03);">
        <h2 style="color: #4a2e1b; font-family: 'Dancing Script', cursive !important; font-size: 34px; font-weight: 700; margin: 0; line-height: 1.1;">Doce Cesta</h2>
        <div style="color: #c5721f; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px;">Painel de Gestão</div>
    </div>
</div>
"""
        st.markdown(html_branding, unsafe_allow_html=True)

        if usuario:
            perfil = usuario.get("perfil", "Usuário")
            login = usuario.get("login", "Admin")
            
            # ==========================================
            # CRACHÁ DE USUÁRIO
            # ==========================================
            html_cracha = f"""
<div style="background: #ffffff; border: 1px solid #e8ddd3; padding: 10px 14px; border-radius: 14px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.04); display: flex; align-items: center; gap: 12px;">
    <div style="background: linear-gradient(135deg, #fef7e0 0%, #fffbf7 100%); border: 1px solid #fce8b2; color: #b06000; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">🧑‍💻</div>
    <div>
        <div style="color: #2c1e14; font-size: 13px; font-weight: 800; line-height: 1.2;">{login}</div>
        <div style="color: #137333; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">{perfil}</div>
    </div>
</div>
"""
            st.markdown(html_cracha, unsafe_allow_html=True)

            # ==========================================
            # MENU DE NAVEGAÇÃO ORGANIZADO
            # ==========================================
            if perfil in ["Administrador", "Operador"]:
                st.markdown("**📦 OPERAÇÃO & VENDAS**")
                st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="📋")
                st.page_link("pages/19_Pedido_Manual.py", label="Venda Varejo (PDV)", icon="🛍️")
                st.page_link("pages/18_Corporativo.py", label="Vendas B2B", icon="🏢")
                st.page_link("pages/16_Previsao.py", label="Previsão de Produção", icon="📈")
                st.page_link("pages/08_Entregas.py", label="Rotas de Entrega", icon="🛵")
                
                st.write("")
                st.markdown("**📊 GESTÃO & FINANCEIRO**")
                st.page_link("pages/03_Clientes.py", label="Base de Clientes", icon="👥")
                st.page_link("pages/06_Financeiro.py", label="Painel Financeiro", icon="💰")
                
                st.write("")
                st.markdown("**🍓 CATÁLOGO DA LOJA**")
                st.page_link("pages/04_Cestas.py", label="Cestas e Kits", icon="🧺")
                st.page_link("pages/05_Produtos.py", label="Produtos e Insumos", icon="🍓")
                st.page_link("pages/15_Categorias.py", label="Categorias", icon="🏷️")
                st.page_link("pages/17_Secoes_Vitrine.py", label="Seções da Vitrine", icon="🖥️")

                st.write("")
                st.markdown("**⚙️ CONFIGURAÇÕES**")
                st.page_link("pages/07_Usuarios.py", label="Gerenciar Usuários", icon="🔑")
                st.page_link("app.py", label="Ver Vitrine da Loja", icon="🌐")

            elif perfil == "Entregador":
                st.markdown("**🛵 ÁREA DO ENTREGADOR**")
                st.page_link("pages/08_Entregas.py", label="Minha Rota", icon="🗺️")

            st.write("")
            st.divider()
            
            if st.button("🚪 Sair (Logout)", use_container_width=True):
                st.session_state.clear()
                st.switch_page("app.py")
        else:
            st.info("Faça login para acessar o painel restrito.")
            st.page_link("app.py", label="Voltar para a Loja", icon="🏠")
