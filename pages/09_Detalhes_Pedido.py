import streamlit as st
import pandas as pd
import requests
import re
import urllib.parse
from datetime import datetime, date

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

st.set_page_config(page_title="Detalhes do Pedido", page_icon="🔍", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# ==========================================
# CSS PREMIUM (ESTILO NOTA FISCAL / FICHA TÉCNICA)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b; }

.ficha-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 30px;
    box-shadow: 0 4px 20px rgba(90, 59, 40, 0.05); margin-bottom: 20px;
}
.ficha-header { border-bottom: 3px solid #c5721f; padding-bottom: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;}
.ficha-header.b2b { border-bottom-color: #137333; }

.section-title { font-size: 16px; font-weight: 800; color: #c5721f; margin-bottom: 10px; margin-top: 20px;}
.section-title.b2b { color: #137333; }

.info-row { border-bottom: 1px dashed #f5eee6; padding: 8px 0; font-size: 14px;}
.info-label { font-weight: 700; color: #775a46; margin-right: 6px; }
.info-value { font-weight: 600; color: #2c1e14; }

.finance-row { display: flex; justify-content: space-between; border-bottom: 1px dashed #f5eee6; padding: 8px 0; font-size: 14px;}
.item-box { background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 14px; }
.val-total { font-size: 22px; font-weight: 800; color: #137333; text-align: right; margin-top: 15px; padding-top: 15px; border-top: 2px solid #e8ddd3;}

div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# Pega o ID da sessão
pedido_id = st.session_state.get('pedido_detalhe_id')

if not pedido_id:
    st.warning("Nenhum pedido selecionado.")
    if st.button("⬅️ Voltar aos Pedidos"):
        st.switch_page("pages/02_Pedidos.py")
    st.stop()

# Carrega os dados do pedido
def obter_detalhe(p_id):
    res = supabase.table("pedidos").select("*").eq("id", p_id).execute()
    return res.data[0] if res.data else None

pedido = obter_detalhe(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()

is_b2b = "[B2B]" in pedido.get('cliente_nome', '')
cliente_limpo = pedido.get('cliente_nome', '').replace("[B2B]", "").strip()
cor_classe = "b2b" if is_b2b else ""
tipo_texto = "🏢 PEDIDO CORPORATIVO (B2B)" if is_b2b else "👤 PEDIDO VAREJO (B2C)"

# Funções de formatação
def formata_data(d_str):
    if not d_str: return ""
    try: return datetime.strptime(str(d_str)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return d_str

def formata_moeda(v):
    try: return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def tratar_preco(v):
    try: return float(str(v).replace(",", "."))
    except: return 0.0

# Botão Voltar
if st.button("⬅️ Voltar para o Mural de Pedidos"):
    st.switch_page("pages/02_Pedidos.py")

st.markdown(f"""
<div class="ficha-card">
    <div class="ficha-header {cor_classe}">
        <div>
            <h2 style="margin:0; color: {'#137333' if is_b2b else '#c5721f'}; font-weight: 800;">DETALHES DO PEDIDO</h2>
            <div style="font-size:12px; color:#666; font-weight:700;">Pedido #{pedido['id']}</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size:14px; font-weight:800;">STATUS: {pedido.get('status', '')}</div>
            <div style="font-size:11px; font-weight:700; color: {'#137333' if is_b2b else '#c5721f'};">{tipo_texto}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"<div class='section-title {cor_classe}'>👤 DADOS DO CLIENTE / DESTINATÁRIO</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-row"><span class="info-label">Nome / Empresa:</span><span class="info-value">{cliente_limpo}</span></div>
    <div class="info-row"><span class="info-label">Contato/Telefone:</span><span class="info-value">{pedido.get('cliente_telefone', '')}</span></div>
    <div class="info-row"><span class="info-label">CPF / CNPJ:</span><span class="info-value">{pedido.get('cliente_cpf', '')}</span></div>
    <div class="info-row"><span class="info-label">Homenagem/Motivo:</span><span class="info-value">{pedido.get('motivo_homenagem', 'Não informado')}</span></div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='section-title {cor_classe}'>📍 LOGÍSTICA E ENTREGA</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-row"><span class="info-label">Data Acordada:</span><span class="info-value">{formata_data(pedido.get('data_entrega'))}</span></div>
    <div class="info-row"><span class="info-label">Período:</span><span class="info-value">{pedido.get('periodo_entrega', '')}</span></div>
    <div class="info-row"><span class="info-label">Recebedor (A/C):</span><span class="info-value">{pedido.get('destinatario_nome', '')}</span></div>
    <div class="info-row" style="border:none;"><span class="info-label">Endereço de Entrega:</span></div>
    <div style="background:#f9f9f9; padding:10px; border-radius:8px; font-size:13px; font-weight:600; color:#333; margin-top:5px;">
        {pedido.get('endereco', 'Não informado')}
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='section-title {cor_classe}'>🎁 DETALHAMENTO DOS PRODUTOS</div>", unsafe_allow_html=True)
    
    produtos_str = pedido.get('produtos', '')
    adicionais_str = pedido.get('adicionais', '')
    
    if produtos_str:
        st.markdown("<div style='font-size:12px; font-weight:700; color:#666; margin-bottom:5px;'>PACOTES E CESTAS:</div>", unsafe_allow_html=True)
        for linha in produtos_str.split("\n"):
            if linha.strip(): st.markdown(f"<div class='item-box'>📦 {linha.strip()}</div>", unsafe_allow_html=True)
            
    if adicionais_str:
        st.markdown("<div style='font-size:12px; font-weight:700; color:#666; margin-top:15px; margin-bottom:5px;'>EXTRAS E INFORMAÇÕES:</div>", unsafe_allow_html=True)
        for linha in adicionais_str.split("\n"):
            linha_limpa = linha.strip()
            if linha_limpa:
                if "Desconto" in linha_limpa:
                    st.markdown(f"<div class='item-box' style='border-color:#fce8b2; background:#fef7e0; color:#b06000;'>🔻 <b>{linha_limpa}</b></div>", unsafe_allow_html=True)
                elif "EXTRAS" not in linha_limpa:
                    st.markdown(f"<div class='item-box'>✨ {linha_limpa}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='section-title {cor_classe}'>💰 RESUMO FINANCEIRO ATUAL</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="finance-row"><span class="info-label">Forma Pagamento:</span><span class="info-value" style="text-align: right;">{pedido.get('pagamento', '')}</span></div>
    <div class="finance-row"><span class="info-label">Taxa de Frete:</span><span class="info-value" style="text-align: right;">{formata_moeda(pedido.get('valor_frete', 0))}</span></div>
    <div class="val-total">TOTAL: {formata_moeda(pedido.get('valor_total', 0))}</div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAINEL DE FECHAMENTO (FRETE, DESCONTO, EXTRAS NÃO CADASTRADOS)
# ==========================================
with st.container(border=True):
    st.markdown("<h4 style='color: #c5721f; margin-top: 0;'>⚙️ Fechamento e Ajustes Financeiros</h4>", unsafe_allow_html=True)
    
    # Extrai o valor do frete e total atual para os inputs
    frete_atual = tratar_preco(pedido.get('valor_frete', 0))
    total_atual = tratar_preco(pedido.get('valor_total', 0))
    
    col_fc1, col_fc2 = st.columns(2)
    with col_fc1:
        novo_frete = st.number_input("Taxa de Frete (R$)", min_value=0.0, step=5.0, value=frete_atual)
    with col_fc2:
        desconto_perc = st.number_input("Desconto Concedido (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0)

    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #5a3b28; margin-top: 10px;'>➕ Inserir Produto/Extra Não Cadastrado</div>", unsafe_allow_html=True)
    col_ex1, col_ex2 = st.columns([3, 1])
    with col_ex1:
        nome_extra_novo = st.text_input("Nome do Item Extra", placeholder="Ex: Urso de pelúcia extra", label_visibility="collapsed")
    with col_ex2:
        valor_extra_novo = st.number_input("Valor R$", min_value=0.0, step=5.0, value=0.0, label_visibility="collapsed")

    # Cálculo automático preliminar
    # Estima subtotal a partir do total atual menos frete
    sub_estimado = total_atual - frete_atual
    v_desconto = sub_estimado * (desconto_perc / 100)
    v_extra = valor_extra_novo if nome_extra_novo.strip() else 0.0
    total_calculado = sub_estimado - v_desconto + novo_frete + v_extra

    if st.button("💾 Aplicar e Salvar Ajustes de Fechamento", use_container_width=True, type="primary"):
        adicionais_atuais = pedido.get('adicionais', '') or ""
        novo_adicional = adicionais_atuais
        if desconto_perc > 0:
            novo_adicional += f"\n🔻 Desconto de {desconto_perc}% aplicado."
        if nome_extra_novo.strip():
            novo_adicional += f"\n✨ 1x {nome_extra_novo.strip()} (R$ {formata_moeda(v_extra)})"

        dados_fechamento = {
            "valor_frete": novo_frete,
            "valor_total": total_calculado,
            "adicionais": novo_adicional.strip()
        }
        try:
            supabase.table("pedidos").update(dados_fechamento).eq("id", pedido_id).execute()
            st.success("✅ Fechamento atualizado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

# ==========================================
# RESUMO PARA PAGAMENTO COM OS ITENS
# ==========================================
with st.container(border=True):
    st.markdown("<h3 style='color: #137333; margin-top: 0; border-bottom: 2px solid #ceead6; padding-bottom: 8px;'>💳 Resumo Oficial para Pagamento</h3>", unsafe_allow_html=True)
    
    st.markdown(f"**Cliente:** {cliente_limpo} | **Telefone:** {pedido.get('cliente_telefone', '-')}")
    st.markdown("**Composição do Pedido:**")
    
    if produtos_str:
        for linha in produtos_str.split("\n"):
            if linha.strip(): st.markdown(f"- 📦 {linha.strip()}")
            
    if adicionais_str:
        for linha in adicionais_str.split("\n"):
            if linha.strip(): st.markdown(f"- ✨ {linha.strip()}")

    st.markdown("---")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown(f"**Forma de Pagamento:** {pedido.get('pagamento', 'Pix')}")
        st.markdown(f"**Taxa de Frete:** {formata_moeda(pedido.get('valor_frete', 0))}")
    with col_r2:
        st.markdown(f"### Valor Final: <span style='color: #137333;'>{formata_moeda(pedido.get('valor_total', 0))}</span>", unsafe_allow_html=True)

    # Botão WhatsApp
    fone_cliente = re.sub(r'\D', '', pedido.get('cliente_telefone', ''))
    resumo_pagamento_wpp = f"""*RESUMO PARA PAGAMENTO — DOCE CESTA BRASÍLIA* 🎁\n\n👤 *Olá {cliente_limpo}!* Segue o resumo dos itens e valor para pagamento:\n\n📦 *Produto:* {pedido.get('cesta_nome')}\n💰 *Valor Total a Pagar:* {formata_moeda(pedido.get('valor_total'))}\n💳 *Forma de Pagamento:* {pedido.get('pagamento')}\n📅 *Entrega:* {formata_data(pedido.get('data_entrega'))} ({pedido.get('periodo_entrega')})\n📍 *Local:* {pedido.get('endereco')}\n\nQualquer dúvida estamos à disposição! 🌻"""
    link_wpp = f"https://wa.me/55{fone_cliente}?text={urllib.parse.quote(resumo_pagamento_wpp)}" if fone_cliente else "#"

    st.write("")
    if fone_cliente:
        st.markdown(f'<a href="{link_wpp}" target="_blank" style="background-color: #25d366 !important; color: white !important; font-weight: 800; border-radius: 12px; padding: 14px; text-align: center; display: block; text-decoration: none;">📱 Enviar Resumo de Pagamento via WhatsApp</a>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Telefone do comprador não cadastrado para envio via WhatsApp.")

st.write("")

# ==========================================
# BOTÕES DE AÇÃO INFERIORES
# ==========================================
col_a1, col_a2, col_a3, col_a4 = st.columns(4)

with col_a1:
    if st.button("✏️ Alterar Pedido Completo", use_container_width=True):
        st.session_state['editar_pedido_id'] = pedido_id
        if is_b2b:
            st.switch_page("pages/18_Corporativo.py")
        else:
            st.switch_page("pages/19_Pedido_Manual.py")

with col_a2:
    status_atual = pedido.get('status')
    if status_atual in ["Pendente", "Pago"]:
        if st.button("⏩ Prod.", use_container_width=True, type="primary"):
            supabase.table("pedidos").update({"status": "Em Produção"}).eq("id", pedido_id).execute()
            st.rerun()
    elif status_atual == "Em Produção":
        if st.button("⏩ Rota", use_container_width=True, type="primary"):
            supabase.table("pedidos").update({"status": "Em Rota de Entrega"}).eq("id", pedido_id).execute()
            st.rerun()
    elif status_atual == "Em Rota de Entrega":
        if st.button("✅ Entregue", use_container_width=True, type="primary"):
            supabase.table("pedidos").update({"status": "Entregue"}).eq("id", pedido_id).execute()
            st.rerun()
    else:
        st.button("✔️ Finalizado", disabled=True, use_container_width=True)

with col_a3:
    if st.button("🗑️ Excluir Pedido", type="primary", use_container_width=True):
        supabase.table("pedidos").delete().eq("id", pedido_id).execute()
        st.session_state['pedido_detalhe_id'] = None
        st.switch_page("pages/02_Pedidos.py")
