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
# CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM
# =====================================================
st.set_page_config(page_title="Chão de Fábrica", page_icon="🏭", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown(
"""
<style>
.block-container { padding-top: 1.5rem !important; padding-bottom: 2.5rem !important; max-width: 1200px; }
h1 { font-size: 26px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 5px !important;}

/* Barra de Resumo (Pills) */
.resumo-bar {
    background: linear-gradient(135deg, #fffbf7, #f7efe6);
    border: 1px solid #dfcdbb;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(90,59,40,0.04);
}
.resumo-header { font-size: 12px; font-weight: 800; color: #9d7d65; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px; }
.pills-container { display: flex; flex-wrap: wrap; gap: 10px; }
.cesta-pill {
    background: #ffffff; border: 1px solid #dfcdbb; padding: 6px 14px; border-radius: 20px; 
    font-size: 14px; font-weight: 700; color: #5a3b28; display: flex; align-items: center; gap: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.cesta-pill-qtd { background: #b06000; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 800; }

/* Cards de Pedido Modernos (Estilo Kanban) */
.pedido-card {
    background: #ffffff;
    border: 1px solid #e8ddd3;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(90,59,40,0.03);
    transition: all 0.2s ease;
}
.pedido-card:hover {
    border-color: #dfcdbb;
    box-shadow: 0 6px 16px rgba(90,59,40,0.08);
}
.card-top {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
}
.pedido-id { font-size: 13px; font-weight: 800; color: #9d7d65; }
.badge-status-pendente { background: #fef7e0; color: #b06000; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 800; }
.badge-status-pronta { background: #e6f4ea; color: #137333; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 800; }

.cliente-titulo { font-size: 16px; font-weight: 800; color: #333; margin-bottom: 2px; }
.cesta-subtitulo { font-size: 14px; font-weight: 700; color: #b06000; margin-bottom: 8px; }
.info-linha-card { font-size: 13px; color: #555; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }

/* Barra de Progresso Customizada */
.progresso-container { background: #f3ece6; border-radius: 6px; height: 8px; width: 100%; margin: 12px 0; overflow: hidden; }
.progresso-barra { background: linear-gradient(90deg, #b06000, #137333); height: 100%; border-radius: 6px; transition: width 0.3s ease; }

/* Responsividade Mobile */
@media (max-width: 768px) {
    .block-container { padding-top: 1rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    h1 { font-size: 22px !important; }
    .cesta-pill { font-size: 13px; padding: 5px 12px; }
}
</style>
""",
unsafe_allow_html=True
)

st.title("🏭 Chão de Fábrica (Fila de Produção)")
st.caption("Acompanhe o andamento das cestas em cards interativos e compactos.")

# =====================================================
# GERENCIAMENTO DE ESTADO PARA O "MODO MONTAGEM" (MODAL/GAVETA)
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
# TELA DE CHECKLIST EM MODO "GAVETA" (QUANDO SELECIONADO)
# =====================================================
if st.session_state.pedido_em_montagem:
    # Busca o pedido atual selecionado
    p_ativo = next((p for p in pedidos if p["id"] == st.session_state.pedido_em_montagem), None)
    
    if p_ativo:
        with st.container(border=True):
            col_tit, col_fechar = st.columns([5, 1])
            with col_tit:
                st.markdown(f"### 🛠️ Montando Pedido #{p_ativo['id']} — {p_ativo.get('cliente_nome')}")
            with col_fechar:
                if st.button("❌ Fechar", use_container_width=True):
                    st.session_state.pedido_em_montagem = None
                    st.rerun()
            
            st.markdown(f"**🎁 Cesta:** {p_ativo.get('cesta_nome')} | **📍 Endereço:** {p_ativo.get('endereco', 'N/I')}")
            st.markdown(f"**🕒 Turno/Horário:** {p_ativo.get('periodo_entrega', '')} - {p_ativo.get('horario_combinado', 'Livre')}")
            if p_ativo.get('pedido_especial'):
                st.info(f"✨ **Solicitação Especial:** {p_ativo.get('pedido_especial')}")
            
            st.divider()
            st.markdown("#### 📦 Checklist de Verificação")
            
            checklist_salvo = p_ativo.get("checklist") or {}
            if isinstance(checklist_salvo, str):
                try: checklist_salvo = json.loads(checklist_salvo)
                except: checklist_salvo = {}
                
            novo_checklist = {}
            
            # 1. Cesta Padrão
            cesta_obj = buscar_cesta(p_ativo.get("cesta_id")) if p_ativo.get("cesta_id") else {}
            descricao_cesta = cesta_obj.get("descricao", "") if cesta_obj else ""
            if descricao_cesta:
                bloco_inclusos = descricao_cesta
                if "Inclusos:" in descricao_cesta: bloco_inclusos = descricao_cesta.split("Inclusos:")[1]
                elif "inclusos:" in descricao_cesta.lower(): bloco_inclusos = descricao_cesta.lower().split("inclusos:")[1]
                bloco_inclusos = bloco_inclusos.split("\n\n")[0]
                
                itens_desc = [i.strip() for i in bloco_inclusos.split(";") if i.strip()]
                if itens_desc:
                    st.caption("Itens Padrão da Cesta:")
                    for idx, item in enumerate(itens_desc):
                        chave_chk = f"📦 {item}"
                        novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_desc_{p_ativo['id']}_{idx}")
            
            # 2. Personalização do Cliente
            produtos = p_ativo.get("produtos", "")
            if produtos:
                st.caption("Personalização do Cliente:")
                for idx, prod in enumerate(produtos.split("\n")):
                    prod_limpo = prod.replace('•', '').strip()
                    if prod_limpo:
                        chave_chk = f"✔️ {prod_limpo}"
                        novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_prod_{p_ativo['id']}_{idx}")

            # 3. Adicionais e Extras
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
            
            valor_extras = float(p_ativo.get("valor_extras", 0))
            if adicionais_bd or valor_extras > 0:
                st.caption("Complementos e Extras:")
                for idx, ad in enumerate(adicionais_bd):
                    chave_chk = f"➕ {ad.get('nome_produto', '')}"
                    novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_ad_{p_ativo['id']}_{idx}")
                if valor_extras > 0:
                    chave_chk = "💲 Acréscimo Cobrado (Extras)"
                    novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_extra_{p_ativo['id']}")
            
            # 4. Mensagem do Cartão
            mensagem = p_ativo.get("mensagem", "")
            if mensagem:
                st.caption("Mensagem do Cartão:")
                st.info(f"_{mensagem}_")
                chave_chk = "✅ Cartão impresso e anexado"
                novo_checklist[chave_chk] = st.checkbox(chave_chk, value=checklist_salvo.get(chave_chk, False), key=f"chk_msg_{p_ativo['id']}")
                
            st.write("")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 Salvar Progresso da Montagem", use_container_width=True):
                    tudo_pronto = len(novo_checklist) > 0 and all(novo_checklist.values())
                    try:
                        supabase.table("pedidos").update({
                            "checklist": novo_checklist,
                            "cesta_montada": tudo_pronto
                        }).eq("id", p_ativo['id']).execute()
                        st.toast("✅ Progresso salvo com sucesso!")
                        time.sleep(0.5)
                        st.rerun(scope="app")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {e}")
            with col_b2:
                if st.button("🚚 Concluir e Enviar p/ Rota", type="primary", use_container_width=True):
                    try:
                        supabase.table("pedidos").update({
                            "checklist": novo_checklist,
                            "cesta_montada": True,
                            "status": "Enviado"
                        }).eq("id", p_ativo['id']).execute()
                        st.success("Cesta pronta e despachada para a rota de entregas!")
                        st.session_state.pedido_em_montagem = None
                        time.sleep(1)
                        st.rerun(scope="app")
                    except Exception as e:
                        st.error(f"❌ Erro ao despachar: {e}")
        st.divider()


# =====================================================
# INTERFACE PRINCIPAL (ABAS POR DATA + CARDS COMPACTOS)
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
                    <div class='resumo-header'>📊 Metas do Dia (Total: {info['total']} cestas)</div>
                    <div class='pills-container'>
                        {html_pills}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
            
            # --- GRID DE CARDS (2 COLUNAS) ---
            pedidos_lista = info["pedidos_lista"]
            col_esq, col_dir = st.columns(2)
            
            for idx, p in enumerate(pedidos_lista):
                pid = p["id"]
                montada = p.get("cesta_montada", False)
                status_badge = '<span class="badge-status-pronta">✅ PRONTA</span>' if montada else '<span class="badge-status-pendente">⏳ PENDENTE</span>'
                
                # Cálculo da barra de progresso baseada no checklist salvo
                chk_atual = p.get("checklist") or {}
                if isinstance(chk_atual, str):
                    try: chk_atual = json.loads(chk_atual)
                    except: chk_atual = {}
                
                total_itens = len(chk_atual) if chk_atual else 1
                itens_marcados = sum(1 for v in chk_atual.values() if v)
                porcentagem = int((itens_marcados / total_itens) * 100) if total_itens > 0 else 0
                
                # Endereço resumido (apenas bairro/cidade)
                endereco_completo = p.get('endereco', 'Endereço não informado')
                bairro = endereco_completo.split(',')[-1].split('(')[0].strip() if ',' in endereco_completo else endereco_completo
                
                card_html = f"""
                <div class="pedido-card">
                    <div class="card-top">
                        <span class="pedido-id">#{pid}</span>
                        {status_badge}
                    </div>
                    <div class="cliente-titulo">{p.get('cliente_nome', '-')}</div>
                    <div class="cesta-subtitulo">🎁 {p.get('cesta_nome', '-')}</div>
                    <div class="info-linha-card">📍 <strong>Local:</strong> {bairro}</div>
                    <div class="info-linha-card">🕒 <strong>Turno:</strong> {p.get('periodo_entrega', 'Livre')} ({p.get('horario_combinado', 'Flexível')})</div>
                    <div class="progresso-container">
                        <div class="progresso-barra" style="width: {porcentagem}%;"></div>
                    </div>
                    <div style="font-size: 11px; color: #775a46; text-align: right; font-weight: 700;">{itens_marcados}/{total_itens} itens verificados ({porcentagem}%)</div>
                </div>
                """
                
                # Altera a coluna de distribuição
                col_alvo = col_esq if idx % 2 == 0 else col_dir
                
                with col_alvo:
                    st.markdown(card_html, unsafe_allow_html=True)
                    # Botão limpo abaixo do card para abrir a montagem sem ocupar espaço fixo
                    if st.button("🔍 Abrir Montagem", key=f"abrir_montagem_{pid}", use_container_width=True):
                        st.session_state.pedido_em_montagem = pid
                        st.rerun()
