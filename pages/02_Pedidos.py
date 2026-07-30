import streamlit as st
import pandas as pd
from datetime import datetime
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

st.set_page_config(page_title="Gestão de Pedidos", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# ==========================================
# CSS PREMIUM (ABAS, CARDS E BOTÕES DISCRETOS)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b; }

.header-banner {
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 25px 20px;
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
    margin-bottom: 20px; text-align: center;
}
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px; font-weight: 700; color: #c5721f; margin: 0; line-height: 1.1; }
.header-sub { font-size: 14px; font-weight: 600; color: #775a46; margin-top: 5px;}

/* ESTILIZAÇÃO DAS ABAS */
.stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; background-color: #faf7f3; padding: 10px; border-radius: 16px; border: 1px solid #e8ddd3;}
.stTabs [data-baseweb="tab"] { height: 45px; background-color: #ffffff; border-radius: 12px; font-weight: 700; color: #775a46; border: 1px solid #e8ddd3; padding: 0 20px; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #c5721f 0%, #a65d14) !important; color: white !important; border: none !important; box-shadow: 0 4px 12px rgba(197, 114, 31, 0.2); }

/* CARDS DE PEDIDOS */
.pedido-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 14px;
    padding: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.03);
    transition: transform 0.2s, box-shadow 0.2s; border-left: 5px solid #c5721f;
}
.pedido-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(90, 59, 40, 0.07); }
.pedido-card.b2b { border-left-color: #137333; }

.badge-b2b { background: #e6f4ea; color: #137333; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 10px; display: inline-block; margin-bottom: 8px; }
.badge-b2c { background: #fef7e0; color: #b06000; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 10px; display: inline-block; margin-bottom: 8px; }

.p-title { font-size: 15px; font-weight: 800; color: #2c1e14; margin-bottom: 4px;}
.p-info { font-size: 13px; color: #666; margin-bottom: 3px;}
.p-valor { font-size: 16px; font-weight: 800; color: #137333; margin-top: 8px; }

/* BOTÕES MENORES E DISCRETOS NO TOPO */
div[data-testid="stButton"] button { border-radius: 10px !important; font-weight: 700 !important; transition: all 0.2s ease;}
div[data-testid="stButton"] button:hover { transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)

# CABEÇALHO
st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Gestão de Pedidos</h1>
    <p class="header-sub">Acompanhe e mova os pedidos entre as etapas de atendimento 📋</p>
</div>
""", unsafe_allow_html=True)

# AÇÕES RÁPIDAS DISCRETAS (BOTÕES MENORES)
col_esp1, col_b1, col_b2, col_esp2 = st.columns([2, 2, 2, 2])
with col_b1:
    if st.button("🛍️ + Varejo (PF)", use_container_width=True):
        st.switch_page("pages/19_Pedido_Manual.py")
with col_b2:
    if st.button("🏢 + Corporativo (B2B)", use_container_width=True):
        st.switch_page("pages/18_Corporativo.py")

st.write("")

# FUNÇÕES E CARREGAMENTO
def mudar_status(p_id, novo_status):
    supabase.table("pedidos").update({"status": novo_status}).eq("id", p_id).execute()
    st.toast(f"✅ Pedido atualizado para: {novo_status}")
    st.rerun()

@st.cache_data(ttl=3, show_spinner=False)
def get_pedidos():
    res = supabase.table("pedidos").select("*").order("created_at", desc=True).execute()
    return res.data or []

pedidos = get_pedidos()

# FILTRO DE VISUALIZAÇÃO GERAL
tipo_filtro = st.radio("Filtrar por Canal:", ["Todos os Canais", "Varejo (B2C)", "Corporativo (B2B)"], horizontal=True)
st.write("")

# SEPARAÇÃO POR ABAS (TABS)
aba_rec, aba_pag, aba_prod, aba_des = st.tabs(["📥 Recebidos", "💳 Pagos", "🍳 Em Produção", "❌ Desistência"])

def renderizar_lista_pedidos(lista_pedidos_etapa):
    if not lista_pedidos_etapa:
        st.info("Nenhum pedido encontrado nesta aba.")
        return

    # Grade de 2 colunas para os cards ficarem elegantes e distribuídos
    for i in range(0, len(lista_pedidos_etapa), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(lista_pedidos_etapa):
                renderizar_card_individual(lista_pedidos_etapa[i])
        with col2:
            if i + 1 < len(lista_pedidos_etapa):
                renderizar_card_individual(lista_pedidos_etapa[i + 1])

def renderizar_card_individual(p):
    is_b2b = "[B2B]" in p['cliente_nome']
    nome_exibicao = p['cliente_nome'].replace("[B2B]", "").strip()
    badge = "<div class='badge-b2b'>🏢 CORPORATIVO</div>" if is_b2b else "<div class='badge-b2c'>👤 VAREJO</div>"
    css_class = "pedido-card b2b" if is_b2b else "pedido-card"
    
    dt_entrega = "A confirmar"
    if p.get('data_entrega'):
        try: dt_entrega = datetime.strptime(p['data_entrega'], "%Y-%m-%d").strftime("%d/%m/%Y")
        except: dt_entrega = p['data_entrega']
    
    status_atual = p.get('status', 'Recebido')
    valor_f = f"R$ {float(p.get('valor_total', 0) or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    with st.container(border=False):
        st.markdown(f"""
        <div class="{css_class}">
            {badge}
            <div class="p-title">👤 {nome_exibicao}</div>
            <div class="p-info">🎁 <b>Produto:</b> {p.get('cesta_nome', 'Misto')}</div>
            <div class="p-info">📅 <b>Entrega:</b> {dt_entrega} ({p.get('periodo_entrega', 'A combinar')})</div>
            <div class="p-info">📍 <b>Endereço:</b> {p.get('endereco', 'Não informado')[:45]}...</div>
            <div class="p-valor">{valor_f} &nbsp; <span style="font-size:11px; color:#775a46; font-weight:600;">({p.get('pagamento', 'Pix')})</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # BOTÕES DE CONTROLE DO CARD
        b_det, b_av, b_des = st.columns([2, 2, 1.5])
        with b_det:
            if st.button("🔍 Ficha", key=f"det_{p['id']}", use_container_width=True):
                st.session_state['pedido_detalhe_id'] = p['id']
                st.switch_page("pages/09_Detalhes_Pedido.py")
        with b_av:
            if status_atual in ["Recebido", "Pendente"]:
                if st.button("💳 Pagar", key=f"pg_{p['id']}", use_container_width=True): mudar_status(p['id'], "Pago")
            elif status_atual == "Pago":
                if st.button("🍳 Produzir", key=f"pr_{p['id']}", use_container_width=True): mudar_status(p['id'], "Em Produção")
            elif status_atual == "Em Produção":
                if st.button("🛵 Concluir", key=f"et_{p['id']}", use_container_width=True): mudar_status(p['id'], "Entregue")
            else:
                st.markdown("<div style='text-align:center; font-size:12px; color:#137333; font-weight:800; padding-top:6px;'>CONCLUÍDO</div>", unsafe_allow_html=True)
        with b_des:
            if status_atual != "Desistência":
                if st.button("❌", key=f"des_{p['id']}", help="Marcar como Desistência", use_container_width=True): mudar_status(p['id'], "Desistência")

# FILTRA OS PEDIDOS POR CANAL
pedidos_filtrados = []
for p in pedidos:
    is_b2b = "[B2B]" in p['cliente_nome']
    if tipo_filtro == "Varejo (B2C)" and is_b2b: continue
    if tipo_filtro == "Empresas (B2B)" and not is_b2b: continue
    pedidos_filtrados.append(p)

# SEPARAÇÃO POR ETAPAS PARA AS ABAS
rec_list = [p for p in pedidos_filtrados if p.get("status", "Recebido") in ["Recebido", "Pendente"]]
pag_list = [p for p in pedidos_filtrados if p.get("status") == "Pago"]
prod_list = [p for p in pedidos_filtrados if p.get("status") in ["Em Produção", "Em Rota de Entrega", "Entregue"]]
des_list = [p for p in pedidos_filtrados if p.get("status") == "Desistência"]

with aba_rec: renderizar_lista_pedidos(rec_list)
with aba_pag: renderizar_lista_pedidos(pag_list)
with aba_prod: renderizar_lista_pedidos(prod_list)
with aba_des: renderizar_lista_pedidos(des_list)

st.write("")
st.divider()
st.caption("📦 Gerenciamento de Pedidos - Doce Cesta Brasília")
