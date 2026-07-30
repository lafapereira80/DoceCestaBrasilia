import streamlit as st
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Painel Administrativo", page_icon="⚙️", layout="wide")
configurar_pagina()
menu_lateral()

# Apenas Admins e Operadores podem ver esta página
administrador_operador()
usuario = st.session_state.get("usuario", {})

# =====================================================
# CSS PREMIUM
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b; }
.block-container { max-width: 1000px; padding-top: 2rem; padding-bottom: 4rem; }

.welcome-box {
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%);
    border: 1px solid #e8ddd3; border-radius: 20px; padding: 30px;
    text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.04);
}
.welcome-title { font-size: 28px; font-weight: 800; color: #c5721f; margin-bottom: 5px; }
.welcome-sub { font-size: 15px; color: #775a46; font-weight: 500; }

.section-title { font-size: 18px; font-weight: 800; color: #5a3b28; margin-top: 20px; margin-bottom: 15px; border-bottom: 2px dashed #f5eee6; padding-bottom: 8px; }

/* Botões do Menu Grid */
div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button {
    height: 70px !important; border-radius: 14px !important; font-weight: 700 !important;
    font-size: 15px !important; border: 1px solid #e8ddd3 !important; background: #ffffff !important;
    transition: all 0.2s ease; display: flex; justify-content: flex-start; padding-left: 20px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
}
div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button:hover {
    border-color: #c5721f !important; transform: translateY(-3px) !important; box-shadow: 0 8px 15px rgba(197,114,31,0.1) !important;
}

/* Links nativos (page_link) */
a[data-testid="stPageLink"] {
    background: #ffffff !important; border: 1px solid #e8ddd3 !important; border-radius: 14px !important;
    padding: 15px 20px !important; transition: all 0.2s ease !important; display: block !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important; font-weight: 700 !important; color: #4a2e1b !important;
}
a[data-testid="stPageLink"]:hover {
    border-color: #c5721f !important; transform: translateY(-3px) !important; box-shadow: 0 8px 15px rgba(197,114,31,0.1) !important; text-decoration: none !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CABEÇALHO
# =====================================================
st.markdown(f"""
<div class="welcome-box">
    <div class="welcome-title">Central de Comando</div>
    <div class="welcome-sub">Bem-vindo(a), <b>{usuario.get('login', 'Admin')}</b>. Selecione um módulo abaixo para começar.</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# GRID DE MÓDULOS
# =====================================================

st.markdown('<div class="section-title">📦 Operação & Atendimento</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1: st.page_link("pages/02_Pedidos.py", label="Gestão de Pedidos", icon="📋")
with col2: st.page_link("pages/08_Entregas.py", label="Rotas de Entrega", icon="🛵")
with col3: st.page_link("pages/03_Clientes.py", label="Base de Clientes", icon="👥")

st.markdown('<div class="section-title">📈 Estratégia & Finanças</div>', unsafe_allow_html=True)
col4, col5, col6 = st.columns(3)
with col4: st.page_link("pages/06_Financeiro.py", label="Painel Financeiro", icon="💰")
with col5: st.page_link("pages/18_Corporativo.py", label="Vendas Corporativas B2B", icon="🏢")
with col6: st.page_link("pages/16_Previsao.py", label="Previsão de Produção", icon="📈")

st.markdown('<div class="section-title">🍓 Catálogo & Vitrine</div>', unsafe_allow_html=True)
col7, col8, col9 = st.columns(3)
with col7: st.page_link("pages/04_Cestas.py", label="Cestas e Kits", icon="🧺")
with col8: st.page_link("pages/05_Produtos.py", label="Itens e Adicionais", icon="🍓")
with col9: st.page_link("pages/17_Secoes_Vitrine.py", label="Seções da Vitrine", icon="🖥️")

if usuario.get("perfil") == "Administrador":
    st.markdown('<div class="section-title">⚙️ Configurações do Sistema</div>', unsafe_allow_html=True)
    col10, col11, col12 = st.columns(3)
    with col10: st.page_link("pages/15_Categorias.py", label="Categorias", icon="🏷️")
    with col11: st.page_link("pages/07_Usuarios.py", label="Usuários do Sistema", icon="🔑")
    with col12: st.page_link("app.py", label="Ver Loja Pública", icon="🌐")

st.write("")
st.divider()
st.caption("Doce Cesta Brasília © 2026 - Central Administrativa")
