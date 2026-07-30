import streamlit as st
import pandas as pd
import requests
import re
import urllib.parse
from datetime import datetime, date

from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Detalhes do Pedido", page_icon="🔍", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# =====================================================
# CSS PREMIUM (UI/UX DASHBOARD CARDS)
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #2c1e14; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1300px !important; }

/* Header Banner */
.order-header {
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%);
    padding: 24px 30px; border-radius: 20px; border: 1px solid #e8ddd3;
    box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04); margin-bottom: 24px;
    display: flex; justify-content: space-between; align-items: center;
}
.order-id { font-size: 32px; font-weight: 800; color: #4a2e1b; margin: 0; line-height: 1.2; letter-spacing: -0.5px; }
.order-type-badge { background: #fef7e0; color: #b06000; padding: 4px 12px; border-radius: 8px; font-size: 11px; font-weight: 800; border: 1px solid #fce8b2; display: inline-block; margin-top: 6px; }
.order-type-badge.corp { background: #e6f4ea; color: #137333; border-color: #ceead6; }
.status-label { font-size: 12px; color: #775a46; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; text-align: right; }
.status-value { font-size: 18px; font-weight: 800; color: #c5721f; text-align: right; }

/* Content Cards */
.info-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 24px;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.02); margin-bottom: 20px; height: 100%;
}
.card-title { font-size: 15px; font-weight: 800; color: #c5721f; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px; text-transform: uppercase; }
.card-title.finance { color: #137333; border-bottom-color: #ceead6; }

/* Data Rows */
.data-group { margin-bottom: 14px; }
.data-label { font-size: 11.5px; color: #8c7362; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
.data-value { font-size: 14.5px; color: #2c1e14; font-weight: 600; }
.highlight-box { background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 10px; padding: 12px; font-size: 14px; font-style: italic; color: #4a2e1b; border-left: 4px solid #c5721f; margin-top: 8px; }

/* Items / Products */
.item-pill { background: #faf7f3; border: 1px solid #e8ddd3; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-size: 13.5px; font-weight: 600; color: #4a2e1b; display: flex; align-items: center; gap: 8px; }
.item-pill.discount { background: #fef7e0; border-color: #fce8b2; color: #b06000; }

/* Finance Summary */
.receipt-box { background: #f9f9f9; border: 1px dashed #ccc; border-radius: 12px; padding: 18px; margin-top: 20px; }
.receipt-line { display: flex; justify-content: space-between; font-size: 14px; color: #555; margin-bottom: 8px; font-weight: 500;}
.receipt-line.total { border-top: 2px solid #ddd; padding-top: 10px; margin-top: 10px; font-size: 20px; font-weight: 800; color: #137333; }

/* Buttons */
div[data-testid="stButton"] button { border-radius: 10px !important; font-weight: 800 !important; font-size: 14px !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button:hover { transform: translateY(-2px) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important; }
.wpp-btn > a { background: #25d366 !important; color: white !important; font-weight: 800 !important; font-size: 15px !important; border-radius: 12px !important; padding: 14px !important; display: flex; justify-content: center; align-items: center; gap: 8px; text-decoration: none !important; transition: all 0.2s ease !important; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.2) !important; }
.wpp-btn > a:hover { background: #1ebd5a !important; transform: translateY(-2px) !important; box-shadow: 0 6px 15px rgba(37, 211, 102, 0.3) !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CARREGAMENTO E VALIDAÇÃO DO PEDIDO
# =====================================================
pedido_id = st.session_state.get('pedido_detalhe_id')

if not pedido_id:
    st.warning("Nenhum pedido selecionado.")
    if st.button("⬅️ Voltar aos Pedidos"):
        st.switch_page("pages/02_Pedidos.py")
    st.stop()

def obter_detalhe(p_id):
    res = supabase.table("pedidos").select("*").eq("id", p_id).execute()
    return res.data[0] if res.data else None

pedido = obter_detalhe(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()

# Helpers de Formatação
is_b2b = "[B2B]" in pedido.get('cliente_nome', '')
cliente_limpo = pedido.get('cliente_nome', '').replace("[B2B]", "").strip()
tipo_classe = "corp" if is_b2b else ""
tipo_texto = "🏢 CORPORATIVO (B2B)" if is_b2b else "🛍️ VAREJO (B2C)"

def formata_data(d_str):
    if not d_str: return "-"
    try: return datetime.strptime(str(d_str)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return d_str

def formata_moeda(v):
    try: return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def tratar_preco(v):
    try: return float(str(v).replace(",", "."))
    except: return 0.0

if st.button("⬅️ Voltar para o Mural", key="btn_voltar_topo"):
    st.switch_page("pages/02_Pedidos.py")

# =====================================================
# BANNER SUPERIOR
# =====================================================
st.markdown(f"""
<div class="order-header">
    <div>
        <h1 class="order-id">Pedido #{pedido['id']}</h1>
        <span class="order-type-badge {tipo_classe}">{tipo_texto}</span>
    </div>
    <div>
        <div class="status-label">STATUS ATUAL</div>
        <div class="status-value">{pedido.get('status', 'Recebido')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# GRID DE INFORMAÇÕES (2 COLUNAS)
# =====================================================
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown(f"""
    <div class="info-card">
        <div class="card-title">👤 Comprador & Destinatário</div>
        <div class="data-group"><div class="data-label">Cliente / Empresa</div><div class="data-value">{cliente_limpo}</div></div>
        <div class="data-group"><div class="data-label">Contato (WhatsApp)</div><div class="data-value">{pedido.get('cliente_telefone', '-')}</div></div>
        <div class="data-group"><div class="data-label">CPF / CNPJ</div><div class="data-value">{pedido.get('cliente_cpf', '-')}</div></div>
        <div class="data-group" style="margin-top: 20px;"><div class="data-label">Recebedor (Destinatário)</div><div class="data-value">{pedido.get('destinatario_nome', '-')}</div></div>
        <div class="data-group"><div class="data-label">Ocasião / Motivo</div><div class="data-value">{pedido.get('motivo_homenagem', '-')}</div></div>
    </div>
    """, unsafe_allow_html=True)

with col_info2:
    endereco_formatado = pedido.get('endereco', 'Não informado')
    msg_cartao = pedido.get('mensagem', '')
    
    html_entrega = f"""
    <div class="info-card">
        <div class="card-title">📍 Logística e Entrega</div>
        <div class="data-group"><div class="data-label">Data Agendada</div><div class="data-value">{formata_data(pedido.get('data_entrega'))}</div></div>
        <div class="data-group"><div class="data-label">Período / Horário</div><div class="data-value">{pedido.get('periodo_entrega', '-')}</div></div>
        <div class="data-group"><div class="data-label">Endereço de Entrega</div><div class="highlight-box" style="border-left-color: #1a73e8;">{endereco_formatado}</div></div>
    """
    if msg_cartao:
        html_entrega += f"""<div class="data-group" style="margin-top: 15px;"><div class="data-label">💌 Mensagem do Cartão</div><div class="highlight-box">"{msg_cartao}"</div></div>"""
    
    html_entrega += "</div>"
    st.markdown(html_entrega, unsafe_allow_html=True)


# =====================================================
# GRID DE PRODUTOS E FECHAMENTO FINANCEIRO
# =====================================================
col_prod, col_fin = st.columns(2)

with col_prod:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎁 Detalhamento do Pedido</div>', unsafe_allow_html=True)
    
    produtos_str = pedido.get('produtos', '')
    adicionais_str = pedido.get('adicionais', '')
    
    if produtos_str:
        st.markdown("<div class='data-label'>Cestas e Pacotes</div>", unsafe_allow_html=True)
        for linha in produtos_str.split("\n"):
            if linha.strip(): st.markdown(f"<div class='item-pill'>📦 {linha.strip()}</div>", unsafe_allow_html=True)
            
    if adicionais_str:
        st.markdown("<div class='data-label' style='margin-top: 15px;'>Extras e Adicionais</div>", unsafe_allow_html=True)
        for linha in adicionais_str.split("\n"):
            linha_limpa = linha.strip()
            if linha_limpa:
                if "Desconto" in linha_limpa:
                    st.markdown(f"<div class='item-pill discount'>🔻 {linha_limpa}</div>", unsafe_allow_html=True)
                elif "EXTRAS" not in linha_limpa:
                    st.markdown(f"<div class='item-pill'>✨ {linha_limpa}</div>", unsafe_allow_html=True)
    
    if not produtos_str and not adicionais_str:
        st.caption("Nenhum item detalhado neste pedido.")
        
    st.markdown('</div>', unsafe_allow_html=True)

with col_fin:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title finance">💰 Fechamento & Pagamento</div>', unsafe_allow_html=True)
    
    frete_atual = tratar_preco(pedido.get('valor_frete', 0))
    total_atual = tratar_preco(pedido.get('valor_total', 0))
    forma_pagamento = pedido.get('pagamento', 'Pix')
    
    # 1. Inputs de Fechamento
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        novo_frete = st.number_input("Frete / Taxa (R$)", min_value=0.0, step=5.0, value=frete_atual)
    with c_f2:
        desconto_perc = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0)

    lista_status = ["Recebido", "Pendente", "Pago", "Em Produção", "Em Rota de Entrega", "Entregue", "Desistência"]
    novo_status = st.selectbox("Status do Pedido", lista_status, index=lista_status.index(pedido.get('status', 'Recebido')) if pedido.get('status') in lista_status else 0)

    st.markdown("<div class='data-label' style='margin-top: 8px;'>Inserir Extra Não Cadastrado</div>", unsafe_allow_html=True)
    c_ex1, c_ex2 = st.columns([2.5, 1])
    with c_ex1: nome_extra_novo = st.text_input("Nome", placeholder="Ex: Vinho", label_visibility="collapsed")
    with c_ex2: valor_extra_novo = st.number_input("Valor", min_value=0.0, step=5.0, value=0.0, label_visibility="collapsed")

    # Cálculos
    sub_estimado = total_atual - frete_atual
    v_desconto = sub_estimado * (desconto_perc / 100)
    v_extra = valor_extra_novo if nome_extra_novo.strip() else 0.0
    total_calculado = sub_estimado - v_desconto + novo_frete + v_extra

    if st.button("💾 Aplicar Ajustes", use_container_width=True):
        adicionais_atuais = pedido.get('adicionais', '') or ""
        novo_adicional = adicionais_atuais
        if desconto_perc > 0: novo_adicional += f"\n🔻 Desconto de {desconto_perc}% aplicado."
        if nome_extra_novo.strip(): novo_adicional += f"\n✨ 1x {nome_extra_novo.strip()} (R$ {formata_moeda(v_extra)})"

        try:
            supabase.table("pedidos").update({
                "valor_frete": novo_frete,
                "valor_total": total_calculado,
                "adicionais": novo_adicional.strip(),
                "status": novo_status
            }).eq("id", pedido_id).execute()
            st.success("✅ Pedido atualizado!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

    # 2. Resumo Extrato
    st.markdown(f"""
    <div class="receipt-box">
        <div class="receipt-line"><span>Cesta Base & Itens</span> <span>R$ {formata_moeda(sub_estimado)}</span></div>
        <div class="receipt-line"><span>Adicionais Atuais</span> <span>Inclusos no Subtotal</span></div>
        <div class="receipt-line" style="color: #b06000;"><span>Desconto Aplicado</span> <span>- R$ {formata_moeda(v_desconto)}</span></div>
        <div class="receipt-line"><span>Taxa de Entrega</span> <span>R$ {formata_moeda(novo_frete)}</span></div>
        <div class="receipt-line"><span>Item Extra Avulso</span> <span>R$ {formata_moeda(v_extra)}</span></div>
        <div class="receipt-line total"><span>TOTAL A PAGAR</span> <span>R$ {formata_moeda(total_calculado)}</span></div>
        <div style="text-align: center; margin-top: 10px; font-size: 12px; font-weight: 700; color: #888;">💳 Forma de Pagamento: {forma_pagamento}</div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Botão WhatsApp
    fone_cliente = re.sub(r'\D', '', pedido.get('cliente_telefone', ''))
    
    texto_resumo = f"""*RESUMO DO PEDIDO — DOCE CESTA BRASÍLIA* 🎁\n\n👤 *Olá {cliente_limpo}!* Segue o resumo para pagamento do seu pedido:\n\n📦 *Produto Principal:* {pedido.get('cesta_nome')}\n💳 *Forma de Pagamento:* {forma_pagamento}\n\n*VALORES:*\n🔸 Subtotal: R$ {formata_moeda(sub_estimado)}\n🚚 Frete: R$ {formata_moeda(novo_frete)}\n"""
    if v_desconto > 0: texto_resumo += f"🔻 Desconto: - R$ {formata_moeda(v_desconto)}\n"
    if v_extra > 0: texto_resumo += f"✨ Adicionais: R$ {formata_moeda(v_extra)}\n"
    texto_resumo += f"━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL A PAGAR: R$ {formata_moeda(total_calculado)}*\n\n📅 *Entrega:* {formata_data(pedido.get('data_entrega'))} ({pedido.get('periodo_entrega')})\n📍 *Local:* {pedido.get('endereco')}\n\nQualquer dúvida, estamos à disposição! 🌻"
    
    link_wpp = f"https://wa.me/55{fone_cliente}?text={urllib.parse.quote(texto_resumo)}" if fone_cliente else "#"

    st.write("")
    if fone_cliente:
        st.markdown(f'<div class="wpp-btn"><a href="{link_wpp}" target="_blank">💬 Enviar Resumo p/ Pagamento no WhatsApp</a></div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ O comprador não possui telefone cadastrado.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# BOTÕES DE AÇÃO INFERIORES (EDIÇÃO COMPLETA E EXCLUSÃO)
# ==========================================
st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
col_a1, col_a2, col_a3, col_a4 = st.columns(4)

with col_a1:
    if st.button("✏️ Editar Pedido Inteiro", use_container_width=True):
        st.session_state['editar_pedido_id'] = pedido_id
        if is_b2b: st.switch_page("pages/18_Corporativo.py")
        else: st.switch_page("pages/19_Pedido_Manual.py")

with col_a2:
    if st.button("⏩ Produção", use_container_width=True):
        supabase.table("pedidos").update({"status": "Em Produção"}).eq("id", pedido_id).execute()
        st.rerun()

with col_a3:
    if st.button("⏩ Rota", use_container_width=True):
        supabase.table("pedidos").update({"status": "Em Rota de Entrega"}).eq("id", pedido_id).execute()
        st.rerun()

with col_a4:
    if st.button("🗑️ Excluir", type="primary", use_container_width=True):
        supabase.table("pedidos").delete().eq("id", pedido_id).execute()
        st.session_state['pedido_detalhe_id'] = None
        st.switch_page("pages/02_Pedidos.py")
