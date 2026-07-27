import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import json
import time

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador
from services.cesta_service import buscar_cesta
from services.pedido_adicional_service import listar_adicionais_pedido

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS AVANÇADO
# =====================================================
st.set_page_config(page_title="Chão de Fábrica", page_icon="🏭", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown(
"""
<style>
/* Layout Principal */
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; max-width: 1200px; }
h1 { font-size: 26px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 5px !important;}

/* Cards de Resumo (Topo) */
.dashboard-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }
.summary-card { 
    flex: 1; min-width: 140px; 
    background: linear-gradient(145deg, #ffffff, #fffaf5); 
    border: 1px solid #dfcdbb; 
    border-radius: 12px; 
    padding: 16px; 
    text-align: center; 
    box-shadow: 0 4px 6px rgba(90, 59, 40, 0.05); 
    transition: transform 0.2s ease;
}
.summary-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(90, 59, 40, 0.08); }
.summary-title { font-size: 13px; font-weight: 700; color: #775a46; text-transform: uppercase; margin-bottom: 4px; }
.summary-value { font-size: 26px; font-weight: 800; color: #137333; line-height: 1; }

/* Estilização dos Expansores (Cards de Pedido) */
div[data-testid="stExpander"] { 
    border: 1px solid #e8ddd3 !important; 
    border-radius: 12px !important; 
    background-color: #ffffff !important; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    margin-bottom: 12px !important;
}
div[data-testid="stExpander"] summary { padding: 12px 16px !important; }
div[data-testid="stExpander"] summary p { font-weight: 800 !important; color: #5a3b28 !important; font-size: 14px !important; }
div[data-testid="stExpander"]:hover { border-color: #dfcdbb !important; }

/* Badges e Textos internos */
.info-linha { font-size: 13px; color: #444; margin-bottom: 4px; }
.info-linha strong { color: #5a3b28; }
.checklist-title { font-size: 13px; font-weight: 800; color: #b06000; margin-top: 12px; margin-bottom: 6px; border-bottom: 1px dashed #f0e0d0; padding-bottom: 2px;}

/* Responsividade Celular */
@media (max-width: 768px) {
    .block-container { padding-top: 1rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    h1 { font-size: 22px !important; }
    .summary-card { min-width: 45%; padding: 12px; }
    .summary-value { font-size: 20px; }
    /* Força os botões a ficarem lado a lado se possível, ou empilhados bonitos */
    div[data-testid="stHorizontalBlock"] { gap: 8px !important; }
}
</style>
""", unsafe_allow_html=True)

st.title("🏭 Chão de Fábrica (Fila de Produção)")
st.caption("Organize as cestas do dia, faça o checklist de montagem e despache direto para a Rota de Entrega.")

# =====================================================
# BUSCA GERAL (SOMENTE STATUS PAGO)
# =====================================================
def buscar_pedidos_pagos():
    res = supabase.table("pedidos").select("*").eq("status", "Pago").execute()
    return res.data or []

pedidos = buscar_pedidos_pagos()

if not pedidos:
    st.success("🎉 Excelente trabalho! Não há pedidos pagos aguardando produção para os próximos dias.")
    st.stop()

# =====================================================
# LÓGICA DE AGRUPAMENTO POR DATA
# =====================================================
resumo = {}
hoje = date.today()

for p in pedidos:
    dt_str = p.get("data_entrega")
    if not dt_str: continue
        
    try:
        dt_obj = datetime.strptime(dt_str[:10], "%Y-%m-%d").date()
        # Ignora atrasados do passado que não foram resolvidos na tela anterior
        if dt_obj < hoje: continue 
        
        dias_diff = (dt_obj - hoje).days
        
        if dias_diff == 0: label_dia = f"HOJE ({dt_obj.strftime('%d/%m')})"
        elif dias_diff == 1: label_dia = f"AMANHÃ ({dt_obj.strftime('%d/%m')})"
        elif dias_diff == 2: label_dia = f"DEPOIS ({dt_obj.strftime('%d/%m')})"
        else: label_dia = f"{dias_diff} DIAS ({dt_obj.strftime('%d/%m')})"
        
        chave_ordem = dt_obj.strftime("%Y-%m-%d")
        
        if chave_ordem not in resumo:
            resumo[chave_ordem] = {"label": label_dia, "cestas_agrupadas": {}, "pedidos_lista": [], "total": 0}
            
        nome_cesta = p.get("cesta_nome", "Cesta Não Informada")
        resumo[chave_ordem]["cestas_agrupadas"][nome_cesta] = resumo[chave_ordem]["cestas_agrupadas"].get(nome_cesta, 0) + 1
        resumo[chave_ordem]["pedidos_lista"].append(p)
        resumo[chave_ordem]["total"] += 1
        
    except: pass
    
dados_previsao = dict(sorted(resumo.items()))

# =====================================================
# RENDERIZAÇÃO DO CHECKLIST (FRAGMENTO ISOLADO)
# =====================================================
@st.fragment
def render_checklist_pedido(p):
    pid = p["id"]
    montada = p.get("cesta_montada", False)
    
    checklist_salvo = p.get("checklist") or {}
    if isinstance(checklist_salvo, str):
        try: checklist_salvo = json.loads(checklist_salvo)
        except: checklist_salvo = {}
        
    status_badge = "✅ PRONTA" if montada else "⏳ PENDENTE"
    
    with st.expander(f"🛒 #{pid} | {p.get('cliente_nome', '-')} | 🎁 {p.get('cesta_nome', '-')} | {status_badge}", expanded=not montada):
        
        # --- Resumo para Contexto (Estilo mais compacto) ---
        st.markdown(f"<div class='info-linha'><strong>📍 Endereço:</strong> {p.get('endereco', 'N/I')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-linha'><strong>🕒 Horário/Turno:</strong> {p.get('periodo_entrega', '')} - {p.get('horario_combinado', '')}</div>", unsafe_allow_html=True)
        if p.get('pedido_especial'):
            st.markdown(f"<div class='info-linha'><strong>✨ Especial:</strong> {p.get('pedido_especial', '')}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='checklist-title'>🧺 Checklist de Montagem</div>", unsafe_allow_html=True)
        novo_checklist = {}
        
        # 1. Cesta Padrão (Limpando "Inclusos:")
        cesta_obj = buscar_cesta(p.get("cesta_id")) if p.get("cesta_id") else {}
        descricao_cesta = cesta_obj.get("descricao", "") if cesta_obj else ""
        if descricao_cesta:
            bloco_inclusos = descricao_cesta
            if "Inclusos:" in descricao_cesta: bloco_inclusos = descricao_cesta.split("Inclusos:")[1]
            elif "inclusos:" in descricao_cesta.lower(): bloco_inclusos = descricao_cesta.lower().split("inclusos:")[1]
            bloco_inclusos = bloco_inclusos.split("\n\n")[0]
            
            itens_desc = [i.strip() for i in bloco_inclusos.split(";") if i.strip()]
            if itens_desc:
                st.caption("Itens Padrão:")
                for idx, item in enumerate(itens_desc):
                    chave_chk = f"📦 {item}"
                    novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_desc_{pid}_{idx}")
        
        # 2. Personalização do Cliente
        produtos = p.get("produtos", "")
        if produtos:
            st.caption("Personalização do Cliente:")
            for idx, prod in enumerate(produtos.split("\n")):
                prod_limpo = prod.replace('•', '').strip()
                if prod_limpo:
                    chave_chk = f"✔️ {prod_limpo}"
                    novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_prod_{pid}_{idx}")

        # 3. Adicionais e Extras
        adicionais_bd = []
        try:
            lista_bruta = listar_adicionais_pedido(pid)
            nomes_vistos = set()
            for ad in lista_bruta:
                nome_ad = ad.get("nome_produto")
                if nome_ad and nome_ad not in nomes_vistos:
                    adicionais_bd.append(ad)
                    nomes_vistos.add(nome_ad)
        except: pass
        
        valor_extras = float(p.get("valor_extras", 0))
        if adicionais_bd or valor_extras > 0:
            st.caption("Complementos e Extras:")
            for idx, ad in enumerate(adicionais_bd):
                chave_chk = f"➕ {ad.get('nome_produto', '')}"
                novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_ad_{pid}_{idx}")
            if valor_extras > 0:
                chave_chk = "💲 Acréscimo Cobrado (Extras)"
                novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_extra_{pid}")
        
        # 4. Mensagem do Cartão
        mensagem = p.get("mensagem", "")
        if mensagem:
            st.caption("Mensagem do Cartão:")
            st.info(f"_{mensagem}_")
            chave_chk = "✅ Cartão impresso e anexado"
            novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_msg_{pid}")
            
        st.write("")
        
        # --- Ações (Botões Lado a Lado) ---
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Salvar Montagem", key=f"btn_salvar_{pid}", use_container_width=True):
                tudo_pronto = len(novo_checklist) > 0 and all(novo_checklist.values())
                supabase.table("pedidos").update({
                    "checklist": novo_checklist,
                    "cesta_montada": tudo_pronto
                }).eq("id", pid).execute()
                st.toast("✅ Progresso salvo com sucesso!")
                time.sleep(0.5)
                st.rerun(scope="app")
                
        with c2:
            if st.button("🚚 Enviar para Rota", key=f"btn_rota_{pid}", type="primary", use_container_width=True):
                # Força a cesta para pronta e despacha
                supabase.table("pedidos").update({
                    "checklist": novo_checklist,
                    "cesta_montada": True,
                    "status": "Enviado"
                }).eq("id", pid).execute()
                st.success("Despachado! Indo para a fila de entregas...")
                time.sleep(1)
                st.rerun(scope="app")


# =====================================================
# INTERFACE DE USUÁRIO (ABAS POR DATA + GRID MASONRY)
# =====================================================
if dados_previsao:
    # Cria as abas (Tabs) com as datas disponíveis
    nomes_abas = [info["label"] for data, info in dados_previsao.items()]
    abas = st.tabs(nomes_abas)
    
    for i, (data, info) in enumerate(dados_previsao.items()):
        with abas[i]:
            st.markdown(f"### 🎯 Meta do Dia (Total: {info['total']} cestas)")
            
            # 1. Cards de Resumo (Métricas do Dia)
            st.markdown("<div class='dashboard-grid'>", unsafe_allow_html=True)
            cols_metricas = st.columns(min(len(info["cestas_agrupadas"]), 4))
            
            for j, (cesta, qtd) in enumerate(info["cestas_agrupadas"].items()):
                with cols_metricas[j % len(cols_metricas)]:
                    st.markdown(
                        f"""
                        <div class='summary-card'>
                            <div class='summary-title'>{cesta}</div>
                            <div class='summary-value'>{qtd}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### 🛠️ Fila de Montagem")
            
            # 2. Grid de Pedidos (2 colunas no Desktop, empilhado no Mobile)
            pedidos_lista = info["pedidos_lista"]
            
            col_esq, col_dir = st.columns(2)
            
            for idx, p in enumerate(pedidos_lista):
                # Distribui alternadamente nas duas colunas para criar um grid inteligente
                if idx % 2 == 0:
                    with col_esq:
                        render_checklist_pedido(p)
                else:
                    with col_dir:
                        render_checklist_pedido(p)
