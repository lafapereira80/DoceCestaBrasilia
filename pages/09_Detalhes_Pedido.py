import streamlit as st
import pandas as pd
import requests
import re
import uuid
import urllib.parse
from datetime import datetime, date

from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.produto_service import listar_produtos_por_categoria_id
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
# CSS PREMIUM (INSPIRADO NA PÁGINA 19)
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 4rem !important; max-width: 1200px; }
h1, h2, h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-bottom: 6px !important; letter-spacing: -0.3px; }

/* Banner Superior */
.header-banner {
    display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 18px 24px;
    border-radius: 16px; border: 1px solid #e8ddd3; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03);
}
.header-title-box { display: flex; flex-direction: column; gap: 4px; }
.header-id { font-size: 22px; font-weight: 800; color: #c5721f; margin: 0; display: flex; align-items: center; gap: 10px; }
.badge-canal { background: #fef7e0; color: #b06000; padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: 800; text-transform: uppercase; border: 1px solid #fce8b2;}
.badge-canal.corp { background: #e6f4ea; color: #137333; border-color: #ceead6; }
.badge-canal.vitrine { background: #e8f0fe; color: #1a73e8; border-color: #d2e3fc; }

/* Cartões Padrão */
.corp-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 20px;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02); margin-bottom: 15px; height: 100%;
}
.corp-title { font-size: 15px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 2px dashed #f5eee6; padding-bottom: 8px;}

/* Linhas de Dados Visualização */
.data-label { font-size: 11px; color: #8c7362; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
.data-value { font-size: 14px; color: #2c1e14; font-weight: 600; margin-bottom: 12px; }
.item-pill { background: #faf7f3; border: 1px solid #e8ddd3; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 13px; font-weight: 600; color: #4a2e1b; }

/* Resumo Financeiro Oficial (Evita vazamento de HTML) */
.resumo-financeiro {
    background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 12px; padding: 16px 20px;
    display: flex; justify-content: space-between; align-items: center; margin-top: 15px;
}
.resumo-item { text-align: center; }
.resumo-label { font-size: 11.5px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; }
.resumo-valor { font-size: 18px; font-weight: 800; color: #4a2e1b; }
.resumo-destaque { font-size: 22px; font-weight: 800; color: #137333; }

/* Botões */
div[data-testid="stButton"] button { border-radius: 10px !important; font-weight: 800 !important; transition: all 0.15s ease !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border: none !important; box-shadow: 0 4px 12px rgba(19, 115, 51, 0.2) !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { transform: translateY(-1px) !important; }
.btn-wpp > a { background: #25d366 !important; color: white !important; font-weight: 800 !important; font-size: 14px !important; border-radius: 10px !important; padding: 12px !important; display: flex; justify-content: center; align-items: center; text-decoration: none !important; box-shadow: 0 4px 10px rgba(37,211,102,0.2) !important; transition: all 0.2s; }
.btn-wpp > a:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(37,211,102,0.3) !important; }
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

# Helpers
is_b2b = "[B2B]" in pedido.get('cliente_nome', '')
is_vitrine = "[VITRINE]" in pedido.get('cliente_nome', '')
cliente_limpo = pedido.get('cliente_nome', '').replace("[B2B]", "").replace("[VITRINE]", "").strip()

if is_b2b:
    tipo_classe = "corp"
    tipo_texto = "🏢 CORPORATIVO (B2B)"
elif is_vitrine:
    tipo_classe = "vitrine"
    tipo_texto = "🌐 LOJA VITRINE"
else:
    tipo_classe = ""
    tipo_texto = "🛍️ VAREJO (B2C)"

id_curto = str(pedido['id']).split('-')[0].upper()

def formata_data(d_str):
    if not d_str: return "-"
    try: return datetime.strptime(str(d_str)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return d_str

def formatar_moeda(valor):
    try: return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

@st.cache_data(ttl=300, show_spinner=False)
def obter_cestas():
    try: return sorted([c for c in listar_cestas() if c.get("ativa", True)], key=lambda x: x.get("nome", ""))
    except: return []

@st.cache_data(ttl=300, show_spinner=False)
def obter_adicionais():
    try:
        categorias = supabase.table("categorias").select("*").execute().data or []
        cat_add = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)
        if cat_add:
            produtos_add = listar_produtos_por_categoria_id(cat_add["id"])
            return sorted([p for p in produtos_add if p.get("ativo", True)], key=lambda x: x.get("nome", ""))
        return []
    except: return []

# CONTROLE DE ESTADO
if "modo_edicao" not in st.session_state:
    st.session_state.modo_edicao = False

if "edit_cart" not in st.session_state or st.session_state.get("edit_pedido_id") != pedido_id:
    st.session_state["edit_cart"] = []
    st.session_state["edit_pedido_id"] = pedido_id
    
    # Pré-carrega uma cesta base simbólica no carrinho para facilitar a edição
    st.session_state["edit_cart"].append({
        "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": pedido.get("cesta_id"), 
        "nome": pedido.get("cesta_nome", "Cesta Anterior"), "preco_unitario": tratar_preco(pedido.get('valor_total', 0)) - tratar_preco(pedido.get('valor_frete', 0)), 
        "quantidade": 1, "descricao": pedido.get("produtos", "")
    })

# =====================================================
# CABEÇALHO COM BOTÃO VOLTAR
# =====================================================
c_head, c_btn = st.columns([4, 1], vertical_alignment="center")
with c_head:
    st.markdown(f"""
    <div class="header-banner">
        <div class="header-title-box">
            <h1 class="header-id">Pedido #{id_curto} <span class="badge-canal {tipo_classe}">{tipo_texto}</span></h1>
        </div>
        <div style="text-align: right;">
            <div class="status-label">STATUS ATUAL</div>
            <div class="status-value">{pedido.get('status', 'Recebido')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c_btn:
    if st.button("⬅️ Voltar ao Mural", use_container_width=True):
        st.session_state.modo_edicao = False
        st.switch_page("pages/02_Pedidos.py")


# =====================================================
# MODO DE VISUALIZAÇÃO E AÇÕES RÁPIDAS
# =====================================================
if not st.session_state.modo_edicao:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="corp-card">
            <div class="corp-title">👤 Informações do Pedido</div>
            <div class="data-label">Cliente / Empresa</div><div class="data-value">{cliente_limpo} ({pedido.get('cliente_telefone', '-')})</div>
            <div class="data-label">CPF / CNPJ</div><div class="data-value">{pedido.get('cliente_cpf', '-')}</div>
            <div class="data-label" style="margin-top:15px;">Recebedor (Destinatário)</div><div class="data-value">{pedido.get('destinatario_nome', '-')}</div>
            <div class="data-label">Ocasião / Motivo</div><div class="data-value">{pedido.get('motivo_homenagem', '-')}</div>
            <div class="data-label" style="margin-top:15px;">Data e Período</div><div class="data-value">{formata_data(pedido.get('data_entrega'))} - {pedido.get('periodo_entrega', '-')}</div>
            <div class="data-label">Endereço de Entrega</div><div class="data-value">{pedido.get('endereco', '-')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="corp-card">', unsafe_allow_html=True)
        st.markdown('<div class="corp-title">🎁 Detalhamento</div>', unsafe_allow_html=True)
        
        produtos_str = pedido.get('produtos', '')
        adicionais_str = pedido.get('adicionais', '')
        msg_cartao = pedido.get('mensagem', '')
        
        if produtos_str:
            for linha in produtos_str.split("\n"):
                if linha.strip(): st.markdown(f"<div class='item-pill'>📦 {linha.strip()}</div>", unsafe_allow_html=True)
        if adicionais_str:
            for linha in adicionais_str.split("\n"):
                linha_limpa = linha.strip()
                if linha_limpa:
                    if "Desconto" in linha_limpa: st.markdown(f"<div class='item-pill discount'>🔻 {linha_limpa}</div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div class='item-pill'>✨ {linha_limpa}</div>", unsafe_allow_html=True)
        
        if msg_cartao:
            st.markdown("<div class='data-label' style='margin-top: 15px;'>💌 Mensagem do Cartão</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='background: #fdfbf8; padding: 10px; border-radius: 8px; font-style: italic; font-size: 13px; color: #4a2e1b; border-left: 3px solid #c5721f;'>\"{msg_cartao}\"</div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # RESUMO FINANCEIRO (Renderizado via HTML seguro inspirado na pág 19)
    total_db = tratar_preco(pedido.get('valor_total', 0))
    frete_db = tratar_preco(pedido.get('valor_frete', 0))
    subtotal_db = total_db - frete_db

    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    st.markdown('<div class="corp-title">💰 Resumo Financeiro & Ações</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="resumo-financeiro">
        <div class="resumo-item">
            <div class="resumo-label">Subtotal / Itens</div>
            <div class="resumo-valor">R$ {formatar_moeda(subtotal_db)}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">Frete</div>
            <div class="resumo-valor">R$ {formatar_moeda(frete_db)}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">Pagamento</div>
            <div class="resumo-valor">{pedido.get('pagamento', 'Pix')}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">VALOR TOTAL</div>
            <div class="resumo-destaque">R$ {formatar_moeda(total_db)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1.5])
    with c_btn1:
        if st.button("✏️ Editar Pedido / Fechamento", use_container_width=True):
            st.session_state.modo_edicao = True
            st.rerun()
    with c_btn2:
        lista_status = ["Recebido", "Pago", "Em Rota de Entrega", "Entregue", "Desistência"]
        novo_status_rapido = st.selectbox("Avançar Status", lista_status, index=lista_status.index(pedido.get('status', 'Recebido')) if pedido.get('status') in lista_status else 0, label_visibility="collapsed")
        if novo_status_rapido != pedido.get('status'):
            supabase.table("pedidos").update({"status": novo_status_rapido}).eq("id", pedido_id).execute()
            st.rerun()
    with c_btn3:
        fone_cliente = re.sub(r'\D', '', pedido.get('cliente_telefone', ''))
        texto_resumo = f"""*RESUMO DO PEDIDO — DOCE CESTA BRASÍLIA* 🎁\n\n👤 *Olá {cliente_limpo}!* Segue o resumo atualizado do seu pedido:\n\n📦 *Produto:* {pedido.get('cesta_nome')}\n💳 *Forma de Pagamento:* {pedido.get('pagamento', 'Pix')}\n\n*VALORES:*\n━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL A PAGAR: R$ {formatar_moeda(total_db)}*\n\n📅 *Entrega:* {formata_data(pedido.get('data_entrega'))} ({pedido.get('periodo_entrega')})\n📍 *Local:* {pedido.get('endereco')}\n\nQualquer dúvida, estamos à disposição! 🌻"""
        link_wpp = f"https://wa.me/55{fone_cliente}?text={urllib.parse.quote(texto_resumo)}" if fone_cliente else "#"
        if fone_cliente:
            st.markdown(f'<div class="btn-wpp"><a href="{link_wpp}" target="_blank">💬 Enviar Resumo (WhatsApp)</a></div>', unsafe_allow_html=True)
        else:
            st.warning("Sem telefone cadastrado.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# MODO EDIÇÃO (INSPIRADO NA PÁG 19 - ZERO REDIRECIONAMENTOS)
# =====================================================
else:
    st.info("✏️ **Modo Edição Ativado.** Altere os dados abaixo e clique em Salvar no final da página.")
    
    st.markdown('<div class="corp-card"><div class="corp-title">👤 1. Dados do Comprador</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: e_nome = st.text_input("Nome Comprador", value=pedido.get('cliente_nome', ''))
    with c2: e_tel = st.text_input("WhatsApp", value=pedido.get('cliente_telefone', ''))
    with c3: e_cpf = st.text_input("CPF / CNPJ", value=pedido.get('cliente_cpf', ''))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="corp-card"><div class="corp-title">💌 2. Destinatário, Entrega e Cartão</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: e_dest = st.text_input("Nome Destinatário", value=pedido.get('destinatario_nome', ''))
    with c5: e_dtel = st.text_input("Tel Destinatário", value=pedido.get('destinatario_telefone', ''))
    with c6: e_motivo = st.text_input("Motivo/Ocasião", value=pedido.get('motivo_homenagem', ''))
    
    e_end = st.text_area("Endereço Completo", value=pedido.get('endereco', ''), height=70)
    
    try: dt_obj = datetime.strptime(str(pedido.get('data_entrega'))[:10], "%Y-%m-%d").date()
    except: dt_obj = date.today()
    
    c7, c8 = st.columns(2)
    with c7: e_data = st.date_input("Data de Entrega", value=dt_obj, format="DD/MM/YYYY")
    with c8: e_per = st.text_input("Período/Horário", value=pedido.get('periodo_entrega', ''))
    e_msg = st.text_area("Mensagem do Cartão", value=pedido.get('mensagem', ''), height=70)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="corp-card"><div class="corp-title">🎁 3. Produtos e Carrinho (Fechamento)</div>', unsafe_allow_html=True)
    
    col_add1, col_add2, col_add3 = st.columns(3)
    cestas_disponiveis = obter_cestas()
    adicionais_disponiveis = obter_adicionais()

    with col_add1:
        cesta_sel = st.selectbox("Nova Cesta", [None] + cestas_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione...")
        if st.button("➕ Inserir Cesta", use_container_width=True) and cesta_sel:
            st.session_state["edit_cart"].append({
                "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_sel["id"], "nome": cesta_sel["nome"], 
                "preco_unitario": tratar_preco(cesta_sel.get("preco")), "quantidade": 1, "descricao": ""
            })
            st.rerun()

    with col_add2:
        adc_sel = st.selectbox("Extra do Catálogo", [None] + adicionais_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione...")
        if st.button("➕ Inserir Extra", use_container_width=True) and adc_sel:
            st.session_state["edit_cart"].append({
                "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": adc_sel["nome"], 
                "preco_unitario": tratar_preco(adc_sel.get("preco")), "quantidade": 1, "descricao": ""
            })
            st.rerun()

    with col_add3:
        txt_man = st.text_input("Extra Manual", placeholder="Ex: Vinho")
        if st.button("➕ Inserir Manual", use_container_width=True) and txt_man.strip():
            st.session_state["edit_cart"].append({
                "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": txt_man.strip(), 
                "preco_unitario": 0.0, "quantidade": 1, "descricao": ""
            })
            st.rerun()

    total_bruto = 0
    if st.session_state["edit_cart"]:
        st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 15px 0;'>", unsafe_allow_html=True)
        h1, h2, h3, h4, h5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
        h1.markdown("<div class='data-label'>Descrição</div>", unsafe_allow_html=True)
        h2.markdown("<div class='data-label'>V. Un. (R$)</div>", unsafe_allow_html=True)
        h3.markdown("<div class='data-label'>Qtd</div>", unsafe_allow_html=True)
        h4.markdown("<div class='data-label'>Subtotal</div>", unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state["edit_cart"]):
            c1, c2, c3, c4, c5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
            with c1: st.markdown(f"<div style='margin-top:6px; font-weight:600; font-size:13.5px;'>{item['nome']}</div>", unsafe_allow_html=True)
            with c2:
                n_preco = st.number_input("V", value=float(item["preco_unitario"]), min_value=0.0, step=1.0, format="%.2f", key=f"e_p_{item['id']}", label_visibility="collapsed")
                st.session_state["edit_cart"][i]["preco_unitario"] = n_preco
            with c3:
                n_qtd = st.number_input("Q", value=int(item["quantidade"]), min_value=1, step=1, key=f"e_q_{item['id']}", label_visibility="collapsed")
                st.session_state["edit_cart"][i]["quantidade"] = n_qtd
            with c4:
                sub_linha = n_preco * n_qtd
                total_bruto += sub_linha
                st.markdown(f"<div style='margin-top:8px; font-weight:800; font-size:14px; color:#137333;'>R$ {formatar_moeda(sub_linha)}</div>", unsafe_allow_html=True)
            with c5:
                if st.button("🗑️", key=f"e_d_{item['id']}"):
                    st.session_state["edit_cart"].pop(i)
                    st.rerun()

    st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 15px 0;'>", unsafe_allow_html=True)
    c_f1, c_f2, c_f3, c_f4 = st.columns(4)
    with c_f1: e_frete = st.number_input("Frete / Taxa (R$)", min_value=0.0, step=5.0, value=tratar_preco(pedido.get('valor_frete', 0)))
    with c_f2: e_desc = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0)
    with c_f3: e_pag = st.selectbox("Pagamento", ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"], index=0)
    with c_f4: 
        lista_status = ["Recebido", "Pago", "Em Rota de Entrega", "Entregue", "Desistência"]
        e_status = st.selectbox("Status", lista_status, index=lista_status.index(pedido.get('status', 'Recebido')) if pedido.get('status') in lista_status else 0)

    valor_desconto = total_bruto * (e_desc / 100)
    total_liquido = total_bruto - valor_desconto + e_frete

    st.markdown(f"""
    <div class="resumo-financeiro">
        <div class="resumo-item"><div class="resumo-label">Subtotal</div><div class="resumo-valor">R$ {formatar_moeda(total_bruto)}</div></div>
        <div class="resumo-item"><div class="resumo-label">Desconto</div><div class="resumo-valor" style="color:#c5221f;">- R$ {formatar_moeda(valor_desconto)}</div></div>
        <div class="resumo-item"><div class="resumo-label">Frete</div><div class="resumo-valor">R$ {formatar_moeda(e_frete)}</div></div>
        <div class="resumo-item"><div class="resumo-label">TOTAL FINAL</div><div class="resumo-destaque">R$ {formatar_moeda(total_liquido)}</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    c_save1, c_save2 = st.columns(2)
    with c_save1:
        if st.button("💾 SALVAR ALTERAÇÕES", type="primary", use_container_width=True):
            if not st.session_state["edit_cart"]: st.error("O carrinho não pode ficar vazio."); st.stop()
            
            lista_cestas = [it for it in st.session_state["edit_cart"] if it["tipo"] == "Cesta"]
            lista_extras = [it for it in st.session_state["edit_cart"] if it["tipo"] == "Extra"]
            
            str_prod = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_cestas]
            str_ext = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_extras]
            
            n_cesta = lista_cestas[0]["nome"] if lista_cestas else "Pedido Editado"
            id_cesta = lista_cestas[0]["cesta_id"] if lista_cestas else None
            
            msg_add = f"Desconto de {e_desc}% aplicado." if e_desc > 0 else ""
            if str_ext: msg_add += "\n\nEXTRAS:\n" + "\n".join(str_ext)

            dados_update = {
                "cliente_nome": e_nome.strip(),
                "cliente_telefone": e_tel,
                "cliente_cpf": e_cpf,
                "destinatario_nome": e_dest.strip(),
                "destinatario_telefone": e_dtel,
                "motivo_homenagem": e_motivo,
                "endereco": e_end,
                "data_entrega": e_data.strftime("%Y-%m-%d"),
                "periodo_entrega": e_per,
                "mensagem": e_msg,
                "cesta_nome": n_cesta,
                "cesta_id": id_cesta,
                "produtos": "\n".join(str_prod),
                "adicionais": msg_add.strip(),
                "pagamento": e_pag,
                "status": e_status,
                "valor_frete": e_frete,
                "valor_total": total_liquido
            }
            try:
                supabase.table("pedidos").update(dados_update).eq("id", pedido_id).execute()
                st.success("✅ Pedido atualizado com sucesso!")
                st.session_state.modo_edicao = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    
    with c_save2:
        if st.button("❌ Cancelar Edição", use_container_width=True):
            st.session_state.modo_edicao = False
            st.rerun()
