import streamlit as st
import pandas as pd
from datetime import datetime
import json

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
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1200px; }
h1 { font-size: 24px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 5px !important; }
h3 { font-size: 18px !important; font-weight: 800 !important; color: #5a3b28; margin-top: 15px !important; }

/* Cartões e Containers */
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 14px 18px !important; margin-bottom: 10px !important; box-shadow: 0 2px 5px rgba(90, 59, 40, 0.04); }

.cliente-header { font-size: 20px; font-weight: 800; color: #5a3b28; margin-bottom: 4px; }
.info-label { font-weight: 700; color: #775a46; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
.info-value { font-weight: 600; color: #333; font-size: 13px !important; margin-bottom: 6px; }

/* Badges de Status */
.badge-status { display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 11px !important; }
.badge-pago { background-color: #e6f4ea; color: #137333; }
.badge-recebido { background-color: #fef7e0; color: #b06000; }
.badge-enviado { background-color: #e8f0fe; color: #1a73e8; }
.badge-entregue { background-color: #f3e8fd; color: #6a1b9a; }
.badge-desistencia { background-color: #fce8e6; color: #c5221f; }

/* Cards de Métricas (KPIs) */
.metric-card { background: #ffffff; border: 1px solid #dfcdbb; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 2px 4px rgba(90,59,40,0.03); }
.metric-value { font-size: 22px; font-weight: 800; color: #5a3b28; margin-top: 2px; }
.metric-title { font-size: 12px; font-weight: 700; color: #775a46; text-transform: uppercase; }
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
# INDICADORES GERAIS (KPIS)
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
    st.markdown(f'<div class="metric-card"><div class="metric-title">💰 Faturamento da Base</div><div class="metric-value" style="color: #2e7d32;">{fat_str}</div></div>', unsafe_allow_html=True)
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
# EXIBIÇÃO DO PERFIL E HISTÓRICO DO CLIENTE ESCOLHIDO
# =====================================================
compras_cliente = cliente_atual["compras"]
compras_cliente.sort(key=lambda x: x.get("created_at", ""), reverse=True)

total_gasto_cli = sum([float(c.get("valor_total", 0) or 0) for c in compras_cliente if str(c.get("status")).capitalize() != "Desistência"])
qtd_compras_cli = len(compras_cliente)

with st.container(border=True):
    col_inf1, col_inf2, col_inf3, col_inf4 = st.columns([2, 1.5, 1.5, 1.5])
    with col_inf1:
        st.markdown(f"<div class='cliente-header'>👤 {cliente_atual['nome']}</div>", unsafe_allow_html=True)
        st.caption("Perfil Cadastrado")
    with col_inf2:
        st.markdown(f'<div class="info-label">CPF</div><div class="info-value">{cliente_atual["cpf"]}</div>', unsafe_allow_html=True)
    with col_inf3:
        tel_limpo = str(cliente_atual["telefone"]).replace("+", "")
        st.markdown(f'<div class="info-label">Telefone / WhatsApp</div><div class="info-value"><a href="https://wa.me/55{tel_limpo}" target="_blank" style="color: #137333; text-decoration: none; font-weight: 700;">📱 +{cliente_atual["telefone"]}</a></div>', unsafe_allow_html=True)
    with col_inf4:
        ltv_str = f"R$ {total_gasto_cli:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(f'<div class="info-label">Total Gasto (LTV)</div><div class="info-value" style="color: #2e7d32; font-size: 15px !important;">{ltv_str}</div>', unsafe_allow_html=True)

    # --- ZONA DE PERIGO (EXCLUSIVO PARA ADMINISTRADOR) ---
    if perfil_usuario == "Administrador":
        st.write("")
        with st.expander("⚙️ Zona de Perigo - Deletar Cliente e Histórico Completo", expanded=False):
            st.error("⚠️ Atenção: Esta ação é irreversível. Ao deletar o comprador, **todos os pedidos e históricos** associados a ele serão permanentemente apagados do banco de dados.")
            confirmar_texto = st.text_input("Digite 'DELETAR' para confirmar a exclusão completa do cliente:", key=f"conf_del_cli_{cliente_atual['cpf']}")
            if st.button("🗑️ Deletar Comprador e Todas as Compras", type="primary", use_container_width=True):
                if confirmar_texto.strip().upper() == "DELETAR":
                    erros_exclusao = 0
                    for comp in compras_cliente:
                        sucesso_p, _ = excluir_pedido_completo(comp["id"])
                        if not sucesso_p:
                            erros_exclusao += 1
                    
                    if erros_exclusao == 0:
                        st.success("✅ Comprador e todas as suas compras foram apagados com sucesso! Atualizando...")
                        st.rerun()
                    else:
                        st.error("❌ Ocorreu um erro ao apagar alguns registros no banco.")
                else:
                    st.warning("⚠️ Digite exatamente a palavra 'DELETAR' para habilitar o botão.")

st.write("")
st.subheader(f"📦 Histórico de Compras ({qtd_compras_cli} registros)")

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

        col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([1.2, 2.8, 1.5, 1.5, 1])
        
        with col_c1:
            st.markdown(f'<div class="info-label">Pedido ID</div><div class="info-value">#{c_id}</div>', unsafe_allow_html=True)
            
        with col_c2:
            st.markdown(f'<div class="info-label">Cesta / Pacote</div><div class="info-value">🎁 {compra.get("cesta_nome", "-")}</div>', unsafe_allow_html=True)
            
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
            st.markdown(f'<div class="info-label">Valor Total</div><div class="info-value" style="color: #2e7d32;">{val_str}</div>', unsafe_allow_html=True)
            
        with col_c5:
            st.markdown(f'<div class="info-label">Status</div><div class="info-value"><span class="badge-status {classe_badge}">{status}</span></div>', unsafe_allow_html=True)

        # Botões de Ação na Compra
        cc_acao1, cc_acao2 = st.columns([4, 1])
        with cc_acao1:
            if st.button("👁️ Abrir Ficha do Pedido", key=f"abrir_pedido_{c_id}", use_container_width=True):
                st.session_state["pedido_aberto"] = c_id
                st.switch_page("pages/09_Detalhes_Pedido.py")
                
        with cc_acao2:
            if perfil_usuario == "Administrador":
                if st.button("🗑️ Deletar", key=f"del_compra_{c_id}", help="Excluir permanentemente este pedido", use_container_width=True):
                    sucesso_del, msg_del = excluir_pedido_completo(c_id)
                    if sucesso_del:
                        st.success("✅ Compra apagada com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_del}")
