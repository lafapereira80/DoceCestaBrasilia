import streamlit as st

def configurar_pagina():
    """Oculta elementos padrão do Streamlit e aplica estilos globais"""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
        
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployMenu {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )

def menu_lateral():
    """Gera o menu lateral dinâmico baseado no perfil do usuário"""
    usuario = st.session_state.get("usuario")

    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #c5721f; font-weight: 800;'>Doce Cesta</h2>", unsafe_allow_html=True)
        st.divider()

        if usuario:
            perfil = usuario.get("perfil")
            st.caption(f"👤 Olá, **{usuario.get('login')}** ({perfil})")
            st.write("")

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
