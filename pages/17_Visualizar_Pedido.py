import streamlit as st
import json
import urllib.parse
import re
from datetime import time as dt_time

from services.pedido_service import buscar_pedido
from services.pedido_adicional_service import listar_adicionais_pedido
from config.supabase import supabase
from services.cesta_service import buscar_cesta
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CACHING
# =====================================================
st.set_page_config(page_title="Visualizar Pedido", page_icon="👁️", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()
usuario = st.session_state.get("usuario", {})

@st.cache_data(ttl=60)
def obter_pedido_cacheado(pid):
    return buscar_pedido(pid)

@st.cache_data(ttl=120)
def obter_adicionais_cacheado(pid):
    try:
        return listar_adicionais_pedido(pid)
    except:
        return []

@st.cache_data(ttl=300)
def obter_cesta_cacheada(cesta_id):
    try:
        return buscar_cesta(cesta_id)
    except:
        return None

@st.cache_data(ttl=60)
def obter_fotos_cacheadas(pid):
    try:
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pid).order("created_at").execute()
        fotos = resposta.data or []
        url_base = st.secrets.get("SUPABASE_URL", "").rstrip("/")
        for foto in fotos:
            if not foto.get("url") and foto.get("arquivo"):
                foto["url"] = f"{url_base}/storage/v1/object/public/pedido_fotos/{foto['arquivo']}"
        return fotos
    except:
        return []

# =====================================================
# CSS PREMIUM (MESMO PADRÃO DA FICHA)
# =====================================================
st.markdown(
"""
<style>
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1250px; }
div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 0px !important; letter-spacing: -0.5px; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

div[data-testid="stVerticalBlockBorderWrapper"] { 
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 16px !important; 
    padding: 20px 24px !important; margin-bottom: 12px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03); 
}

.card-title { font-size: 16px !important; font-weight: 800 !important; color: #5a3b28 !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #f3ece6; padding-bottom: 6px; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.info-value { margin-bottom: 12px; color: #2c1e14; font-weight: 800; font-size: 14px !important; }

.resumo-container { background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%); border: 1px solid #e8ddd3; border-radius: 14px; padding: 18px; display: flex; flex-direction: column; gap: 8px; }
.resumo-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px !important; color: #444; padding: 4px 0; border-bottom: 1px dashed #e8ddd3; }
.resumo-row:last-child { border-bottom: none; padding-top: 10px; }
.resumo-label { font-weight: 600; color: #775a46; }
.resumo-val { font-weight: 800; color: #2c1e14; }
.resumo-total-val { font-size: 24px !important; font-weight: 800 !important; color: #137333 !important; }

.pgto-badge { background: #f3ece6; color: #5a3b28; padding: 3px 10px; border-radius: 8px; font-weight: 800; border: 1px solid #dfcdbb; font-size: 11px; text-transform: uppercase; }
.badge-montada { background-color: #e6f4ea; color: #137333; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 800; border: 1px solid #ceead6; margin-left: 10px; display: inline-block; text-transform: uppercase; letter-spacing: 0.5px; }

div[data-testid="stButton"] > button { border-radius: 10px !important; min-height: 42px !important; font-weight: 800 !important; font-size: 14px !important; }
div[data-testid="stLinkButton"] > a { width: 100% !important; border-radius: 10px !important; min-height: 42px !important; font-weight: 800 !important; font-size: 14px !important; display: flex !important; align-items: center !important; justify-content: center !important; background-color: #25D366 !important; color: white !important; border: none !important; }

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0px 0px; font-weight: 800; color: #5a3b28; background-color: #faf7f3; border: 1px solid #e8ddd3; padding: 10px 20px; }
.stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #c5721f !important; border-bottom: 2px solid #c5721f !important; }

@media (max-width: 768px) { 
    .block-container { padding: 1rem 0.5rem !important; } 
    h1 { font-size: 24px !important; } 
}
</style>
""",
unsafe_allow_html=True
)

if "pedido_aberto" not in st.session_state:
    st.error("Nenhum pedido selecionado.")
    if st.button("⬅ Voltar"):
        st.switch_page("pages/13_Historico_Cliente.py")
    st.stop()

pedido_id = st.session_state["pedido_aberto"]
pedido = obter_pedido_cacheado(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()

# =====================================================
# FUNÇÕES AUXILIARES DE LEITURA
# =====================================================
lista_bruta_adicionais = obter_adicionais_cacheado(pedido["id"])
adicionais_pedido = []
nomes_vistos = set()
for ad in lista_bruta_adicionais:
    nome_ad = ad.get("nome_produto")
    if nome_ad and nome_ad not in nomes_vistos:
        adicionais_pedido.append(ad)
        nomes_vistos.add(nome_ad)

itens_consulta_salvos = pedido.get("itens_consulta") or {}
if isinstance(itens_consulta_salvos, str):
    try:
        itens_consulta_salvos = json.loads(itens_consulta_salvos)
    except:
        itens_consulta_salvos = {}

def formatar_valor(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
    except: return "R$ 0,00"

def formatar_data(data):
    if not data: return "-"
    try:
        ano, mes, dia = str(data)[:10].split("-")
        return f"{dia}/{mes}/{ano}"
    except: return str(data)

def obter_icone_pagamento(metodo):
    m = str(metodo).strip().lower()
    if "pix" in m: return '<div class="pgto-badge" style="background: #e6f4ea; border-color: #137333; color: #137333;">⚡ PIX</div>'
    elif "cart" in m: return '<div class="pgto-badge" style="background: #e8f0fe; border-color: #1a73e8; color: #1a73e8;">💳 CARTÃO</div>'
    elif "dinheiro" in m: return '<div class="pgto-badge" style="background: #fef7e0; border-color: #b06000; color: #b06000;">💵 DINHEIRO</div>'
    elif "transfer" in m: return '<div class="pgto-badge" style="background: #f3ece6; border-color: #5a3b28; color: #5a3b28;">🏦 TRANSF.</div>'
    return f'<span class="pgto-badge">{metodo}</span>'

# =====================================================
# CABEÇALHO (APENAS LEITURA)
# =====================================================
col_t1, col_t2 = st.columns([3.5, 1.2])
with col_t1:
    st.title("👁️ Visualização de Pedido")
    badge_montada = '<span class="badge-montada">✅ Cesta Montada</span>' if pedido.get("cesta_montada") else ''
    st.markdown(f"**ID #{pedido.get('id')}** | Status: **{pedido.get('status','-')}** {badge_montada}", unsafe_allow_html=True)
with col_t2:
    st.write("")
    if st.button("⬅ Voltar ao Histórico", use_container_width=True):
        st.switch_page("pages/13_Historico_Cliente.py")

st.write("")

# =====================================================
# ABAS DE VISUALIZAÇÃO (100% TRAVADAS)
# =====================================================
aba_geral, aba_itens, aba_financeiro, aba_anexos = st.tabs([
    "📋 1. Visão Geral & Logística", 
    "🍓 2. Personalização & Extras", 
    "💰 3. Fechamento Financeiro", 
    "📷 4. Anotações & Polaroids"
])

# 1. VISÃO GERAL
with aba_geral:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.container(border=True):
            st.markdown('<div class="card-title">👤 Informações de Contato</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-label">Comprador</div><div class="info-value">{pedido.get("cliente_nome") or "-"} <span style="font-size:12px;color:#666;">(CPF: {pedido.get("cliente_cpf") or "-"})</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">📞 +{pedido.get("cliente_telefone") or "-"}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-label">Homenageado (Destinatário)</div><div class="info-value">{pedido.get("destinatario_nome") or "-"} (📞 {pedido.get("destinatario_telefone") or "Não inf."})</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-label">Motivo</div><div class="info-value">{pedido.get("motivo_homenagem") or "-"}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="card-title">💌 Cartão de Homenagem</div>', unsafe_allow_html=True)
            st.text_area("", value=pedido.get("mensagem") or "Sem mensagem informada.", disabled=True, height=85, label_visibility="collapsed")

    with col_g2:
        with st.container(border=True):
            st.markdown('<div class="card-title">🎁 Detalhes da Entrega e Pacote</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: 
                st.markdown(f'<div class="info-label">Cesta Adquirida</div><div class="info-value">{pedido.get("cesta_nome","-")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-label">Data Limite</div><div class="info-value">{formatar_data(pedido.get("data_entrega"))}</div>', unsafe_allow_html=True)
            with c2: 
                st.markdown(f'<div class="info-label">Forma de Pagto</div><div class="info-value">{obter_icone_pagamento(pedido.get("pagamento", "-"))}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-label">Período Ideal</div><div class="info-value">{pedido.get("periodo_entrega","-")}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="card-title">✨ Observações Especiais</div>', unsafe_allow_html=True)
            st.text_area("", value=pedido.get("pedido_especial") or "Nenhuma solicitação especial.", disabled=True, height=85, label_visibility="collapsed")

    with st.container(border=True):
        st.markdown('<div class="card-title">📍 Localização e Roteirização (GPS)</div>', unsafe_allow_html=True)
        endereco_pedido = pedido.get("endereco", "")
        st.text_area("", value=endereco_pedido if endereco_pedido else "O cliente não informou o endereço completo.", disabled=True, height=65, label_visibility="collapsed")
        if endereco_pedido:
            endereco_limpo_gps = re.sub(r'\(CEP:.*?\)', '', endereco_pedido).strip()
            endereco_encoded = urllib.parse.quote(endereco_limpo_gps)
            col_map1, col_map2 = st.columns(2)
            with col_map1: st.link_button("🗺️ Abrir no Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_encoded}", use_container_width=True)
            with col_map2: st.link_button("🚗 Abrir Rota no Waze", url=f"https://waze.com/ul?q={endereco_encoded}&navigate=yes", use_container_width=True)

# 2. PERSONALIZAÇÃO & EXTRAS
with aba_itens:
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        with st.container(border=True):
            st.markdown('<div class="card-title">🛒 Checklist / Composição da Cesta</div>', unsafe_allow_html=True)
            produtos = pedido.get("produtos", "")
            if produtos:
                for item in produtos.split("\n"): st.markdown(f"<div style='font-size:13px; margin-bottom:6px; font-weight:600;'>✅ {item.replace('•','').strip()}</div>", unsafe_allow_html=True)
            else: st.caption("Nenhum item configurado.")

    with col_i2:
        with st.container(border=True):
            st.markdown('<div class="card-title">🎀 Adicionais e Extras do Pedido</div>', unsafe_allow_html=True)
            if adicionais_pedido:
                for adicional in adicionais_pedido:
                    nome = adicional.get("nome_produto", "-")
                    valor = adicional.get("valor_unitario")
                    if valor is not None:
                        st.markdown(f"<div style='font-size:13px; margin-bottom:6px; font-weight:600;'>➕ {nome} - <span style='color:#137333;'>{formatar_valor(valor)}</span></div>", unsafe_allow_html=True)
                    else:
                        val_manual = itens_consulta_salvos.get(nome, 0)
                        st.markdown(f"<div style='font-size:13px; margin-bottom:6px; font-weight:600;'>➕ {nome} - <span style='color:#137333;'>{formatar_valor(val_manual)}</span></div>", unsafe_allow_html=True)
            else: st.caption("Nenhum adicional solicitado.")

# 3. FECHAMENTO FINANCEIRO
with aba_financeiro:
    valor_cesta = 0.0
    cesta = obter_cesta_cacheada(pedido.get("cesta_id"))
    if cesta: valor_cesta = float(cesta.get("preco", 0) or 0)

    valor_adicionais_catalogo = 0.0
    for ad in adicionais_pedido:
        nome_ad = ad.get("nome_produto")
        val_ad = ad.get("valor_unitario")
        if val_ad is not None: valor_adicionais_catalogo += float(val_ad)
        else: valor_adicionais_catalogo += float(itens_consulta_salvos.get(nome_ad, 0) or 0)

    # Soma extras avulsos salvos no JSON
    valor_extras_total = 0.0
    extras_lista_visualizacao = []
    for k, v in itens_consulta_salvos.items():
        if "Valor Manual de" not in k and not k.startswith("Valor de "):
            valor_extras_total += float(v)
            extras_lista_visualizacao.append({"nome": k, "valor": float(v)})

    valor_frete = float(pedido.get("valor_frete") or 0)
    desconto = float(pedido.get("desconto") or 0)
    valor_total_calculado = max(0, valor_cesta + valor_adicionais_catalogo + valor_frete + valor_extras_total - desconto)

    col_f1, col_f2 = st.columns([1.2, 1])
    with col_f1:
        with st.container(border=True):
            st.markdown('<div class="card-title">💰 Informações Logísticas e Fiscais</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-label">Horário Fixo de Entrega</div><div class="info-value">🕒 {pedido.get("horario_combinado") or "Não definido"}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-label">Status do Pedido</div><div class="info-value">{pedido.get("status")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-label">Cesta Montada</div><div class="info-value">{"✅ Sim" if pedido.get("cesta_montada") else "⏳ Não"}</div>', unsafe_allow_html=True)

    with col_f2:
        with st.container(border=True):
            st.markdown('<div class="card-title">🧮 Extrato do Recibo Oficial</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="resumo-container">
                    <div class="resumo-row"><span class="resumo-label">🎁 Valor da Cesta</span><span class="resumo-val">{formatar_valor(valor_cesta)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🎀 Adicionais (Catálogo)</span><span class="resumo-val">{formatar_valor(valor_adicionais_catalogo)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🚚 Taxa de Entrega</span><span class="resumo-val">{formatar_valor(valor_frete)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">➕ Extras Dinâmicos</span><span class="resumo-val">{formatar_valor(valor_extras_total)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🏷️ Desconto</span><span class="resumo-val" style="color: #c5221f;">- {formatar_valor(desconto)}</span></div>
                    <div class="resumo-row"><span class="resumo-label" style="font-size:15px; font-weight:800; color:#2c1e14;">💰 VALOR FINAL</span><span class="resumo-total-val">{formatar_valor(valor_total_calculado)}</span></div>
                </div>
                """, unsafe_allow_html=True
            )

# 4. ANOTAÇÕES & POLAROIDS
with aba_anexos:
    col_an1, col_an2 = st.columns(2)
    with col_an1:
        with st.container(border=True):
            st.markdown('<div class="card-title">📝 Anotações Internas</div>', unsafe_allow_html=True)
            st.text_area("", value=pedido.get("anotacoes_internas") or "Nenhuma anotação registrada.", disabled=True, height=140, label_visibility="collapsed")

    with col_an2:
        with st.container(border=True):
            st.markdown('<div class="card-title">📷 Fotos Polaroid & Anexos</div>', unsafe_allow_html=True)
            fotos = obter_fotos_cacheadas(pedido["id"])
            if fotos:
                colunas = st.columns(2)
                for i, foto in enumerate(fotos):
                    with colunas[i % 2]:
                        link_imagem = foto.get("url")
                        if link_imagem:
                            st.image(link_imagem, caption=foto.get("nome_original", "Foto"), use_container_width=True)
                        else: st.caption("⚠️ Link quebrado.")
            else: st.caption("Nenhum anexo ou Polaroid neste pedido.")

st.write("")
st.divider()
if st.button("⬅ Voltar para o Histórico de Clientes", use_container_width=True):
    st.switch_page("pages/13_Historico_Cliente.py")

st.write("")
st.caption("📋 Ficha de Visualização - Doce Cesta Brasília")
