import streamlit as st
import pandas as pd
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
# CSS PREMIUM (UI/UX DASHBOARD CARDS)
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; font-size: 14px !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1200px !important; }

/* Header Banner - FONTE DO MESMO TAMANHO PADRÃO */
.order-header {
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%);
    padding: 16px 20px; border-radius: 12px; border: 1px solid #e8ddd3;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02); margin-bottom: 20px;
    display: flex; justify-content: space-between; align-items: center;
}
.order-text { font-size: 14px; font-weight: 800; color: #4a2e1b; margin: 0; display: flex; align-items: center; gap: 8px; }
.order-type-badge { background: #fef7e0; color: #b06000; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800; border: 1px solid #fce8b2; text-transform: uppercase; }
.order-type-badge.corp { background: #e6f4ea; color: #137333; border-color: #ceead6; }
.order-type-badge.vitrine { background: #e8f0fe; color: #1a73e8; border-color: #d2e3fc; }
.status-text { font-size: 14px; font-weight: 800; color: #c5721f; text-align: right; text-transform: uppercase;}

/* Cartões HTML (Visualização) */
.info-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 12px; padding: 20px;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02); margin-bottom: 16px; height: 100%;
}
.card-title { font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; border-bottom: 1px dashed #e8ddd3; padding-bottom: 6px; text-transform: uppercase; }

/* Linhas de Dados */
.data-label { font-size: 11.5px; color: #8c7362; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
.data-value { font-size: 14px; color: #2c1e14; font-weight: 600; margin-bottom: 12px; }
.item-pill { background: #faf7f3; border: 1px solid #e8ddd3; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 13.5px; font-weight: 600; color: #4a2e1b; }
.item-pill.discount { background: #fef7e0; border-color: #fce8b2; color: #b06000; }

/* Resumo Financeiro Seguro */
.resumo-financeiro {
    background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 10px; padding: 16px;
    display: flex; justify-content: space-between; align-items: center; margin-top: 15px;
}
.resumo-item { text-align: center; }
.resumo-label { font-size: 11.5px; font-weight: 700; color: #775a46; text-transform: uppercase; }
.resumo-valor { font-size: 15px; font-weight: 800; color: #4a2e1b; margin-top: 4px; }
.resumo-destaque { font-size: 16px; font-weight: 800; color: #137333; margin-top: 4px; }

/* Botões Nativos */
div[data-testid="stButton"] button { border-radius: 8px !important; font-weight: 800 !important; font-size: 13px !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.06) !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border: none !important; box-shadow: 0 4px 12px rgba(19, 115, 51, 0.15) !important; }
.btn-wpp > a { background: #25d366 !important; color: white !important; font-weight: 800 !important; font-size: 13px !important; border-radius: 8px !important; padding: 12px !important; display: flex; justify-content: center; align-items: center; text-decoration: none !important; box-shadow: 0 4px 10px rgba(37,211,102,0.2) !important; transition: all 0.2s; }
.btn-wpp > a:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(37,211,102,0.3) !important; }

/* Containers Fechados do Streamlit */
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

# Helpers e Formatação (Tratamento Anti-NoneType/Null)
cliente_nome_banco = pedido.get('cliente_nome') or ''
is_b2b = "[B2B]" in cliente_nome_banco
is_vitrine = "[VITRINE]" in cliente_nome_banco
cliente_limpo = cliente_nome_banco.replace("[B2B]", "").replace("[VITRINE]", "").strip()

if is_b2b:
    tipo_classe = "corp"
    tipo_texto = "🏢 CORPORATIVO"
elif is_vitrine:
    tipo_classe = "vitrine"
    tipo_texto = "🌐 VITRINE"
else:
    tipo_classe = ""
    tipo_texto = "🛍️ VAREJO"

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

@st.cache_data(ttl=300, show_spinner=False)
def carregar_config_cesta_cached(cesta_id):
    try: return carregar_configuracao_cesta(cesta_id)
    except: return []

# CONTROLE DE ESTADO
if "modo_edicao" not in st.session_state:
    st.session_state.modo_edicao = False

if "edit_cart" not in st.session_state or st.session_state.get("edit_pedido_id") != pedido_id:
    st.session_state["edit_cart"] = []
    st.session_state["edit_pedido_id"] = pedido_id
    
    st.session_state["edit_cart"].append({
        "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": pedido.get("cesta_id"), 
        "nome": pedido.get("cesta_nome") or "Cesta/Pacote Base", "preco_unitario": tratar_preco(pedido.get('valor_total', 0)) - tratar_preco(pedido.get('valor_frete', 0)), 
        "quantidade": 1, "descricao": pedido.get("produtos") or ""
    })

# Lista exata de status permitidos (Somente Recebido, Pago, Desistência)
STATUS_PERMITIDOS = ["Recebido", "Pago", "Desistência"]

# =====================================================
# CABEÇALHO COM BOTÃO VOLTAR
# =====================================================
c_head, c_btn = st.columns([4, 1], vertical_alignment="center")
with c_head:
    st.markdown(f"""
    <div class="order-header">
        <div class="order-text">
            Pedido #{id_curto} <span class="order-type-badge {tipo_classe}">{tipo_texto}</span>
        </div>
        <div class="status-text">
            STATUS: {pedido.get('status') or 'Recebido'}
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
        html_info1 = f"""
        <div class="info-card">
            <div class="card-title">👤 Informações do Pedido</div>
            <div class="data-label">Cliente / Empresa</div><div class="data-value">{cliente_limpo} ({pedido.get('cliente_telefone') or '-'})</div>
            <div class="data-label">CPF / CNPJ</div><div class="data-value">{pedido.get('cliente_cpf') or '-'}</div>
            <div class="data-label" style="margin-top:10px;">Recebedor (Destinatário)</div><div class="data-value">{pedido.get('destinatario_nome') or '-'}</div>
            <div class="data-label">Ocasião / Motivo</div><div class="data-value">{pedido.get('motivo_homenagem') or '-'}</div>
            <div class="data-label" style="margin-top:10px;">Data e Período</div><div class="data-value">{formata_data(pedido.get('data_entrega'))} - {pedido.get('periodo_entrega') or '-'}</div>
            <div class="data-label">Endereço de Entrega</div><div class="data-value">{pedido.get('endereco') or '-'}</div>
        """
        anotacoes_internas = (pedido.get('anotacoes_internas') or '').strip()
        if anotacoes_internas:
            html_info1 += f"""
            <div class="data-label" style="margin-top:15px; color:#b06000;">⚠️ Anotações Internas</div>
            <div style="background: #fef7e0; padding: 10px; border-radius: 8px; font-size: 13px; color: #b06000; border-left: 3px solid #b06000;">{anotacoes_internas}</div>
            """
        html_info1 += "</div>"
        st.markdown(html_info1, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎁 Detalhamento</div>', unsafe_allow_html=True)
        
        produtos_str = (pedido.get('produtos') or '')
        adicionais_str = (pedido.get('adicionais') or '')
        msg_cartao = (pedido.get('mensagem') or '')
        
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

    # RESUMO FINANCEIRO E AÇÕES
    total_db = tratar_preco(pedido.get('valor_total', 0))
    frete_db = tratar_preco(pedido.get('valor_frete', 0))
    subtotal_db = total_db - frete_db

    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #137333; margin-bottom: 8px; text-transform: uppercase;'>💰 Resumo Financeiro & Ações</div>", unsafe_allow_html=True)
        
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
                <div class="resumo-valor">{pedido.get('pagamento') or 'Pix'}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">VALOR TOTAL</div>
                <div class="resumo-destaque">R$ {formatar_moeda(total_db)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
        with c_btn1:
            if st.button("✏️ Editar Pedido Completo", use_container_width=True):
                st.session_state.modo_edicao = True
                st.rerun()
        with c_btn2:
            status_atual = pedido.get('status') or 'Recebido'
            idx_st = STATUS_PERMITIDOS.index(status_atual) if status_atual in STATUS_PERMITIDOS else 0
            novo_status_rapido = st.selectbox("Avançar Status", STATUS_PERMITIDOS, index=idx_st, label_visibility="collapsed")
            if novo_status_rapido != status_atual:
                supabase.table("pedidos").update({"status": novo_status_rapido}).eq("id", pedido_id).execute()
                st.rerun()
        with c_btn3:
            fone_cliente = re.sub(r'\D', '', pedido.get('cliente_telefone') or '')
            texto_resumo = f"""*RESUMO DO PEDIDO — DOCE CESTA BRASÍLIA* 🎁\n\n👤 *Olá {cliente_limpo}!* Segue o resumo atualizado do seu pedido:\n\n📦 *Produto:* {pedido.get('cesta_nome') or 'Pedido Customizado'}\n💳 *Forma de Pagamento:* {pedido.get('pagamento') or 'Pix'}\n\n*VALORES:*\n━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL A PAGAR: R$ {formatar_moeda(total_db)}*\n\n📅 *Entrega:* {formata_data(pedido.get('data_entrega'))} ({pedido.get('periodo_entrega') or '-'})\n📍 *Local:* {pedido.get('endereco') or '-'}\n\nQualquer dúvida, estamos à disposição! 🌻"""
            link_wpp = f"https://wa.me/55{fone_cliente}?text={urllib.parse.quote(texto_resumo)}" if fone_cliente else "#"
            if fone_cliente:
                st.markdown(f'<div class="btn-wpp"><a href="{link_wpp}" target="_blank">💬 WhatsApp Resumo</a></div>', unsafe_allow_html=True)
            else:
                st.warning("Sem telefone.")


# =====================================================
# MODO EDIÇÃO (TOTALMENTE NATIVO E SEGURO)
# =====================================================
else:
    st.info("✏️ **Modo Edição Ativado.** Altere os dados abaixo e clique em Salvar no final da página.")
    
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 1px dashed #e8ddd3; padding-bottom: 6px;'>👤 1. DADOS DO COMPRADOR</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: e_nome = st.text_input("Nome Comprador", value=pedido.get('cliente_nome') or '')
        with c2: e_tel = st.text_input("WhatsApp", value=pedido.get('cliente_telefone') or '')
        with c3: e_cpf = st.text_input("CPF / CNPJ", value=pedido.get('cliente_cpf') or '')

    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 1px dashed #e8ddd3; padding-bottom: 6px;'>💌 2. DESTINATÁRIO, ENTREGA E CARTÃO</div>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4: e_dest = st.text_input("Nome Destinatário", value=pedido.get('destinatario_nome') or '')
        with c5: e_dtel = st.text_input("Tel Destinatário", value=pedido.get('destinatario_telefone') or '')
        with c6: e_motivo = st.text_input("Motivo/Ocasião", value=pedido.get('motivo_homenagem') or '')
        
        e_end = st.text_area("Endereço Completo", value=pedido.get('endereco') or '', height=70)
        
        try: dt_obj = datetime.strptime(str(pedido.get('data_entrega'))[:10], "%Y-%m-%d").date()
        except: dt_obj = date.today()
        
        c7, c8 = st.columns(2)
        with c7: e_data = st.date_input("Data de Entrega", value=dt_obj, format="DD/MM/YYYY")
        with c8: e_per = st.text_input("Período/Horário", value=pedido.get('periodo_entrega') or '')
        
        c9, c10 = st.columns(2)
        with c9: e_msg = st.text_area("Mensagem do Cartão", value=pedido.get('mensagem') or '', height=70)
        with c10: e_anotacoes = st.text_area("Anotações Internas (Não aparece p/ cliente)", value=pedido.get('anotacoes_internas') or '', height=70)

    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 1px dashed #e8ddd3; padding-bottom: 6px;'>🎁 3. PRODUTOS E CARRINHO (FECHAMENTO)</div>", unsafe_allow_html=True)
        
        col_add1, col_add2, col_add3 = st.columns(3)
        cestas_disponiveis = obter_cestas()
        adicionais_disponiveis = obter_adicionais()

        with col_add1:
            st.markdown("<div style='font-size: 12px; font-weight: 700; color: #775a46; margin-bottom: 4px;'>📦 Nova Cesta / Pacote</div>", unsafe_allow_html=True)
            cesta_sel = st.selectbox("Cestas", [None] + cestas_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione uma Cesta...", label_visibility="collapsed")
            
            selecoes_cesta_edit = {}
            if cesta_sel:
                cfg = carregar_config_cesta_cached(cesta_sel["id"])
                if cfg and any(grp.get("produtos") for grp in cfg):
                    st.markdown("<div style='font-size: 11.5px; font-weight: 700; color: #137333; margin-top: 5px; margin-bottom: 5px;'>🍓 Opções de Cesta:</div>", unsafe_allow_html=True)
                    for grp in cfg:
                        cat = grp.get("categoria", "Geral")
                        prods = grp.get("produtos", [])
                        maximo = grp.get("max_escolhas", 1)
                        if not prods: continue
                        if maximo == 1:
                            esc = st.selectbox(f"{cat}", prods, format_func=lambda p: p["nome"], key=f"edit_rad_{cesta_sel['id']}_{cat}")
                            if esc: selecoes_cesta_edit[cat] = [esc]
                        else:
                            escs = st.multiselect(f"{cat} (Máx: {maximo})", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"edit_mul_{cesta_sel['id']}_{cat}")
                            selecoes_cesta_edit[cat] = escs

            if st.button("➕ Inserir Cesta", use_container_width=True):
                if cesta_sel:
                    itens_sel_str = ""
                    if selecoes_cesta_edit:
                        opcoes_str = " | ".join([f"{cat}: {', '.join([i['nome'] for i in itens])}" for cat, itens in selecoes_cesta_edit.items() if itens])
                        if opcoes_str: itens_sel_str = f"Itens: {opcoes_str}"

                    st.session_state["edit_cart"].append({
                        "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_sel["id"], "nome": cesta_sel["nome"], 
                        "preco_unitario": tratar_preco(cesta_sel.get("preco")), "quantidade": 1, "descricao": itens_sel_str
                    })
                    st.rerun()

        with col_add2:
            st.markdown("<div style='font-size: 12px; font-weight: 700; color: #775a46; margin-bottom: 4px;'>✨ Extra do Catálogo</div>", unsafe_allow_html=True)
            adc_sel = st.selectbox("Extras", [None] + adicionais_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione...", label_visibility="collapsed")
            if st.button("➕ Inserir Extra", use_container_width=True) and adc_sel:
                st.session_state["edit_cart"].append({
                    "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": adc_sel["nome"], 
                    "preco_unitario": tratar_preco(adc_sel.get("preco")), "quantidade": 1, "descricao": ""
                })
                st.rerun()

        with col_add3:
            st.markdown("<div style='font-size: 12px; font-weight: 700; color: #775a46; margin-bottom: 4px;'>✍️ Extra Personalizado</div>", unsafe_allow_html=True)
            txt_man = st.text_input("Extra Manual", placeholder="Ex: Vinho Personalizado", label_visibility="collapsed")
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
                with c1:
                    icone = "📦" if item["tipo"] == "Cesta" else "✨"
                    st.markdown(f"<div style='margin-top:6px; font-weight:600; font-size:13px;'>{icone} {item['nome']}</div>", unsafe_allow_html=True)
                    if item.get("descricao"): st.caption(item["descricao"])
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
        with c_f3: e_pag = st.selectbox("Pagamento", ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"], index=["Pix", "Cartão de Crédito", "Faturamento", "Transferência"].index(pedido.get('pagamento') or 'Pix') if pedido.get('pagamento') in ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"] else 0)
        with c_f4: 
            status_atual = pedido.get('status') or 'Recebido'
            idx_e_status = STATUS_PERMITIDOS.index(status_atual) if status_atual in STATUS_PERMITIDOS else 0
            e_status = st.selectbox("Status", STATUS_PERMITIDOS, index=idx_e_status)

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
    
    st.write("")
    c_save1, c_save2 = st.columns(2)
    with c_save1:
        if st.button("💾 SALVAR ALTERAÇÕES", type="primary", use_container_width=True):
            if not st.session_state["edit_cart"]: st.error("O carrinho não pode ficar vazio."); st.stop()
            
            lista_cestas = [it for it in st.session_state["edit_cart"] if it["tipo"] == "Cesta"]
            lista_extras = [it for it in st.session_state["edit_cart"] if it["tipo"] == "Extra"]
            
            str_prod = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})\n{it.get('descricao','')}".strip() for it in lista_cestas]
            str_ext = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_extras]
            
            n_cesta = lista_cestas[0]["nome"] if lista_cestas else "Pedido Editado"
            id_cesta = lista_cestas[0]["cesta_id"] if lista_cestas else None
            
            msg_add = f"Desconto de {e_desc}% aplicado." if e_desc > 0 else ""
            if str_ext: msg_add += "\n\nEXTRAS E ADICIONAIS:\n" + "\n".join(str_ext)

            dados_update = {
                "cliente_nome": e_nome.strip() + (" [B2B]" if is_b2b else (" [VITRINE]" if is_vitrine else "")),
                "cliente_telefone": e_tel,
                "cliente_cpf": e_cpf,
                "destinatario_nome": e_dest.strip(),
                "destinatario_telefone": e_dtel,
                "motivo_homenagem": e_motivo,
                "endereco": e_end,
                "data_entrega": e_data.strftime("%Y-%m-%d"),
                "periodo_entrega": e_per,
                "mensagem": e_msg,
                "anotacoes_internas": e_anotacoes.strip(),
                "cesta_nome": n_cesta,
                "cesta_id": id_cesta,
                "produtos": "\n\n".join(str_prod),
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
