import streamlit as st
import base64
import mimetypes
from pathlib import Path
import importlib
import json

from services.cesta_service import listar_cestas
from services.produto_service import listar_produtos_por_categoria_id
from services.vitrine_service import obter_configuracao_vitrine

def obter_categorias():
    try:
        cat_service = importlib.import_module("services.categoria_service")
        for nome_funcao in dir(cat_service):
            if "listar_categoria" in nome_funcao: return getattr(cat_service, nome_funcao)()
    except: pass 
    try:
        from config.supabase import supabase
        return supabase.table("categorias").select("*").execute().data or []
    except Exception as e: return []

st.set_page_config(page_title="Doce Cesta Brasília | Vitrine de Cestas", page_icon="🎁", layout="wide", initial_sidebar_state="collapsed")

def image_to_base64(img_path):
    img_path = str(img_path).strip()
    if img_path.startswith("http") or img_path.startswith("data:image"): return img_path
    try:
        with open(img_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            mime = mimetypes.guess_type(img_path)[0] or "image/jpeg"
            return f"data:{mime};base64,{b64}"
    except: return img_path

# Carrega todas as configurações do Banco
config_vitrine = obter_configuracao_vitrine()

cabecalho_titulo = config_vitrine.get("cabecalho_titulo", "Doce Cesta Brasília")
cabecalho_subtitulo = config_vitrine.get("cabecalho_subtitulo", "Cestas personalizadas para momentos inesquecíveis 💝")

texto_boas_vindas = config_vitrine.get("boas_vindas_texto", "").replace('\n', '<br>')
itens_como_pedir = config_vitrine.get("como_pedir_itens", [])
if isinstance(itens_como_pedir, str):
    try: itens_como_pedir = json.loads(itens_como_pedir)
    except: itens_como_pedir = []
html_lista_como_pedir = "".join([f"<li>{item}</li>" for item in itens_como_pedir])

catalogo_titulo = config_vitrine.get("catalogo_titulo", "🎁 Catálogo de Cestas")
catalogo_subtitulo = config_vitrine.get("catalogo_subtitulo", "Escolha a cesta perfeita, confira os itens detalhados e personalize do seu jeito.")

adicionais_titulo = config_vitrine.get("adicionais_titulo", "🎀 Incremente seu presente com nossos Adicionais Especiais:")

rodape_titulo = config_vitrine.get("rodape_titulo", "Fale Conosco")
rodape_texto = config_vitrine.get("rodape_texto", "")
rodape_wpp_num = config_vitrine.get("rodape_whatsapp_numero", "5561999759079")
rodape_wpp_texto = config_vitrine.get("rodape_whatsapp_texto", "💬 (61) 99975-9079")
rodape_insta_usu = config_vitrine.get("rodape_instagram_usuario", "docecestabrasilia")
rodape_insta_texto = config_vitrine.get("rodape_instagram_texto", "📸 @docecestabrasilia")

ordem_layout = config_vitrine.get("ordem_layout", ["textos", "catalogo", "adicionais"])
if isinstance(ordem_layout, str):
    try: ordem_layout = json.loads(ordem_layout)
    except: ordem_layout = ["textos", "catalogo", "adicionais"]

mostrar_textos = config_vitrine.get("mostrar_textos", True)
mostrar_catalogo = config_vitrine.get("mostrar_catalogo", True)
mostrar_adicionais = config_vitrine.get("mostrar_adicionais", True)
mostrar_rodape = config_vitrine.get("mostrar_rodape", True)

st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Montserrat:wght@400;500;600;700;800&display=swap');
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { visibility: hidden !important; height: 0px !important; }
footer { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }
html, body, [class*="css"]  { font-family: 'Montserrat', sans-serif !important; }
.block-container { max-width: 1080px !important; padding-top: 1rem !important; padding-bottom: 3rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
.header-banner { display: flex; align-items: center; justify-content: center; gap: 24px; margin-bottom: 1.5rem; width: 100%; background: #ffffff; padding: 20px 24px; border-radius: 18px; border: 1px solid #e8ddd3; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.04); }
.header-logo { width: 140px; height: auto; object-fit: contain; flex-shrink: 0; }
.header-text { display: flex; flex-direction: column; justify-content: center; text-align: left; }
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; }
.header-subtitle { font-size: 14px !important; font-weight: 500 !important; color: #5a3b28 !important; margin-top: 4px !important; margin-bottom: 0 !important; letter-spacing: 0.5px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-bottom: 1rem; margin-top: 1rem;}
.info-card { background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); border: 1px solid #e2d2c3; border-radius: 16px; padding: 12px 24px; box-shadow: 0 3px 10px rgba(90, 59, 40, 0.03); display: flex; flex-direction: column; height: 100%; }
.info-title { font-family: 'Dancing Script', cursive !important; font-size: 38px !important; font-weight: 700 !important; color: #c5721f !important; margin-top: 0 !important; margin-bottom: 16px !important; text-align: center; }
.info-text { font-size: 14.5px !important; color: #5a3b28 !important; line-height: 1.6 !important; font-weight: 400 !important; text-align: justify; }
.info-text strong { color: #2e7d32 !important; }
.como-pedir-list { text-align: left; font-size: 14px; color: #5a3b28; line-height: 1.6; margin: 0; padding-left: 20px; }
.como-pedir-list li { margin-bottom: 10px; }
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 18px !important; padding: 18px !important; margin-bottom: 12px !important; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.04); transition: all 0.25s ease !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #cbab92 !important; box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08); }
@media (min-width: 641px) { div[data-testid="stHorizontalBlock"] { align-items: center !important; } }
.card-cesta-titulo { font-family: 'Dancing Script', cursive !important; font-size: 36px !important; font-weight: 700 !important; color: #c5721f !important; margin-top: 0px !important; margin-bottom: 8px !important; line-height: 1.1 !important; }
.card-cesta-desc { font-size: 13.5px !important; color: #4d3e35 !important; line-height: 1.55 !important; text-align: justify !important; margin-bottom: 14px !important; background: #fcf9f5; padding: 14px; border-radius: 12px; border: 1px solid #f0e6dc; }
.card-cesta-preco { font-size: 24px !important; font-weight: 800 !important; color: #2e7d32 !important; margin-bottom: 16px !important; }
div[data-testid="stButton"] button { background: linear-gradient(135deg, #c5721f 0%, #a65d14 100%) !important; color: white !important; border-radius: 30px !important; height: 50px !important; font-size: 15px !important; font-weight: 700 !important; border: none !important; box-shadow: 0 4px 14px rgba(197, 114, 31, 0.3) !important; transition: all 0.3s ease !important; text-transform: uppercase; letter-spacing: 0.5px; }
div[data-testid="stButton"] button:hover { transform: translateY(-3px) !important; box-shadow: 0 6px 18px rgba(197, 114, 31, 0.45) !important; background: linear-gradient(135deg, #b56210 0%, #914f0f 100%) !important; }
.lightbox-wrapper { text-align: center; margin-bottom: 6px; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.lightbox-toggle { display: none !important; }
.lightbox-image { width: 60%; border-radius: 12px; cursor: zoom-in; transition: transform 0.2s ease, box-shadow 0.2s ease; box-shadow: 0 4px 10px rgba(90, 59, 40, 0.1); object-fit: cover; }
.lightbox-image:hover { transform: scale(1.02); box-shadow: 0 6px 15px rgba(90, 59, 40, 0.2); }
.imagem-legenda { text-align: center; font-size: 11.5px; color: #888; margin-top: 8px; font-style: italic; }
.lightbox-modal { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.85); z-index: 999999; display: flex; align-items: center; justify-content: center; opacity: 0; visibility: hidden; transition: opacity 0.3s ease; cursor: zoom-out; }
.lightbox-modal img { max-width: 90vw; max-height: 90vh; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
.lightbox-toggle:checked ~ .lightbox-modal { opacity: 1; visibility: visible; }
.adicionais-hero-card { background: linear-gradient(135deg, #ffffff 0%, #faf5f0 100%); border: 1px solid #e2d2c3; border-radius: 16px; padding: 20px 24px; margin-top: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 3px 10px rgba(90, 59, 40, 0.03); }
.adicionais-hero-title { font-family: 'Montserrat', sans-serif !important; font-size: 16px; font-weight: 700; color: #5a3b28; margin-bottom: 16px; }
.adicionais-grid-css { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.adicional-item-box { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 14px; padding: 12px 8px; text-align: center; box-shadow: 0 4px 10px rgba(90, 59, 40, 0.04); display: flex; flex-direction: column; justify-content: space-between; align-items: center; }
.adicional-img-small { width: 60px; height: 60px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); cursor: zoom-in; display: block; margin: 0 auto; }
.adicional-img-placeholder { width: 60px; height: 60px; background: linear-gradient(135deg, #fdfbf8 0%, #f5eee6 100%); display: flex; align-items: center; justify-content: center; font-size: 22px; border-radius: 8px; border: 1px solid #f0e6dc; margin: 0 auto; }
.adicional-nome { font-size: 11.5px; font-weight: 700; color: #4d3e35; margin-top: 6px; margin-bottom: 4px; min-height: 28px; line-height: 1.25; }
.adicional-preco-fixo { color: #2e7d32; font-weight: 800; font-size: 12px; }
.adicional-preco-consulta { color: #c5721f; font-weight: 700; background: #fff8ef; padding: 2px 6px; border-radius: 10px; font-size: 9.5px; display: inline-block; }
.footer-container { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 18px; padding: 24px; text-align: center; margin-top: 2rem; box-shadow: 0 2px 8px rgba(90, 59, 40, 0.03); }
.footer-title { font-family: 'Dancing Script', cursive !important; font-size: 32px !important; font-weight: 700 !important; color: #c5721f; margin-bottom: 8px; }
.footer-text { font-size: 13.5px; color: #5a3b28; margin-bottom: 16px; line-height: 1.5; }
.social-btn-box { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }
.social-btn-box a { display: inline-flex; align-items: center; gap: 8px; color: white !important; padding: 12px 24px; border-radius: 12px; font-weight: 600; text-decoration: none; font-size: 14px; transition: all 0.2s ease; }
.btn-whatsapp { background: #25d366 !important; box-shadow: 0 3px 8px rgba(37, 211, 102, 0.25); }
.btn-instagram { background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%) !important; box-shadow: 0 3px 8px rgba(220, 39, 67, 0.25); }
@media (max-width: 900px) { .adicionais-grid-css { grid-template-columns: repeat(3, 1fr) !important; } }
@media (max-width: 640px) {
    .block-container { padding-top: 0.5rem !important; padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
    .header-banner { flex-direction: column !important; align-items: center !important; text-align: center !important; padding: 20px 16px !important; gap: 12px !important; }
    .header-text { align-items: center !important; text-align: center !important; width: 100% !important; }
    .header-logo { width: 110px !important; margin: 0 auto !important; }
    .header-title { font-size: 36px !important; margin-bottom: 6px !important; }
    .info-card { padding: 12px 16px !important; } 
    .info-title { font-size: 32px !important; }
    .card-cesta-titulo { font-size: 30px !important; text-align: center; }
    .card-cesta-preco { font-size: 22px !important; text-align: center; }
    .lightbox-image { width: 80%; }
    .adicionais-grid-css { grid-template-columns: repeat(2, 1fr) !important; gap: 10px !important; }
}
</style>
""",
unsafe_allow_html=True
)

logo_path = Path("assets/logo.webp")
logo_html = ""
if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    logo_html = f'<img src="data:image/webp;base64,{encoded_logo}" class="header-logo" alt="Logo">'

st.markdown(
    f"""<div class="header-banner">{logo_html}<div class="header-text"><h1 class="header-title">{cabecalho_titulo}</h1><p class="header-subtitle">{cabecalho_subtitulo}</p></div></div>""",
    unsafe_allow_html=True
)

def renderizar_textos():
    st.markdown(f"""<div class="info-grid"><div class="info-card"><div class="info-title">Bem-vindo(a)</div><div class="info-text">{texto_boas_vindas}</div></div><div class="info-card"><div class="info-title">Como fazer o pedido</div><ul class="como-pedir-list">{html_lista_como_pedir}</ul></div></div>""", unsafe_allow_html=True)

def renderizar_catalogo():
    st.markdown(f"<h3 style='font-family: \"Montserrat\", sans-serif; color:#5a3b28; margin-top:0; margin-bottom:4px; font-weight:800; font-size: 22px;'>{catalogo_titulo}</h3>", unsafe_allow_html=True)
    st.caption(f"{catalogo_subtitulo}")
    try:
        cestas = listar_cestas()
        cestas = [c for c in cestas if c.get("ativa", True)]
        for cesta in cestas:
            if "ordem" not in cesta or cesta["ordem"] is None: cesta["ordem"] = 999 
        cestas = sorted(cestas, key=lambda c: c["ordem"])
    except: cestas = []

    if not cestas: st.info("Nenhuma cesta cadastrada no momento.")
    else:
        for cesta in cestas:
            with st.container(border=True):
                col_img, col_text = st.columns([1.2, 2], gap="medium")
                with col_img:
                    imagem_url = cesta.get("imagem")
                    if imagem_url and str(imagem_url).strip():
                        img_src = image_to_base64(imagem_url)
                        st.markdown(f"""<div class="lightbox-wrapper"><label style="cursor: zoom-in; width: 100%; display: flex; flex-direction: column; align-items: center;"><input type="checkbox" class="lightbox-toggle"><img src="{img_src}" class="lightbox-image" title="Clique para ampliar"><div class="lightbox-modal"><img src="{img_src}"></div></label><div class="imagem-legenda">👆 Toque na foto para ampliar</div></div>""", unsafe_allow_html=True)
                    fotos_extras = cesta.get("fotos_adicionais", [])
                    if isinstance(fotos_extras, list) and len(fotos_extras) > 0:
                        st.caption("📸 Outros ângulos:")
                        cols_extras = st.columns(min(len(fotos_extras), 3))
                        for f_idx, f_url in enumerate(fotos_extras[:3]):
                            if f_url and str(f_url).strip():
                                with cols_extras[f_idx]: st.image(str(f_url).strip(), use_container_width=True)
                with col_text:
                    st.markdown(f'<div class="card-cesta-titulo">{cesta["nome"]}</div>', unsafe_allow_html=True)
                    if cesta.get("descricao") and str(cesta["descricao"]).strip(): st.markdown(f'<div class="card-cesta-desc">{cesta["descricao"]}</div>', unsafe_allow_html=True)
                    try: st.markdown(f'<div class="card-cesta-preco">R$ {float(cesta.get("preco", 0)):,.2f}</div>'.replace(",", "X").replace(".", ",").replace("X","."), unsafe_allow_html=True)
                    except: st.markdown('<div class="card-cesta-preco">Preço sob consulta</div>', unsafe_allow_html=True)
                    if st.button("🛒 Monte sua Cesta", key=f"cesta_btn_{cesta['id']}", use_container_width=True):
                        st.session_state["cesta_selecionada_home"] = cesta["id"]
                        st.switch_page("pages/formcompra.py")

def renderizar_adicionais():
    try:
        categorias = obter_categorias() 
        cat_adicionais = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)
        produtos_adicionais = listar_produtos_por_categoria_id(cat_adicionais["id"]) if cat_adicionais else []
    except: produtos_adicionais = []

    if produtos_adicionais:
        cards_html = ""
        for prod in produtos_adicionais:
            nome_p, preco_p, imagem_p = prod.get("nome", ""), prod.get("preco"), prod.get("imagem")
            if preco_p is not None and str(preco_p).strip() != "":
                try: span_preco = f'<span class="adicional-preco-fixo">R$ {float(preco_p):,.2f}</span>'.replace(",", "X").replace(".", ",").replace("X",".")
                except: span_preco = '<span class="adicional-preco-consulta">Sob Consulta</span>'
            else: span_preco = '<span class="adicional-preco-consulta">Sob Consulta</span>'

            if imagem_p and str(imagem_p).strip():
                img_src = image_to_base64(imagem_p)
                img_html = f'<label style="cursor: zoom-in; display: inline-block; margin-bottom: 4px;"><input type="checkbox" class="lightbox-toggle"><img src="{img_src}" class="adicional-img-small" title="Clique para ampliar"><div class="lightbox-modal"><img src="{img_src}"></div></label>'
            else: img_html = f'<div class="adicional-img-placeholder">🎀</div>'
            cards_html += f'<div class="adicional-item-box">{img_html}<div class="adicional-nome">{nome_p}</div><div>{span_preco}</div></div>'

        st.markdown(f"""<div class="adicionais-hero-card"><div class="adicionais-hero-title">{adicionais_titulo}<span style="font-size: 12px; font-weight: normal; color: #888; display: block; margin-top: 4px;">👉 Toque em qualquer foto para ampliar</span></div><div class="adicionais-grid-css">{cards_html}</div></div>""", unsafe_allow_html=True)


for bloco in ordem_layout:
    if bloco == "textos" and mostrar_textos: renderizar_textos()
    elif bloco == "catalogo" and mostrar_catalogo: renderizar_catalogo()
    elif bloco == "adicionais" and mostrar_adicionais: renderizar_adicionais()


if mostrar_rodape:
    link_wpp = f"https://wa.me/{rodape_wpp_num}?text=Olá!%20Gostaria%20de%20tirar%20dúvidas%20sobre%20as%20cestas."
    link_insta = f"https://instagram.com/{rodape_insta_usu}"
    
    st.markdown(
        f"""
        <div class="footer-container">
            <div class="footer-title">{rodape_titulo}</div>
            <div class="footer-text">{rodape_texto}</div>
            <div class="social-btn-box">
                <a href="{link_wpp}" target="_blank" class="btn-whatsapp">{rodape_wpp_texto}</a>
                <a href="{link_insta}" target="_blank" class="btn-instagram">{rodape_insta_texto}</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")
st.page_link("pages/99_Admin.py", label="Área Administrativa", icon="🔒")
