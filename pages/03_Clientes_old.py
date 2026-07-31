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
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 2px !important; letter-spacing: -0.5px; }
h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-top: 15px !important; margin-bottom: 10px !important; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

/* Cards de Métricas (KPIs) */
.metric-card {
    background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%);
    border: 1px solid #e8ddd3;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.metric-title { font-size: 12px; font-weight: 800; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
.metric-value { font-size: 26px; font-weight: 800; color: #4a2e1b; }

div[data-testid="stVerticalBlockBorderWrapper"] { 
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 14px !important; 
    padding: 16px 20px !important; margin-bottom: 10px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.02); 
}
.cliente-header { font-size: 22px; font-weight: 800; color: #2c1e14; margin-bottom: 2px; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 10px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.info-value { font-weight: 700; color: #333; font-size: 14px !important; margin-bottom: 6px; }

/* Badges de Status */
.badge-status { display: inline-block; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11px !important; text-transform: uppercase; text-align: center; }
.badge-pago { background-color: #e6f4ea; color: #137333; border: 1px solid #ceead6; }
.badge-recebido { background-color: #fef7e0; color: #b06000; border: 1px solid #fce8b2; }
.badge-enviado { background-color: #e8f0fe; color: #1a73e8; border: 1px solid #d2e3fc; }
.badge-entregue { background-color: #f3e8fd; color: #6a1b9a; border: 1px solid #e9d2fd; }
.badge-desistencia { background-color: #fce8e6; color: #c5221f; border: 1px solid #fad2cf; }

div[data-testid="stColumn"] div[data-testid="stButton"] button { 
    font-size: 14px !important; padding: 4px 6px !important; border-radius: 10px !important; 
    min-height: 38px !important; border: 1px solid #e8ddd3 !important; background: #faf7f3 !important; 
    font-weight: 800 !important;
}

@media (max-width: 768px) { h1 { font-size: 24px !important; } }
</style>
""",
unsafe_allow_html=True
)

st.title("👥 Base de Clientes")
st.caption("Pesquise por Nome, CPF ou Celular para carregar o perfil e o histórico de compras.")

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

# Filtra ignorando "Recebido" e "Desistência"
pedidos_filtrados = [p for p in pedidos_brutos if str(p.get("status", "")).strip().capitalize() not in ["Recebido", "Desistência"]]

if not pedidos_filtrados:
    st.info("Nenhum cliente com pedidos válidos na base.")
    st.stop()

clientes_dict = {}
for p in pedidos_filtrados:
    chave_cli = str(p.get("cliente_cpf") or p.get("cliente_telefone") or p.get("cliente_nome")).strip().lower()
    if not chave_cli or chave_cli == "none": continue
        
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

# =====================================================
# SELETOR / PESQUISA FLEXÍVEL
# =====================================================
opcoes_select = ["🔍 Selecione ou digite o nome, CPF ou celular..."] + [f"{c['nome']} (CPF: {c['cpf']})" if c['cpf'] != '-' else f"{c['nome']} (Tel: {c['telefone']})" for c in lista_clientes]

cliente_selecionado_str = st.selectbox("Pesquisar Cliente na Base:", opcoes_select)

# REQUISITO: Se não selecionar, nada abaixo é exibido
if cliente_selecionado_str == "🔍 Selecione ou digite o nome, CPF ou celular...":
    st.write("")
    st.info("💡 Utilize o campo acima para pesquisar e selecionar um cliente e visualizar seu perfil completo e histórico.")
    st.stop()

idx_escolhido = opcoes_select.index(cliente_selecionado_str) - 1
cliente_atual = lista_clientes[idx_escolhido]

# Salva na sessão e redireciona para o histórico consolidado
st.session_state["cliente_historico_alvo"] = cliente_atual['cpf'] if cliente_atual['cpf'] != '-' else cliente_atual['telefone']
st.switch_page("pages/13_Historico_Cliente.py")
