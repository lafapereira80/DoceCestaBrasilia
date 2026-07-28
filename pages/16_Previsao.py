import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import time

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador
from services.cesta_service import buscar_cesta
from services.pedido_adicional_service import listar_adicionais_pedido

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E DESIGN PREMIUM
# =====================================================
st.set_page_config(page_title="Painel de Produção", page_icon="🏭", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b !important; margin-bottom: 2px !important; letter-spacing: -0.5px; }
h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-top: 15px !important; margin-bottom: 10px !important; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

/* =========================================
   BARRA DE RESUMO DAS METAS (PILLS)
========================================== */
.resumo-bar {
    background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%);
    border: 1px solid #e8ddd3;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.resumo-header { font-size: 13px; font-weight: 800; color: #775a46; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; }
.pills-container { display: flex; flex-wrap: wrap; gap: 10px; }
.cesta-pill {
    background: #faf7f3; border: 1px solid #e8ddd3; padding: 6px 14px; border-radius: 20px; 
    font-size: 14px; font-weight: 800; color: #5a3b28; display: flex; align-items: center; gap: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s ease;
}
.cesta-pill:hover { border-color: #d2bfae; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(90,59,40,0.08); }
.cesta-pill-qtd { background: #b06000; color: #ffffff; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 800; }

/* =========================================
   CARDS KANBAN (PEDIDOS NA FILA)
========================================== */
.pedido-card {
    background: #ffffff;
    border: 1px solid #e8ddd3;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.pedido-card:hover {
    border-color: #d2bfae;
    box-shadow: 0 8px 20px rgba(90,59,40,0.08);
    transform: translateY(-2px);
}
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #f3ece6; padding-bottom: 6px; }
.pedido-id { font-size: 13px; font-weight: 800; color: #9d7d65; text-transform: uppercase; letter-spacing: 0.5px; }

/* Badges Status Kanban */
.badge-status-pendente { background: #fef7e0; color: #b06000; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 800; border: 1px solid #fce8b2; }
.badge-status-pronta { background: #e6f4ea; color: #137333; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 800; border: 1px solid #ceead6; }

/* Textos do Card Kanban */
.cliente-titulo { font-size: 17px; font-weight: 800; color: #2c1e14; margin-bottom: 2px; }
.cesta-subtitulo { font-size: 15px; font-weight: 800; color: #b06000; margin-bottom: 10px; }
.info-linha-card { font-size: 13px; color: #555; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; font-weight: 500; }

/* Barra de Progresso Customizada */
.progresso-container { background: #f3ece6; border-radius: 8px; height: 8px; width: 100%; margin: 14px 0 6px 0; overflow: hidden; }
.progresso-barra { background: linear-gradient(90deg, #b06000, #137333); height: 100%; border-radius: 8px; transition: width 0.4s ease; }

/* =========================================
   ESTILIZAÇÃO DA GAVETA DE MONTAGEM (CHECKLIST)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 14px !important;
    padding: 20px 24px !important;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05);
}

.montagem-header { background: #faf7f3; border: 1px solid #e8ddd3; border-radius: 12px; padding: 16px; margin-bottom: 16px; border-left: 4px solid #b06000; }
.secao-titulo { font-size: 14px; font-weight: 800; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 15px; margin-bottom: 10px; border-bottom: 1px dashed #dfcdbb; padding-bottom: 4px; }

/* Checkboxes (Pílulas Clicáveis) */
div[data-testid="stCheckbox"] {
    background: #faf7f3;
    border: 1px solid #e8ddd3;
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    transition: all 0.2s ease;
}
div[data-testid="stCheckbox"]:hover {
    background: #fdfcfb;
    border-color: #d2bfae;
    transform: translateX(2px);
}

/* =========================================
   BOTÕES DE AÇÃO
========================================== */
div[data-testid="stButton"] > button { font-size: 14px !important; font-weight: 800 !important; border-radius: 10px !important; min-height: 40px !important; transition: all 0.2s ease; }
div[data-testid="stButton"] > button:hover { transform: scale(1.02); }

/* =========================================
   RESPONSIVIDADE MOBILE E BOTÕES (LADO A LADO)
========================================== */
@media (max-width: 768px) {
    .block-container { padding: 1rem 0.5rem !important; }
    h1 { font-size: 24px !important; }
    .cesta-pill { font-size: 13px; padding: 5px 12px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 14px 16px !important; }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-top: 10px !important;
        justify-content: space-between;
    }
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important;
    }
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) button {
        width: 100% !important; padding: 6px 0px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)

st.title("🏭 Painel de Produção (Chão de Fábrica)")
st.caption("Acompanhe o volume diário, abra a gaveta de montagem e valide os itens via checklist.")

# =====================================================
# GERENCIAMENTO DE ESTADO PARA O "MODO MONTAGEM"
# =====================================================
if "pedido_em_montagem" not in st.session_state:
    st.session_state.pedido_em_montagem = None

# =====================================================
# BUSCA GERAL (SOMENTE STATUS PAGO)
# =====================================================
def buscar_pedidos_pagos():
    res = supabase.table("pedidos").select("*").eq("status", "Pago").execute()
    return res.data or []

pedidos = buscar_pedidos_pagos()

if not pedidos:
    st.success("🎉 Excelente trabalho! A fila de produção está limpa. Não há pedidos pagos aguardando montagem.")
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
# TELA DE CHECKLIST EM MODO "GAVETA" (COM SELECIONAR TODOS)
# =====================================================
if st.session_state.pedido_em_montagem:
    p_ativo = next((p for p in pedidos if p["id"] == st.session_state.pedido_em_montagem), None)
    
    if p_ativo:
        st.write("")
        with st.container(border=True):
            col_tit, col_fechar = st.columns([4, 1])
            with col_tit:
                st.markdown(f"### 🛠️ Montagem da Cesta (Pedido #{p_ativo['id']})")
            with col_fechar:
                if st.button("❌ Fechar Painel", use_container_width=True):
                    st.session_state.pedido_em_montagem = None
                    st.rerun()
            
            # Cabeçalho Compacto do Pedido
            st.markdown(
                f"""
                <div class="montagem-header">
                    <div style="font-size: 18px; font-weight: 800; color: #2c1e14;">👤 {p_ativo.get('cliente_nome')}</div>
                    <div style="font-size: 15px; font-weight: 800; color: #b06000; margin-top: 4px; margin-bottom: 8px;">🎁 {p_ativo.get('cesta_nome')}</div>
                    <div style="font-size: 13px; color: #444; margin-top: 4px;">📍 <strong>Endereço:</strong> {p_ativo.get('endereco', 'N/I')}</div>
                    <div style="font-size: 13px; color: #444; margin-top: 2px;">🕒 <strong>Turno Ideal:</strong> {p_ativo.get('periodo_entrega', '')} ({p_ativo.get('horario_combinado', 'Livre')})</div>
                </div>
                """, unsafe_allow_html=True
            )
            
            if p_ativo.get('pedido_especial'):
                st.warning(f"✨ **Atenção - Solicitação Especial:** {p_ativo.get('pedido_especial')}")
            
            st.markdown("#### 📋 Checklist de Verificação Oficial")
            
            checklist_salvo = p_ativo.get("checklist") or {}
            if isinstance(checklist_salvo, str):
                try: checklist_salvo = json.loads(checklist_salvo)
                except: checklist_salvo = {}

            # Tratamento seguro para itens_consulta do banco (onde ficam salvos os extras dinâmicos e manuais)
            itens_consulta_salvos = p_ativo.get("itens_consulta") or {}
            if isinstance(itens_consulta_salvos, str):
                try: itens_consulta_salvos = json.loads(itens_consulta_salvos)
                except: itens_consulta_salvos = {}

            # Descobre antecipadamente todas as chaves de itens que compõem este pedido específico
            chaves_itens_pedido = []
            
            # 1. Itens Padrão
            cesta_obj = buscar_cesta(p_ativo.get("cesta_id")) if p_ativo.get("cesta_id") else {}
            descricao_cesta = cesta_obj.get("descricao", "") if cesta_obj else ""
            if descricao_cesta:
                bloco_inclusos = descricao_cesta
                if "Inclusos:" in descricao_cesta: bloco_inclusos = descricao_cesta.split("Inclusos:")[1]
                elif "inclusos:" in descricao_cesta.lower(): bloco_inclusos = descricao_cesta.lower().split("inclusos:")[1]
                bloco_inclusos = bloco_inclusos.split("\n\n")[0]
                for item in [i.strip() for i in bloco_inclusos.split(";") if i.strip()]:
                    chaves_itens_pedido.append(f"📦 {item}")
            
            # 2. Personalização
            produtos = p_ativo.get("produtos", "")
            if produtos:
                for prod_limpo in [p.replace('•', '').strip() for p in produtos.split("\n") if p.replace('•', '').strip()]:
                    chaves_itens_pedido.append(f"✔️ {prod_limpo}")
            
            # 3. Adicionais de Catálogo
            adicionais_bd = []
            try:
                lista_bruta = listar_adicionais_pedido(p_ativo['id'])
                nomes_vistos = set()
                for ad in lista_bruta:
                    nome_ad = ad.get("nome_produto")
                    if nome_ad and nome_ad not in nomes_vistos:
                        adicionais_bd.append(ad)
                        nomes_vistos.add(nome_ad)
            except: pass

            for ad in adicionais_bd:
                nome_ad = ad.get("nome_produto", "")
                if nome_ad:
                    chave_ad = f"➕ {nome_ad}"
                    if chave_ad not in chaves_itens_pedido:
                        chaves_itens_pedido.append(chave_ad)

            # 4. Extras Dinâmicos / Personalizados salvos no JSON do pedido
            for k, v in itens_consulta_salvos.items():
                if "Valor Manual de" not in k and not k.startswith("Valor de "):
                    chave_extra = f"🔹 {k}"
                    if chave_extra not in chaves_itens_pedido:
                        chaves_itens_pedido.append(chave_extra)
            
            # 5. Cartão
            if p_ativo.get("mensagem", ""):
                chaves_itens_pedido.append("✅ Cartão impresso e posicionado")

            # Botões de Ação Rápida em Lote (Marcar / Desmarcar Todos)
            col_m1, col_m2 = st.columns(2)
            marcar_todos_click = col_m1.button("✅ Marcar Todos os Itens", use_container_width=True)
            desmarcar_todos_click = col_m2.button("❌ Desmarcar Todos", use_container_width=True)
            
            if marcar_todos_click:
                for k in chaves_itens_pedido:
                    st.session_state[f"chk_item_{p_ativo['id']}_{k}"] = True
                st.toast("✅ Todos os itens foram marcados!")
                st.rerun()
            elif desmarcar_todos_click:
                for k in chaves_itens_pedido:
                    st.session_state[f"chk_item_{p_ativo['id']}_{k}"] = False
                st.toast("❌ Todos os itens foram desmarcados!")
                st.rerun()

            novo_checklist = {}
            
            # --- RENDERIZAÇÃO DOS ITENS PADRÃO ---
            itens_desc = []
            if descricao_cesta:
                bloco_inclusos = descricao_cesta
                if "Inclusos:" in descricao_cesta: bloco_inclusos = descricao_cesta.split("Inclusos:")[1]
                elif "inclusos:" in descricao_cesta.lower(): bloco_inclusos = descricao_cesta.lower().split("inclusos:")[1]
                bloco_inclusos = bloco_inclusos.split("\n\n")[0]
                itens_desc = [i.strip() for i in bloco_inclusos.split(";") if i.strip()]

            if itens_desc:
                st.markdown("<div class='secao-titulo'>📦 Itens Padrão do Catálogo</div>", unsafe_allow_html=True)
                cols_padrao = st.columns(2)
                for idx, item in enumerate(itens_desc):
                    chave_chk = f"📦 {item}"
                    val_padrao = checklist_salvo.get(chave_chk, False)
                    session_key = f"chk_item_{p_ativo['id']}_{chave_chk}"
                    if session_key in st.session_state:
                        val_padrao = st.session_state[session_key]

                    with cols_padrao[idx % 2]:
                        novo_checklist[chave_chk] = st.checkbox(chave_chk, value=val_padrao, key=session_key)
            
            # --- RENDERIZAÇÃO DA PERSONALIZAÇÃO ---
            if produtos:
                st.markdown("<div class='secao-titulo'>🍓 Personalização Escolhida no Fechamento</div>", unsafe_allow_html=True)
                prods_lista = [p.replace('•', '').strip() for p in produtos.split("\n") if p.replace('•', '').strip()]
                cols_pers = st.columns(2)
                for idx, prod_limpo in enumerate(prods_lista):
                    chave_chk = f"✔️ {prod_limpo}"
                    val_padrao = checklist_salvo.get(chave_chk, False)
                    session_key = f"chk_item_{p_ativo['id']}_{chave_chk}"
                    if session_key in st.session_state:
                        val_padrao = st.session_state[session_key]

                    with cols_pers[idx % 2]:
                        novo_checklist[chave_chk] = st.checkbox(chave_chk, value=val_padrao, key=session_key)

            # --- RENDERIZAÇÃO DOS ADICIONAIS DE CATÁLOGO E EXTRAS DINÂMICOS ---
            if adicionais_bd or itens_consulta_salvos:
                st.markdown("<div class='secao-titulo'>🎀 Adicionais e Extras do Pedido</div>", unsafe_allow_html=True)
                cols_add = st.columns(2)
                contador_add = 0
                
                # Adicionais de Catálogo
                for ad in adicionais_bd:
                    nome_ad = ad.get('nome_produto', '')
                    if nome_ad:
                        chave_chk = f"➕ {nome_ad}"
                        val_padrao = checklist_salvo.get(chave_chk, False)
                        session_key = f"chk_item_{p_ativo['id']}_{chave_chk}"
                        if session_key in st.session_state:
                            val_padrao = st.session_state[session_key]

                        with cols_add[contador_add % 2]:
                            novo_checklist[chave_chk] = st.checkbox(chave_chk, value=val_padrao, key=session_key)
                        contador_add += 1

                # Extras Dinâmicos / Personalizados
                for k, v in itens_consulta_salvos.items():
                    if "Valor Manual de" not in k and not k.startswith("Valor de "):
                        chave_chk = f"🔹 {k}"
                        val_padrao = checklist_salvo.get(chave_chk, False)
                        session_key = f"chk_item_{p_ativo['id']}_{chave_chk}"
                        if session_key in st.session_state:
                            val_padrao = st.session_state[session_key]

                        with cols_add[contador_add % 2]:
                            novo_checklist[chave_chk] = st.checkbox(chave_chk, value=val_padrao, key=session_key)
                        contador_add += 1
            
            # --- RENDERIZAÇÃO DA MENSAGEM DO CARTÃO ---
            mensagem = p_ativo.get("mensagem", "")
            if mensagem:
                st.markdown("<div class='secao-titulo'>💌 Mensagem do Cartão</div>", unsafe_allow_html=True)
                st.info(f"_{mensagem}_")
                chave_chk = "✅ Cartão impresso e posicionado"
                val_padrao = checklist_salvo.get(chave_chk, False)
                session_key = f"chk_item_{p_ativo['id']}_{chave_chk}"
                if session_key in st.session_state:
                    val_padrao = st.session_state[session_key]

                novo_checklist[chave_chk] = st.checkbox(chave_chk, value=val_padrao, key=session_key)
                
            st.write("")
            st.divider()
            
            # --- BOTÕES DE AÇÃO INFERIORES ---
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 Salvar Checklist (Progresso)", use_container_width=True):
                    tudo_pronto = len(novo_checklist) > 0 and all(novo_checklist.values())
                    try:
                        supabase.table("pedidos").update({
                            "checklist": novo_checklist,
                            "cesta_montada": tudo_pronto
                        }).eq("id", p_ativo['id']).execute()
                        st.toast("✅ Progresso da montagem salvo!")
                        time.sleep(0.5)
                        st.rerun(scope="app")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {e}")
            with col_b2:
                if st.button("🚚 Finalizar e Despachar para Rota", type="primary", use_container_width=True):
                    try:
                        supabase.table("pedidos").update({
                            "checklist": novo_checklist,
                            "cesta_montada": True,
                            "status": "Enviado"
                        }).eq("id", p_ativo['id']).execute()
                        st.success("✅ Excelente! Cesta pronta e despachada para a equipe de rotas/entregas.")
                        st.session_state.pedido_em_montagem = None
                        time.sleep(1.5)
                        st.rerun(scope="app")
                    except Exception as e:
                        st.error(f"❌ Erro ao despachar: {e}")
        st.divider()


# =====================================================
# INTERFACE PRINCIPAL (ABAS POR DATA + CARDS KANBAN)
# =====================================================
if dados_previsao:
    nomes_abas = [info["label"] for data, info in dados_previsao.items()]
    abas = st.tabs(nomes_abas)
    
    for i, (data, info) in enumerate(dados_previsao.items()):
        with abas[i]:
            
            # --- BARRA DE RESUMO (PILLS) ---
            html_pills = ""
            for cesta, qtd in info["cestas_agrupadas"].items():
                html_pills += f"<div class='cesta-pill'>📦 {cesta} <span class='cesta-pill-qtd'>{qtd}</span></div>"
                
            st.markdown(
                f"""
                <div class='resumo-bar'>
                    <div class='resumo-header'>📊 Resumo de Metas do Dia (Total Fila: {info['total']} cestas)</div>
                    <div class='pills-container'>
                        {html_pills}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
            
            # --- GRID DE CARDS KANBAN (2 COLUNAS) ---
            pedidos_lista = info["pedidos_lista"]
            col_esq, col_dir = st.columns(2)
            
            for idx, p in enumerate(pedidos_lista):
                pid = p["id"]
                montada = p.get("cesta_montada", False)
                status_badge = '<span class="badge-status-pronta">✅ PRONTA</span>' if montada else '<span class="badge-status-pendente">⏳ PENDENTE</span>'
                
                chk_atual = p.get("checklist") or {}
                if isinstance(chk_atual, str):
                    try: chk_atual = json.loads(chk_atual)
                    except: chk_atual = {}
                
                total_itens = len(chk_atual) if chk_atual else 1
                itens_marcados = sum(1 for v in chk_atual.values() if v)
                porcentagem = int((itens_marcados / total_itens) * 100) if total_itens > 0 else 0
                
                endereco_completo = p.get('endereco', 'Endereço não informado')
                bairro = endereco_completo.split(',')[-1].split('(')[0].strip() if ',' in endereco_completo else endereco_completo
                
                card_html = f"""
                <div class="pedido-card">
                    <div class="card-top">
                        <span class="pedido-id">Pedido #{pid}</span>
                        {status_badge}
                    </div>
                    <div class="cliente-titulo">{p.get('cliente_nome', '-')}</div>
                    <div class="cesta-subtitulo">🎁 {p.get('cesta_nome', '-')}</div>
                    <div class="info-linha-card">📍 <strong>Localização:</strong> {bairro}</div>
                    <div class="info-linha-card">🕒 <strong>Turno Ideal:</strong> {p.get('periodo_entrega', 'Livre')} ({p.get('horario_combinado', 'Flexível')})</div>
                    <div class="progresso-container">
                        <div class="progresso-barra" style="width: {porcentagem}%;"></div>
                    </div>
                    <div style="font-size: 11px; color: #775a46; text-align: right; font-weight: 800;">Verificação: {itens_marcados}/{total_itens} ({porcentagem}%)</div>
                </div>
                """
                
                col_alvo = col_esq if idx % 2 == 0 else col_dir
                
                with col_alvo:
                    st.markdown(card_html, unsafe_allow_html=True)
                    if st.button("🔍 Abrir Gaveta de Montagem", key=f"abrir_montagem_{pid}", use_container_width=True):
                        st.session_state.pedido_em_montagem = pid
                        st.rerun()

st.write("")
st.divider()
st.caption("🏭 Controle Oficial de Produção - Doce Cesta Brasília")
