import streamlit as st
import pandas as pd
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

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

.kanban-col { background: #fdfbf8; border-radius: 12px; padding: 15px; border: 1px solid #e8ddd3; height: 100%; }
.kanban-title { font-weight: 800; color: #5a3b28; margin-bottom: 15px; text-align: center; font-size: 16px; border-bottom: 2px dashed #e8ddd3; padding-bottom: 10px;}

.pedido-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 12px;
    padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    transition: transform 0.2s; border-left: 4px solid #c5721f;
}
.pedido-card:hover { transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.08); }
.pedido-card.b2b { border-left-color: #137333; } /* Verde para B2B */

.badge-b2b { background: #e6f4ea; color: #137333; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 10px; display: inline-block; margin-bottom: 5px; }
.badge-b2c { background: #fef7e0; color: #b06000; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 10px; display: inline-block; margin-bottom: 5px; }

.p-title { font-size: 14px; font-weight: 800; color: #2c1e14; margin-bottom: 3px;}
.p-info { font-size: 12px; color: #666; margin-bottom: 2px;}

div[data-testid="stButton"] button { border-radius: 8px !important; font-weight: 700 !important; font-size: 12px !important; padding: 2px 10px !important; height: auto !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Mural de Produção</h1>
    <p class="header-sub">Acompanhe e gerencie todos os pedidos (Varejo e Corporativo) 📋</p>
</div>
""", unsafe_allow_html=True)

# Função para atualizar status rápido
def mudar_status(p_id, novo_status):
    supabase.table("pedidos").update({"status": novo_status}).eq("id", p_id).execute()
    st.rerun()

# Carrega Pedidos
@st.cache_data(ttl=10, show_spinner=False)
def get_pedidos():
    res = supabase.table("pedidos").select("*").order("created_at", desc=True).execute()
    return res.data or []

pedidos = get_pedidos()

# Filtro rápido
tipo_filtro = st.radio("Filtrar por:", ["Todos os Pedidos", "Varejo (B2C)", "Empresas (B2B)"], horizontal=True)

# KANBAN BOARD
col_pend, col_prod, col_rota = st.columns(3)

def renderizar_card(p, coluna):
    is_b2b = "[B2B]" in p['cliente_nome']
    nome_exibicao = p['cliente_nome'].replace("[B2B]", "").strip()
    badge = "<div class='badge-b2b'>🏢 CORPORATIVO</div>" if is_b2b else "<div class='badge-b2c'>👤 VAREJO</div>"
    css_class = "pedido-card b2b" if is_b2b else "pedido-card"
    
    # Formata a data de entrega
    dt_entrega = "A confirmar"
    if p.get('data_entrega'):
        try: dt_entrega = datetime.strptime(p['data_entrega'], "%Y-%m-%d").strftime("%d/%m")
        except: dt_entrega = p['data_entrega']
    
    with coluna:
        st.markdown(f"""
        <div class="{css_class}">
            {badge}
            <div class="p-title">{nome_exibicao}</div>
            <div class="p-info">📦 <b>Produto:</b> {p.get('cesta_nome', 'Misto')}</div>
            <div class="p-info">📅 <b>Entrega:</b> {dt_entrega} ({p.get('periodo_entrega', '')})</div>
        </div>
        """, unsafe_allow_html=True)
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("Ver Detalhes", key=f"det_{p['id']}", use_container_width=True):
                st.session_state['pedido_detalhe_id'] = p['id']
                st.switch_page("pages/09_Detalhes_Pedidos.py")
        with c_btn2:
            if p['status'] in ["Pendente", "Pago"]:
                if st.button("⏩ Produção", key=f"av_{p['id']}", type="primary", use_container_width=True): mudar_status(p['id'], "Em Produção")
            elif p['status'] == "Em Produção":
                if st.button("⏩ Rota", key=f"av_{p['id']}", type="primary", use_container_width=True): mudar_status(p['id'], "Em Rota de Entrega")
            elif p['status'] == "Em Rota de Entrega":
                if st.button("✅ Entregue", key=f"av_{p['id']}", type="primary", use_container_width=True): mudar_status(p['id'], "Entregue")

# Distribui os pedidos nas colunas
with col_pend: st.markdown("<div class='kanban-title'>🔴 Novos / Pendentes</div>", unsafe_allow_html=True)
with col_prod: st.markdown("<div class='kanban-title'>🟡 Em Produção</div>", unsafe_allow_html=True)
with col_rota: st.markdown("<div class='kanban-title'>🔵 Na Rota / Finalizados</div>", unsafe_allow_html=True)

for p in pedidos:
    # Aplica o filtro B2B/B2C
    is_b2b = "[B2B]" in p['cliente_nome']
    if tipo_filtro == "Varejo (B2C)" and is_b2b: continue
    if tipo_filtro == "Empresas (B2B)" and not is_b2b: continue
    
    status = p.get("status", "")
    if status in ["Pendente", "Pago"]: renderizar_card(p, col_pend)
    elif status == "Em Produção": renderizar_card(p, col_prod)
    elif status in ["Em Rota de Entrega", "Entregue"]: renderizar_card(p, col_rota)
