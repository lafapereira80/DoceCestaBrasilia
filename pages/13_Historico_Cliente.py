import streamlit as st
import pandas as pd
import re
from datetime import datetime
import urllib.parse

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador


# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS
# =====================================================
st.set_page_config(page_title="Ficha do Cliente", page_icon="📇", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown(
"""
<style>
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1000px; }
h1 { font-size: 24px !important; font-weight: 700 !important; color: #5a3b28; margin-bottom: 2px !important; }
.kpi-card { background: #fff8ef; border: 1px solid #e6d1bb; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 4px rgba(90,59,40,0.04); }
.kpi-title { font-size: 13px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 24px; font-weight: 800; color: #2e7d32; margin-top: 4px; }

div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 14px 16px !important; margin-bottom: 8px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.03); transition: all 0.2s ease; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #c9b19c !important; box-shadow: 0 4px 8px rgba(90, 59, 40, 0.08); }

.info-label { font-weight: 700; color: #775a46; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
.info-value { margin-bottom: 4px; color: #222; font-weight: 800; font-size: 15px !important; }

.status-badge { font-weight: 700; padding: 3px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; display: inline-block;}
div[data-testid="stButton"] button { font-size: 13px !important; border-radius: 8px !important; min-height: 36px !important; }
</style>
""",
unsafe_allow_html=True
)

# =====================================================
# VALIDAÇÃO DE SESSÃO
# =====================================================
# Espera-se que a página de Clientes tenha salvo o CPF ou Telefone na sessão para buscar
if "cliente_selecionado_doc" not in st.session_state:
    st.warning("⚠️ Nenhum cliente selecionado. Volte para a tela de Clientes e selecione um.")
    if st.button("⬅️ Voltar para Clientes", use_container_width=True):
        st.switch_page("pages/03_Clientes.py")
    st.stop()

doc_cliente = st.session_state["cliente_selecionado_doc"]


# =====================================================
# FUNÇÕES DE FORMATAÇÃO E STATUS
# =====================================================
def formatar_valor(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def formatar_data(data_str):
    try: return datetime.strptime(str(data_str)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return "-"

def cor_status_html(status):
    s = str(status).lower()
    if s == "pago": return '<span class="status-badge" style="background: #e6f4ea; color: #137333; border: 1px solid #137333;">PAGO</span>'
    if s == "enviado": return '<span class="status-badge" style="background: #e8f0fe; color: #1a73e8; border: 1px solid #1a73e8;">ENVIADO</span>'
    if s == "entregue": return '<span class="status-badge" style="background: #f3e8fd; color: #6a1b9a; border: 1px solid #6a1b9a;">ENTREGUE</span>'
    if "desist" in s: return '<span class="status-badge" style="background: #fce8e6; color: #c5221f; border: 1px solid #c5221f;">DESISTÊNCIA</span>'
    return '<span class="status-badge" style="background: #fef7e0; color: #b06000; border: 1px solid #b06000;">RECEBIDO</span>'


# =====================================================
# BUSCA DE DADOS NO BANCO
# =====================================================
try:
    # Tenta buscar primeiro por CPF, se não achar tenta por telefone
    res = supabase.table("pedidos").select("*").eq("cliente_cpf", doc_cliente).order("created_at", desc=True).execute()
    pedidos = res.data or []
    
    if not pedidos:
        res = supabase.table("pedidos").select("*").eq("cliente_telefone", doc_cliente).order("created_at", desc=True).execute()
        pedidos = res.data or []
except Exception as e:
    st.error("Erro ao comunicar com o banco de dados.")
    st.stop()

if not pedidos:
    st.error("Cliente não encontrado ou sem pedidos.")
    st.stop()


# Extrai os dados do cliente do último pedido feito
ultimo_pedido = pedidos[0]
nome = ultimo_pedido.get("cliente_nome", "Não informado")
telefone = ultimo_pedido.get("cliente_telefone", "")
cpf = ultimo_pedido.get("cliente_cpf", "")

pedidos_validos = [p for p in pedidos if str(p.get("status")).capitalize() not in ["Desistência", "Desistencia"]]
total_gasto = sum(float(p.get("valor_total", 0) or 0) for p in pedidos_validos if str(p.get("status")).capitalize() in ["Pago", "Enviado", "Entregue"])
ticket_medio = total_gasto / len(pedidos_validos) if len(pedidos_validos) > 0 else 0


# =====================================================
# CABEÇALHO E AÇÕES
# =====================================================
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("📇 Ficha do Cliente")
with col_t2:
    if st.button("⬅️ Voltar para Clientes", use_container_width=True):
        del st.session_state["cliente_selecionado_doc"]
        st.switch_page("pages/03_Clientes.py")


# =====================================================
# DADOS DO CLIENTE E KPIS
# =====================================================
with st.container(border=True):
    c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
    with c1: st.markdown(f'<div class="info-label">Nome Completo</div><div class="info-value">{nome}</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="info-label">Documento (CPF)</div><div class="info-value">{cpf if cpf else "N/A"}</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="info-label">Telefone</div><div class="info-value">+{telefone}</div>', unsafe_allow_html=True)
    with c4:
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        tel_wpp = f"55{telefone}" if len(str(telefone)) <= 11 else telefone
        link_wpp = f"https://wa.me/{tel_wpp}"
        st.link_button("💬 Chamar WhatsApp", url=link_wpp, use_container_width=True)

st.write("")
k1, k2, k3 = st.columns(3)
with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total de Pedidos</div><div class="kpi-value" style="color:#5a3b28;">{len(pedidos)}</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-title">LTV (Total Gasto)</div><div class="kpi-value">{formatar_valor(total_gasto)}</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Ticket Médio</div><div class="kpi-value">{formatar_valor(ticket_medio)}</div></div>', unsafe_allow_html=True)


# =====================================================
# LINHA DO TEMPO DE PEDIDOS
# =====================================================
st.write("")
st.subheader("🛍️ Linha do Tempo de Pedidos")

for ped in pedidos:
    with st.container(border=True):
        p1, p2, p3, p4, p5 = st.columns([1, 2, 1.5, 1.5, 1])
        
        with p1:
            st.caption(formatar_data(ped.get("created_at")))
            st.markdown(f"**#{ped.get('id')}**")
            
        with p2:
            st.markdown(f"**🎁 {ped.get('cesta_nome', 'Cesta Não Informada')}**")
            st.caption(f"Homenageado: {ped.get('destinatario_nome', 'N/A')}")
            
        with p3:
            st.markdown(f"**{formatar_valor(ped.get('valor_total'))}**")
            st.caption(f"{ped.get('pagamento', 'N/A')}")
            
        with p4:
            st.markdown(cor_status_html(ped.get("status")), unsafe_allow_html=True)
            
        with p5:
            if st.button("👁️ Abrir", key=f"abrir_{ped.get('id')}", use_container_width=True):
                st.session_state["pedido_aberto"] = ped.get("id")
                st.switch_page("pages/09_Detalhes_Pedido.py")
