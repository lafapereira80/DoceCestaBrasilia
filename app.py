import streamlit as st
import base64
import mimetypes
import urllib.parse
from pathlib import Path
from datetime import date

from config.supabase import supabase
from utils.formatacao import NOME_LOJA, NOME_LOJA_CURTO, TELEFONE_WHATSAPP, TELEFONE_EXIBICAO, INSTAGRAM_ARROBA, INSTAGRAM_URL

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(page_title=f"{NOME_LOJA} | Vitrine", page_icon="🎁", layout="wide", initial_sidebar_state="collapsed")

# ==========================================================
# CSS BOUTIQUE DE LUXO (O Segredo do Novo Design)
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Montserrat:wght@300;400;500;600;700;800&display=swap');

/* Oculta barras padrão */
section[data-testid="stSidebar"], [data-testid="collapsedControl"], header, footer, .stAppDeployMenu { display: none !important; }

/* Fundo da Página e Fontes Globais */
.stApp { background-color: #FCF9F2; }
html, body, [class*="css"], p, span, div { font-family: 'Montserrat', sans-serif; color: #2C1E14; }

/* Ajuste de Largura */
.block-container { max-width: 1100px !important; padding-top: 2rem !important; padding-bottom: 4rem !important; }

/* Hero Banner Exclusivo */
.hero-banner {
    text-align: center; padding: 3rem 2rem; margin-bottom: 2.5rem;
    background: radial-gradient(circle, #FFFFFF 0%, #FCF9F2 100%);
    border-bottom: 1px solid #F0E6DC; border-radius: 0 0 40px 40px;
    box-shadow: 0 10px 30px rgba(139, 90, 43, 0.03);
}
.hero-logo { width: 140px; height: auto; margin-bottom: 15px; filter: drop-shadow(0px 8px 16px rgba(0,0,0,0.08)); }
.hero-title { font-family: 'Dancing Script', cursive; font-size: clamp(40px, 6vw, 65px); color: #C5721F; margin: 0; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.03); }
.hero-subtitle { font-weight: 400; font-size: clamp(14px, 2vw, 18px); color: #8B5A2B; margin-top: 10px; letter-spacing: 1px; }

/* Cards Institucionais (Bem-vindo / Como pedir) */
.boutique-card {
    background: #FFFFFF; border: 1px solid #F0E6DC; border-radius: 16px; padding: 2.5rem 2rem; height: 100%;
    box-shadow: 0 10px 30px rgba(139, 90, 43, 0.04); transition: transform 0.4s ease, box-shadow 0.4s ease; text-align: center;
}
.boutique-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(139, 90, 43, 0.08); }
.card-title { font-family: 'Dancing Script', cursive; font-size: 38px; color: #C5721F; margin-top: 0; margin-bottom: 15px; line-height: 1; }
.card-text { font-size: 15px; line-height: 1.7; color: #555555; font-weight: 400; }
.card-list { text-align: left; font-size: 14px; color: #555555; line-height: 1.8; list-style-type: none; padding: 0; margin-top: 15px; }
.card-list li { margin-bottom: 8px; border-bottom: 1px dashed #F0E6DC; padding-bottom: 8px; }
.card-list li:last-child { border-bottom: none; }
.card-list b { color: #2C1E14; }

/* Abas (Tabs) do Streamlit */
div[data-testid="stTabs"] button { font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; font-size: 16px !important; color: #8B5A2B !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #C5721F !important; border-bottom-color: #C5721F !important; }

/* Container das Cestas (Streamlit nativo estilizado) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important; border: 1px solid #F0E6DC !important; border-radius: 20px !important;
    padding: 30px !important; margin-bottom: 25px !important; box-shadow: 0 10px 30px rgba(139, 90, 43, 0.03) !important;
    transition: all 0.4s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #E0D4C8 !important; box-shadow: 0 15px 40px rgba(139, 90, 43, 0.08) !important; transform: translateY(-3px); }

/* Detalhes da Cesta */
.cesta-nome { font-family: 'Dancing Script', cursive; font-size: clamp(34px, 4vw, 46px); color: #C5721F; margin: 0 0 10px 0; line-height: 1.1; }
.cesta-desc { font-size: 14px; color: #555555; line-height: 1.7; background: #FCF9F2; padding: 18px; border-radius: 12px; border-left: 3px solid #C5721F; margin-bottom: 20px; }
.cesta-preco { font-size: 32px; font-weight: 800; color: #2C1E14; margin-bottom: 20px; letter-spacing: -1px; }

/* Botões Arredondados de Luxo */
div[data-testid="stButton"] button {
    background-color: #2C1E14 !important; color: #FFFFFF !important; border-radius: 30px !important; 
    border: none !important; height: 55px !important; font-size: 15px !important; font-weight: 600 !important; 
    letter-spacing: 1px !important; text-transform: uppercase !important; transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(44, 30, 20, 0.2) !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #C5721F !important; box-shadow: 0 8px 25px rgba(197, 114, 31, 0.3) !important; transform: scale(1.02) !important;
}

/* Lightbox Elegante */
.lightbox-wrapper { text-align: center; }
.lightbox-toggle { display: none !important; }
.lightbox-image { width: 100%; max-width: 350px; border-radius: 16px; cursor: zoom-in; box-shadow: 0 8px 25px rgba(0,0,0,0.06); border: 1px solid #F0E6DC; transition: transform 0.4s ease; }
.lightbox-image:hover { transform: scale(1.02); }
.imagem-legenda { font-size: 11px; color: #8B5A2B; margin-top: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.lightbox-modal { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(252, 249, 242, 0.95); z-index: 999999; display: flex; align-items: center; justify-content: center; opacity: 0; visibility: hidden; transition: opacity 0.3s ease; cursor: zoom-out; backdrop-filter: blur(5px); }
.lightbox-modal img { max-width: 90vw; max-height: 90vh; border-radius: 16px; box-shadow: 0 20px 50px rgba(0,0,0,0.15); border: 4px solid #FFFFFF; }
.lightbox-toggle:checked ~ .lightbox-modal { opacity: 1; visibility: visible; }

/* Grid de Adicionais (Puro HTML/CSS para ser 100% Fluido) */
.extras-section { margin-top: 4rem; padding-top: 3rem; border-top: 1px solid #F0E6DC; text-align: center; }
.extras-title { font-family: 'Dancing Script', cursive; font-size: 40px; color: #C5721F; margin-bottom: 5px; }
.extras-sub { font-size: 14px; color: #8B5A2B; margin-bottom: 30px; }
.extras-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 20px; }
.extra-card { background: #FFFFFF; border: 1px solid #F0E6DC; border-radius: 16px; padding: 20px 10px; text-align: center; box-shadow: 0 5px 15px rgba(139, 90, 43, 0.03); transition: all 0.3s ease; }
.extra-card:hover { transform: translateY(-5px); border-color: #C5721F; box-shadow: 0 10px 25px rgba(139, 90, 43, 0.08); }
.extra-img { width: 80px; height: 80px; object-fit: cover; border-radius: 50%; border: 3px solid #FCF9F2; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 12px; }
.extra-placeholder { width: 80px; height: 80px; border-radius: 50%; background: #FCF9F2; border: 2px dashed #E0D4C8; display: flex; align-items: center; justify-content: center; font-size: 30px; margin: 0 auto 12px auto; color: #C5721F;}
.extra-nome { font-size: 13px; font-weight: 700; color: #2C1E14; margin-bottom: 8px; line-height: 1.3; min-height: 34px;}
.extra-preco { font-size: 15px; font-weight: 800; color: #C5721F; }

/* Rodapé Elegante */
.footer-box { margin-top: 4rem; background: #FFFFFF; border: 1px solid #F0E6DC; border-radius: 20px; padding: 3rem 2rem; text-align: center; box-shadow: 0 10px 30px rgba(139, 90, 43, 0.03); }
.footer-box h2 { font-family: 'Dancing Script', cursive; font-size: 36px; color: #C5721F; margin-top: 0; margin-bottom: 10px; }
.footer-box p { font-size: 15px; color: #555; margin-bottom: 25px; }
.btn-social { display: inline-flex; align-items: center; gap: 10px; padding: 12px 30px; border-radius: 30px; text-decoration: none; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease; margin: 5px; }
.btn-wpp { background-color: #25D366; color: #FFFFFF; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.2); }
.btn-wpp:hover { background-color: #1EBE57; transform: translateY(-3px); box-shadow: 0 8px 20px rgba(37, 211, 102, 0.3); }
.btn-insta { background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: #FFFFFF; box-shadow: 0 4px 15px rgba(220, 39, 67, 0.2); }
.btn-insta:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(220, 39, 67, 0.3); }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# LÓGICA E CACHING 
# ==========================================================
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

# ==========================================================
# RENDERIZAÇÃO DA PÁGINA (HERO + CARDS)
# ==========================================================
logo_path = Path("assets/logo.webp")
logo_html = f'<img src="data:image/webp;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" class="hero-logo">' if logo_path.exists() else ""

st.markdown(f"""
<div class="hero-banner">
    {logo_html}
    <h1 class="hero-title">{NOME_LOJA_CURTO}</h1>
    <div class="hero-subtitle">Memórias inesquecíveis em formato de presente 💝</div>
</div>
""", unsafe_allow_html=True)

# Usando as colunas nativas do Streamlit para não quebrar o layout mobile
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="boutique-card">
        <h2 class="card-title">Bem-vindo(a)</h2>
        <p class="card-text">É uma alegria receber você aqui! Acreditamos que todo dia alguém que amamos está vivendo um momento especial.<br><br>Nossas cestas são cuidadosamente montadas no estilo <strong>grazing</strong>, proporcionando sabores únicos e experiências visuais deslumbrantes. Desfrute o melhor da vida com quem você ama!</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="boutique-card">
        <h2 class="card-title">Como Pedir</h2>
        <ul class="card-list">
            <li>✨ Escolha uma opção abaixo e clique em <b>"Montar Cesta"</b></li>
            <li>⏳ Encomendas com no mínimo <b>24h de antecedência</b></li>
            <li>🚗 Entrega via <b>Uber Flash</b> ou retirada presencial</li>
            <li>💌 Todas as opções incluem um <b>cartão personalizável</b></li>
            <li>💳 Pagamento seguro via <b>PIX</b> ou <b>Cartão de Crédito</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center; font-family: \"Dancing Script\", cursive; font-size: 45px; color: #2C1E14; margin-top: 3rem; margin-bottom: 1.5rem;'>Nosso Catálogo</h2>", unsafe_allow_html=True)

with st.spinner("Preparando as doçuras..."):
    secoes, cestas = obter_vitrine_oficial()
    produtos_adicionais = obter_adicionais_vitrine()

if not cestas:
    st.info("Nosso catálogo está sendo renovado. Volte em instantes!")
else:
    nomes_secoes = [sec["nome"] for sec in secoes]
    abas = st.tabs(nomes_secoes) if len(nomes_secoes) > 1 else [st.container()]

    for i, aba in enumerate(abas):
        with aba:
            st.write("") 
            cestas_da_aba = [c for c in cestas if c.get("secao_vitrine", "Cestas de Café") == nomes_secoes[i]]
            
            for cesta in cestas_da_aba:
                with st.container(border=True):
                    # Alinhamento vertical center garante que a imagem e o texto fiquem harmoniosos
                    c_img, c_txt = st.columns([1, 1.8], gap="large", vertical_alignment="center")
                    
                    with c_img:
                        if cesta.get("imagem"):
                            img_src = image_to_base64(cesta["imagem"])
                            st.markdown(f"""
                                <div class="lightbox-wrapper">
                                    <label>
                                        <input type="checkbox" class="lightbox-toggle">
                                        <img src="{img_src}" class="lightbox-image" title="Ampliar">
                                        <div class="lightbox-modal"><img src="{img_src}"></div>
                                    </label>
                                    <div class="imagem-legenda">👆 Toque para ampliar</div>
                                </div>
                            """, unsafe_allow_html=True)

                    with c_txt:
                        st.markdown(f'<h3 class="cesta-nome">{cesta["nome"]}</h3>', unsafe_allow_html=True)
                        if cesta.get("descricao"): 
                            st.markdown(f'<div class="cesta-desc">{str(cesta["descricao"]).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                        
                        try:
                            preco = float(cesta.get("preco", 0))
                            st.markdown(f'<div class="cesta-preco">R$ {preco:,.2f}</div>'.replace(",", "X").replace(".", ",").replace("X","."), unsafe_allow_html=True)
                        except:
                            st.markdown('<div class="cesta-preco" style="font-size: 20px;">Preço sob consulta</div>', unsafe_allow_html=True)
                        
                        if st.button("🛒 Quero Montar Esta Cesta", key=f"btn_{cesta['id']}", use_container_width=True):
                            st.session_state["cesta_selecionada_home"] = cesta["id"]
                            st.switch_page("pages/01_Inicio.py")

# ==========================================================
# EXTRAS E ADICIONAIS (GRID PURO HTML/CSS)
# ==========================================================
if produtos_adicionais:
    cards_html = ""
    for prod in produtos_adicionais:
        preco_txt = f"R$ {float(prod.get('preco', 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X",".") if prod.get('preco') else "Consulta"
        
        if prod.get("imagem"):
            img_html = f'<label style="cursor:zoom-in;"><input type="checkbox" class="lightbox-toggle"><img src="{image_to_base64(prod["imagem"])}" class="extra-img"><div class="lightbox-modal"><img src="{image_to_base64(prod["imagem"])}"></div></label>'
        else:
            icone = "📷" if "polaroid" in prod.get("nome", "").lower() else "🎀"
            img_html = f'<div class="extra-placeholder">{icone}</div>'
            
        cards_html += f'<div class="extra-card">{img_html}<div class="extra-nome">{prod["nome"]}</div><div class="extra-preco">{preco_txt}</div></div>'

    st.markdown(f"""
    <div class="extras-section">
        <h2 class="extras-title">🎀 Toque Especial</h2>
        <div class="extras-sub">Adicionais incríveis para deixar o presente perfeito. Você poderá escolhê-los na próxima tela.</div>
        <div class="extras-grid">{cards_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# RODAPÉ
# ==========================================================
texto_wpp = "Olá! Gostaria de tirar dúvidas sobre as cestas."
link_wpp = f"https://wa.me/{TELEFONE_WHATSAPP}?text={urllib.parse.quote(texto_wpp)}"

st.markdown(f"""
<div class="footer-box">
    <h2>Fale Conosco</h2>
    <p>Ficou com alguma dúvida sobre entregas, prazos ou quer fazer uma encomenda corporativa?<br>Nossa equipe está pronta para te atender com todo o carinho.</p>
    <div>
        <a href="{link_wpp}" target="_blank" class="btn-social btn-wpp">💬 {TELEFONE_EXIBICAO}</a>
        <a href="{INSTAGRAM_URL}" target="_blank" class="btn-social btn-insta">📸 {INSTAGRAM_ARROBA}</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.markdown(f'<div style="text-align:center; font-size:12px; color:#8B5A2B; margin-top:20px;">{NOME_LOJA} © {date.today().year}</div>', unsafe_allow_html=True)
st.page_link("pages/99_Admin.py", label="Acesso Restrito Administrativo", icon="🔒")
