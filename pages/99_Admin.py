import streamlit as st
from datetime import datetime
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS PREMIUM
# =====================================================
st.set_page_config(page_title="Painel Administrativo", page_icon="🔒", layout="wide")
configurar_pagina()

st.markdown(
"""
<style>
/* =========================================
   ESPAÇAMENTOS GERAIS
========================================== */
.block-container { padding-top: 2.5rem !important; padding-bottom: 4rem !important; max-width: 1200px; }
h1 { color: #4a2e1b !important; font-weight: 800 !important; font-size: 32px !important; margin-bottom: 0px !important; letter-spacing: -0.5px; }
.subtitle { color: #775a46; font-size: 16px; margin-bottom: 30px; font-weight: 500; }

/* =========================================
   TELA DE LOGIN REFINADA
========================================== */
.login-header {
    text-align: center;
    margin-bottom: 25px;
}
.login-logo-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #fdfbf9 0%, #f3ece6 100%);
    border: 1px solid #dfcdbb;
    border-radius: 24px;
    font-size: 40px;
    box-shadow: 0 8px 16px rgba(90, 59, 40, 0.08);
    margin-bottom: 15px;
}
.login-title {
    font-size: 26px;
    font-weight: 800;
    color: #4a2e1b;
    margin-bottom: 5px;
    letter-spacing: -0.5px;
}
.login-sub {
    font-size: 14px;
    color: #775a46;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.login-header) {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 24px !important;
    padding: 40px 30px !important;
    box-shadow: 0 12px 32px rgba(90, 59, 40, 0.06) !important;
    margin: 4vh auto;
}

/* =========================================
   CABEÇALHOS DAS SEÇÕES DO DASHBOARD
========================================== */
.section-header {
    font-size: 18px;
    font-weight: 800;
    color: #5a3b28;
    margin-top: 15px;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f3ece6;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* =========================================
   CARDS DO DASHBOARD (APP STYLE)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-content) {
    background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%);
    border: 1px solid #e8ddd3 !important;
    border-radius: 20px !important;
    padding: 20px 20px 10px 20px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-content):hover {
    border-color: #d2bfae !important;
    box-shadow: 0 10px 25px rgba(90, 59, 40, 0.08) !important;
    transform: translateY(-4px);
}

.card-content {
    display: flex;
    flex-direction: column;
    height: 140px; /* Garante alinhamento perfeito do grid */
}
.icon-box {
    width: 48px;
    height: 48px;
    background: #faf7f3;
    border: 1px solid #e8ddd3;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 15px;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04);
}
.c-title { font-size: 17px; font-weight: 800; color: #2c1e14; margin-bottom: 6px; letter-spacing: -0.3px; }
.c-desc { font-size: 13px; color: #666; line-height: 1.45; flex-grow: 1; }

/* =========================================
   BOTÕES DE LINK DAS PÁGINAS
========================================== */
div[data-testid="stPageLink"] { margin-top: 10px !important; margin-bottom: 0 !important; }
div[data-testid="stPageLink"] a { 
    background-color: #ffffff !important; 
    color: #5a3b28 !important; 
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important; 
    font-weight: 800 !important; 
    font-size: 14px !important; 
    padding: 12px 14px !important; 
    display: flex !important; 
    justify-content: center !important; 
    transition: all 0.2s ease !important; 
}
div[data-testid="stPageLink"] a:hover { 
    background-color: #5a3b28 !important; 
    color: #ffffff !important; 
    border-color: #5a3b28 !important;
}

/* =========================================
   RESPONSIVIDADE (CELULARES)
========================================== */
@media (max-width: 768px) {
    .block-container { padding: 1.5rem 1rem !important; }
    .card-content { height: auto; margin-bottom: 10px; } /* Libera altura no mobile */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.login-header) { padding: 30px 20px !important; }
    h1 { font-size: 26px !important; }
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
# TELA DE LOGIN PREMIUM
# =====================================================
if "usuario" not in st.session_state:
    
    col_vazia1, col_login, col_vazia2 = st.columns([1, 1.2, 1])
    
    with col_login:
        with st.container(border=True):
            st.markdown(
                """
                <div class="login-header">
                    <div class="login-logo-box">🎁</div>
                    <div class="login-title">Doce Cesta Brasília</div>
                    <div class="login-sub">Acesso restrito a colaboradores</div>
                </div>
                """, unsafe_allow_html=True
            )
            
            login = st.text_input("Usuário", placeholder="Digite seu login")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            
            st.write("")
            if st.button("🚪 Entrar no Sistema", use_container_width=True, type="primary"):
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
# CARREGA MENU, USUÁRIO E SAUDAÇÃO INTELIGENTE
# =====================================================
menu_lateral()
usuario = st.session_state.usuario
perfil = usuario.get("perfil", "Operador")

hora_atual = datetime.now().hour
if hora_atual < 12: saudacao = "Bom dia"
elif hora_atual < 18: saudacao = "Boa tarde"
else: saudacao = "Boa noite"

nome_formatado = str(usuario.get('login', 'Usuário')).capitalize()

st.markdown(f"<h1>👋 {saudacao}, {nome_formatado}!</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Painel de Controle • Perfil de acesso: <strong>{perfil}</strong></div>", unsafe_allow_html=True)


# =====================================================
# DASHBOARD DE ATALHOS (AGRUPADO E ORGANIZADO)
# =====================================================

# -----------------------------------------------------
# VISAO DO ENTREGADOR (Apenas Logística)
# -----------------------------------------------------
if perfil == "Entregador":
    st.markdown("<div class='section-header'>🛵 Logística e Roteirização</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="icon-box">🗺️</div>
                    <div class="c-title">Minhas Entregas</div>
                    <div class="c-desc">Acesse as rotas do dia, ative o GPS nativo e confirme as entregas realizadas na casa do cliente.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/08_Entregas.py", label="Abrir Rota de Entrega")

# -----------------------------------------------------
# VISÃO DO OPERADOR E ADMINISTRADOR
# -----------------------------------------------------
else:
    # --- GRUPO 1: OPERAÇÃO E LOGÍSTICA ---
    st.markdown("<div class='section-header'>🚀 Operação e Logística</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="icon-box">📦</div>
                    <div class="c-title">Gestão de Pedidos</div>
                    <div class="c-desc">Aprove pagamentos, acompanhe a fila de montagem e crie pedidos manuais (balcão/WhatsApp).</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/02_Pedidos.py", label="Acessar Pedidos")
            
    with c2:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="icon-box">📅</div>
                    <div class="c-title">Painel de Produção</div>
                    <div class="c-desc">Verifique o volume de montagem diário e imprima as fichas técnicas para a equipe.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/16_Previsao.py", label="Acessar Produção")

    with c3:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="icon-box">🛵</div>
                    <div class="c-title">Rotas e Despacho</div>
                    <div class="c-desc">Distribua os pedidos entre os motoboys e acompanhe as entregas em tempo real.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/08_Entregas.py", label="Monitorar Entregas")


    # --- GRUPO 2: CATÁLOGO E VENDAS ---
    st.write("")
    st.markdown("<div class='section-header'>🛍️ Catálogo e Vendas</div>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    
    with c4:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="icon-box">👥</div>
                    <div class="c-title">Base de Clientes</div>
                    <div class="c-desc">Consulte o histórico completo de compras, dados de contato e o LTV de cada cliente.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/03_Clientes.py", label="Acessar Clientes")
            
    with c5:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="icon-box">🎁</div>
                    <div class="c-title">Cestas e Vitrine</div>
                    <div class="c-desc">Crie novas cestas, edite preços e defina a ordem em que elas aparecem para o cliente.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/04_Cestas.py", label="Montar Cestas")

    with c6:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="icon-box">🛒</div>
                    <div class="c-title">Produtos & Extras</div>
                    <div class="c-desc">Gerencie o estoque interno, adicione chocolates, bebidas e itens adicionais avulsos.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/05_Produtos.py", label="Estoque de Itens")


    # --- GRUPO 3: EXCLUSIVA ADMINISTRADOR ---
    if perfil == "Administrador":
        st.write("")
        st.markdown("<div class='section-header'>⚙️ Gestão Avançada (Administrador)</div>", unsafe_allow_html=True)
        c7, c8, c9 = st.columns(3)
        
        with c7:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="card-content">
                        <div class="icon-box">💰</div>
                        <div class="c-title">Visão Financeira</div>
                        <div class="c-desc">Acompanhe faturamento bruto, relatórios detalhados e saúde financeira do negócio.</div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.page_link("pages/06_Financeiro.py", label="Painel Financeiro")
                
        with c8:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="card-content">
                        <div class="icon-box">🔐</div>
                        <div class="c-title">Equipe e Usuários</div>
                        <div class="c-desc">Cadastre novos operadores, motoboys e limite o que cada pessoa pode ver e fazer.</div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.page_link("pages/07_Usuarios.py", label="Controle de Acessos")
        
        with c9:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="card-content">
                        <div class="icon-box">📂</div>
                        <div class="c-title">Estrutura (Categorias)</div>
                        <div class="c-desc">Organize o sistema criando categorias de produtos (ex: Frios, Bebidas Quentes, Frutas).</div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.page_link("pages/15_Categorias.py", label="Gerir Categorias")
