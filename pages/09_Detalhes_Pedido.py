import streamlit as st
import pandas as pd
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador
from datetime import datetime

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

/* Linhas de Dados Cadastrais (Texto colado ao título) */
.info-row { border-bottom: 1px dashed #f5eee6; padding: 8px 0; font-size: 14px;}
.info-label { font-weight: 700; color: #775a46; margin-right: 6px; }
.info-value { font-weight: 600; color: #2c1e14; }

/* Linhas Financeiras (Valores jogados para a direita) */
.finance-row { display: flex; justify-content: space-between; border-bottom: 1px dashed #f5eee6; padding: 8px 0; font-size: 14px;}

.item-box { background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 14px; }
.item-box b { color: #5a3b28; }

.val-total { font-size: 22px; font-weight: 800; color: #137333; text-align: right; margin-top: 15px; padding-top: 15px; border-top: 2px solid #e8ddd3;}

div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 800 !important; }

@media print {
    header, footer, section[data-testid="stSidebar"], div[data-testid="stButton"] { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important;}
    .ficha-card { box-shadow: none !important; border: none !important; padding: 0 !important; }
}
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
@st.cache_data(ttl=5, show_spinner=False)
def obter_detalhe(p_id):
    res = supabase.table("pedidos").select("*").eq("id", p_id).execute()
    return res.data[0] if res.data else None

pedido = obter_detalhe(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()

is_b2b = "[B2B]" in pedido['cliente_nome']
cliente_limpo = pedido['cliente_nome'].replace("[B2B]", "").strip()
cor_classe = "b2b" if is_b2b else ""
tipo_texto = "🏢 PEDIDO CORPORATIVO (B2B)" if is_b2b else "👤 PEDIDO VAREJO (B2C)"

# Funções de formatação
def formata_data(d_str):
    if not d_str: return ""
    try: return datetime.strptime(d_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return d_str

def formata_moeda(v):
    try: return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

# Botão Voltar Corrigido (Sem erro de callback)
if st.button("⬅️ Voltar para o Mural de Pedidos"):
    st.switch_page("pages/02_Pedidos.py")

st.markdown(f"""
<div class="ficha-card">
    <div class="ficha-header {cor_classe}">
        <div>
            <h2 style="margin:0; color: {'#137333' if is_b2b else '#c5721f'}; font-weight: 800;">FICHA DE PRODUÇÃO</h2>
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

    if pedido.get('mensagem'):
        st.markdown(f"<div class='section-title {cor_classe}'>💌 MENSAGEM DO CARTÃO</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#f9f9f9; padding:12px; border-radius:8px; font-size:14px; font-style:italic; color:#4a2e1b; border-left: 3px solid #c5721f;">
            "{pedido.get('mensagem')}"
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

    st.markdown(f"<div class='section-title {cor_classe}'>💰 RESUMO FINANCEIRO</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="finance-row"><span class="info-label">Forma Pagamento:</span><span class="info-value" style="text-align: right;">{pedido.get('pagamento', '')}</span></div>
    <div class="finance-row"><span class="info-label">Taxa de Frete:</span><span class="info-value" style="text-align: right;">{formata_moeda(pedido.get('valor_frete', 0))}</span></div>
    <div class="val-total">TOTAL: {formata_moeda(pedido.get('valor_total', 0))}</div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# BOTÕES DE AÇÃO NA FICHA
# ==========================================
st.write("")
col_a1, col_a2, col_a3, col_a4 = st.columns(4)

with col_a1:
    if st.button("🖨️ Imprimir Ficha", use_container_width=True):
        st.info("Pressione Ctrl + P (ou Cmd + P) no seu teclado para gerar o documento limpo!")

with col_a2:
    if st.button("✏️ Alterar Pedido", use_container_width=True):
        # Salva o ID para edição e redireciona dependendo do tipo
        st.session_state['editar_pedido_id'] = pedido_id
        if is_b2b:
            st.switch_page("pages/18_Corporativo.py")
        else:
            # Caso queira direcionar para o fluxo de varejo caso possua
            st.warning("A edição direta está otimizada para o painel Corporativo (B2B).")

with col_a3:
    # Botão rápido para avançar status
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

with col_a4:
    if st.button("🗑️ Excluir", type="primary", use_container_width=True):
        supabase.table("pedidos").delete().eq("id", pedido_id).execute()
        st.session_state['pedido_detalhe_id'] = None
        st.switch_page("pages/02_Pedidos.py")
