import streamlit as st
import pandas as pd
from datetime import datetime
import json
import time

from config.supabase import supabase
from services.pedido_service import excluir_pedido_completo
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
   CARDS DE MÉTRICAS (KPIs)
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
   CARDS GERAIS (PERFIL E HISTÓRICO)
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
    transform: translateY(-2px); 
}

/* =========================================
   ACORDEÃO (EXPANDER ZONA DE PERIGO)
========================================== */
div[data-testid="stExpander"] { background: #ffffff; border: 1px solid #fad2cf !important; border-radius: 16px !important; box-shadow: 0 4px 15px rgba(197, 34, 31, 0.05) !important; overflow: hidden; margin-top: 15px; margin-bottom: 15px; }
div[data-testid="stExpander"] summary { background: #fffaf9; padding: 15px 20px !important; font-size: 15px !important; font-weight: 800 !important; color: #c5221f !important; transition: all 0.3s ease; }
div[data-testid="stExpander"] summary:hover { background: #fce8e6; }
div[data-testid="stExpanderDetails"] { padding: 20px !important; }

/* =========================================
   TIPOGRAFIA INTERNA DOS CARDS
========================================== */
.cliente-header { font-size: 22px; font-weight: 800; color: #2c1e14; margin-bottom: 2px; letter-spacing: -0.5px; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 10px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.info-value { font-weight: 700; color: #333; font-size: 14px !important; margin-bottom: 6px; }

/* =========================================
   BADGES DE STATUS
========================================== */
.badge-status { display: inline-block; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; text-align: center; }
.badge-pago { background-color: #e6f4ea; color: #137333; border: 1px solid #ceead6; }
.badge-recebido { background-color: #fef7e0; color: #b06000; border: 1px solid #fce8b2; }
.badge-enviado { background-color: #e8f0fe; color: #1a73e8; border: 1px solid #d2e3fc; }
.badge-entregue { background-color: #f3e8fd; color: #6a1b9a; border: 1px solid #e9d2fd; }
.badge-desistencia { background-color: #fce8e6; color: #c5221f; border: 1px solid #fad2cf; }

/* =========================================
   BOTÕES DE AÇÃO NA TABELA
========================================== */
div[data-testid="stColumn"] div[data-testid="stButton"] button { font-size: 14px !important; padding: 4px 6px !important; border-radius: 10px !important; min-height: 38px !important; border: 1px solid #e8ddd3 !important; background: #faf7f3 !important; transition: all 0.2s ease; display: flex; justify-content: center; align-items: center; }
div[data-testid="stColumn"] div[data-testid="stButton"] button:hover { background: #e8ddd3 !important; transform: scale(1.02); }

/* =========================================
   RESPONSIVIDADE MOBILE E BOTÕES (LADO A LADO)
========================================== */
@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
    
    /* Força os botões de ação a ficarem na horizontal no mobile */
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-top: 10px !important;
        justify-content: space-between;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {
        flex: 1 1 0% !important; 
        min-width: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) button {
        width: 100% !important;
        padding: 6px 0px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)

st.title("👥 Base e Histórico de Clientes")
st.caption("Central completa de relacionamento, histórico de compras, LTV e ferramentas de gestão da base.")

# =====================================================
# BUSCA E PROCESSAMENTO DE DADOS
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
    st.info("Nenhum pedido ou cliente registrado no sistema.")
    st.stop()

# Agrupa por identificador único (CPF, senão Telefone, senão Nome)
clientes_dict = {}
for p in pedidos_brutos:
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
# INDICADORES GERAIS (KPIS) PREMIUM
# =====================================================
total_clientes = len(lista_clientes)
todos_pedidos_validos = [p for p in pedidos_brutos if str(p.get("status")).capitalize() != "Desistência"]
faturamento_total = sum([float(p.get("valor_total", 0) or 0) for p in todos_pedidos_validos])
ticket_medio = faturamento_total / len(todos_pedidos_validos) if todos_pedidos_validos else 0

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
# SELETOR DE CLIENTES
# =====================================================
opcoes_select = ["🔍 Selecione ou digite o nome de um cliente..."] + [f"{c['nome']} (CPF: {c['cpf']})" if c['cpf'] != '-' else f"{c['nome']} (Tel: {c['telefone']})" for c in lista_clientes]

cliente_selecionado_str = st.selectbox("Pesquisar na Base de Clientes:", opcoes_select)

if cliente_selecionado_str == "🔍 Selecione ou digite o nome de um cliente...":
    st.write("")
    st.info("💡 Selecione um cliente acima para visualizar o perfil completo, histórico detalhado de compras e ferramentas de gestão.")
    st.stop()

idx_escolhido = opcoes_select.index(cliente_selecionado_str) - 1
cliente_atual = lista_clientes[idx_escolhido]

# =====================================================
# EXIBIÇÃO DO PERFIL DO CLIENTE ESCOLHIDO
# =====================================================
compras_cliente = cliente_atual["compras"]
compras_cliente.sort(key=lambda x: x.get("created_at", ""), reverse=True)

total_gasto_cli = sum([float(c.get("valor_total", 0) or 0) for c in compras_cliente if str(c.get("status")).capitalize() != "Desistência"])
qtd_compras_cli = len(compras_cliente)

st.write("")
with st.container(border=True):
    col_inf1, col_inf2, col_inf3, col_inf4 = st.columns([2.5, 1.5, 2, 1.5])
    with col_inf1:
        st.markdown(f"<div class='cliente-header'>👤 {cliente_atual['nome']}</div>", unsafe_allow_html=True)
        st.caption("Perfil Oficial do Cliente")
    with col_inf2:
        st.markdown(f'<div class="info-label">CPF</div><div class="info-value">{cliente_atual["cpf"]}</div>', unsafe_allow_html=True)
    with col_inf3:
        tel_limpo = str(cliente_atual["telefone"]).replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        st.markdown(f'<div class="info-label">Contato / WhatsApp</div><div class="info-value"><a href="https://wa.me/55{tel_limpo}" target="_blank" style="color: #137333; text-decoration: none; font-weight: 800;">📱 +{cliente_atual["telefone"]}</a></div>', unsafe_allow_html=True)
    with col_inf4:
        ltv_str = f"R$ {total_gasto_cli:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(f'<div class="info-label">Total Gasto (LTV)</div><div class="info-value" style="color: #137333; font-size: 16px !important;">{ltv_str}</div>', unsafe_allow_html=True)

# =====================================================
# ZONA DE PERIGO (EXCLUSIVO PARA ADMINISTRADOR)
# =====================================================
if perfil_usuario == "Administrador":
    with st.expander("⚙️ Zona de Perigo - Excluir Cliente Permanentemente", expanded=False):
        st.error("⚠️ Atenção: Esta ação é irreversível. Ao deletar o comprador, **todos os pedidos e históricos** associados a ele serão apagados do banco de dados para sempre.")
        
        chave_input_del = f"conf_del_cli_{cliente_atual['cpf']}"
        confirmar_texto = st.text_input("Digite 'DELETAR' abaixo para confirmar a exclusão completa:", key=chave_input_del)
        
        if st.button("🗑️ Deletar Comprador e Todas as Compras", type="primary", use_container_width=True):
            if confirmar_texto.strip().upper() == "DELETAR":
                erros_exclusao = 0
                for comp in compras_cliente:
                    sucesso_p, _ = excluir_pedido_completo(comp["id"])
                    if not sucesso_p:
                        erros_exclusao += 1
                
                if erros_exclusao == 0:
                    st.success("✅ Comprador e todas as suas compras foram apagados com sucesso!")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Ocorreu um erro ao apagar alguns registros no banco.")
            else:
                st.warning("⚠️ Digite exatamente a palavra 'DELETAR' no campo acima para habilitar a exclusão.")

# =====================================================
# HISTÓRICO DE COMPRAS (CARDS PREMIUM)
# =====================================================
st.write("")
st.subheader(f"📦 Histórico de Compras ({qtd_compras_cli} pedidos)")

for compra in compras_cliente:
    with st.container(border=True):
        c_id = compra.get("id")
        status = str(compra.get("status", "Recebido")).strip().capitalize()
        
        # Estilização do badge de status
        classe_badge = "badge-recebido"
        if status == "Pago": classe_badge = "badge-pago"
        elif status == "Enviado": classe_badge = "badge-enviado"
        elif status == "Entregue": classe_badge = "badge-entregue"
        elif "Desistência" in status or "Desistencia" in status: classe_badge = "badge-desistencia"

        col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([1.2, 3.0, 1.6, 1.6, 1.2])
        
        with col_c1:
            st.markdown(f'<div class="info-label">Pedido ID</div><div class="info-value">#{c_id}</div>', unsafe_allow_html=True)
            
        with col_c2:
            st.markdown(f'<div class="info-label">Pacote Adquirido</div><div class="info-value">🎁 {compra.get("cesta_nome", "-")}</div>', unsafe_allow_html=True)
            
        with col_c3:
            dt_entrega = compra.get("data_entrega", "-")
            if dt_entrega and len(str(dt_entrega)) >= 10:
                dt_fmt = f"{dt_entrega[8:10]}/{dt_entrega[5:7]}/{dt_entrega[0:4]}"
            else:
                dt_fmt = str(dt_entrega)
            st.markdown(f'<div class="info-label">Data Entrega</div><div class="info-value">🗓️ {dt_fmt}</div>', unsafe_allow_html=True)
            
        with col_c4:
            val = float(compra.get("valor_total", 0) or 0)
            val_str = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f'<div class="info-label">Valor Total</div><div class="info-value" style="color: #137333;">{val_str}</div>', unsafe_allow_html=True)
            
        with col_c5:
            st.markdown(f'<div class="info-label">Status</div><div><span class="badge-status {classe_badge}">{status}</span></div>', unsafe_allow_html=True)

        # Botões de Ação na Compra
        st.write("")
        cc_acao1, cc_acao2 = st.columns([1, 1])
        with cc_acao1:
            if st.button("👁️ Abrir Ficha do Pedido", key=f"abrir_pedido_{c_id}", use_container_width=True):
                st.session_state["pedido_aberto"] = c_id
                st.switch_page("pages/09_Detalhes_Pedido.py")
                
        with cc_acao2:
            if perfil_usuario == "Administrador":
                if st.button("🗑️ Deletar Histórico", key=f"del_compra_{c_id}", help="Excluir permanentemente este pedido específico", use_container_width=True):
                    sucesso_del, msg_del = excluir_pedido_completo(c_id)
                    if sucesso_del:
                        st.toast("✅ Compra apagada com sucesso!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_del}")
