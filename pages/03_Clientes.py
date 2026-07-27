import streamlit as st
import pandas as pd
import re
import urllib.parse
from datetime import datetime

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador


# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS
# =====================================================
st.set_page_config(page_title="Clientes", page_icon="👥", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown(
"""
<style>
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1200px; }
h1 { font-size: 24px !important; font-weight: 700 !important; color: #5a3b28; margin-bottom: 2px !important; }
.kpi-card { background: #fff8ef; border: 1px solid #e6d1bb; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 4px rgba(90,59,40,0.04); }
.kpi-title { font-size: 13px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 24px; font-weight: 800; color: #2e7d32; margin-top: 4px; }
.kpi-value-alt { font-size: 24px; font-weight: 800; color: #5a3b28; margin-top: 4px; }

div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 14px 16px !important; margin-bottom: 8px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.03); transition: all 0.2s ease; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #c9b19c !important; box-shadow: 0 4px 8px rgba(90, 59, 40, 0.08); }

.cli-nome { font-size: 16px !important; font-weight: 800 !important; color: #333; margin-bottom: 2px; }
.cli-doc { font-size: 12px !important; color: #666; font-weight: 600; }
.cli-metric { font-size: 13px !important; font-weight: 700; color: #5a3b28; background: #faf7f3; padding: 4px 10px; border-radius: 8px; border: 1px solid #e8ddd3; display: inline-block; margin-top: 6px;}
.cli-metric-val { color: #2e7d32; font-weight: 800; }

.hist-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px dashed #e8ddd3; font-size: 12px; }
.hist-row:last-child { border-bottom: none; }
.hist-date { font-weight: 600; color: #5a3b28; width: 80px; }
.hist-cesta { flex: 1; color: #333; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0 10px; }
.hist-status { font-weight: 700; padding: 2px 6px; border-radius: 6px; font-size: 10px; text-transform: uppercase; }

div[data-testid="stLinkButton"] > a { background-color: #25D366 !important; color: white !important; font-weight: 700 !important; border: none !important; padding: 4px 12px !important; border-radius: 8px !important; font-size: 13px !important; }
div[data-testid="stLinkButton"] > a:hover { background-color: #128C7E !important; }

@media (max-width: 768px) {
    .block-container { padding-top: 0.5rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    h1 { font-size: 20px !important; }
    .kpi-card { padding: 12px; }
    .kpi-value, .kpi-value-alt { font-size: 20px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 12px !important; }
    .cli-nome { font-size: 15px !important; }
}
</style>
""",
unsafe_allow_html=True
)

# =====================================================
# FUNÇÕES DE FORMATAÇÃO
# =====================================================
def formatar_valor(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def formatar_cpf(cpf):
    c = re.sub(r'\D', '', str(cpf))
    if len(c) == 11: return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"
    return cpf

def formatar_data(data_str):
    try: return datetime.strptime(str(data_str)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return "-"

def cor_status(status):
    s = str(status).lower()
    if s == "pago": return "background: #e6f4ea; color: #137333; border: 1px solid #137333;"
    if s == "enviado": return "background: #e8f0fe; color: #1a73e8; border: 1px solid #1a73e8;"
    if s == "entregue": return "background: #f3e8fd; color: #6a1b9a; border: 1px solid #6a1b9a;"
    if "desist" in s: return "background: #fce8e6; color: #c5221f; border: 1px solid #c5221f;"
    return "background: #fef7e0; color: #b06000; border: 1px solid #b06000;" # Recebido


# =====================================================
# BUSCA E PROCESSAMENTO DE DADOS (AGRUPAMENTO)
# =====================================================
@st.cache_data(ttl=30)
def carregar_dados_clientes():
    try:
        res = supabase.table("pedidos").select("*").order("created_at", desc=True).execute()
        pedidos = res.data or []
    except Exception:
        return []

    clientes_dict = {}

    for p in pedidos:
        status = str(p.get("status", "")).strip().capitalize()
        
        # Só consideramos o cliente se ele tiver pedidos válidos (ignoramos desistências para o ranking)
        if status in ["Desistência", "Desistencia"]:
            continue

        cpf = re.sub(r'\D', '', str(p.get("cliente_cpf", "")))
        tel = re.sub(r'\D', '', str(p.get("cliente_telefone", "")))
        nome = str(p.get("cliente_nome", "")).strip()
        
        # A chave primária é o CPF. Se não tiver, agrupa pelo Telefone.
        chave = cpf if cpf else tel
        if not chave: continue
        
        if chave not in clientes_dict:
            clientes_dict[chave] = {
                "nome": nome,
                "cpf": cpf,
                "telefone": tel,
                "total_gasto": 0.0,
                "qtd_pedidos": 0,
                "pedidos": [],
                "ultima_compra": p.get("created_at")
            }
            
        clientes_dict[chave]["pedidos"].append(p)
        clientes_dict[chave]["qtd_pedidos"] += 1
        
        # Soma o valor APENAS se o pedido foi Pago, Enviado ou Entregue
        if status in ["Pago", "Enviado", "Entregue"]:
            clientes_dict[chave]["total_gasto"] += float(p.get("valor_total", 0) or 0)

    # Converte para lista e ordena pelos que mais gastaram
    lista_final = list(clientes_dict.values())
    lista_final.sort(key=lambda x: x["total_gasto"], reverse=True)
    return lista_final

clientes = carregar_dados_clientes()


# =====================================================
# TÍTULO E KPIS GERAIS
# =====================================================
st.title("👥 Gestão de Clientes")
st.caption("Acompanhe o histórico e o engajamento dos seus clientes.")

if clientes:
    total_clientes = len(clientes)
    receita_total = sum(c["total_gasto"] for c in clientes)
    ticket_medio = receita_total / total_clientes if total_clientes > 0 else 0

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Clientes Ativos</div><div class="kpi-value-alt">{total_clientes}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Receita Gerada</div><div class="kpi-value">{formatar_valor(receita_total)}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Ticket Médio</div><div class="kpi-value">{formatar_valor(ticket_medio)}</div></div>', unsafe_allow_html=True)

st.write("")


# =====================================================
# PESQUISA E LISTAGEM
# =====================================================
pesquisa = st.text_input("🔍 Buscar cliente por Nome, CPF ou Telefone...")

if pesquisa:
    termo = pesquisa.lower().strip()
    clientes = [c for c in clientes if termo in c["nome"].lower() or termo in c["cpf"] or termo in c["telefone"]]

if not clientes:
    st.info("Nenhum cliente encontrado com os filtros atuais.")
    st.stop()

st.markdown("### 🏆 Ranking de Clientes")

for cli in clientes:
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 1.5])
        
        with c1:
            st.markdown(f'<div class="cli-nome">{cli["nome"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="cli-doc">CPF: {formatar_cpf(cli["cpf"]) if cli["cpf"] else "Não informado"} | 📱 +{cli["telefone"]}</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown(
                f'<div class="cli-metric">📦 Pedidos: {cli["qtd_pedidos"]} | 💰 Gasto: <span class="cli-metric-val">{formatar_valor(cli["total_gasto"])}</span></div>', 
                unsafe_allow_html=True
            )
            
        with c3:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            
            # Tratamento de DDI para WhatsApp (Mesma inteligência do painel de pedidos)
            tel_wpp = cli["telefone"]
            if len(tel_wpp) == 10 or len(tel_wpp) == 11:
                tel_wpp = f"55{tel_wpp}"
                
            texto_wpp = urllib.parse.quote(f"Olá {cli['nome']}, tudo bem? Aqui é da Doce Cesta Brasília!")
            link_wpp = f"https://wa.me/{tel_wpp}?text={texto_wpp}"
            st.link_button("💬 Falar no WhatsApp", url=link_wpp, use_container_width=True)

        # Histórico expansível embutido (A "página derivada" agora vive aqui dentro)
        with st.expander(f"📦 Ver Histórico de Pedidos ({cli['qtd_pedidos']})"):
            for ped in cli["pedidos"]:
                data_ped = formatar_data(ped.get("created_at"))
                cesta_ped = ped.get("cesta_nome", "Cesta Genérica")
                status_ped = str(ped.get("status", "Recebido")).capitalize()
                valor_ped = formatar_valor(ped.get("valor_total"))
                estilo_badge = cor_status(status_ped)
                
                st.markdown(
                    f"""
                    <div class="hist-row">
                        <div class="hist-date">{data_ped}</div>
                        <div class="hist-cesta">🎁 {cesta_ped}</div>
                        <div style="font-weight: 700; color: #2e7d32; width: 90px; text-align: right; margin-right: 10px;">{valor_ped}</div>
                        <div class="hist-status" style="{estilo_badge}">{status_ped}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
