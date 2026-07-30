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
# CSS PREMIUM (ABAS COM LINHA INFERIOR E CARDS AMPLOS EM LINHA ÚNICA)
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

/* ABAS: SEM FUNDO, APENAS LINHA INDICADORA NA SELECIONADA */
.stTabs [data-baseweb="tab-list"] { 
    gap: 30px; justify-content: center; background-color: transparent; border-bottom: 2px solid #e8ddd3; padding: 0; margin-bottom: 25px; 
}
.stTabs [data-baseweb="tab"] { 
    height: 45px; background-color: transparent !important; border-radius: 0 !important; font-weight: 700; font-size: 14px; color: #775a46; 
    border: none !important; box-shadow: none !important; padding: 0 10px; transition: color 0.2s ease; 
}
.stTabs [data-baseweb="tab"]:hover { color: #c5721f; }
.stTabs [aria-selected="true"] { 
    color: #c5721f !important; border-bottom: 3px solid #c5721f !important; background: transparent !important; box-shadow: none !important; 
}

/* CARD EM LINHA ÚNICA (UTILIZANDO TODA A LARGURA DA TELA) */
.pedido-card-linha {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 12px;
    padding: 14px 20px; margin-bottom: 12px; box-shadow: 0 3px 10px rgba(90, 59, 40, 0.02);
    display: flex; align-items: center; justify-content: space-between; gap: 15px;
    border-left: 5px solid #c5721f; transition: all 0.2s ease;
}
.pedido-card-linha:hover { box-shadow: 0 6px 18px rgba(90, 59, 40, 0.06); transform: translateY(-1px); }
.pedido-card-linha.b2b { border-left-color: #137333; }

.badge-b2b { background: #e6f4ea; color: #137333; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 8px; margin-bottom: 3px; display: inline-block;}
.badge-b2c { background: #fef7e0; color: #b06000; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 8px; margin-bottom: 3px; display: inline-block;}

.col-info { flex: 1; min-width: 150px; font-size: 12.5px; color: #5a3b28; }
.col-info b { color: #2c1e14; }

div[data-testid="stButton"] button { border-radius: 10px !important; font-weight: 700 !important; font-size: 12px !important; padding: 6px 10px !important;}
</style>
""", unsafe_allow_html=True)

# CABEÇALHO
st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Gestão de Pedidos</h1>
    <p class="header-sub">Acompanhe e mova os pedidos entre as etapas de atendimento 📋</p>
</div>
""", unsafe_allow_html=True)

# AÇÕES RÁPIDAS DISCRETAS
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

# SEPARAÇÃO POR ABAS EXATAS (Recebidos, Pago, Desistência)
aba_rec, aba_pag, aba_des = st.tabs(["📥 Recebidos", "💳 Pago", "❌ Desistência"])

def renderizar_lista_pedidos(lista_pedidos_etapa):
    if not lista_pedidos_etapa:
        st.info("Nenhum pedido encontrado nesta etapa.")
        return

    for p in lista_pedidos_etapa:
        renderizar_card_linha(p)

def renderizar_card_linha(p):
    is_b2b = "[B2B]" in p['cliente_nome']
    nome_exibicao = p['cliente_nome'].replace("[B2B]", "").strip()
    badge = "<div class='badge-b2b'>CORP</div>" if is_b2b else "<div class='badge-b2c'>VAREJO</div>"
    css_class = "pedido-card-linha b2b" if is_b2b else "pedido-card-linha"
    
    dt_entrega = "A confirmar"
    if p.get('data_entrega'):
        try: dt_entrega = datetime.strptime(p['data_entrega'], "%Y-%m-%d").strftime("%d/%m/%Y")
        except: dt_entrega = p['data_entrega']
    
    status_atual = p.get('status', 'Recebido')
    valor_f = f"R$ {float(p.get('valor_total', 0) or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([2.2, 2.2, 2.8, 1.4, 1.6])
    
    with col_c1:
        st.markdown(f"""
        <div>
            {badge}
            <div style="font-weight: 800; font-size: 14px; color: #2c1e14;">👤 {nome_exibicao}</div>
            <div style="font-size: 11.5px; color: #775a46;">📞 {p.get('cliente_telefone', '-')}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c2:
        st.markdown(f"""
        <div>
            <div style="font-weight: 700; font-size: 13px; color: #5a3b28;">🎁 {p.get('cesta_nome', 'Misto')}</div>
            <div style="font-size: 11.5px; color: #8c7362;">💳 {p.get('pagamento', 'Pix')} &bull; <b style="color:#137333;">{valor_f}</b></div>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown(f"""
        <div>
            <div style="font-size: 12px; color: #4a2e1b;">📅 <b>{dt_entrega}</b> ({p.get('periodo_entrega', 'A combinar')})</div>
            <div style="font-size: 11px; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{p.get('endereco', 'Não informado')}">📍 {p.get('endereco', 'Não informado')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c4:
        if st.button("🔍 Ficha", key=f"det_{p['id']}", use_container_width=True):
            st.session_state['pedido_detalhe_id'] = p['id']
            st.switch_page("pages/09_Detalhes_Pedido.py")

    with col_c5:
        b_acao, b_canc = st.columns(2)
        with b_acao:
            if status_atual in ["Recebido", "Pendente"]:
                if st.button("💳", key=f"pg_{p['id']}", help="Marcar como Pago", use_container_width=True): mudar_status(p['id'], "Pago")
            elif status_atual == "Pago":
                if st.button("↩️", key=f"rec_{p['id']}", help="Retornar para Recebidos", use_container_width=True): mudar_status(p['id'], "Recebido")
            else:
                st.markdown("<div style='font-size:10px; color:#137333; font-weight:800; text-align:center; padding-top:6px;'>-</div>", unsafe_allow_html=True)
        with b_canc:
            if status_atual != "Desistência":
                if st.button("❌", key=f"des_{p['id']}", help="Marcar como Desistência", use_container_width=True): mudar_status(p['id'], "Desistência")
            else:
                if st.button("🔄", key=f"ret_{p['id']}", help="Restaurar para Recebidos", use_container_width=True): mudar_status(p['id'], "Recebido")

# FILTRA OS PEDIDOS POR CANAL
pedidos_filtrados = []
for p in pedidos:
    is_b2b = "[B2B]" in p['cliente_nome']
    if tipo_filtro == "Varejo (B2C)" and is_b2b: continue
    if tipo_filtro == "Empresas (B2B)" and not is_b2b: continue
    pedidos_filtrados.append(p)

# SEPARAÇÃO EXATA POR ABAS DE ACORDO COM O STATUS DO BANCO
rec_list = [p for p in pedidos_filtrados if p.get("status", "Recebido") in ["Recebido", "Pendente"]]
pag_list = [p for p in pedidos_filtrados if p.get("status") in ["Pago", "Em Produção", "Em Rota de Entrega", "Entregue"]]
des_list = [p for p in pedidos_filtrados if p.get("status") == "Desistência"]

with aba_rec: renderizar_lista_pedidos(rec_list)
with aba_pag: renderizar_lista_pedidos(pag_list)
with aba_des: renderizar_lista_pedidos(des_list)

st.write("")
st.divider()
st.caption("📦 Gerenciamento de Pedidos - Doce Cesta Brasília")
