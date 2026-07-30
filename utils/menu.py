import streamlit as st

def configurar_pagina():
    """Oculta elementos padrão do Streamlit e aplica estilos globais e fontes premium"""
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
        </style>
        """,
        unsafe_allow_html=True
    )

def menu_lateral():
    """Gera o menu lateral dinâmico baseado no perfil do usuário"""
    usuario = st.session_state.get("usuario")

    with st.sidebar:
        # ==========================================
        # NOVO BRANDING PREMIUM (TOPO DO MENU)
        # Código HTML alinhado à esquerda para não virar bloco de código no Markdown
        # ==========================================
        html_branding = """
<div style="background: linear-gradient(135deg, #c5721f 0%, #a65d14 100%); padding: 25px 15px; border-radius: 18px; text-align: center; margin-bottom: 25px; margin-top: 10px; box-shadow: 0 8px 20px rgba(197, 114, 31, 0.25); position: relative; overflow: hidden; border: 1px solid #d88e44;">
    <div style="position: absolute; top: -20px; left: -20px; width: 70px; height: 70px; background: rgba(255,255,255,0.15); border-radius: 50%;"></div>
    <div style="position: absolute; bottom: -30px; right: -10px; width: 90px; height: 90px; background: rgba(255,255,255,0.08); border-radius: 50%;"></div>
    <h2 style="color: #ffffff; font-family: 'Dancing Script', cursive !important; font-size: 42px; font-weight: 700; margin: 0; line-height: 1.1; text-shadow: 2px 2px 4px rgba(0,0,0,0.15); position: relative; z-index: 1;">Doce Cesta</h2>
    <div style="color: #fdfbf8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-top: 8px; opacity: 0.95; position: relative; z-index: 1;">Painel de Gestão</div>
</div>
"""
        st.markdown(html_branding, unsafe_allow_html=True)

        if usuario:
            perfil = usuario.get("perfil", "Usuário")
            login = usuario.get("login", "Admin")
            
            # ==========================================
            # NOVO CRACHÁ DE USUÁRIO
            # ==========================================
            html_cracha = f"""
<div style="background: #ffffff; border: 1px solid #e8ddd3; padding: 12px 15px; border-radius: 14px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.04); display: flex; align-items: center; gap: 12px;">
    <div style="background: linear-gradient(135deg, #fef7e0 0%, #fffbf7 100%); border: 1px solid #fce8b2; color: #b06000; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">🧑‍💻</div>
    <div>
        <div style="color: #2c1e14; font-size: 14px; font-weight: 800; line-height: 1.2;">{login}</div>
        <div style="color: #137333; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">{perfil}</div>
    </div>
</div>
"""
            st.markdown(html_cracha, unsafe_allow_html=True)

            # ==========================================
            # MENU DE NAVEGAÇÃO
            # ==========================================
            if perfil in ["Administrador", "Operador"]:
                st.markdown("**📦 OPERAÇÃO & VENDAS**")
                st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="📋")
                st.page_link("pages/08_Entregas.py", label="Rotas de Entrega", icon="🛵")
                st.page_link("pages/03_Clientes.py", label="Base de Clientes", icon="👥")
                
                st.write("")
                st.markdown("**📊 GESTÃO & FINANCEIRO**")
                st.page_link("pages/06_Financeiro.py", label="Painel Financeiro", icon="💰")
                st.page_link("pages/18_Corporativo.py", label="Vendas B2B", icon="🏢")
                st.page_link("pages/16_Previsao.py", label="Previsão de Produção", icon="📈")
                
                st.write("")
                st.markdown("**🍓 CATÁLOGO DA LOJA**")
                st.page_link("pages/04_Cestas.py", label="Cestas e Kits", icon="🧺")
                st.page_link("pages/05_Produtos.py", label="Produtos e Insumos", icon="🍓")
                st.page_link("pages/15_Categorias.py", label="Categorias", icon="🏷️")
                st.page_link("pages/17_Secoes_Vitrine.py", label="Seções da Vitrine", icon="🖥️")

                if perfil == "Administrador":
                    st.write("")
                    st.markdown("**⚙️ CONFIGURAÇÕES**")
                    st.page_link("pages/07_Usuarios.py", label="Gerenciar Usuários", icon="🔑")

            elif perfil == "Entregador":
                st.markdown("**🛵 ÁREA DO ENTREGADOR**")
                st.page_link("pages/08_Entregas.py", label="Minha Rota", icon="🗺️")

            st.write("")
            st.divider()
            
            st.page_link("app.py", label="Ver Vitrine da Loja", icon="🌐")
            
            if st.button("🚪 Sair (Logout)", use_container_width=True):
                st.session_state.clear()
                st.switch_page("app.py")
        else:
            st.info("Faça login para acessar o painel restrito.")
            st.page_link("app.py", label="Voltar para a Loja", icon="🏠")
