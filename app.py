import streamlit as st
import base64
import mimetypes
import urllib.parse
from pathlib import Path
from datetime import date

from config.supabase import supabase
from utils.formatacao import NOME_LOJA, NOME_LOJA_CURTO, TELEFONE_WHATSAPP, TELEFONE_EXIBICAO, INSTAGRAM_ARROBA, INSTAGRAM_URL

st.set_page_config(page_title=f"{NOME_LOJA} | Vitrine", page_icon="🎁", layout="wide", initial_sidebar_state="collapsed")

# Injeta o CSS Global limpo e moderno
def injetar_css():
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
injetar_css()

@st.cache_data(ttl=60, show_spinner=False)
def obter_vitrine_oficial():
    try:
        res_secoes = supabase.table("vitrine_secoes").select("*").eq("ativa", True).order("ordem").execute()
        res_cestas = supabase.table("cestas").select("*").eq("ativa", True).order("ordem").execute()
        return res_secoes.data or [{"nome": "Cestas de Café", "ordem": 1}], res_cestas.data or []
    except: return [{"nome": "Catálogo", "ordem": 1}], []

@st.cache_data(ttl=60, show_spinner=False)
def obter_adicionais_vitrine():
    try:
        categorias = supabase.table("categorias").select("*").execute().data or []
        cat_add = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)
        if cat_add: return supabase.table("produtos").select("*").eq("categoria_id", cat_add["id"]).eq("ativo", True).execute().data or []
    except: pass
    return []

def image_to_base64(img_path):
    img_path = str(img_path).strip()
    if img_path.startswith("http") or img_path.startswith("data:image"): return img_path
    try:
        with open(img_path, "rb") as f:
            return f"data:{mimetypes.guess_type(img_path)[0] or 'image/jpeg'};base64,{base64.b64encode(f.read()).decode()}"
    except: return img_path

if "cesta_selecionada_home" not in st.session_state: st.session_state["cesta_selecionada_home"] = None

# CABEÇALHO
logo_path = Path("assets/logo.webp")
logo_html = f'<img src="data:image/webp;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" class="header-logo">' if logo_path.exists() else "🎁"

st.markdown(f"""
<div class="header-banner">
    {logo_html}
    <div class="header-text">
        <h1 class="header-title">{NOME_LOJA_CURTO}</h1>
        <p class="header-subtitle">Cestas personalizadas para criar memórias inesquecíveis 💝</p>
    </div>
</div>
""", unsafe_allow_html=True)

# BEM-VINDO
st.markdown("""
<div class="info-grid">
    <div class="info-card">
        <h2 style="font-family: 'Dancing Script', cursive; font-size: 38px; color: #c5721f; text-align: center; margin-top:0;">Bem-vindo(a)</h2>
        <p style="text-align: justify; line-height: 1.6;">Nossas cestas são cuidadosamente montadas no estilo <strong>grazing</strong> e proporcionam não apenas sabores únicos, como a oportunidade de <strong>criar memórias inesquecíveis!</strong></p>
    </div>
    <div class="info-card">
        <h2 style="font-family: 'Dancing Script', cursive; font-size: 38px; color: #c5721f; text-align: center; margin-top:0;">Como Pedir</h2>
        <ul style="line-height: 1.6; padding-left: 20px;">
            <li>✨ Escolha no catálogo e clique em <b>"Monte sua Cesta"</b>.</li>
            <li>⏳ Peça com no mínimo <b>24h de antecedência</b>.</li>
            <li>🚗 Entrega via <b>Uber Flash</b> ou retirada em mãos.</li>
            <li>💳 Pagamento rápido via <b>PIX</b> ou <b>Cartão</b>.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h3>🎁 Catálogo Oficial</h3>", unsafe_allow_html=True)

with st.spinner("Preparando a vitrine..."):
    secoes, cestas = obter_vitrine_oficial()
    produtos_adicionais = obter_adicionais_vitrine()

if not cestas:
    st.info("O catálogo está sendo atualizado.")
else:
    nomes_secoes = [sec["nome"] for sec in secoes]
    abas = st.tabs(nomes_secoes) if len(nomes_secoes) > 1 else [st.container()]

    for i, aba in enumerate(abas):
        with aba:
            st.write("") 
            cestas_da_aba = [c for c in cestas if c.get("secao_vitrine", "Cestas de Café") == nomes_secoes[i]]
            
            for cesta in cestas_da_aba:
                with st.container(border=True):
                    col_img, col_text = st.columns([1.2, 2], gap="large", vertical_alignment="center")
                    with col_img:
                        if cesta.get("imagem"):
                            img_src = image_to_base64(cesta["imagem"])
                            st.markdown(f"""
                                <label style="cursor: zoom-in; width: 100%; text-align: center; display: block;">
                                    <input type="checkbox" style="display:none;">
                                    <img src="{img_src}" style="width: 75%; border-radius: 16px; border: 1px solid #e8ddd3;">
                                </label>
                            """, unsafe_allow_html=True)
                    with col_text:
                        st.markdown(f'<h2 style="font-family: \'Dancing Script\', cursive; font-size: 42px; color: #c5721f; margin:0;">{cesta["nome"]}</h2>', unsafe_allow_html=True)
                        if cesta.get("descricao"): st.markdown(f'<div style="background: #faf7f3; padding: 16px; border-radius: 12px; font-size: 14px; margin-bottom: 15px;">{str(cesta["descricao"]).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                        preco = float(cesta.get("preco", 0))
                        st.markdown(f'<div style="font-size: 26px; font-weight: 800; color: #137333; margin-bottom: 15px;">R$ {preco:,.2f}</div>'.replace(",", "X").replace(".", ",").replace("X","."), unsafe_allow_html=True)
                        
                        # O Botão de montagem agora tem cor laranja forte (Estilo da Cesta)
                        st.markdown("""<style>div[data-testid="stButton"] button { background: linear-gradient(135deg, #c5721f 0%, #9e520b) !important; box-shadow: 0 4px 15px rgba(197, 114, 31, 0.25) !important;}</style>""", unsafe_allow_html=True)
                        if st.button("🛒 Quero Montar Esta Cesta", key=f"btn_{cesta['id']}", use_container_width=True):
                            st.session_state["cesta_selecionada_home"] = cesta["id"]
                            st.switch_page("pages/01_Inicio.py")

if produtos_adicionais:
    cards_html = ""
    for prod in produtos_adicionais:
        preco_txt = f"R$ {float(prod.get('preco', 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X",".") if prod.get('preco') else "Consulta"
        img_html = f'<img src="{image_to_base64(prod["imagem"])}" style="width:70px; height:70px; object-fit:cover; border-radius:10px;">' if prod.get("imagem") else "🎀"
        cards_html += f'<div class="adicional-item-box">{img_html}<div style="font-size:12px; font-weight:700; margin-top:8px;">{prod["nome"]}</div><div style="color:#137333; font-weight:800; font-size:14px;">{preco_txt}</div></div>'

    st.markdown(f"""
    <div class="adicionais-hero-card">
        <h3 style="margin-top:0;">🎀 Incremente seu presente (Extras)</h3>
        <p style="font-size:13px; color:#888;">Você poderá escolher os itens na próxima tela.</p>
        <div class="adicionais-grid-css">{cards_html}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.divider()
st.markdown(f'<div style="text-align:center; font-size:13px; font-weight: 500;">Dúvidas? <a href="https://wa.me/{TELEFONE_WHATSAPP}" target="_blank" style="color:#137333; font-weight:800; text-decoration:none;">Chame no WhatsApp</a><br>{NOME_LOJA} © {date.today().year}</div>', unsafe_allow_html=True)
st.page_link("pages/99_Admin.py", label="Acesso Restrito Administrativo", icon="🔒")
