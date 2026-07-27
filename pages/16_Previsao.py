import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from services.telegram_service import enviar_notificacao_telegram
from utils.permissao import administrador_operador

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
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 900px; }
h1 { font-size: 24px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 5px !important;}
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 16px !important; margin-bottom: 12px !important; box-shadow: 0 2px 6px rgba(90, 59, 40, 0.04); }
.data-titulo { font-size: 16px; font-weight: 800; color: #b06000; text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #fef7e0; padding-bottom: 4px;}
.cesta-item { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; display: flex; justify-content: space-between;}
.cesta-qtd { background: #e6f4ea; color: #137333; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 800;}
</style>
""", unsafe_allow_html=True)

st.title("📅 Previsão de Produção (Cestas Pagas)")
st.caption("Acompanhe o volume de cestas que precisam ser montadas para os próximos dias.")

# =====================================================
# LÓGICA DE BUSCA E AGRUPAMENTO
# =====================================================
@st.cache_data(ttl=60) # Atualiza a cada 1 minuto
def buscar_previsao_producao():
    # Busca apenas pedidos PAGOS
    res = supabase.table("pedidos").select("id, cesta_nome, data_entrega").eq("status", "Pago").execute()
    pedidos = res.data or []
    
    if not pedidos: return {}

    # Agrupa por data e conta as cestas
    resumo = {}
    hoje = date.today()
    
    for p in pedidos:
        dt_str = p.get("data_entrega")
        if not dt_str: continue
            
        try:
            dt_obj = datetime.strptime(dt_str[:10], "%Y-%m-%d").date()
            if dt_obj < hoje: continue # Ignora atrasados não resolvidos aqui
            
            dias_diff = (dt_obj - hoje).days
            
            if dias_diff == 0: label_dia = f"HOJE ({dt_obj.strftime('%d/%m')})"
            elif dias_diff == 1: label_dia = f"AMANHÃ ({dt_obj.strftime('%d/%m')})"
            elif dias_diff == 2: label_dia = f"DEPOIS DE AMANHÃ ({dt_obj.strftime('%d/%m')})"
            else: label_dia = f"DAQUI A {dias_diff} DIAS ({dt_obj.strftime('%d/%m')})"
            
            # Ordenação interna (chave para organizar o dicionário)
            chave_ordem = dt_obj.strftime("%Y-%m-%d")
            
            if chave_ordem not in resumo:
                resumo[chave_ordem] = {"label": label_dia, "cestas": {}, "total": 0}
                
            nome_cesta = p.get("cesta_nome", "Cesta Não Informada")
            resumo[chave_ordem]["cestas"][nome_cesta] = resumo[chave_ordem]["cestas"].get(nome_cesta, 0) + 1
            resumo[chave_ordem]["total"] += 1
            
        except: pass
        
    # Ordena as datas cronologicamente
    resumo_ordenado = dict(sorted(resumo.items()))
    return resumo_ordenado

dados_previsao = buscar_previsao_producao()


# =====================================================
# FUNÇÃO DE DISPARO DO TELEGRAM
# =====================================================
def disparar_alerta_telegram(dados):
    if not dados:
        enviar_notificacao_telegram("ℹ️ *PREVISÃO DE PRODUÇÃO*\nNenhum pedido pago pendente para os próximos dias.")
        return
        
    texto = "⚠️ *ALERTA DE PRODUÇÃO - PRÓXIMOS DIAS* ⚠️\n\n"
    
    for data, info in dados.items():
        texto += f"📅 *{info['label']}* - Total: {info['total']} cesta(s)\n"
        for cesta, qtd in info["cestas"].items():
            texto += f"   📦 {qtd}x {cesta}\n"
        texto += "\n"
        
    texto += "Acesse o sistema para ver os detalhes."
    enviar_notificacao_telegram(texto)


# =====================================================
# INTERFACE DE USUÁRIO
# =====================================================
if not dados_previsao:
    st.success("🎉 Não há pedidos pagos aguardando produção para os próximos dias.")
else:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for data, info in dados_previsao.items():
            with st.container(border=True):
                st.markdown(f"<div class='data-titulo'>{info['label']} (Total: {info['total']})</div>", unsafe_allow_html=True)
                for cesta, qtd in info["cestas"].items():
                    st.markdown(f"<div class='cesta-item'><span>📦 {cesta}</span> <span class='cesta-qtd'>{qtd} un</span></div>", unsafe_allow_html=True)

    with col2:
        with st.container(border=True):
            st.markdown("### ⚙️ Alertas Telegram")
            st.write("O sistema compila todas as cestas com status **Pago** e organiza por data para a linha de produção.")
            
            st.write("")
            if st.button("🚀 Enviar Resumo Agora", type="primary", use_container_width=True):
                with st.spinner("Enviando para o Telegram..."):
                    disparar_alerta_telegram(dados_previsao)
                st.success("✅ Alerta enviado com sucesso!")
