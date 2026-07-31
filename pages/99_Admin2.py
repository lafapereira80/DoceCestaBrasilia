import streamlit as st
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

st.set_page_config(page_title="Painel Administrativo", page_icon="⚙️", layout="wide")
configurar_pagina()
menu_lateral()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b; }
.block-container { max-width: 1000px; padding-top: 2rem; padding-bottom: 4rem; }

.login-header { text-align: center; margin-top: 4vh; margin-bottom: 20px; }
.login-logo { font-size: 50px; margin-bottom: 10px; }
.login-title { font-size: 26px; font-weight: 800; color: #c5721f; margin-bottom: 5px; }
.login-subtitle { font-size: 14px; color: #775a46; font-weight: 500; }

div[data-testid="stForm"] { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 20px; padding: 30px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); }

.welcome-box { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.welcome-title { font-size: 28px; font-weight: 800; color: #c5721f; margin-bottom: 5px; }
.welcome-sub { font-size: 15px; color: #775a46; font-weight: 500; }

.section-title { font-size: 18px; font-weight: 800; color: #5a3b28; margin-top: 20px; margin-bottom: 15px; border-bottom: 2px dashed #f5eee6; padding-bottom: 8px; }

a[data-testid="stPageLink"] { background: #ffffff !important; border: 1px solid #e8ddd3 !important; border-radius: 14px !important; padding: 15px 20px !important; transition: all 0.2s ease !important; display: block !important; box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important; font-weight: 700 !important; color: #4a2e1b !important; }
a[data-testid="stPageLink"]:hover { border-color: #c5721f !important; transform: translateY(-3px) !important; box-shadow: 0 8px 15px rgba(197,114,31,0.1) !important; text-decoration: none !important; }
div[data-testid="stFormSubmitButton"] button { border-radius: 12px !important; font-weight: 800 !important; height: 45px !important; background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border: none !important;}
div[data-testid="stFormSubmitButton"] button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 15px rgba(19, 115, 51, 0.2) !important; }
</style>
""", unsafe_allow_html=True)

if "usuario" not in st.session_state or not st.session_state["usuario"]:
    st.markdown("""
    <div class="login-header">
        <div class="login-logo">🔒</div>
        <div class="login-title">Acesso Restrito</div>
        <div class="login-subtitle">Área de Gestão - Doce Cesta Brasília</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_esp1, col_login, col_esp2 = st.columns([1, 1.5, 1])
    with col_login:
        with st.form("form_login"):
            usuario_input = st.text_input("Login", placeholder="Digite seu usuário")
            senha_input = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            st.write("")
            submit_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit_login:
                if usuario_input and senha_input:
                    with st.spinner("Autenticando..."):
                        try:
                            res = supabase.table("usuarios").select("*").eq("login", usuario_input.strip()).eq("senha", senha_input.strip()).execute()
                            if res.data and len(res.data) > 0:
                                st.session_state["usuario"] = res.data[0]
                                st.rerun() 
                            else:
                                st.error("❌ Usuário ou senha incorretos.")
                        except Exception as e:
                            st.error("⚠️ Erro de conexão com o banco de dados. Tente novamente.")
                else:
                    st.warning("⚠️ Preencha usuário e senha para continuar.")
    st.stop()

from utils.permissao import administrador_operador
administrador_operador()
usuario = st.session_state.get("usuario", {})

st.markdown(f"""
<div class="welcome-box">
    <div class="welcome-title">Central de Comando</div>
    <div class="welcome-sub">Bem-vindo(a), <b>{usuario.get('login', 'Admin')}</b>. Selecione um módulo abaixo para começar.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📦 Operação & Atendimento</div>', unsafe_allow_html=True)
col1, col2, col3, col_pdv = st.columns(4)
with col1: st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="📋")
with col2: st.page_link("pages/19_Pedido_Manual.py", label="Venda Varejo (PDV)", icon="🛍️") # Botão recuperado!
with col3: st.page_link("pages/08_Entregas.py", label="Rotas de Entrega", icon="🛵")
with col_pdv: st.page_link("pages/03_Clientes.py", label="Base de Clientes", icon="👥")

st.markdown('<div class="section-title">📈 Estratégia & Finanças</div>', unsafe_allow_html=True)
col4, col5, col6 = st.columns(3)
with col4: st.page_link("pages/06_Financeiro.py", label="Painel Financeiro", icon="💰")
with col5: st.page_link("pages/18_Corporativo.py", label="Vendas B2B", icon="🏢")
with col6: st.page_link("pages/16_Previsao.py", label="Previsão de Produção", icon="📈")

st.markdown('<div class="section-title">🍓 Catálogo & Vitrine</div>', unsafe_allow_html=True)
col7, col8, col9, col10_vit = st.columns(4)
with col7: st.page_link("pages/04_Cestas.py", label="Cestas e Kits", icon="🧺")
with col8: st.page_link("pages/05_Produtos.py", label="Itens e Adicionais", icon="🍓")
with col9: st.page_link("pages/15_Categorias.py", label="Categorias", icon="🏷️")
with col10_vit: st.page_link("pages/17_Secoes_Vitrine.py", label="Seções da Vitrine", icon="🖥️")

if usuario.get("perfil") == "Administrador":
    st.markdown('<div class="section-title">⚙️ Configurações do Sistema</div>', unsafe_allow_html=True)
    col10, col11, col12 = st.columns(3)
    with col10: st.page_link("pages/07_Usuarios.py", label="Gerenciar Usuários", icon="🔑")
    with col11: st.page_link("app.py", label="Ver Loja Pública", icon="🌐")

st.write("")
st.divider()
st.caption("Doce Cesta Brasília © 2026 - Central Administrativa")
