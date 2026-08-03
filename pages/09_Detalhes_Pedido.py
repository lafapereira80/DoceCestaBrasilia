import html
import streamlit as st
import pandas as pd
import re
import uuid
from datetime import datetime, date

from config.supabase import supabase
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.foto_service import salvar_fotos
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador
from utils.formatacao import formatar_moeda, tratar_preco, formatar_data_br, gerar_link_wpp, gerar_resumo_whatsapp
from utils.email_service import enviar_email_cobranca

try:
    from services.infinitepay_service import gerar_link_checkout_infinitepay
except ImportError:
    gerar_link_checkout_infinitepay = None


def esc(valor, padrao='-'):
    """Escapa texto vindo do banco antes de inserir em blocos HTML (evita XSS/quebra de layout)."""
    texto = str(valor) if valor not in (None, '') else padrao
    return html.escape(texto)


# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS
# =====================================================
st.set_page_config(page_title="Detalhes do Pedido", page_icon="🔍", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #4a2e1b;
    --ink-strong: #2c1e14;
    --muted: #8c7362;
    --border: #e8ddd3;
    --brand: #c5721f;
    --ok: #137333;
    --ok-bg: #e6f4ea;
    --info: #1a73e8;
    --info-bg: #e8f0fe;
    --warn: #b06000;
    --warn-bg: #fef7e0;
    --purple: #6a1b9a;
    --purple-bg: #f3e8fd;
}

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: var(--ink) !important; font-size: 14px !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1200px !important; }

.order-header {
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%);
    padding: 16px 20px; border-radius: 14px; border: 1px solid var(--border);
    box-shadow: 0 4px 14px rgba(90, 59, 40, 0.04); margin-bottom: 20px;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
}
.order-text { font-size: 14px; font-weight: 800; color: var(--ink); margin: 0; display: flex; align-items: center; gap: 8px; }

.order-type-badge {
    padding: 4px 9px; border-radius: 20px; font-size: 10.5px; font-weight: 800; border: 1px solid transparent;
    text-transform: uppercase; letter-spacing: .02em;
}
.order-type-badge.corp { background: var(--ok-bg); color: var(--ok); border-color: #ceead6; }
.order-type-badge.vitrine { background: var(--info-bg); color: var(--info); border-color: #d2e3fc; }
.order-type-badge:not(.corp):not(.vitrine) { background: var(--warn-bg); color: var(--warn); border-color: #fce8b2; }

.status-text { font-size: 14px; font-weight: 800; color: var(--brand); text-align: right; text-transform: uppercase; display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }

.info-card { background: #ffffff; border: 1px solid var(--border); border-radius: 14px; padding: 20px; box-shadow: 0 4px 14px rgba(90, 59, 40, 0.03); margin-bottom: 16px; height: 100%; transition: box-shadow .2s ease; }
.info-card:hover { box-shadow: 0 8px 22px rgba(90, 59, 40, 0.07); }
.card-title { font-size: 14px; font-weight: 800; color: var(--brand); margin-bottom: 12px; display: flex; align-items: center; gap: 6px; border-bottom: 1px dashed var(--border); padding-bottom: 6px; text-transform: uppercase; }

.data-label { font-size: 11.5px; color: var(--muted); font-weight: 700; text-transform: uppercase; margin-bottom: 2px; letter-spacing: .02em; }
.data-value { font-size: 14px; color: var(--ink-strong); font-weight: 600; margin-bottom: 12px; }
.item-pill { background: #faf7f3; border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 13.5px; font-weight: 600; color: var(--ink); }
.item-pill.discount { background: var(--warn-bg); border-color: #fce8b2; color: var(--warn); }

.resumo-financeiro { background: #fdfbf8; border: 1px solid var(--border); border-radius: 12px; padding: 16px; display: flex; justify-content: space-between; align-items: center; margin-top: 15px; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
.resumo-item { text-align: center; }
.resumo-label { font-size: 11.5px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: .02em; }
.resumo-valor { font-size: 15px; font-weight: 800; color: var(--ink); margin-top: 4px; }
.resumo-destaque { font-size: 16px; font-weight: 800; color: var(--ok); margin-top: 4px; }

.section-step { font-size: 14px; font-weight: 800; margin-bottom: 8px; margin-top: 15px; display: flex; align-items: center; gap: 8px; }
.step-num { width: 22px; height: 22px; border-radius: 50%; background: var(--brand); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; flex-shrink: 0; }

div[data-testid="stButton"] button { border-radius: 10px !important; font-weight: 800 !important; font-size: 13px !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button:hover { transform: translateY(-1px); }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border: none !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { box-shadow: 0 6px 16px rgba(19, 115, 51, .25); }
.btn-wpp > a { background: #25d366 !important; color: white !important; font-weight: 800 !important; font-size: 13px !important; border-radius: 10px !important; padding: 12px !important; display: flex; justify-content: center; align-items: center; text-decoration: none !important; transition: all .2s ease; }
.btn-wpp > a:hover { box-shadow: 0 6px 16px rgba(37, 211, 102, .3); transform: translateY(-1px); }
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff !important; border-radius: 14px !important; border: 1px solid var(--border) !important; padding: 18px !important; margin-bottom: 15px !important; }

@media (max-width: 1024px) {
    .info-card { padding: 16px; }
    .resumo-financeiro { justify-content: flex-start; gap: 18px; }
}

@media (max-width: 640px) {
    .block-container { padding-left: .8rem !important; padding-right: .8rem !important; padding-top: 1rem !important; }
    .order-header { padding: 12px 14px; flex-direction: column; align-items: flex-start; }
    .order-text { font-size: 13px; flex-wrap: wrap; }
    .status-text { text-align: left; justify-content: flex-start; width: 100%; }
    .info-card { padding: 14px; }
    .card-title { font-size: 12.5px; }
    .data-label { font-size: 10.5px; }
    .data-value { font-size: 13px; margin-bottom: 10px; }
    .item-pill { font-size: 12.5px; padding: 7px 10px; }
    .resumo-financeiro { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; padding: 14px; text-align: left; }
    .resumo-item { text-align: left; }
    .resumo-valor { font-size: 13.5px; }
    .resumo-destaque { font-size: 15px; }
    .section-step { font-size: 13px; }
    .step-num { width: 20px; height: 20px; font-size: 11px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 14px !important; }
}
</style>
""", unsafe_allow_html=True)


def salvar_nota_interna(pid, key):
    nova_nota = st.session_state[key]
    try:
        supabase.table("pedidos").update({"anotacoes_internas": nova_nota}).eq("id", pid).execute()
        st.toast("✅ Anotação interna salva com sucesso!")
    except Exception as e:
        st.toast(f"❌ Erro ao salvar anotação: {e}", icon="⚠️")


pedido_id = st.session_state.get('pedido_detalhe_id')
if not pedido_id:
    st.warning("Nenhum pedido selecionado.")
    if st.button("⬅️ Voltar aos Pedidos"): st.switch_page("pages/02_Pedidos.py")
    st.stop()

def obter_detalhe(p_id):
    res = supabase.table("pedidos").select("*").eq("id", p_id).execute()
    return res.data[0] if res.data else None

pedido = obter_detalhe(pedido_id)
if not pedido: st.stop()

cliente_id = pedido.get('cliente_id')
email_cliente = ""
if cliente_id:
    try:
        res_cliente = supabase.table("clientes").select("email").eq("id", cliente_id).execute()
        if res_cliente.data and 'email' in res_cliente.data[0] and res_cliente.data[0]["email"]:
            email_cliente = res_cliente.data[0]["email"]
    except: pass

cliente_nome_banco = pedido.get('cliente_nome') or ''
is_b2b = "[B2B]" in cliente_nome_banco
is_vitrine = "[VITRINE]" in cliente_nome_banco
cliente_limpo = cliente_nome_banco.replace("[B2B]", "").replace("[VITRINE]", "").strip()
tipo_classe = "corp" if is_b2b else ("vitrine" if is_vitrine else "")
tipo_texto = "🏢 CORPORATIVO" if is_b2b else ("🌐 VITRINE" if is_vitrine else "🛍️ VAREJO")
id_curto = str(pedido['id']).split('-')[0].upper()

# =====================================================
# CARREGAMENTO DIRETO DO BANCO (SEM CACHE)
# =====================================================
def obter_cestas():
    try:
        res = supabase.table("cestas").select("*").execute()
        return sorted(res.data or [], key=lambda x: x.get("nome", ""))
    except Exception as e: 
        return []

def obter_adicionais():
    try:
        cat_add = next((c for c in supabase.table("categorias").select("*").execute().data if c.get("nome", "").strip().lower() == "adicionais"), None)
        if cat_add:
            prods = supabase.table("produtos").select("*").eq("categoria_id", cat_add["id"]).execute()
            return sorted(prods.data or [], key=lambda x: x.get("nome", ""))
        return []
    except: return []

def carregar_config_cesta_no_cache(cesta_id):
    try: return carregar_configuracao_cesta(cesta_id)
    except: return []

def obter_fotos_do_pedido(pid):
    try:
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pid).execute()
        fotos = resposta.data or []
        supa_url = st.secrets.get("SUPABASE_URL", "").rstrip("/")
        for foto in fotos:
            if not foto.get("url") and foto.get("arquivo"):
                try:
                    link = supabase.storage.from_("pedido_fotos").get_public_url(foto["arquivo"])
                    foto["url"] = link if isinstance(link, str) else link.get("publicURL", link.get("publicUrl", ""))
                except:
                    if supa_url: foto["url"] = f"{supa_url}/storage/v1/object/public/pedido_fotos/{foto['arquivo']}"
        return fotos
    except: return []

vd_db = 0.0
for l in (pedido.get('adicionais') or '').split('\n'):
    if "Desconto" in l or "desconto" in l.lower():
        m = re.search(r'R\$\s*([\d\.,]+)', l)
        if m:
            try: vd_db += float(m.group(1).replace('.', '').replace(',', '.'))
            except: pass

total_db = tratar_preco(pedido.get('valor_total', 0))
frete_db = tratar_preco(pedido.get('valor_frete', 0))
subtotal_db = total_db - frete_db + vd_db  
desc_perc_inicial = float(round((vd_db / subtotal_db) * 100, 2)) if subtotal_db > 0 else 0.0

if "modo_edicao" not in st.session_state: st.session_state.modo_edicao = False
if "edit_cart" not in st.session_state or st.session_state.get("edit_pedido_id") != pedido_id:
    st.session_state["edit_cart"] = [{"id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": pedido.get("cesta_id"), "nome": pedido.get("cesta_nome") or "Cesta", "preco_unitario": subtotal_db, "quantidade": 1, "descricao": pedido.get("produtos") or ""}]
    st.session_state["edit_pedido_id"] = pedido_id

STATUS_PERMITIDOS = ["Recebido", "Pago", "Em Rota", "Entregue", "Desistência"]

# =====================================================
# CABEÇALHO COM TICKETS
# =====================================================
c_head, c_btn = st.columns([4, 1], vertical_alignment="center")
with c_head:
    tx_id_topo = pedido.get("infinitepay_transaction_id")
    badge_infinite = '<span style="background: #111; color: #00ffaa; padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 800; margin-right: 6px; border: 1px solid #333;">♾️ INFINITEPAY</span>' if tx_id_topo else ''

    status_db = pedido.get('status') or 'Recebido'
    entregador = pedido.get('entregador_login')
    is_montada = pedido.get('cesta_montada', False)
    
    tickets_visuais = []

    if status_db == 'Em Montagem':
        tickets_visuais.append('<span style="background: #fdf7e3; color: #b06000; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; border: 1px solid #fce8b2; margin-right: 6px;">⚙️ MONTAGEM INICIADA</span>')
    elif status_db == 'Pronto' or is_montada:
        tickets_visuais.append('<span style="background: #e6f4ea; color: #137333; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; border: 1px solid #ceead6; margin-right: 6px;">✅ CESTA MONTADA</span>')

    if status_db == 'Entregue':
        tickets_visuais.append('<span style="background: #f3e8fd; color: #6a1b9a; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; border: 1px solid #e9d2fd; margin-right: 6px;">🎉 PEDIDO ENTREGUE</span>')
    elif status_db in ['Enviado', 'Em Rota de Entrega'] or (entregador and status_db not in ['Entregue', 'Desistência']):
        tickets_visuais.append('<span style="background: #e8f0fe; color: #1a73e8; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; border: 1px solid #d2e3fc; margin-right: 6px;">🛵 PARA ENTREGA (ROTA)</span>')

    tickets_str = "".join(tickets_visuais)

    st.markdown(f"""
    <div class="order-header">
        <div class="order-text">Pedido #{id_curto} <span class="order-type-badge {tipo_classe}">{tipo_texto}</span></div>
        <div class="status-text">{badge_infinite} {tickets_str}</div>
    </div>
    """, unsafe_allow_html=True)
with c_btn:
    if st.button("⬅️ Voltar ao Mural", use_container_width=True):
        st.session_state.modo_edicao = False
        st.switch_page("pages/02_Pedidos.py")

# =====================================================
# MODO DE VISUALIZAÇÃO E AJUSTES RÁPIDOS
# =====================================================
if not st.session_state.modo_edicao:
    col1, col2 = st.columns(2)
    with col1:
        html_info1 = f"""<div class="info-card">
            <div class="card-title">👤 Informações do Pedido</div>
            <div class="data-label">Cliente / Empresa</div><div class="data-value">{esc(cliente_limpo)} ({esc(pedido.get('cliente_telefone'))})</div>
            <div class="data-label">CPF / CNPJ</div><div class="data-value">{esc(pedido.get('cliente_cpf'))}</div>
            <div class="data-label">E-mail Cadastrado</div><div class="data-value">{esc(email_cliente, 'Não informado')}</div>
            <div class="data-label" style="margin-top:10px;">Recebedor (Destinatário)</div><div class="data-value">{esc(pedido.get('destinatario_nome'))}</div>
            <div class="data-label">Ocasião / Motivo</div><div class="data-value">{esc(pedido.get('motivo_homenagem'))}</div>
            <div class="data-label" style="margin-top:10px;">Data e Período</div><div class="data-value">{esc(formatar_data_br(pedido.get('data_entrega')))} - {esc(pedido.get('periodo_entrega'))}</div>
            <div class="data-label">Endereço de Entrega</div><div class="data-value">{esc(pedido.get('endereco'))}</div>"""
        if (pedido.get('pedido_especial') or '').strip():
            html_info1 += f"""<div class="data-label" style="margin-top:15px; color:#5b21b6;">✨ Pedido Especial</div>
            <div style="background:#ede9fe; padding:10px; border-radius:8px; font-size:13px; color:#5b21b6; border-left:3px solid #5b21b6;">{esc(pedido.get('pedido_especial'))}</div>"""
        st.markdown(html_info1 + "</div>", unsafe_allow_html=True)

    with col2:
        html_info2 = """<div class="info-card"><div class="card-title">🎁 Detalhamento</div>"""
        
        cesta_principal = pedido.get('cesta_nome') or 'Cesta Personalizada'
        html_info2 += f"<div class='item-pill' style='background: #fef7e0; border-color: #fce8b2; color: #b06000; font-size: 14.5px;'>🛍️ <b>{esc(cesta_principal)}</b></div>"
        
        if pedido.get('produtos'):
            for linha in pedido.get('produtos').split("\n"):
                if linha.strip(): html_info2 += f"<div class='item-pill' style='margin-left: 15px;'>📦 {esc(linha.strip())}</div>"
                
        if pedido.get('adicionais'):
            html_info2 += "<div style='margin-top: 15px; margin-bottom: 5px; font-size: 11.5px; font-weight: 700; color: #8c7362; text-transform: uppercase;'>Adicionais e Extras</div>"
            for linha in pedido.get('adicionais').split("\n"):
                linha_limpa = linha.strip()
                if linha_limpa and not "EXTRAS E ADICIONAIS" in linha_limpa:
                    if "desconto" in linha_limpa.lower(): html_info2 += f"<div class='item-pill discount'>🔻 {esc(linha_limpa)}</div>"
                    else: html_info2 += f"<div class='item-pill'>✨ {esc(linha_limpa)}</div>"
                    
        if pedido.get('mensagem'):
            html_info2 += f"""<div class='data-label' style='margin-top: 15px;'>💌 Mensagem do Cartão</div>
            <div style='background:#fdfbf8; padding:10px; border-radius:8px; font-style:italic; font-size:13px; color:#4a2e1b; border-left:3px solid #c5721f;'>"{esc(pedido.get('mensagem'))}"</div>"""
        
        st.markdown(html_info2 + "</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div style='font-size: 13px; font-weight: 800; color: #b06000; margin-bottom: 4px;'>⚠️ Anotações Internas</div>", unsafe_allow_html=True)
        st.text_area("Anotações Internas", value=pedido.get('anotacoes_internas') or '', height=80, key=f"nota_{pedido_id}", on_change=salvar_nota_interna, args=(pedido_id, f"nota_{pedido_id}"), label_visibility="collapsed")

    # ==========================================================
    # EXIBIÇÃO DE FOTOS POLAROID DO CLIENTE 
    # ==========================================================
    fotos_anexadas = obter_fotos_do_pedido(pedido_id)
    
    if fotos_anexadas:
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #d1476a; margin-bottom: 8px; margin-top: 15px; text-transform: uppercase;'>📷 Fotos Polaroid / Anexos do Cliente</div>", unsafe_allow_html=True)
        with st.container(border=True):
            cols_fotos = st.columns(len(fotos_anexadas) if len(fotos_anexadas) < 4 else 4)
            for i, foto in enumerate(fotos_anexadas):
                with cols_fotos[i % 4]:
                    url_foto = foto.get("url")
                    if url_foto:
                        try:
                            st.image(url_foto, caption=foto.get("nome_original", f"Foto {i+1}"), use_container_width=True)
                            st.markdown(f'<div style="text-align: center;"><a href="{url_foto}" target="_blank" style="font-size:12px; text-decoration:none; color:#1a73e8; font-weight:700; border: 1px solid #d2e3fc; padding: 4px 10px; border-radius: 6px; background: #e8f0fe; display: inline-block; margin-top: 4px;">📥 Ampliar Imagem</a></div>', unsafe_allow_html=True)
                        except:
                            st.error("❌ Link da imagem quebrado.")
    else:
        adicionais_texto = str(pedido.get("adicionais", "")).lower()
        if "polaroid" in adicionais_texto or "foto" in adicionais_texto:
            st.warning("⚠️ **Aviso Importante:** Este pedido inclui 'Polaroid' ou 'Fotos' na lista de adicionais, mas nenhuma imagem foi encontrada anexada a ele no sistema.")

    st.markdown("<div class='section-step'><span class='step-num'>⚡</span><span style='color:#137333;'>Ajustes Rápidos & Valores</span></div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        with c_f1: e_frete_rapido = st.number_input("Frete / Taxa (R$)", min_value=0.0, step=5.0, value=float(frete_db), key=f"frete_rap_{pedido_id}")
        with c_f2: e_desc_rapido = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=float(desc_perc_inicial), key=f"desc_rap_{pedido_id}")
        
        pag_idx = ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"].index(pedido.get('pagamento') or 'Pix') if pedido.get('pagamento') in ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"] else 0
        with c_f3: e_pag_rapido = st.selectbox("Pagamento", ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"], index=pag_idx, key=f"pag_rap_{pedido_id}")
        
        st_idx = STATUS_PERMITIDOS.index(status_db) if status_db in STATUS_PERMITIDOS else 0
        with c_f4: e_status_rapido = st.selectbox("Status Físico", STATUS_PERMITIDOS, index=st_idx, key=f"status_rap_{pedido_id}")
        
        novo_vd = subtotal_db * (e_desc_rapido / 100)
        novo_total = subtotal_db - novo_vd + e_frete_rapido
        
        linha_html_desconto = f'<div class="resumo-item"><div class="resumo-label">Desconto</div><div class="resumo-valor" style="color:#c5221f;">- R$ {formatar_moeda(novo_vd)}</div></div>' if novo_vd > 0 else ''
        html_resumo = f"""<div class="resumo-financeiro">
        <div class="resumo-item"><div class="resumo-label">Subtotal</div><div class="resumo-valor">R$ {formatar_moeda(subtotal_db)}</div></div>{linha_html_desconto}
        <div class="resumo-item"><div class="resumo-label">Frete</div><div class="resumo-valor">R$ {formatar_moeda(e_frete_rapido)}</div></div>
        <div class="resumo-item"><div class="resumo-label">Pagamento</div><div class="resumo-valor">{esc(e_pag_rapido)}</div></div>
        <div class="resumo-item"><div class="resumo-label">TOTAL FINAL</div><div class="resumo-destaque">R$ {formatar_moeda(novo_total)}</div></div></div>"""
        st.markdown(html_resumo.replace('\n', ''), unsafe_allow_html=True)
        
        mudou_valores = (round(e_frete_rapido, 2) != round(frete_db, 2)) or (round(e_desc_rapido, 2) != round(desc_perc_inicial, 2)) or (e_pag_rapido != pedido.get('pagamento')) or (e_status_rapido != status_db)
        
        if mudou_valores:
            st.warning("⚠️ Você alterou os valores/status acima. Para aplicá-los e gerar um novo link de pagamento, clique em Salvar.")
            if st.button("💾 SALVAR AJUSTES RÁPIDOS", type="primary", use_container_width=True):
                ads_list = [l.strip() for l in (pedido.get('adicionais') or '').split('\n') if l.strip()]
                ads_list = [l for l in ads_list if not ("desconto" in l.lower())]
                if novo_vd > 0: ads_list.insert(0, f"Desconto: - R$ {formatar_moeda(novo_vd)}")
                
                update_data = {
                    "valor_frete": e_frete_rapido, "valor_total": novo_total, "pagamento": e_pag_rapido,
                    "status": e_status_rapido, "adicionais": "\n".join(ads_list)
                }
                if round(e_frete_rapido, 2) != round(frete_db, 2) or round(e_desc_rapido, 2) != round(desc_perc_inicial, 2):
                    update_data["infinitepay_url"] = None
                    update_data["infinitepay_transaction_id"] = None
                    
                try:
                    supabase.table("pedidos").update(update_data).eq("id", pedido_id).execute()
                    st.success("✅ Ajustes salvos com sucesso!")
                    st.rerun()
                except Exception as e: st.error(f"Erro ao salvar: {e}")

    # ===== BOTÕES E NOTIFICAÇÕES SEMPRE VISÍVEIS =====
    st.write("")
    link_pagamento_atual = pedido.get('infinitepay_url')
    if link_pagamento_atual: 
        st.success(f"🔗 **Link de Pagamento Gerado:** {link_pagamento_atual}")
    else:
        if st.button("💳 Gerar Link Encurtado para Pagamento", use_container_width=True):
            if gerar_link_checkout_infinitepay:
                with st.spinner("Gerando link seguro..."):
                    link_gerado = gerar_link_checkout_infinitepay(pedido_id=pedido_id, valor_total=total_db, cliente_nome=cliente_limpo, cliente_tel=pedido.get('cliente_telefone') or '')
                    if link_gerado:
                        supabase.table("pedidos").update({"infinitepay_url": link_gerado}).eq("id", pedido_id).execute()
                        st.success("✅ Link gerado!")
                        st.rerun()

    tx_id = pedido.get("infinitepay_transaction_id")
    if tx_id:
        data_pagamento = pedido.get("data_pagamento")
        try: data_f = datetime.strptime(str(data_pagamento)[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y às %H:%M:%S")
        except: data_f = str(data_pagamento)
        st.markdown(f"""
        <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px; margin:15px 0; display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;">
            <div><div class="data-label" style="color:#166534;">💳 Pagamento</div><div class="data-value" style="color:#15803d; font-size:15px;">♾️ InfinitePay ({esc(tx_id)})</div></div>
            <div><div class="data-label" style="color:#166534;">Horário da Aprovação</div><div class="data-value" style="color:#15803d; font-size:15px;">⏰ {esc(data_f)}</div></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-step' style='color:#1E293B;'>📲 Notificar Cliente</div>", unsafe_allow_html=True)
    fone_cliente = re.sub(r'\D', '', pedido.get('cliente_telefone') or '')
    linhas_wpp = "\n".join([f"📦 {p.strip()}" for p in (pedido.get('produtos') or '').split('\n') if p.strip()]) or f"📦 {pedido.get('cesta_nome') or 'Itens do Pedido'}"
    linhas_extras_wpp = "".join([f"🎀 {l.strip()}\n" for l in (pedido.get('adicionais') or '').split('\n') if l.strip() and "desconto" not in l.lower() and "EXTRAS" not in l.upper()])
    if linhas_extras_wpp: linhas_wpp += "\n" + linhas_extras_wpp.strip()

    texto_resumo = gerar_resumo_whatsapp(
        cliente=cliente_limpo, destinatario=pedido.get('destinatario_nome') or 'O mesmo',
        data=formatar_data_br(pedido.get('data_entrega')), periodo=pedido.get('periodo_entrega') or 'A combinar',
        local=pedido.get('endereco') or 'Não informado', itens_str=linhas_wpp,
        subtotal=subtotal_db, desconto=vd_db, frete=frete_db, total=total_db,
        pagamento=pedido.get('pagamento') or 'Pix', link_pagamento=link_pagamento_atual
    )

    with st.container(border=True):
        c_wpp, c_mail = st.columns(2)
        with c_wpp:
            link_wpp = gerar_link_wpp(fone_cliente, texto_resumo)
            if fone_cliente: st.markdown(f'<div class="btn-wpp"><a href="{link_wpp}" target="_blank">💬 Enviar Resumo (WhatsApp)</a></div>', unsafe_allow_html=True)
            else: st.warning("Sem telefone cadastrado.")
        with c_mail:
            e_col1, e_col2 = st.columns([2, 1])
            with e_col1: email_input = st.text_input("E-mail", value=email_cliente, placeholder="cliente@email.com", label_visibility="collapsed", key=f"email_dest_{pedido_id}")
            with e_col2:
                if st.button("✉️ Disparar E-mail", use_container_width=True):
                    if email_input:
                        sucesso, msg_retorno = enviar_email_cobranca(email_input, cliente_limpo, id_curto, texto_resumo, link_pagamento_atual)
                        if sucesso:
                            st.success(msg_retorno)
                            if cliente_id and email_input.strip() != email_cliente:
                                try:
                                    supabase.table("clientes").update({"email": email_input.strip()}).eq("id", cliente_id).execute()
                                except Exception as e:
                                    st.toast(f"⚠️ E-mail enviado, mas não foi possível atualizar o cadastro do cliente: {e}")
                        else: st.error(msg_retorno)
                    else: st.warning("⚠️ Digite um e-mail.")

    st.write("")
    if st.button("✏️ Editar Carrinho / Dados Completos", use_container_width=True):
        st.session_state.modo_edicao = True
        st.rerun()

    # ==========================================================
    # 🚨 ZONA DE PERIGO (LIMPEZA TOTAL DO PEDIDO E FOTOS)
    # ==========================================================
    if status_db == 'Desistência':
        st.markdown("<hr style='margin: 30px 0; border: none; border-top: 1px dashed #fce8e6;'>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div style='color: #c5221f; font-weight: 800; font-size: 15px; margin-bottom: 5px;'>🚨 ZONA DE PERIGO: Exclusão Definitiva</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 13px; color: #4a2e1b; margin-bottom: 12px; line-height: 1.5;'>Como este pedido foi marcado como <b>Desistência</b>, você pode apagá-lo definitivamente para organizar seu painel. <br>Isso irá limpar o banco de dados e <b>apagar permanentemente os arquivos físicos de fotos (Polaroid)</b> do servidor para não consumir sua memória.</div>", unsafe_allow_html=True)
            
            if st.button("🗑️ APAGAR PEDIDO E RASTROS PERMANENTEMENTE", type="primary", use_container_width=True):
                with st.spinner("Limpando banco de dados e arquivos..."):
                    try:
                        # 1. Buscar e apagar os arquivos físicos do Bucket de Fotos
                        fotos_bd = supabase.table("pedido_fotos").select("arquivo").eq("pedido_id", pedido_id).execute()
                        if fotos_bd.data:
                            arquivos = [f["arquivo"] for f in fotos_bd.data if f.get("arquivo")]
                            if arquivos:
                                supabase.storage.from_("pedido_fotos").remove(arquivos)
                        
                        # 2. Apagar das tabelas dependentes (Evita erro de Foreign Key)
                        supabase.table("pedido_fotos").delete().eq("pedido_id", pedido_id).execute()
                        supabase.table("pedido_adicionais").delete().eq("pedido_id", pedido_id).execute()
                        
                        # 3. Apagar o pedido principal
                        supabase.table("pedidos").delete().eq("id", pedido_id).execute()
                        
                        st.session_state['pedido_detalhe_id'] = None
                        st.success("✅ Pedido e fotos apagados com sucesso!")
                        st.switch_page("pages/02_Pedidos.py")
                    except Exception as e:
                        st.error(f"Erro ao excluir o pedido: {e}")

# =====================================================
# MODO EDIÇÃO (EDIÇÃO PROFUNDA - CARRINHO E COMPRADOR)
# =====================================================
else:
    st.info("✏️ **Modo de Edição Profunda Ativado.** Altere os dados abaixo e clique em Salvar.")
    with st.container(border=True):
        st.markdown("<div class='card-title'>👤 1. DADOS DO COMPRADOR</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: e_nome = st.text_input("Nome Comprador", value=pedido.get('cliente_nome') or '')
        with c2: e_tel = st.text_input("WhatsApp", value=pedido.get('cliente_telefone') or '')
        c3, c4 = st.columns(2)
        with c3: e_cpf = st.text_input("CPF / CNPJ", value=pedido.get('cliente_cpf') or '')
        with c4: e_email = st.text_input("E-mail (Salva no Perfil)", value=email_cliente)

    with st.container(border=True):
        st.markdown("<div class='card-title'>💌 2. DESTINATÁRIO, ENTREGA E CARTÃO</div>", unsafe_allow_html=True)
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
        with c9: 
            e_msg = st.text_area("Mensagem do Cartão", value=pedido.get('mensagem') or '', height=70)
            e_pedido_especial = st.text_area("Pedido Especial", value=pedido.get('pedido_especial') or '', height=70)
        with c10: 
            e_anotacoes = st.text_area("Anotações Internas", value=pedido.get('anotacoes_internas') or '', height=185)

    with st.container(border=True):
        st.markdown("<div class='card-title'>🎁 3. PRODUTOS E CARRINHO (FECHAMENTO)</div>", unsafe_allow_html=True)
        st.info("💡 **Dica:** Para alterar os itens/sabores da cesta atual, clique na lixeira (🗑️) abaixo, selecione a cesta novamente no campo, marque as novas opções e clique em Inserir.")
        
        col_add1, col_add2, col_add3 = st.columns(3)
        cestas_disponiveis, adicionais_disponiveis = obter_cestas(), obter_adicionais()
        
        with col_add1:
            cesta_atual_id = str(pedido.get("cesta_id")) if pedido.get("cesta_id") else None
            cesta_idx = 0
            if cesta_atual_id:
                for idx_c, c in enumerate(cestas_disponiveis):
                    if str(c["id"]) == cesta_atual_id:
                        cesta_idx = idx_c + 1
                        break
            
            cesta_sel = st.selectbox("Catálogo de Cestas / Kits", [None] + cestas_disponiveis, index=cesta_idx, format_func=lambda x: f"{x['nome']} ({x.get('secao_vitrine', 'Geral')})" if x else "Selecione...")
            
            selecoes_cesta_edit = {}
            if cesta_sel:
                cfg = carregar_config_cesta_no_cache(cesta_sel["id"])
                if cfg and any(grp.get("produtos") for grp in cfg):
                    st.markdown("<div style='font-size: 11.5px; font-weight: 700; color: #137333; margin-top: 5px; margin-bottom: 5px;'>🍓 Opções de Cesta:</div>", unsafe_allow_html=True)
                    for grp in cfg:
                        cat = grp.get("categoria", "Geral")
                        prods = grp.get("produtos", [])
                        maximo = grp.get("max_escolhas", 1)
                        if not prods: continue
                        if maximo == 1:
                            esc_prod = st.selectbox(f"{cat}", prods, format_func=lambda p: p["nome"], key=f"edit_rad_{cesta_sel['id']}_{cat}")
                            if esc_prod: selecoes_cesta_edit[cat] = [esc_prod]
                        else:
                            escs_prod = st.multiselect(f"{cat} (Máx: {maximo})", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"edit_mul_{cesta_sel['id']}_{cat}")
                            selecoes_cesta_edit[cat] = escs_prod
                else:
                    st.info("📌 Esta cesta não possui opções de personalização configuradas no sistema.")

            if st.button("➕ Inserir Cesta", use_container_width=True) and cesta_sel:
                produtos_txt = []
                if selecoes_cesta_edit:
                    for cat_nome, itens in selecoes_cesta_edit.items():
                        for it_prod in itens:
                            produtos_txt.append(f"{cat_nome}: {it_prod['nome']}")
                itens_sel_str = "\n".join(produtos_txt)

                preco_base = cesta_sel.get("preco")
                preco_calc = tratar_preco(preco_base) if preco_base is not None else 0.0

                st.session_state["edit_cart"].append({
                    "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_sel["id"], 
                    "nome": cesta_sel["nome"], "preco_unitario": preco_calc, 
                    "quantidade": 1, "descricao": itens_sel_str
                })
                st.rerun()
                
        with col_add2:
            adc_sel = st.selectbox("Extra do Catálogo", [None] + adicionais_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione...")
            if st.button("➕ Inserir Extra", use_container_width=True) and adc_sel:
                preco_base_adc = adc_sel.get("preco")
                preco_calc_adc = tratar_preco(preco_base_adc) if preco_base_adc is not None else 0.0
                st.session_state["edit_cart"].append({"id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": adc_sel["nome"], "preco_unitario": preco_calc_adc, "quantidade": 1, "descricao": ""})
                st.rerun()
                
        with col_add3:
            txt_man = st.text_input("Extra Manual", placeholder="Ex: Vinho Personalizado")
            if st.button("➕ Inserir Manual", use_container_width=True) and txt_man.strip():
                st.session_state["edit_cart"].append({"id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": txt_man.strip(), "preco_unitario": 0.0, "quantidade": 1, "descricao": ""})
                st.rerun()

        total_bruto = 0
        if st.session_state["edit_cart"]:
            st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
            for i, item in enumerate(st.session_state["edit_cart"]):
                c1, c2, c3, c4, c5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
                with c1: 
                    st.markdown(f"**{esc(item['nome'])}**")
                    if item.get("descricao"):
                        desc_html = item['descricao'].replace('\n', '<br>')
                        st.markdown(f"<div style='font-size:11px; color:#8c7362; line-height:1.2;'>{desc_html}</div>", unsafe_allow_html=True)
                with c2: n_preco = st.number_input("V", value=float(item["preco_unitario"]), key=f"e_p_{item['id']}", label_visibility="collapsed")
                with c3: n_qtd = st.number_input("Q", value=int(item["quantidade"]), min_value=1, key=f"e_q_{item['id']}", label_visibility="collapsed")
                with c4:
                    st.session_state["edit_cart"][i]["preco_unitario"] = n_preco
                    st.session_state["edit_cart"][i]["quantidade"] = n_qtd
                    sub_linha = n_preco * n_qtd
                    total_bruto += sub_linha
                    st.markdown(f"**R$ {formatar_moeda(sub_linha)}**")
                with c5:
                    if st.button("🗑️", key=f"e_d_{item['id']}"):
                        st.session_state["edit_cart"].pop(i)
                        st.rerun()

        # ==========================================================
        # 📷 DETECTOR INTELIGENTE E GERENCIADOR DE FOTOS (MODO EDIÇÃO)
        # ==========================================================
        carrinho_atual = st.session_state.get("edit_cart", [])
        termos_foto = ["polaroid", "foto", "revelação", "retrato", "imagem"]
        precisa_foto_edit = any(any(termo in str(item.get("nome", "")).lower() for termo in termos_foto) for item in carrinho_atual)
        
        fotos_existentes_edit = obter_fotos_do_pedido(pedido_id)

        fotos_upload_edit = []
        if precisa_foto_edit or fotos_existentes_edit:
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='background: #fdfbf8; border: 1px solid #e8ddd3; padding: 18px; border-radius: 12px;'>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 15px; font-weight: 800; color: #d1476a; margin-bottom: 12px;'>📷 Gerenciar Fotos Polaroid / Anexos</div>", unsafe_allow_html=True)
            
            # --- Exibir e Excluir fotos existentes ---
            if fotos_existentes_edit:
                st.markdown("<div style='font-size: 13px; font-weight: 700; color: #4a2e1b; margin-bottom: 8px;'>Fotos Já Salvas no Pedido:</div>", unsafe_allow_html=True)
                cols_fotos_edit = st.columns(len(fotos_existentes_edit) if len(fotos_existentes_edit) < 4 else 4)
                for idx, f_obj in enumerate(fotos_existentes_edit):
                    with cols_fotos_edit[idx % 4]:
                        if f_obj.get("url"):
                            st.image(f_obj["url"], use_container_width=True)
                            if st.button("🗑️ Remover", key=f"del_foto_edit_{f_obj['id']}", use_container_width=True):
                                with st.spinner("Excluindo..."):
                                    if f_obj.get("arquivo"):
                                        try: supabase.storage.from_("pedido_fotos").remove([f_obj["arquivo"]])
                                        except: pass
                                    supabase.table("pedido_fotos").delete().eq("id", f_obj["id"]).execute()
                                st.toast("✅ Foto removida com sucesso!")
                                st.rerun()
                st.markdown("<hr style='margin: 15px 0; border-top: 1px dashed #e8ddd3;'>", unsafe_allow_html=True)
            
            # --- Upload de novas fotos ---
            if precisa_foto_edit:
                st.markdown("<div style='font-size: 13px; font-weight: 700; color: #4a2e1b; margin-bottom: 8px;'>Adicionar Novas Imagens:</div>", unsafe_allow_html=True)
                fotos_upload_edit = st.file_uploader(
                    "Arraste ou selecione os arquivos", 
                    type=["jpg", "jpeg", "png", "webp", "heic"], 
                    accept_multiple_files=True, 
                    key="uploader_edit_polaroid_condicional",
                    label_visibility="collapsed"
                )
                if fotos_upload_edit:
                    st.success(f"✅ {len(fotos_upload_edit)} nova(s) foto(s) selecionada(s). Clique em SALVAR para enviar!")
            
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        with c_f1: e_frete = st.number_input("Frete / Taxa (R$)", min_value=0.0, step=5.0, value=tratar_preco(pedido.get('valor_frete', 0)))
        with c_f2: e_desc = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=desc_perc_inicial)
        with c_f3: e_pag = st.selectbox("Pagamento Edit", ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"], index=["Pix", "Cartão de Crédito", "Faturamento", "Transferência"].index(pedido.get('pagamento') or 'Pix') if pedido.get('pagamento') in ["Pix", "Cartão de Crédito", "Faturamento", "Transferência"] else 0)
        with c_f4: 
            status_atual = pedido.get('status') or 'Recebido'
            e_status = st.selectbox("Status Físico Edit", STATUS_PERMITIDOS, index=STATUS_PERMITIDOS.index(status_atual) if status_atual in STATUS_PERMITIDOS else 0)

        valor_desconto = total_bruto * (e_desc / 100)
        total_liquido = total_bruto - valor_desconto + e_frete
        st.markdown(f"<div class='resumo-financeiro'><div class='resumo-item'>TOTAL FINAL</div><div class='resumo-destaque'>R$ {formatar_moeda(total_liquido)}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    c_save1, c_save2 = st.columns(2)
    with c_save1:
        if st.button("💾 SALVAR ALTERAÇÕES COMPLETAS", type="primary", use_container_width=True):
            if not st.session_state["edit_cart"]: st.error("Carrinho vazio."); st.stop()
            
            lista_cestas = [it for it in st.session_state["edit_cart"] if it["tipo"] == "Cesta"]
            lista_extras = [it for it in st.session_state["edit_cart"] if it["tipo"] == "Extra"]
            
            str_prod = [f"{it.get('descricao','')}".strip() for it in lista_cestas if it.get('descricao')]
            str_ext = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_extras]
            
            n_cesta = lista_cestas[0]["nome"] if lista_cestas else "Pedido Editado"
            id_cesta = lista_cestas[0]["cesta_id"] if lista_cestas else None
            
            msg_add = f"Desconto: - R$ {formatar_moeda(valor_desconto)}" if valor_desconto > 0 else ""
            if str_ext: msg_add += "\nEXTRAS E ADICIONAIS:\n" + "\n".join(str_ext)

            dados_update = {
                "cliente_nome": e_nome.strip() + (" [B2B]" if is_b2b else (" [VITRINE]" if is_vitrine else "")),
                "cliente_telefone": e_tel, "cliente_cpf": e_cpf, "destinatario_nome": e_dest.strip(),
                "destinatario_telefone": e_dtel, "motivo_homenagem": e_motivo, "endereco": e_end,
                "data_entrega": e_data.strftime("%Y-%m-%d"), "periodo_entrega": e_per, "mensagem": e_msg,
                "anotacoes_internas": e_anotacoes.strip(), "pedido_especial": e_pedido_especial.strip(),
                "cesta_nome": n_cesta, "cesta_id": id_cesta, "produtos": "\n\n".join(str_prod),
                "adicionais": msg_add.strip(), "pagamento": e_pag, "status": e_status,
                "valor_frete": e_frete, "valor_total": total_liquido
            }
            try:
                supabase.table("pedidos").update(dados_update).eq("id", pedido_id).execute()
                
                # Se houver fotos novas anexadas, envia para o Bucket
                if fotos_upload_edit:
                    with st.spinner("📦 Salvando fotos Polaroid no servidor..."):
                        salvar_fotos(pedido_id, fotos_upload_edit)

                if cliente_id and e_email.strip() != email_cliente:
                    try:
                        supabase.table("clientes").update({"email": e_email.strip()}).eq("id", cliente_id).execute()
                    except Exception as e:
                        st.toast(f"⚠️ Pedido salvo, mas não foi possível atualizar o e-mail do cliente: {e}")
                st.success("✅ Atualizado!")
                st.session_state.modo_edicao = False
                st.rerun()
            except Exception as e: st.error(f"Erro: {e}")
    with c_save2:
        if st.button("❌ Cancelar", use_container_width=True): st.session_state.modo_edicao = False; st.rerun()
