import streamlit as st
import pandas as pd
from datetime import datetime
import json

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

st.set_page_config(page_title="Mural de Pedidos", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1300px !important; }

.header-title { font-size: 28px !important; font-weight: 800 !important; color: #c5721f !important; margin-bottom: 5px;}
.header-subtitle { font-size: 13px !important; color: #775a46 !important; font-weight: 600 !important; margin-bottom: 20px;}

.pedido-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 12px; padding: 18px;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02); margin-bottom: 15px; transition: all 0.2s ease;
}
.pedido-card:hover { border-color: #c5721f; box-shadow: 0 6px 15px rgba(197, 114, 31, 0.1); transform: translateY(-2px); }

.card-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #e8ddd3; padding-bottom: 10px; margin-bottom: 10px; }
.pedido-id { font-size: 16px; font-weight: 800; color: #137333; margin: 0; }
.tag-tipo { font-size: 10px; font-weight: 800; padding: 4px 8px; border-radius: 6px; text-transform: uppercase; border: 1px solid transparent; }
.tag-b2b { background: #e6f4ea; color: #137333; border-color: #ceead6; }
.tag-vitrine { background: #e8f0fe; color: #1a73e8; border-color: #d2e3fc; }
.tag-varejo { background: #fef7e0; color: #b06000; border-color: #fce8b2; }

.pedido-info { font-size: 13px; color: #5a3b28; margin-bottom: 4px; font-weight: 500; }
.pedido-info b { color: #2c1e14; font-weight: 700; }
.pedido-total { font-size: 18px; font-weight: 800; color: #137333; margin-top: 10px; }

/* Destaque discreto para a Etapa Logística */
.linha-producao { color: #0d4e22; font-weight: 700; font-size: 11.5px; margin-top: 8px; padding-top: 8px; border-top: 1px solid #f3ece6; }

div[data-testid="stSelectbox"] label { display: none !important; }
div[data-testid="stButton"] button { border-radius: 8px !important; font-weight: 800 !important; transition: all 0.2s; }
</style>
""", unsafe_allow_html=True)

# OS STATUS OFICIAIS DO BANCO
STATUS_PERMITIDOS = ["Recebido", "Pago", "Enviado", "Em Rota de Entrega", "Entregue", "Desistência"]

def alterar_status_callback(pedido_id, widget_key):
    novo_status = st.session_state[widget_key]
    try:
        supabase.table("pedidos").update({"status": novo_status}).eq("id", pedido_id).execute()
        st.toast(f"✅ Pedido atualizado para: {novo_status}!")
    except: pass

st.markdown("<div class='header-title'>📋 Mural Central de Pedidos</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Acompanhe a situação e etapa dos pedidos.</div>", unsafe_allow_html=True)

with st.spinner("Carregando pedidos ativos..."):
    res = supabase.table("pedidos").select("*").in_("status", ["Recebido", "Pago", "Enviado", "Em Rota de Entrega", "Desistência"]).order("data_entrega", desc=False).execute()
    todos_pedidos = res.data or []

qtd_recebido = sum(1 for p in todos_pedidos if p.get('status') == 'Recebido')
qtd_pago = sum(1 for p in todos_pedidos if p.get('status') == 'Pago')
qtd_rota = sum(1 for p in todos_pedidos if p.get('status') in ['Enviado', 'Em Rota de Entrega'])

filtro_selecionado = st.radio("Filtro:", [f"Recebidos ({qtd_recebido})", f"Pagos ({qtd_pago})", f"Em Rota ({qtd_rota})", "Todos"], horizontal=True)

pedidos_filtrados = []
for p in todos_pedidos:
    st_atual = p.get('status', '')
    if filtro_selecionado.startswith("Recebidos") and st_atual == "Recebido": pedidos_filtrados.append(p)
    elif filtro_selecionado.startswith("Pagos") and st_atual == "Pago": pedidos_filtrados.append(p)
    elif filtro_selecionado.startswith("Em Rota") and st_atual in ["Enviado", "Em Rota de Entrega"]: pedidos_filtrados.append(p)
    elif filtro_selecionado.startswith("Todos"): pedidos_filtrados.append(p)

if not pedidos_filtrados:
    st.info("Nenhum pedido encontrado no filtro.")
    st.stop()

cols = st.columns(3)
for idx, p in enumerate(pedidos_filtrados):
    col = cols[idx % 3] 
    pid = p['id']
    id_curto = str(pid).split('-')[0].upper()
    
    # Tratamento Visual
    cliente_bruto = str(p.get('cliente_nome') or '')
    if "[B2B]" in cliente_bruto: tag_html = '<span class="tag-tipo tag-b2b">🏢 B2B</span>'
    elif "[VITRINE]" in cliente_bruto: tag_html = '<span class="tag-tipo tag-vitrine">🌐 VITRINE</span>'
    else: tag_html = '<span class="tag-tipo tag-varejo">🛍️ VAREJO</span>'
    cliente_limpo = cliente_bruto.replace('[B2B]', '').replace('[VITRINE]', '').strip()
    
    try: data_f = datetime.strptime(str(p.get('data_entrega'))[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: data_f = "Não definida"
    try: valor_f = f"{float(p.get('valor_total', 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: valor_f = "0,00"

    # ==========================================
    # LÓGICA DO TEXTO DISCRETO (LINHA DO TEMPO)
    # ==========================================
    chk_str = p.get('checklist') or "{}"
    if isinstance(chk_str, str):
        try: chk_str = json.loads(chk_str)
        except: chk_str = {}
        
    status_db = p.get('status', '')
    entregador = p.get('entregador_login')
    cesta_montada = p.get('cesta_montada', False)
    
    if status_db == 'Entregue': 
        texto_discreto = "🎉 Pedido entregue ao destinatário"
    elif status_db in ['Enviado', 'Em Rota de Entrega'] or entregador:
        texto_discreto = "🛵 Saiu para entrega (Rota)"
    elif cesta_montada:
        texto_discreto = "✅ Cesta montada na fábrica"
    elif chk_str and any(chk_str.values()):
        texto_discreto = "⚙️ Montagem iniciada (fábrica)"
    else:
        texto_discreto = "⏳ Aguardando montagem"

    with col:
        with st.container(border=False):
            html_card = f"""
            <div class="pedido-card">
                <div class="card-header">
                    <h3 class="pedido-id">#{id_curto}</h3>
                    {tag_html}
                </div>
                <div class="pedido-info"><b>👤 Cliente:</b> {cliente_limpo}</div>
                <div class="pedido-info"><b>🎁 Cesta:</b> {p.get('cesta_nome') or '-'}</div>
                <div class="pedido-info"><b>📅 Entrega:</b> {data_f} ({p.get('periodo_entrega') or '-'})</div>
                <div class="pedido-info linha-producao">🛠️ Etapa Logística: {texto_discreto}</div>
                <div class="pedido-total">R$ {valor_f}</div>
            </div>
            """
            st.markdown(html_card.replace('\n', ''), unsafe_allow_html=True)
            
            c_status, c_btn = st.columns([1.5, 1])
            with c_status:
                idx_st = STATUS_PERMITIDOS.index(status_db) if status_db in STATUS_PERMITIDOS else 0
                widget_key = f"st_{pid}"
                st.selectbox("Status Oficial", STATUS_PERMITIDOS, index=idx_st, key=widget_key, on_change=alterar_status_callback, args=(pid, widget_key), label_visibility="collapsed")
            with c_btn:
                if st.button("Detalhes", key=f"btn_{pid}", use_container_width=True, type="primary"):
                    st.session_state['pedido_detalhe_id'] = pid
                    st.switch_page("pages/09_Detalhes_Pedido.py")
