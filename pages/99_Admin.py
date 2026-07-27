import streamlit as st
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS PREMIUM
# =====================================================
st.set_page_config(page_title="Administração", page_icon="🔒", layout="wide")
configurar_pagina()

st.markdown(
"""
<style>
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1100px; }
h1, h2, h3 { color: #5a3b28 !important; font-weight: 800 !important; }
.subtitle { color: #775a46; font-size: 15px; margin-bottom: 30px; }

/* Centralizador de Login */
.login-container { max-width: 400px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 16px; border: 1px solid #dfcdbb; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.08); text-align: center; }
.login-logo { font-size: 40px; margin-bottom: 10px; }
.login-title { font-size: 22px; font-weight: 800; color: #5a3b28; margin-bottom: 20px; }

/* Grid do Dashboard */
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 14px !important; padding: 16px !important; margin-bottom: 12px !important; box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04); transition: all 0.2s ease; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #c9b19c !important; transform: translateY(-3px); box-shadow: 0 6px 12px rgba(90, 59, 40, 0.1); }

.card-icon { font-size: 28px; margin-bottom: 8px; }
.card-title { font-size: 16px; font-weight: 800; color: #333; margin-bottom: 4px; }
.card-desc { font-size: 12px; color: #666; line-height: 1.4; margin-bottom: 16px; flex-grow: 1; }

div[data-testid="stPageLink"] > a { background-color: #f3ece6 !important; color: #5a3b28 !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 13px !important; padding: 10px !important; justify-content: center !important; transition: all 0.2s ease; border: 1px solid #dfcdbb !important; }
div[data-testid="stPageLink"] > a:hover { background-color: #5a3b28 !important; color: #ffffff !important; border-color: #5a3b28 !important; }

/* Botões Nativos */
div[data-testid="stButton"] button { border-radius: 8px !important; font-weight: 700 !important; }

@media (max-width: 768px) {
    .block-container { padding-top: 1rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    .login-container { padding: 20px; }
}
</style>
""",
unsafe_allow_html=True
)

# =====================================================
# ROTINA DE LOGOUT (SEGURO)
# =====================================================
if st.session_state.get("fazer_logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# =====================================================
# TELA DE LOGIN
# =====================================================
if "usuario" not in st.session_state:
    st.markdown("<div style='margin-top: 5vh;'></div>", unsafe_allow_html=True)
    
    col_l1, col_login, col_l3 = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown(
            """
            <div class="login-container">
                <div class="login-logo">🎁</div>
                <div class="login-title">Doce Cesta Brasília</div>
            </div>
            """, unsafe_allow_html=True
        )
        
        with st.container(border=True):
            st.write("🔒 **Acesso Restrito**")
            login = st.text_input("Usuário", placeholder="Digite seu login")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            
            st.write("")
            if st.button("Entrar no Sistema", use_container_width=True, type="primary"):
                if login and senha:
                    try:
                        res = supabase.table("usuarios").select("*").eq("login", login).eq("senha", senha).execute()
                        if res.data and len(res.data) > 0:
                            st.session_state["usuario"] = res.data[0]
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha incorretos.")
                    except Exception as e:
                        st.error("❌ Erro ao conectar ao banco de dados.")
                else:
                    st.warning("⚠️ Preencha usuário e senha.")
                    
    st.stop()


# =====================================================
# CARREGA MENU E DADOS DO USUÁRIO
# =====================================================
menu_lateral()
usuario = st.session_state.usuario
perfil = usuario.get("perfil", "Operador")

st.markdown(f"<h1>👋 Olá, {usuario.get('login', 'Usuário')}!</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Bem-vindo ao Painel de Controle ({perfil}). O que vamos fazer hoje?</div>", unsafe_allow_html=True)


# =====================================================
# DASHBOARD DE ATALHOS (BASEADO NO PERFIL)
# =====================================================

# -----------------------------------------------------
# VISAO DO ENTREGADOR (Apenas Logística)
# -----------------------------------------------------
if perfil == "Entregador":
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        with st.container(border=True):
            st.markdown('<div class="card-icon">🛵</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Minhas Entregas</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-desc">Acesse suas rotas, utilize o GPS e confirme as entregas realizadas.</div>', unsafe_allow_html=True)
            st.page_link("pages/08_Entregas.py", label="Abrir Rota", use_container_width=True)

# -----------------------------------------------------
# VISÃO DO OPERADOR E ADMINISTRADOR (Completo)
# -----------------------------------------------------
else:
    # Primeira Linha - Atendimento e Logística
    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.container(border=True):
            st.markdown('<div class="card-icon">📦</div><div class="card-title">Pedidos</div><div class="card-desc">Gerencie novos pedidos, aprove pagamentos e crie pedidos manuais.</div>', unsafe_allow_html=True)
            st.page_link("pages/02_Pedidos.py", label="Acessar Pedidos")
            
    with c2:
        with st.container(border=True):
            st.markdown('<div class="card-icon">🛵</div><div class="card-title">Rotas de Entrega</div><div class="card-desc">Painel logístico para visualização e acompanhamento dos Entregadores.</div>', unsafe_allow_html=True)
            st.page_link("pages/08_Entregas.py", label="Monitorar Entregas")

    with c3:
        with st.container(border=True):
            st.markdown('<div class="card-icon">👥</div><div class="card-title">Clientes</div><div class="card-desc">Veja o histórico de compras, LTV e o ranking dos seus melhores clientes.</div>', unsafe_allow_html=True)
            st.page_link("pages/03_Clientes.py", label="Base de Clientes")

    # Segunda Linha - Catálogo
    st.write("")
    c4, c5, c6 = st.columns(3)
    
    with c4:
        with st.container(border=True):
            st.markdown('<div class="card-icon">🧺</div><div class="card-title">Cestas base</div><div class="card-desc">Crie e edite as cestas principais que serão exibidas na vitrine da loja.</div>', unsafe_allow_html=True)
            st.page_link("pages/04_Cestas.py", label="Montar Cestas")
            
    with c5:
        with st.container(border=True):
            st.markdown('<div class="card-icon">🍫</div><div class="card-title">Produtos / Complementos</div><div class="card-desc">Estoque de produtos internos e itens adicionais (como Polaroid e Canecas).</div>', unsafe_allow_html=True)
            st.page_link("pages/05_Produtos.py", label="Estoque de Itens")

    with c6:
        with st.container(border=True):
            st.markdown('<div class="card-icon">📂</div><div class="card-title">Categorias</div><div class="card-desc">Organize as categorias para estruturar perfeitamente o seu catálogo.</div>', unsafe_allow_html=True)
            st.page_link("pages/15_Categorias.py", label="Gerir Categorias")

    # Terceira Linha - Apenas para Administradores (Financeiro e Permissões)
    if perfil == "Administrador":
        st.write("")
        st.markdown("### ⚙️ Gestão Avançada")
        c7, c8, c9 = st.columns(3)
        
        with c7:
            with st.container(border=True):
                st.markdown('<div class="card-icon">💰</div><div class="card-title">Financeiro</div><div class="card-desc">Relatórios detalhados, faturamento mensal e balanço geral da empresa.</div>', unsafe_allow_html=True)
                st.page_link("pages/06_Financeiro.py", label="Painel Financeiro")
                
        with c8:
            with st.container(border=True):
                st.markdown('<div class="card-icon">🔐</div><div class="card-title">Usuários</div><div class="card-desc">Cadastre novos operadores ou entregadores e gerencie senhas de acesso.</div>', unsafe_allow_html=True)
                st.page_link("pages/07_Usuarios.py", label="Controle de Acessos")
        
        with c9:
            # Coluna vazia para alinhar o grid bonitinho
            st.empty()
