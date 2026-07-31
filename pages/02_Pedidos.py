import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Mural de Pedidos", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# =====================================================
# CSS PREMIUM & PERFORMANCE
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1300px !important; }

.header-title { font-size: 28px !important; font-weight: 800 !important; color: #c5721f !important; margin-bottom: 5px;}
.header-subtitle { font-size: 13px !important; color: #775a46 !important; font-weight: 600 !important; margin-bottom: 20px;}

/* Estilo dos Cartões de Pedido */
.pedido-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 12px; padding: 18px;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02); margin-bottom: 15px;
    transition: all 0.2s ease;
}
.pedido-card:hover { border-color: #c5721f; box-shadow: 0 6px 15px rgba(197, 114, 31, 0.1); transform: translateY(-2px); }
.pedido-id { font-size: 16px; font-weight: 800; color: #137333; margin-bottom: 8px; border-bottom: 1px dashed #e8ddd3; padding-bottom: 6px;}
.pedido-info { font-size: 13px; color: #5a3b28; margin-bottom: 4px; font-weight: 500; }
.pedido-info b { color: #2c1e14; font-weight: 700; }
.pedido-total { font-size: 18px; font-weight: 800; color: #137333; margin-top: 10px; }

/* Ajustes de Selectbox e Botões nativos para ficar compacto */
div[data-testid="stSelectbox"] label { display: none !important; }
div[data-testid="stButton"] button { border-radius: 8px !important; font-weight: 800 !important; transition: all 0.2s; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CALLBACKS (A MÁGICA PARA NÃO PRECISAR CLICAR DUAS VEZES)
# =====================================================
# Esta função atualiza o banco no exato milissegundo em que você altera o SelectBox
def alterar_status_callback(pedido_id, widget_key):
    novo_status = st.session_state[widget_key]
    try:
        supabase.table("pedidos").update({"status": novo_status}).eq("id", pedido_id).execute()
        st.toast(f"✅ Pedido atualizado para: {novo_status}!")
    except Exception as e:
        st.error("Erro ao atualizar o status.")

def ir_para_detalhes(pedido_id):
    st.session_state['pedido_detalhe_id'] = pedido_id
    st.switch_page("pages/09_Detalhes_Pedido.py")

# =====================================================
# BUSCA OTIMIZADA NO BANCO DE DADOS
# =====================================================
st.markdown("<div class='header-title'>📋 Mural Central de Pedidos</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Gerencie os status e acesse os detalhes rapidamente.</div>", unsafe_allow_html=True)

# Filtro rápido superior
filtro_status = st.radio("Filtrar por Status:", ["Ativos (Recebido/Pago/Rota)", "Todos", "Entregues", "Desistências"], horizontal=True)

with st.spinner("Carregando pedidos..."):
    # Selecionamos apenas as colunas necessárias para não sobrecarregar a memória e deixar rápido!
    query = supabase.table("pedidos").select("id, cliente_nome, cesta_nome, valor_total, data_entrega, periodo_entrega, status, pagamento").order("data_entrega", desc=False)
    res = query.execute()
    todos_pedidos = res.data or []

# Aplicação do Filtro na memória (muito mais rápido que buscar do banco várias vezes)
pedidos_filtrados = []
for p in todos_pedidos:
    st_atual = p.get('status', '')
    if filtro_status == "Ativos (Recebido/Pago/Rota)" and st_atual in ["Recebido", "Pago", "Em Rota de Entrega"]:
        pedidos_filtrados.append(p)
    elif filtro_status == "Entregues" and st_atual == "Entregue":
        pedidos_filtrados.append(p)
    elif filtro_status == "Desistências" and st_atual == "Desistência":
        pedidos_filtrados.append(p)
    elif filtro_status == "Todos":
        pedidos_filtrados.append(p)

if not pedidos_filtrados:
    st.info("Nenhum pedido encontrado para o filtro atual.")
    st.stop()

# =====================================================
# RENDERIZAÇÃO DOS CARTÕES EM GRID (3 COLUNAS)
# =====================================================
STATUS_PERMITIDOS = ["Recebido", "Pago", "Em Rota de Entrega", "Entregue", "Desistência"]

cols = st.columns(3)
for idx, p in enumerate(pedidos_filtrados):
    col = cols[idx % 3] # Distribui os cards harmoniosamente
    
    pid = p['id']
    id_curto = str(pid).split('-')[0].upper()
    cliente = str(p.get('cliente_nome', '')).replace('[B2B]', '').replace('[VITRINE]', '').strip()
    
    try: data_f = datetime.strptime(str(p.get('data_entrega'))[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: data_f = "Não definida"
    
    try: valor_f = f"{float(p.get('valor_total', 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: valor_f = "0,00"

    with col:
        with st.container(border=False):
            st.markdown(f"""
            <div class="pedido-card">
                <div class="pedido-id">Pedido #{id_curto}</div>
                <div class="pedido-info"><b>👤 Cliente:</b> {cliente}</div>
                <div class="pedido-info"><b>🎁 Cesta:</b> {p.get('cesta_nome', '-')}</div>
                <div class="pedido-info"><b>📅 Entrega:</b> {data_f} ({p.get('periodo_entrega', '-')})</div>
                <div class="pedido-info"><b>💳 Pagto:</b> {p.get('pagamento', '-')}</div>
                <div class="pedido-total">R$ {valor_f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            c_status, c_btn = st.columns([1.5, 1])
            with c_status:
                status_atual = p.get('status', 'Recebido')
                idx_st = STATUS_PERMITIDOS.index(status_atual) if status_atual in STATUS_PERMITIDOS else 0
                widget_key = f"st_{pid}"
                
                # A MÁGICA: O on_change aciona a função de callback no exato momento do clique!
                st.selectbox("Status", STATUS_PERMITIDOS, index=idx_st, key=widget_key, 
                             on_change=alterar_status_callback, args=(pid, widget_key), label_visibility="collapsed")
            with c_btn:
                # O on_click altera a página sem precisar rodar a tela duas vezes
                st.button("Ver Detalhes", key=f"btn_{pid}", use_container_width=True, type="primary", 
                          on_click=ir_para_detalhes, args=(pid,))
