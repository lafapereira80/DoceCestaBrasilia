import streamlit as st
from datetime import datetime
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS PREMIUM (SEGURO)
# =====================================================
st.set_page_config(page_title="Administração", page_icon="🔒", layout="wide")
configurar_pagina()

st.markdown(
"""
<style>
/* =========================================
   ESPAÇAMENTOS GERAIS
========================================== */
.block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1150px; }
h1, h2, h3 { color: #5a3b28 !important; font-weight: 800 !important; margin-bottom: 0px !important; }
.subtitle { color: #775a46; font-size: 16px; margin-bottom: 35px; font-weight: 500; }

/* =========================================
   TELA DE LOGIN CENTRALIZADA
========================================== */
.login-box { 
    background: #ffffff; padding: 40px; border-radius: 20px; 
    border: 1px solid #dfcdbb; box-shadow: 0 12px 32px rgba(90, 59, 40, 0.08); 
    text-align: center; margin: 5vh auto;
}
.login-logo { font-size: 54px; margin-bottom: 5px; line-height: 1; }
.login-title { font-size: 24px; font-weight: 800; color: #5a3b28; margin-bottom: 25px; }

/* =========================================
   DASHBOARD: ESTILO INTERNO DOS CARTÕES
========================================== */
/* Efeito de destaque suave nos contêineres do Streamlit */
div[data-testid="stVerticalBlockBorderWrapper"] {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    border-radius: 14px !important;
    border-color: #e8ddd3 !important;
    background-color: #ffffff;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #c9b19c !important;
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08) !important;
    transform: translateY(-3px);
}

/* Conteúdo flexível dentro do cartão para manter alinhamento */
.card-content {
    display: flex;
    flex-direction: column;
    height: 125px; /* Altura fixa garante que o grid não quebre */
}
.c-icon { font-size: 34px; margin-bottom: 10px; line-height: 1; }
.c-title { font-size: 16px; font-weight: 800; color: #333; margin-bottom: 6px; }
.c-desc { font-size: 13px; color: #666; line-height: 1.4; flex-grow: 1; }

/* =========================================
   BOTÕES DE AÇÃO DOS CARTÕES
========================================== */
div[data-testid="stPageLink"] { margin-top: 8px !important; margin-bottom: 0 !important; }
div[data-testid="stPageLink"] a { 
    background-color: #f3ece6 !important; color: #5a3b28 !important; 
    border-radius: 10px !important; font-weight: 700 !important; font-size: 14px !important; 
    padding: 10px 14px !important; display: flex !important; justify-content: center !important; 
    transition: all 0.2s ease !important; border: 1px solid transparent !important;
}
div[data-testid="stPageLink"] a:hover { 
    background-color: #5a3b28 !important; color: #ffffff !important; 
    transform: translateY(-2px); box-shadow: 0 4px 10px rgba(90,59,40,0.2);
}

/* =========================================
   RESPONSIVIDADE (CELULARES)
========================================== */
@media (max-width: 768px) {
    .block-container { padding: 1.5rem 1rem !important; }
    .card-content { height: auto; margin-bottom: 12px; } /* Libera a altura no mobile */
    .login-box { padding: 30px 20px; }
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
# TELA DE LOGIN BLINDADA
# =====================================================
if "usuario" not in st.session_state:
    
    col_vazia1, col_login, col_vazia2 = st.columns([1, 1.2, 1])
    
    with col_login:
        st.markdown(
            """
            <div class="login-box">
                <div class="login-logo">🎁</div>
                <div class="login-title">Doce Cesta Brasília</div>
            </div>
            """, unsafe_allow_html=True
        )
        
        with st.container(border=True):
            st.markdown("<div style='text-align: center; color: #775a46; font-weight: 700; margin-bottom: 15px;'>🔒 ACESSO RESTRITO</div>", unsafe_allow_html=True)
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
            st.markdown(
                """
                <div class="card-content">
                    <div class="c-icon">🛵</div>
                    <div class="c-title">Minhas Entregas</div>
                    <div class="c-desc">Acesse suas rotas, utilize o GPS e confirme as entregas realizadas.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/08_Entregas.py", label="Abrir Rota de Entrega")

# -----------------------------------------------------
# VISÃO DO OPERADOR E ADMINISTRADOR (Completo)
# -----------------------------------------------------
else:
    # --- PRIMEIRA LINHA: ATENDIMENTO E LOGÍSTICA ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="c-icon">📦</div>
                    <div class="c-title">Gestão de Pedidos</div>
                    <div class="c-desc">Administre as vendas, aprove pagamentos e crie pedidos manuais (WhatsApp).</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/02_Pedidos.py", label="Acessar Pedidos")
            
    with c2:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="c-icon">🛵</div>
                    <div class="c-title">Rotas de Entrega</div>
                    <div class="c-desc">Painel logístico em tempo real para visualização e acompanhamento de entregas.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/08_Entregas.py", label="Monitorar Entregas")

    with c3:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="c-icon">👥</div>
                    <div class="c-title">Base de Clientes</div>
                    <div class="c-desc">Veja o histórico de compras, LTV e o ranking dos seus melhores clientes.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/03_Clientes.py", label="Acessar Clientes")


    # --- SEGUNDA LINHA: CATÁLOGO ---
    st.write("")
    c4, c5, c6 = st.columns(3)
    
    with c4:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="c-icon">🧺</div>
                    <div class="c-title">Cestas Base</div>
                    <div class="c-desc">Crie e edite as cestas e pacotes principais exibidos na vitrine da loja.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/04_Cestas.py", label="Montar Cestas")
            
    with c5:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="c-icon">🍫</div>
                    <div class="c-title">Produtos & Extras</div>
                    <div class="c-desc">Estoque de produtos internos, chocolates, vinhos e itens de adicionais.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/05_Produtos.py", label="Estoque de Itens")

    with c6:
        with st.container(border=True):
            st.markdown(
                """
                <div class="card-content">
                    <div class="c-icon">📂</div>
                    <div class="c-title">Categorias</div>
                    <div class="c-desc">Estruture e organize perfeitamente os produtos dentro do seu catálogo.</div>
                </div>
                """, unsafe_allow_html=True
            )
            st.page_link("pages/15_Categorias.py", label="Gerir Categorias")


    # --- TERCEIRA LINHA: EXCLUSIVA ADMINISTRADOR ---
    if perfil == "Administrador":
        st.write("")
        st.markdown("### ⚙️ Gestão Avançada")
        c7, c8, c9 = st.columns(3)
        
        with c7:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="card-content">
                        <div class="c-icon">💰</div>
                        <div class="c-title">Financeiro</div>
                        <div class="c-desc">Relatórios detalhados, faturamento e balanço da empresa.</div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.page_link("pages/06_Financeiro.py", label="Painel Financeiro")
                
        with c8:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="card-content">
                        <div class="c-icon">🔐</div>
                        <div class="c-title">Usuários</div>
                        <div class="c-desc">Cadastre operadores, entregadores e controle acessos.</div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.page_link("pages/07_Usuarios.py", label="Controle de Acessos")
        
        with c9:
            st.empty() # Mantém o grid alinhado vazio
