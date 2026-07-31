import streamlit as st
from pathlib import Path

try:
    from utils.formatacao import NOME_LOJA_CURTO
except ImportError:
    NOME_LOJA_CURTO = "Doce Cesta"

def configurar_pagina():
    css_path = Path("assets/style.css")
    css_extra = ""
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_extra = f.read()
            
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
        
        html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif !important; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployMenu {{display: none;}}
        [data-testid="stSidebarNav"] {{display: none !important;}}
        {css_extra}
        </style>
        """,
        unsafe_allow_html=True
    )

def menu_lateral():
    usuario = st.session_state.get("usuario")

    with st.sidebar:
        html_branding = f"""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 25px;">
            <div style="position: relative; z-index: 2; margin-bottom: -22px;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: linear-gradient(135deg, #c5721f 0%, #a65d14 100%); border-radius: 50%; border: 4px solid #ffffff; color: white; font-size: 20px; box-shadow: 0 4px 10px rgba(197, 114, 31, 0.25);">🧺</div>
            </div>
            <div style="background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 32px 15px 15px 15px; position: relative; z-index: 1; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                <h2 style="color: #4a2e1b; font-family: 'Dancing Script', cursive !important; font-size: 34px; font-weight: 700; margin: 0; line-height: 1.1;">{NOME_LOJA_CURTO}</h2>
                <div style="color: #c5721f; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px;">Painel de Gestão</div>
            </div>
        </div>
        """
        st.markdown(html_branding, unsafe_allow_html=True)

        if usuario:
            perfil = usuario.get("perfil", "Usuário")
            login = usuario.get("login", "Admin")
            
            html_cracha = f"""
            <div style="background: #ffffff; border: 1px solid #e8ddd3; padding: 12px 15px; border-radius: 14px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 12px;">
                <div style="background: linear-gradient(135deg, #fef7e0 0%, #fffbf7 100%); border: 1px solid #fce8b2; color: #b06000; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">🧑‍💻</div>
                <div>
                    <div style="color: #2c1e14; font-size: 14px; font-weight: 800; line-height: 1.2;">{login}</div>
                    <div style="color: #137333; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;">{perfil}</div>
                </div>
            </div>
            """
            st.markdown(html_cracha, unsafe_allow_html=True)

            if perfil in ["Administrador", "Operador"]:
                st.markdown("**📦 OPERAÇÃO & VENDAS**")
                st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="📋")
                st.page_link("pages/19_Pedido_Manual.py", label="Venda Varejo (PDV)", icon="🛍️") # Botão recuperado!
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
