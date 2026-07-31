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
    padding: 18px 24px; border-radius: 12px; border: 1px solid #e8ddd3;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03); margin-bottom: 24px;
    display: flex; justify-content: space-between; align-items: center;
}
.order-id { font-size: 20px; font-weight: 800; color: #775a46; margin: 0; line-height: 1.2; letter-spacing: -0.5px; }
.order-type-badge { background: #fef7e0; color: #b06000; padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: 800; border: 1px solid #fce8b2; display: inline-block; margin-top: 4px; }
.order-type-badge.corp { background: #e6f4ea; color: #137333; border-color: #ceead6; }
.status-label { font-size: 11px; color: #775a46; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; text-align: right; }
.status-value { font-size: 16px; font-weight: 800; color: #c5721f; text-align: right; }

/* Content Cards Superiores (HTML Custom) */
.info-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 12px; padding: 18px;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02); margin-bottom: 18px; height: 100%;
}
.card-title { font-size: 13.5px; font-weight: 800; color: #c5721f; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; border-bottom: 2px dashed #f5eee6; padding-bottom: 8px; text-transform: uppercase; }

/* Data Rows */
.data-group { margin-bottom: 10px; }
.data-label { font-size: 11px; color: #8c7362; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
.data-value { font-size: 13.5px; color: #2c1e14; font-weight: 600; }
.highlight-box { background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 8px; padding: 10px; font-size: 13px; font-style: italic; color: #4a2e1b; border-left: 4px solid #c5721f; margin-top: 6px; }

/* Items / Products */
.item-pill { background: #faf7f3; border: 1px solid #e8ddd3; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 12.5px; font-weight: 600; color: #4a2e1b; }
.item-pill.discount { background: #fef7e0; border-color: #fce8b2; color: #b06000; }

/* Receipt */
.receipt-box { background: #fdfbf8; border: 1px dashed #dfcdbb; border-radius: 10px; padding: 16px; margin-top: 15px; }
.receipt-line { display: flex; justify-content: space-between; font-size: 13px; color: #5a3b28; margin-bottom: 6px; font-weight: 600;}
.receipt-line.total { border-top: 2px dashed #dfcdbb; padding-top: 10px; margin-top: 10px; font-size: 16px; font-weight: 800; color: #137333; }

/* Buttons */
div[data-testid="stButton"] button { border-radius: 10px !important; font-weight: 800 !important; font-size: 13px !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.06) !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border: none !important; box-shadow: 0 4px 12px rgba(19, 115, 51, 0.15) !important; }

/* Containers nativos */
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff !important; border-radius: 12px !important; border: 1px solid #e8ddd3 !important; padding: 18px !important; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02) !important; margin-bottom: 15px !important; }
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
id_curto = str(pedido['id']).split('-')[0].upper()

def formata_data(d_str):
    if not d_str: return "-"
    try: return datetime.strptime(str(d_str)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return d_str

def formata_moeda(v):
    # ATENÇÃO: Esta função retorna apenas o número formatado, sem o "R$"
    # para evitar a redundância "R$ R$ 240,00" no HTML.
    try: return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

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
        <h1 class="order-id">Pedido #{id_curto}</h1>
        <span class="order-type-badge {tipo_classe}">{tipo_texto}</span>
    </div>
    <div>
        <div class="status-label">STATUS ATUAL</div>
        <div class="status-value">{pedido.get('status', 'Recebido')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# GRID SUPERIOR (INFORMAÇÕES ESTÁTICAS)
# =====================================================
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown(f"""
    <div class="info-card">
        <div class="card-title">👤 Comprador & Destinatário</div>
        <div class="data-group"><div class="data-label">Cliente / Empresa</div><div class="data-value">{cliente_limpo}</div></div>
        <div class="data-group"><div class="data-label">Contato (WhatsApp)</div><div class="data-value">{pedido.get('cliente_telefone', '-')}</div></div>
        <div class="data-group"><div class="data-label">CPF / CNPJ</div><div class="data-value">{pedido.get('cliente_cpf', '-')}</div></div>
        <div class="data-group" style="margin-top: 15px;"><div class="data-label">Recebedor (Destinatário)</div><div class="data-value">{pedido.get('destinatario_nome', '-')}</div></div>
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
# GRID INFERIOR (DETALHAMENTO E FECHAMENTO NATIVOS)
# =====================================================
col_prod, col_fin = st.columns(2)

# CAIXA DA ESQUERDA: DETALHAMENTO DO PEDIDO
with col_prod:
    with st.container(border=True):
        st.markdown("<h4 style='color: #c5721f; margin-top: 0; font-size: 14px; text-transform: uppercase;'>🎁 Detalhamento do Pedido</h4>", unsafe_allow_html=True)
        st.divider()
        
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

# CAIXA DA DIREITA: FECHAMENTO & PAGAMENTO
with col_fin:
    with st.container(border=True):
        st.markdown("<h4 style='color: #137333; margin-top: 0; font-size: 14px; text-transform: uppercase;'>💰 Fechamento & Pagamento</h4>", unsafe_allow_html=True)
        st.divider()
        
        frete_atual_db = tratar_preco(pedido.get('valor_frete', 0))
        total_atual_db = tratar_preco(pedido.get('valor_total', 0))
        forma_pagamento = pedido.get('pagamento', 'Pix')
        
        # Inputs de Fechamento (Zerados)
        c_f1, c_f2 = st.columns(2)
        with c_f1: novo_frete = st.number_input("Adicionar Frete/Taxa (R$)", min_value=0.0, step=5.0, value=0.0)
        with c_f2: desconto_perc = st.number_input("Aplicar Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0)

        # Status Restritos
        lista_status = ["Recebido", "Pago", "Em Produção", "Em Rota de Entrega"]
        status_db = pedido.get('status', 'Recebido')
        idx_status = lista_status.index(status_db) if status_db in lista_status else 0
        novo_status = st.selectbox("Atualizar Status", lista_status, index=idx_status)

        st.markdown("<div class='data-label' style='margin-top: 8px;'>Inserir Extra Não Cadastrado</div>", unsafe_allow_html=True)
        c_ex1, c_ex2 = st.columns([2.5, 1])
        with c_ex1: nome_extra_novo = st.text_input("Nome", placeholder="Ex: Cartão Extra", label_visibility="collapsed")
        with c_ex2: valor_extra_novo = st.number_input("Valor", min_value=0.0, step=5.0, value=0.0, label_visibility="collapsed")

        # Cálculos Matemáticos
        v_desconto_novo = total_atual_db * (desconto_perc / 100)
        v_extra_novo = valor_extra_novo if nome_extra_novo.strip() else 0.0
        
        total_calculado = total_atual_db - v_desconto_novo + novo_frete + v_extra_novo

        # Resumo do Extrato em Tempo Real (Corrigido para evitar o duplo "R$ R$")
        st.markdown(f"""
        <div class="receipt-box">
            <div class="receipt-line"><span>Total Atual do Pedido</span> <span>R$ {formata_moeda(total_atual_db)}</span></div>
            {f'<div class="receipt-line" style="color: #b06000;"><span>Novo Desconto ({desconto_perc}%)</span> <span>- R$ {formata_moeda(v_desconto_novo)}</span></div>' if desconto_perc > 0 else ''}
            {f'<div class="receipt-line"><span>Novo Frete/Taxa</span> <span>+ R$ {formata_moeda(novo_frete)}</span></div>' if novo_frete > 0 else ''}
            {f'<div class="receipt-line"><span>Novo Item Extra</span> <span>+ R$ {formata_moeda(v_extra_novo)}</span></div>' if v_extra_novo > 0 else ''}
            <div class="receipt-line total"><span>TOTAL FINAL A PAGAR</span> <span>R$ {formata_moeda(total_calculado)}</span></div>
            <div style="text-align: center; margin-top: 10px; font-size: 11.5px; font-weight: 700; color: #888;">💳 Forma de Pagamento: {forma_pagamento}</div>
        </div>
        """, unsafe_allow_html=True)

        # Botão Salvar Dados
        st.write("")
        if st.button("💾 Salvar Dados e Atualizar", use_container_width=True, type="primary"):
            adicionais_atuais = pedido.get('adicionais', '') or ""
            novo_adicional = adicionais_atuais
            
            if desconto_perc > 0: novo_adicional += f"\n🔻 Desconto extra de {desconto_perc}% aplicado."
            if nome_extra_novo.strip(): novo_adicional += f"\n✨ 1x {nome_extra_novo.strip()} (R$ {formata_moeda(v_extra_novo)})"

            try:
                supabase.table("pedidos").update({
                    "valor_frete": frete_atual_db + novo_frete,
                    "valor_total": total_calculado,
                    "adicionais": novo_adicional.strip(),
                    "status": novo_status
                }).eq("id", pedido_id).execute()
                st.success("✅ Pedido salvo e atualizado!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

        # Botão WhatsApp
        fone_cliente = re.sub(r'\D', '', pedido.get('cliente_telefone', ''))
        texto_resumo = f"""*RESUMO DO PEDIDO — DOCE CESTA BRASÍLIA* 🎁\n\n👤 *Olá {cliente_limpo}!* Segue o resumo atualizado do seu pedido:\n\n📦 *Produto Principal:* {pedido.get('cesta_nome')}\n💳 *Forma de Pagamento:* {forma_pagamento}\n\n*VALORES ATUALIZADOS:*\n━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL A PAGAR: R$ {formata_moeda(total_calculado)}*\n\n📅 *Entrega:* {formata_data(pedido.get('data_entrega'))} ({pedido.get('periodo_entrega')})\n📍 *Local:* {pedido.get('endereco')}\n\nQualquer dúvida, estamos à disposição! 🌻"""
        link_wpp = f"https://wa.me/55{fone_cliente}?text={urllib.parse.quote(texto_resumo)}" if fone_cliente else "#"
        
        st.write("")
        if fone_cliente:
            st.markdown(f'<a href="{link_wpp}" target="_blank" style="background: #25d366; color: white; font-weight: 800; font-size: 13px; border-radius: 10px; padding: 10px; display: flex; justify-content: center; text-decoration: none; box-shadow: 0 4px 10px rgba(37,211,102,0.2);">💬 Enviar Resumo p/ Pagamento (WhatsApp)</a>', unsafe_allow_html=True)

# ==========================================
# BOTÃO DE EDIÇÃO GERAL (REDIRECIONAMENTO PRÉ-PREENCHIDO)
# ==========================================
st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    if st.button("✏️ Editar Pedido Inteiro (Cestas, Endereços e Itens)", use_container_width=True):
        
        lista_itens_recriados = []
        lista_itens_recriados.append({
            "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": pedido.get("cesta_id"), "nome": pedido.get("cesta_nome", "Cesta"),
            "preco_unitario": 0.0, "quantidade": 1, "descricao": pedido.get("produtos", "")
        })
        
        st.session_state['pedido_editando_id'] = pedido_id
        
        if is_b2b:
            st.session_state['corp_nome'] = cliente_limpo
            st.session_state['corp_cnpj'] = pedido.get('cliente_cpf', '')
            st.session_state['corp_tel'] = pedido.get('cliente_telefone', '')
            st.session_state['corp_end'] = pedido.get('endereco', '')
            st.session_state['itens_orcamento_corp'] = lista_itens_recriados
            st.switch_page("pages/18_Corporativo.py")
        else:
            st.session_state['man_nome'] = cliente_limpo
            st.session_state['in_nome'] = cliente_limpo
            st.session_state['man_cpf'] = pedido.get('cliente_cpf', '')
            st.session_state['in_cpf'] = pedido.get('cliente_cpf', '')
            st.session_state['man_tel'] = pedido.get('cliente_telefone', '')
            st.session_state['in_tel'] = pedido.get('cliente_telefone', '')
            st.session_state['man_dest_nome'] = pedido.get('destinatario_nome', '')
            st.session_state['man_dest_tel'] = pedido.get('destinatario_telefone', '')
            st.session_state['man_motivo'] = pedido.get('motivo_homenagem', '')
            st.session_state['man_msg'] = pedido.get('mensagem', '')
            st.session_state['man_rua'] = pedido.get('endereco', '')
            st.session_state['in_rua'] = pedido.get('endereco', '')
            st.session_state['man_frete'] = tratar_preco(pedido.get('valor_frete', 0))
            st.session_state['man_pag'] = pedido.get('pagamento', 'Pix')
            st.session_state['man_status'] = pedido.get('status', 'Recebido')
            st.session_state['itens_orcamento_varejo'] = lista_itens_recriados
            st.switch_page("pages/19_Pedido_Manual.py")
