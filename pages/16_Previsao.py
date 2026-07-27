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
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Previsão de Produção", page_icon="📅", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown(
"""
<style>
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1000px; }
h1 { font-size: 24px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 5px !important;}
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 16px !important; margin-bottom: 12px !important; box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04); }
.data-titulo { font-size: 16px; font-weight: 800; color: #b06000; text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #fef7e0; padding-bottom: 4px;}
.cesta-item { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; display: flex; justify-content: space-between;}
.cesta-qtd { background: #e6f4ea; color: #137333; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 800;}
div[data-testid="stExpander"] { border: 1px solid #dfcdbb !important; border-radius: 10px !important; background-color: #fffaf5 !important; }
div[data-testid="stExpander"] summary p { font-weight: 800 !important; color: #5a3b28 !important; font-size: 15px !important; }
</style>
""", unsafe_allow_html=True)

st.title("📅 Chão de Fábrica (Fila de Montagem)")
st.caption("Monte as cestas pagas agrupadas por data e, ao finalizar, despache para as Rotas de Entrega.")

# =====================================================
# BUSCA GERAL (SOMENTE STATUS PAGO)
# =====================================================
def buscar_pedidos_pagos():
    res = supabase.table("pedidos").select("*").eq("status", "Pago").execute()
    return res.data or []

pedidos = buscar_pedidos_pagos()

if not pedidos:
    st.success("🎉 Não há pedidos pagos aguardando produção para os próximos dias.")
    st.stop()

# =====================================================
# LÓGICA DE AGRUPAMENTO
# =====================================================
resumo = {}
hoje = date.today()

for p in pedidos:
    dt_str = p.get("data_entrega")
    if not dt_str: continue
        
    try:
        dt_obj = datetime.strptime(dt_str[:10], "%Y-%m-%d").date()
        if dt_obj < hoje: continue # Ignora atrasados do passado
        
        dias_diff = (dt_obj - hoje).days
        
        if dias_diff == 0: label_dia = f"HOJE ({dt_obj.strftime('%d/%m')})"
        elif dias_diff == 1: label_dia = f"AMANHÃ ({dt_obj.strftime('%d/%m')})"
        elif dias_diff == 2: label_dia = f"DEPOIS DE AMANHÃ ({dt_obj.strftime('%d/%m')})"
        else: label_dia = f"DAQUI A {dias_diff} DIAS ({dt_obj.strftime('%d/%m')})"
        
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
    
    with st.expander(f"🛒 Pedido #{pid} | {p.get('cliente_nome', '-')} | 🎁 {p.get('cesta_nome', '-')} | {status_badge}"):
        
        # --- Resumo para Contexto ---
        st.markdown(f"**📍 Endereço:** {p.get('endereco', 'Não informado')}")
        st.markdown(f"**🕒 Horário/Turno:** {p.get('periodo_entrega', '')} - {p.get('horario_combinado', '')}")
        st.markdown(f"**✨ Especial:** {p.get('pedido_especial', '')}")
        st.divider()
        
        st.markdown("#### 🧺 Checklist de Montagem")
        novo_checklist = {}
        
        # 1. Cesta Padrão (Limpando "Inclusos:")
        cesta_obj = buscar_cesta(p.get("cesta_id")) if p.get("cesta_id") else {}
        descricao_cesta = cesta_obj.get("descricao", "") if cesta_obj else ""
        if descricao_cesta:
            bloco_inclusos = descricao_cesta
            if "Inclusos:" in descricao_cesta: bloco_inclusos = descricao_cesta.split("Inclusos:")[1]
            elif "inclusos:" in descricao_cesta.lower(): bloco_inclusos = descricao_cesta.lower().split("inclusos:")[1]
            bloco_inclusos = bloco_inclusos.split("\n\n")[0]
            
            st.write("**Itens Padrão:**")
            itens_desc = [i.strip() for i in bloco_inclusos.split(";") if i.strip()]
            for idx, item in enumerate(itens_desc):
                chave_chk = f"📦 {item}"
                novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_desc_{pid}_{idx}")
        
        # 2. Personalização do Cliente
        produtos = p.get("produtos", "")
        if produtos:
            st.write("**Personalização:**")
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
            st.write("**Complementos e Extras:**")
            for idx, ad in enumerate(adicionais_bd):
                chave_chk = f"➕ {ad.get('nome_produto', '')}"
                novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_ad_{pid}_{idx}")
            if valor_extras > 0:
                chave_chk = "💲 Acréscimo Cobrado (Extras)"
                novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_extra_{pid}")
        
        # 4. Mensagem do Cartão
        mensagem = p.get("mensagem", "")
        if mensagem:
            st.write("**Mensagem do Cartão:**")
            st.info(f"_{mensagem}_")
            chave_chk = "✅ Cartão impresso e anexado à cesta"
            novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_msg_{pid}")
            
        st.divider()
        
        # --- Ações ---
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
            if st.button("🚚 Enviar para Rota de Entrega", key=f"btn_rota_{pid}", type="primary", use_container_width=True):
                # Força a cesta para pronta e despacha
                supabase.table("pedidos").update({
                    "checklist": novo_checklist,
                    "cesta_montada": True,
                    "status": "Enviado"
                }).eq("id", pid).execute()
                st.success("Despachado! Movendo para a fila de entregas...")
                time.sleep(1)
                st.rerun(scope="app")


# =====================================================
# INTERFACE DE USUÁRIO (PAINEL DE PRODUÇÃO)
# =====================================================
for data, info in dados_previsao.items():
    with st.container(border=True):
        st.markdown(f"<div class='data-titulo'>{info['label']} (Total: {info['total']})</div>", unsafe_allow_html=True)
        
        # Resumo de Cestas
        for cesta, qtd in info["cestas_agrupadas"].items():
            st.markdown(f"<div class='cesta-item'><span>📦 {cesta}</span> <span class='cesta-qtd'>{qtd} un</span></div>", unsafe_allow_html=True)
        
        st.write("")
        st.markdown("<h5 style='color:#5a3b28;'>🛠️ Pedidos para Montar:</h5>", unsafe_allow_html=True)
        
        # Renderiza os expansores de checklist para cada pedido
        for p in info["pedidos_lista"]:
            render_checklist_pedido(p)
