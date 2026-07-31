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

@media (max-width: 768px) { h1 { font-size: 24px !important; } }
</style>
""",
unsafe_allow_html=True
)

st.title("👥 Base de Clientes")
st.caption("Pesquise por Nome, CPF ou Celular para carregar o perfil e o histórico de compras.")

# =====================================================
# BUSCA OTIMIZADA E À PROVA DE FALHAS (FALLBACK)
# =====================================================
@st.cache_data(ttl=30)
def carregar_dados_clientes():
    try:
        # TENTA LER A VIEW CRIADA NO SUPABASE (MÁXIMA PERFORMANCE)
        res = supabase.table("vw_resumo_clientes").select("*").execute()
        if res.data:
            return res.data, True
    except:
        pass
    
    # ROTA DE FUGA (FALLBACK): Baixa apenas 6 colunas de texto (Ignora fotos e descrições)
    try:
        res = supabase.table("pedidos").select("id, cliente_nome, cliente_cpf, cliente_telefone, valor_total, status").execute()
        return res.data or [], False
    except:
        return [], False

dados, veio_da_view = carregar_dados_clientes()

if not dados:
    st.info("Nenhum cliente com pedidos válidos na base.")
    st.stop()

# =====================================================
# PROCESSAMENTO DOS DADOS PARA A LISTA
# =====================================================
lista_clientes = []
faturamento_total = 0
total_pedidos = 0

if veio_da_view:
    # A View já entregou tudo mastigado do servidor
    for c in dados:
        lista_clientes.append({
            "nome": c.get("nome", "Cliente sem nome"),
            "cpf": c.get("cpf") or "-",
            "telefone": c.get("telefone") or "-"
        })
        faturamento_total += float(c.get("total_gasto") or 0)
        total_pedidos += int(c.get("total_pedidos") or 0)
else:
    # Agrupamento manual com alta performance (se a View falhar)
    clientes_dict = {}
    for p in dados:
        if str(p.get("status", "")).strip().capitalize() in ["Recebido", "Desistência", "Desistencia"]:
            continue
            
        chave_cli = str(p.get("cliente_cpf") or p.get("cliente_telefone") or p.get("cliente_nome")).strip().lower()
        if not chave_cli or chave_cli == "none": continue
            
        if chave_cli not in clientes_dict:
            clientes_dict[chave_cli] = {
                "nome": p.get("cliente_nome", "Cliente sem nome"),
                "cpf": p.get("cliente_cpf", "-"),
                "telefone": p.get("cliente_telefone", "-"),
                "total_gasto": 0,
                "total_pedidos": 0
            }
        clientes_dict[chave_cli]["total_gasto"] += float(p.get("valor_total", 0) or 0)
        clientes_dict[chave_cli]["total_pedidos"] += 1
        
        faturamento_total += float(p.get("valor_total", 0) or 0)
        total_pedidos += 1
        
    lista_clientes = list(clientes_dict.values())

# Ordena a lista de forma alfabética
lista_clientes = sorted(lista_clientes, key=lambda x: x["nome"])

# =====================================================
# INDICADORES GERAIS (KPIS)
# =====================================================
total_clientes = len(lista_clientes)
ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0

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

if cliente_selecionado_str == "🔍 Selecione ou digite o nome, CPF ou celular...":
    st.write("")
    st.info("💡 Utilize o campo acima para pesquisar e selecionar um cliente e visualizar seu perfil completo e histórico.")
    st.stop()

idx_escolhido = opcoes_select.index(cliente_selecionado_str) - 1
cliente_atual = lista_clientes[idx_escolhido]

# Salva a chave primária na sessão e redireciona (telefone ou cpf)
st.session_state["cliente_historico_alvo"] = cliente_atual['cpf'] if cliente_atual['cpf'] != '-' else cliente_atual['telefone']
st.switch_page("pages/13_Historico_Cliente.py")
