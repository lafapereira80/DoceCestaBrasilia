import streamlit as st
import pandas as pd
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador
from datetime import datetime

st.set_page_config(page_title="Gestão de Pedidos", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# ==========================================
# CSS PREMIUM (KANBAN E CARDS)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b; }

.header-banner {
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 25px;
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
    text-align: center; margin-bottom: 25px;
}
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px; font-weight: 700; color: #c5721f; margin: 0; }
.header-sub { font-size: 14px; font-weight: 600; color: #775a46; }

.kanban-title { font-weight: 800; color: #5a3b28; margin-bottom: 15px; text-align: center; font-size: 15px; border-bottom: 2px dashed #e8ddd3; padding-bottom: 10px;}

.pedido-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 12px;
    padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    transition: transform 0.2s; border-left: 4px solid #c5721f;
}
.pedido-card:hover { transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.08); }
.pedido-card.b2b { border-left-color: #137333; }

.badge-b2b { background: #e6f4ea; color: #137333; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 10px; display: inline-block; margin-bottom: 5px; }
.badge-b2c { background: #fef7e0; color: #b06000; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 10px; display: inline-block; margin-bottom: 5px; }

.p-title { font-size: 14px; font-weight: 800; color: #2c1e14; margin-bottom: 3px;}
.p-info { font-size: 12px; color: #666; margin-bottom: 2px;}

div[data-testid="stButton"] button { border-radius: 8px !important; font-weight: 700 !important; font-size: 12px !important; padding: 2px 10px !important; height: auto !important;}
</style>
""", unsafe_allow_html=True)

# Cabeçalho com o botão de Criar Pedido Manual de volta
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <div class="header-banner" style="text-align: left; margin-bottom: 0;">
        <h1 class="header-title">Gestão de Pedidos</h1>
        <p class="header-sub">Acompanhe o fluxo completo de Varejo e Corporativo 📋</p>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("➕ Criar Pedido Manual", use_container_width=True, type="primary"):
        st.switch_page("pages/18_Corporativo.py") # Ou para a página de cadastro manual se houver outra

st.write("")

# Função para atualizar status rápido
def mudar_status(p_id, novo_status):
    supabase.table("pedidos").update({"status": novo_status}).eq("id", p_id).execute()
    st.rerun()

# Carrega Pedidos
@st.cache_data(ttl=5, show_spinner=False)
def get_pedidos():
    res = supabase.table("pedidos").select("*").order("created_at", desc=True).execute()
    return res.data or []

pedidos = get_pedidos()

# Filtro rápido
tipo_filtro = st.radio("Filtrar por:", ["Todos os Pedidos", "Varejo (B2C)", "Empresas (B2B)"], horizontal=True)

st.markdown("<hr style='border-top: 1px solid #e8ddd3; margin: 15px 0;'>", unsafe_allow_html=True)

# KANBAN BOARD COM OS 4 STATUS ORIGINAIS + DESISTÊNCIA
col_rec, col_pag, col_prod, col_ent = st.columns(4)

def renderizar_card(p, coluna):
    is_b2b = "[B2B]" in p['cliente_nome']
    nome_exibicao = p['cliente_nome'].replace("[B2B]", "").strip()
    badge = "<div class='badge-b2b'>🏢 CORPORATIVO</div>" if is_b2b else "<div class='badge-b2c'>👤 VAREJO</div>"
    css_class = "pedido-card b2b" if is_b2b else "pedido-card"
    
    dt_entrega = "A confirmar"
    if p.get('data_entrega'):
        try: dt_entrega = datetime.strptime(p['data_entrega'], "%Y-%m-%d").strftime("%d/%m")
        except: dt_entrega = p['data_entrega']
    
    status_atual = p.get('status', 'Recebido')
    
    with coluna:
        st.markdown(f"""
        <div class="{css_class}">
            {badge}
            <div class="p-title">{nome_exibicao}</div>
            <div class="p-info">📦 <b>Produto:</b> {p.get('cesta_nome', 'Misto')}</div>
            <div class="p-info">📅 <b>Entrega:</b> {dt_entrega}</div>
            <div class="p-info">💳 <b>Status:</b> <i>{status_atual}</i></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de Ação por Card
        if st.button("🔍 Detalhes", key=f"det_{p['id']}", use_container_width=True):
            st.session_state['pedido_detalhe_id'] = p['id']
            st.switch_page("pages/09_Detalhes_Pedido.py")
            
        c_av, c_des = st.columns(2)
        with c_av:
            if status_atual in ["Recebido", "Pendente"]:
                if st.button("Pagar", key=f"pg_{p['id']}", use_container_width=True): mudar_status(p['id'], "Pago")
            elif status_atual == "Pago":
                if st.button("Produzir", key=f"pr_{p['id']}", use_container_width=True): mudar_status(p['id'], "Em Produção")
            elif status_atual == "Em Produção":
                if st.button("Entregar", key=f"et_{p['id']}", use_container_width=True): mudar_status(p['id'], "Entregue")
        with c_des:
            if status_atual != "Desistência":
                if st.button("❌", key=f"des_{p['id']}", help="Marcar como Desistência", use_container_width=True): mudar_status(p['id'], "Desistência")

# Títulos das Colunas
with col_rec: st.markdown("<div class='kanban-title'>📥 Recebidos</div>", unsafe_allow_html=True)
with col_pag: st.markdown("<div class='kanban-title'>💳 Pagos</div>", unsafe_allow_html=True)
with col_prod: st.markdown("<div class='kanban-title'>🍳 Em Produção / Entregues</div>", unsafe_allow_html=True)
with col_ent: st.markdown("<div class='kanban-title'>⚠️ Desistência</div>", unsafe_allow_html=True)

# Distribuição dos Pedidos nas Colunas
for p in pedidos:
    is_b2b = "[B2B]" in p['cliente_nome']
    if tipo_filtro == "Varejo (B2C)" and is_b2b: continue
    if tipo_filtro == "Empresas (B2B)" and not is_b2b: continue
    
    status = p.get("status", "Recebido")
    
    if status in ["Recebido", "Pendente"]: renderizar_card(p, col_rec)
    elif status == "Pago": renderizar_card(p, col_pag)
    elif status in ["Em Produção", "Em Rota de Entrega", "Entregue"]: renderizar_card(p, col_prod)
    elif status == "Desistência": renderizar_card(p, col_ent)
