import streamlit as st
import pandas as pd
from datetime import datetime
import time

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E DESIGN PREMIUM
# =====================================================
st.set_page_config(page_title="Gestão de Clientes", page_icon="👥", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.get("usuario", {})
perfil_usuario = usuario.get("perfil", "Operador")

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 2px !important; letter-spacing: -0.5px; }
h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-top: 15px !important; margin-bottom: 10px !important; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

/* =========================================
   CARDS DE MÉTRICAS (KPIS)
========================================== */
.metric-card {
    background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%);
    border: 1px solid #e8ddd3;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.metric-card:hover {
    border-color: #d2bfae;
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08);
    transform: translateY(-3px);
}
.metric-title { font-size: 12px; font-weight: 800; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
.metric-value { font-size: 26px; font-weight: 800; color: #4a2e1b; }

/* =========================================
   CONTAINERS E CARDS DA BASE
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] { 
    background: #ffffff; 
    border: 1px solid #e8ddd3 !important; 
    border-radius: 14px !important; 
    padding: 16px 20px !important; 
    margin-bottom: 10px !important; 
    box-shadow: 0 2px 8px rgba(0,0,0,0.02); 
    transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1); 
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { 
    border-color: #d2bfae !important; 
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08); 
}

.cliente-header { font-size: 18px; font-weight: 800; color: #2c1e14; margin-bottom: 2px; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 10px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.info-value { font-weight: 700; color: #333; font-size: 13px !important; margin-bottom: 4px; }

/* Botões da Tabela */
div[data-testid="stColumn"] div[data-testid="stButton"] button { 
    font-size: 13px !important; padding: 4px 6px !important; border-radius: 10px !important; 
    min-height: 38px !important; border: 1px solid #e8ddd3 !important; background: #faf7f3 !important; 
    transition: all 0.2s ease; display: flex; justify-content: center; align-items: center; font-weight: 800 !important; 
}
div[data-testid="stColumn"] div[data-testid="stButton"] button:hover { background: #e8ddd3 !important; transform: scale(1.02); }

@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
}
</style>
""",
unsafe_allow_html=True
)

st.title("👥 Base de Clientes")
st.caption("Consulte os clientes cadastrados por Nome, CPF ou Celular e acesse o histórico de compras.")

# =====================================================
# BUSCA E PROCESSAMENTO DE DADOS (FILTRANDO STATUS)
# =====================================================
@st.cache_data(ttl=30)
def carregar_dados_clientes():
    try:
        res = supabase.table("pedidos").select("*").execute()
        return res.data or []
    except:
        return []

pedidos_brutos = carregar_dados_clientes()

if not pedidos_brutos:
    st.info("Nenhum pedido registrado no sistema.")
    st.stop()

# REQUISITO: Ignora pedidos com status "Recebido" ou "Desistência"
pedidos_filtrados = []
for p in pedidos_brutos:
    st_p = str(p.get("status", "")).strip().capitalize()
    if st_p not in ["Recebido", "Desistência"]:
        pedidos_filtrados.append(p)

if not pedidos_filtrados:
    st.info("Nenhum cliente com pedidos válidos (Pago, Enviado ou Entregue) na base.")
    st.stop()

# Agrupa por identificador único (CPF, senão Telefone, senão Nome)
clientes_dict = {}
for p in pedidos_filtrados:
    chave_cli = str(p.get("cliente_cpf") or p.get("cliente_telefone") or p.get("cliente_nome")).strip().lower()
    if not chave_cli or chave_cli == "none":
        continue
        
    if chave_cli not in clientes_dict:
        clientes_dict[chave_cli] = {
            "nome": p.get("cliente_nome", "Cliente sem nome"),
            "cpf": p.get("cliente_cpf", "-"),
            "telefone": p.get("cliente_telefone", "-"),
            "compras": []
        }
    clientes_dict[chave_cli]["compras"].append(p)

lista_clientes = sorted(list(clientes_dict.values()), key=lambda x: x["nome"])

# =====================================================
# INDICADORES GERAIS (KPIS)
# =====================================================
total_clientes = len(lista_clientes)
faturamento_total = sum([float(p.get("valor_total", 0) or 0) for p in pedidos_filtrados])
ticket_medio = faturamento_total / len(pedidos_filtrados) if pedidos_filtrados else 0

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">👥 Total de Clientes</div><div class="metric-value">{total_clientes}</div></div>', unsafe_allow_html=True)
with col_kpi2:
    fat_str = f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(f'<div class="metric-card"><div class="metric-title">💰 Faturamento da Base</div><div class="metric-value" style="color: #137333;">{fat_str}</div></div>', unsafe_allow_html=True)
with col_kpi3:
    tkt_str = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(f'<div class="metric-card"><div class="metric-title">📊 Ticket Médio</div><div class="metric-value">{tkt_str}</div></div>', unsafe_allow_html=True)

st.write("")
st.subheader("📋 Pesquisa de Clientes")

# =====================================================
# CAMPO DE PESQUISA FLEXÍVEL (NOME, CPF OU CELULAR)
# =====================================================
termo_busca = st.text_input("🔍 Buscar cliente por Nome, CPF ou Celular:", placeholder="Digite parte do nome, CPF ou número de WhatsApp...")

# Aplica o filtro com base no termo digitado
lista_exibicao = lista_clientes
if termo_busca.strip():
    termo = termo_busca.strip().lower()
    lista_exibicao = [
        c for c in lista_clientes 
        if termo in c['nome'].lower() or termo in str(c['cpf']).lower() or termo in str(c['telefone']).lower()
    ]

if not lista_exibicao:
    st.warning("⚠️ Nenhum cliente encontrado com os dados informados.")
    st.stop()

st.caption(f"Exibindo {len(lista_exibicao)} cliente(s) encontrado(s).")

# =====================================================
# LISTAGEM EM CARDS DA BASE DE CLIENTES
# =====================================================
for cliente in lista_exibicao:
    compras_cli = cliente["compras"]
    qtd_pedidos = len(compras_cli)
    ltv_cli = sum([float(c.get("valor_total", 0) or 0) for c in compras_cli])
    ltv_str = f"R$ {ltv_cli:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    with st.container(border=True):
        col_c1, col_c2, col_c3, col_c4 = st.columns([2.5, 1.5, 1.5, 1.5])
        with col_c1:
            st.markdown(f"<div class='cliente-header'>👤 {cliente['nome']}</div>", unsafe_allow_html=True)
        with col_c2:
            st.markdown(f'<div class="info-label">CPF / Tel</div><div class="info-value">{cliente["cpf"] if cliente["cpf"] != "-" else cliente["telefone"]}</div>', unsafe_allow_html=True)
        with col_c3:
            st.markdown(f'<div class="info-label">Total de Pedidos</div><div class="info-value">📦 {qtd_pedidos} pedido(s)</div>', unsafe_allow_html=True)
        with col_c4:
            st.markdown(f'<div class="info-label">Volume Gasto (LTV)</div><div class="info-value" style="color: #137333;">{ltv_str}</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("📊 Ver Histórico Completo do Cliente", key=f"btn_cli_{cliente['cpf']}_{cliente['nome']}", use_container_width=True):
            st.session_state["cliente_historico_alvo"] = cliente['cpf'] if cliente['cpf'] != '-' else cliente['telefone']
            st.switch_page("pages/13_Historico_Cliente.py")

st.write("")
st.divider()
st.caption("👥 Gestão Oficial da Base - Doce Cesta Brasília")
