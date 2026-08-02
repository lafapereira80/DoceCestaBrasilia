import streamlit as st
import base64
import html
import mimetypes
from pathlib import Path

from config.supabase import supabase

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Doce Cesta Brasília | Vitrine Oficial",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ASSETS_DIR = Path("assets").resolve()


def _url_imagem_segura(url):
    """Só aceita http(s) ou data-URI de imagem — bloqueia esquemas perigosos (ex: javascript:)."""
    url = str(url or "").strip()
    if url.startswith(("http://", "https://", "data:image/")):
        return url
    return ""


# ==========================================================
# CACHING DINÂMICO (VITRINE SEMPRE ATUALIZADA)
# ==========================================================
@st.cache_data(ttl=5, show_spinner=False)
def obter_vitrine_oficial():
    """Busca as seções e cestas ativas direto do banco de dados"""
    try:
        res_secoes = supabase.table("vitrine_secoes").select("*").eq("ativa", True).order("ordem").execute()
        secoes = res_secoes.data or []
        
        res_cestas = supabase.table("cestas").select("*").eq("ativa", True).order("ordem").execute()
        cestas = res_cestas.data or []
        
        if not secoes:
            secoes = [{"nome": "Cestas de Café", "ordem": 1}]
            
        return secoes, cestas
    except Exception as e:
        print(f"Erro ao carregar vitrine: {e}")
        return [{"nome": "Catálogo", "ordem": 1}], []

@st.cache_data(ttl=5, show_spinner=False)
def obter_adicionais_vitrine():
    """Busca os produtos cadastrados na categoria de Adicionais"""
    try:
        categorias = supabase.table("categorias").select("*").execute().data or []
        cat_add = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)
        
        if cat_add:
            res_prods = supabase.table("produtos").select("*").eq("categoria_id", cat_add["id"]).eq("ativo", True).execute()
            return res_prods.data or []
    except:
        pass
    return []

# Função auxiliar para garantir que o Lightbox leia qualquer tipo de imagem
@st.cache_data(show_spinner=False)
def image_to_base64(img_path):
    """
    Converte uma imagem local em data-URI base64.
    Por segurança, só lê arquivos dentro da pasta assets/ do projeto — evita que um
    valor inesperado no campo 'imagem' do banco vire leitura arbitrária de arquivo
    do servidor. URLs http(s) e data-URIs passam direto, sem tocar o disco.
    """
    img_path = str(img_path).strip()
    if not img_path:
        return ""
    if img_path.startswith("http") or img_path.startswith("data:image"):
        return img_path
    try:
        caminho_resolvido = (ASSETS_DIR / img_path).resolve()
        caminho_resolvido.relative_to(ASSETS_DIR)  # levanta ValueError se sair de assets/
        with open(caminho_resolvido, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            mime = mimetypes.guess_type(str(caminho_resolvido))[0] or "image/jpeg"
            return f"data:{mime};base64,{b64}"
    except Exception:
        return ""

# ==========================================================
# CSS PREMIUM E LIGHTBOX (VITRINE DO CLIENTE)
# ==========================================================

st.markdown(
"""
<style>
/* Importação de Fontes Elegantes */
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Montserrat:wght@400;500;600;700;800&display=swap');

/* Remoção de elementos padrão do Streamlit (Modo Vitrine) */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { visibility: hidden !important; height: 0px !important; }
footer { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }
.stAppDeployMenu { display: none !important; }

/* Fontes Globais */
html, body, [class*="css"]  {
    font-family: 'Montserrat', sans-serif !important;
}

/* Container Principal */
.block-container {
    max-width: 1150px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* =========================================
   BANNER / CABEÇALHO PRINCIPAL
========================================= */
.header-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
    margin-bottom: 2rem;
    width: 100%;
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%);
    padding: 24px 30px;
    border-radius: 20px;
    border: 1px solid #e8ddd3;
    box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
    position: relative; 
    top: 0;
    transition: all 0.3s ease;
}
.header-banner:hover { top: -2px; }

.header-logo { width: 150px; height: auto; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.05)); }
.header-text { display: flex; flex-direction: column; justify-content: center; text-align: left; }
.header-title {
    font-family: 'Dancing Script', cursive !important;
    font-size: 48px !important;
    font-weight: 700 !important;
    color: #c5721f !important;
    margin: 0 !important;
    line-height: 1.1 !important;
}
.header-subtitle {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #5a3b28 !important;
    margin-top: 6px !important;
    margin-bottom: 0 !important;
    letter-spacing: 0.5px;
}

/* =========================================
   GRID PARA OS CARDS INSTITUCIONAIS
========================================= */
.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 24px;
    margin-bottom: 2.5rem; 
}
.info-card {
    background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%);
    border: 1px solid #e8ddd3;
    border-radius: 18px;
    padding: 20px 28px; 
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03);
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative; 
    top: 0;
    transition: all 0.3s ease;
}
.info-card:hover {
    border-color: #d2bfae;
    box-shadow: 0 8px 25px rgba(90, 59, 40, 0.06);
    top: -3px;
}
.info-title {
    font-family: 'Dancing Script', cursive !important;
    font-size: 38px !important;
    font-weight: 700 !important;
    color: #c5721f !important;
    margin-top: 0 !important;
    margin-bottom: 16px !important;
    text-align: center;
}
.info-text {
    font-size: 14.5px !important;
    color: #4a2e1b !important;
    line-height: 1.6 !important;
    font-weight: 500 !important;
    text-align: justify;
}
.info-text strong { color: #2e7d32 !important; font-weight: 700 !important; }

/* Lista de Como Pedir */
.como-pedir-list { text-align: left; font-size: 14px; color: #4a2e1b; line-height: 1.6; margin: 0; padding-left: 20px; font-weight: 500; }
.como-pedir-list li { margin-bottom: 12px; }
.como-pedir-list li:last-child { margin-bottom: 0; }

/* =========================================
   ABAS (TABS) PARA SEÇÕES
========================================= */
div[data-testid="stTabs"] button {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important; font-size: 16px !important; color: #8c7362 !important; padding-bottom: 10px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] { color: #c5721f !important; border-bottom-color: #c5721f !important; }


/* =========================================
   CARDS DE CESTA (LISTA HORIZONTAL)
========================================= */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 20px !important;
    padding: 24px !important;
    margin-bottom: 20px !important; 
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03);
    position: relative; 
    top: 0;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #cbab92 !important;
    box-shadow: 0 12px 30px rgba(90, 59, 40, 0.08);
    top: -4px;
}

@media (min-width: 641px) { div[data-testid="stHorizontalBlock"] { align-items: center !important; } }

/* NOME DA CESTA */
.card-cesta-titulo {
    font-family: 'Dancing Script', cursive !important;
    font-size: 42px !important;
    font-weight: 700 !important;
    color: #c5721f !important;
    margin-top: 0px !important;
    margin-bottom: 10px !important;
    line-height: 1.1 !important;
}

/* Texto de Descrição */
.card-cesta-desc {
    font-size: 14px !important;
    color: #4d3e35 !important;
    line-height: 1.6 !important;
    text-align: justify !important;
    margin-bottom: 16px !important;
    background: #faf7f3;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #f0e6dc;
}

.card-cesta-preco {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #137333 !important;
    margin-bottom: 18px !important;
}

/* BOTÃO MONTE SUA CESTA */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #c5721f 0%, #9e520b 100%) !important;
    color: white !important;
    border-radius: 14px !important; 
    height: 54px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(197, 114, 31, 0.25) !important;
    position: relative; 
    top: 0;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="stButton"] button:hover {
    top: -3px !important;
    box-shadow: 0 8px 20px rgba(197, 114, 31, 0.4) !important;
    background: linear-gradient(135deg, #b56210 0%, #874609 100%) !important;
}

/* =========================================
   LIGHTBOX CSS (CORRIGIDO PARA TELA CHEIA)
========================================= */
.lightbox-wrapper { text-align: center; margin-bottom: 10px; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.lightbox-toggle { display: none !important; }
.lightbox-image {
    width: 65%; 
    border-radius: 14px;
    cursor: zoom-in;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.1);
    object-fit: cover;
    border: 1px solid #e8ddd3;
}
.lightbox-image:hover { transform: scale(1.03); box-shadow: 0 8px 20px rgba(90, 59, 40, 0.15); }
.imagem-legenda { text-align: center; font-size: 12px; color: #888; margin-top: 10px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.lightbox-modal {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-color: rgba(0, 0, 0, 0.85); z-index: 999999;
    display: flex; align-items: center; justify-content: center;
    opacity: 0; visibility: hidden; transition: opacity 0.3s ease; cursor: zoom-out;
}
.lightbox-modal img { max-width: 90vw; max-height: 90vh; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
.lightbox-toggle:checked ~ .lightbox-modal { opacity: 1; visibility: visible; }

/* =========================================
   GRID CSS DE ADICIONAIS (EXTRAS AVULSOS)
========================================= */
.adicionais-hero-card {
    background: linear-gradient(135deg, #ffffff 0%, #faf7f3 100%);
    border: 1px solid #e8ddd3;
    border-radius: 20px;
    padding: 24px 30px;
    margin-top: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03);
}
.adicionais-hero-title { font-size: 18px; font-weight: 800; color: #5a3b28; margin-bottom: 20px; }
.adicionais-grid-css { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }

/* REGRAS DE LAYOUT CORRIGIDAS (SEM TRANSFORM) */
.adicional-item-box {
    background: #ffffff;
    border: 1px solid #e8ddd3;
    border-radius: 16px;
    padding: 16px 10px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(90, 59, 40, 0.02);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    position: relative; 
    top: 0;
    transition: all 0.3s ease;
}
.adicional-item-box:hover {
    border-color: #d2bfae;
    top: -4px; /* Move a caixa sem quebrar o modal de tela cheia */
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08);
}

.adicional-img-small { width: 70px; height: 70px; object-fit: cover; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); cursor: zoom-in; display: block; margin: 0 auto; border: 1px solid #f0e6dc; }
.adicional-img-placeholder { width: 70px; height: 70px; background: linear-gradient(135deg, #fdfbf8 0%, #f5eee6 100%); display: flex; align-items: center; justify-content: center; font-size: 26px; border-radius: 10px; border: 1px dashed #dfcdbb; margin: 0 auto; }
.adicional-nome { font-size: 12.5px; font-weight: 700; color: #4a2e1b; margin-top: 10px; margin-bottom: 6px; min-height: 32px; line-height: 1.3; }
.adicional-preco-fixo { color: #137333; font-weight: 800; font-size: 14px; }
.adicional-preco-consulta { color: #c5721f; font-weight: 800; background: #fff8ef; padding: 4px 8px; border-radius: 8px; font-size: 10px; text-transform: uppercase; border: 1px solid #fce8b2; display: inline-block; }

/* =========================================
   RODAPÉ (FALE CONOSCO)
========================================= */
.footer-container {
    background: #ffffff;
    border: 1px solid #e8ddd3;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    margin-top: 3rem;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03);
}
.footer-title { font-family: 'Dancing Script', cursive !important; font-size: 38px !important; font-weight: 700 !important; color: #c5721f; margin-bottom: 10px; }
.footer-text { font-size: 14px; color: #5a3b28; margin-bottom: 20px; line-height: 1.6; font-weight: 500; }
.social-btn-box { display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }
.social-btn-box a {
    display: inline-flex; align-items: center; gap: 8px; color: white !important;
    padding: 14px 28px; border-radius: 14px; font-weight: 800; text-decoration: none; font-size: 15px;
    position: relative; 
    top: 0;
    transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px;
}
.social-btn-box a:hover { top: -3px; }
.btn-whatsapp { background: #25d366 !important; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3); }
.btn-whatsapp:hover { box-shadow: 0 6px 16px rgba(37, 211, 102, 0.45); }
.btn-instagram { background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%) !important; box-shadow: 0 4px 12px rgba(220, 39, 67, 0.3); }
.btn-instagram:hover { box-shadow: 0 6px 16px rgba(220, 39, 67, 0.45); }

/* =========================================
   RESPONSIVO — TABLET (≤ 1024px)
========================================= */
@media (max-width: 1024px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .header-title { font-size: 40px !important; }
    .header-logo { width: 120px; }
    .info-title { font-size: 32px !important; }
    .card-cesta-titulo { font-size: 34px !important; }
    .adicionais-grid-css { grid-template-columns: repeat(4, 1fr) !important; }
}

/* =========================================
   RESPONSIVO EXCLUSIVO MOBILE
========================================= */
@media (max-width: 900px) { .adicionais-grid-css { grid-template-columns: repeat(3, 1fr) !important; } }

@media (max-width: 640px) {
    .block-container { padding-top: 1rem !important; padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
    
    /* GANTE ALINHAMENTO CENTRAL NO CELULAR PARA O TOPO */
    .header-banner { flex-direction: column !important; align-items: center !important; text-align: center !important; padding: 24px 16px !important; gap: 16px !important; }
    .header-text { align-items: center !important; text-align: center !important; width: 100% !important; }
    .header-logo { width: 120px !important; margin: 0 auto !important; }
    .header-title { font-size: 40px !important; margin-bottom: 6px !important; text-align: center !important; }
    .header-subtitle { text-align: center !important; font-size: 14px !important; }
    
    .info-card { padding: 16px 20px !important; } 
    .info-title { font-size: 34px !important; }
    .card-cesta-titulo { font-size: 32px !important; text-align: center; }
    .card-cesta-preco { font-size: 24px !important; text-align: center; }
    .lightbox-image { width: 85%; }
    
    /* Celular: Força exatamente 2 colunas lado a lado nos adicionais */
    .adicionais-grid-css { grid-template-columns: repeat(2, 1fr) !important; gap: 12px !important; }
}
</style>
""",
unsafe_allow_html=True
)

# ==========================================================
# INICIALIZAÇÃO DA SESSÃO
# ==========================================================
if "cesta_selecionada_home" not in st.session_state:
    st.session_state["cesta_selecionada_home"] = None

# ==========================================================
# CABEÇALHO / LOGO DA MARCA
# ==========================================================
@st.cache_data(show_spinner=False)
def carregar_logo_base64():
    caminho = Path("assets/logo.webp")
    if not caminho.exists():
        return ""
    with open(caminho, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_b64 = carregar_logo_base64()
logo_html = f'<img src="data:image/webp;base64,{logo_b64}" class="header-logo" alt="Logo Doce Cesta Brasília">' if logo_b64 else ""

st.markdown(
    f"""
    <div class="header-banner">
        {logo_html}
        <div class="header-text">
            <h1 class="header-title">Doce Cesta Brasília</h1>
            <p class="header-subtitle">Cestas personalizadas para criar memórias inesquecíveis 💝</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# SEÇÃO: BEM-VINDO & COMO PEDIR 
# ==========================================================
st.markdown(
    """<div class="info-grid"><div class="info-card"><div class="info-title">Bem-vindo(a)</div><div class="info-text"><div style="text-align: center; margin-bottom: 12px;">É uma alegria receber você aqui! Acreditamos que todo dia alguém que amamos está vivendo um momento especial.</div>Nossas cestas são cuidadosamente montadas no estilo <strong>grazing</strong> e proporcionam não apenas sabores únicos e envolventes, como também a oportunidade de <strong>criar memórias inesquecíveis!</strong><br><br><div style="text-align: center;">Desfrute o melhor da vida com um bom café e uma excelente companhia!</div></div></div><div class="info-card"><div class="info-title">Como fazer o pedido</div><ul class="como-pedir-list"><li>✨ Defina através do nosso catálogo abaixo a opção desejada e clique em <b>"Monte sua Cesta"</b>.</li><li>⏳ Peça sua Doce Cesta com no mínimo <b>24h de antecedência</b> (ou <b>72h</b> caso possua mini bolo).</li><li>🕒 <b>Atendimento:</b> Segunda a sexta de 7h às 19h | Sábado de 8h às 12h.</li><li>🚗 A entrega poderá ser realizada via <b>Uber Flash / 99 Entrega</b> ou retirada em mãos.</li><li>💌 Todas as cestas contêm um <b>cartão personalizável</b> para o homenageado.</li><li>💳 <b>Pagamento:</b> PIX ou link de Cartão de Crédito.</li></ul></div></div>""",
    unsafe_allow_html=True
)

# ==========================================================
# TÍTULO PRINCIPAL DO CATÁLOGO
# ==========================================================
st.markdown("<h3 style='font-family: \"Montserrat\", sans-serif; color:#4a2e1b; margin-top:10px; margin-bottom:4px; font-weight:800; font-size: 26px; letter-spacing: -0.5px;'>🎁 Catálogo Oficial</h3>", unsafe_allow_html=True)
st.caption("Escolha a cesta perfeita, confira os itens detalhados e personalize do seu jeito em nosso formulário.")

# ==========================================================
# CARREGAMENTO DOS DADOS DINÂMICOS
# ==========================================================
with st.spinner("Preparando a vitrine..."):
    secoes, cestas = obter_vitrine_oficial()
    produtos_adicionais = obter_adicionais_vitrine()

if not cestas:
    st.info("O catálogo está sendo atualizado. Nenhuma cesta disponível no momento.")
else:
    # ==========================================================
    # CATÁLOGO DE CESTAS DINÂMICO (COM ABAS)
    # ==========================================================
    nomes_secoes = [sec["nome"] for sec in secoes]

    if len(nomes_secoes) > 1:
        abas = st.tabs(nomes_secoes)
    else:
        abas = [st.container()]

    for i, aba in enumerate(abas):
        secao_atual = nomes_secoes[i]
        
        with aba:
            st.write("") # Respiro visual
            
            # Filtra cestas desta aba específica
            cestas_da_aba = [c for c in cestas if c.get("secao_vitrine", "Cestas de Café") == secao_atual]
            
            if not cestas_da_aba:
                st.write(f"*(Nenhuma opção disponível no momento em {html.escape(str(secao_atual))})*")
                continue

            for cesta in cestas_da_aba:
                with st.container(border=True):
                    col_img, col_text = st.columns([1.2, 2], gap="large")

                    cesta_nome_seguro = html.escape(str(cesta.get("nome") or "Cesta"))

                    with col_img:
                        imagem_url = cesta.get("imagem")
                        if imagem_url and str(imagem_url).strip():
                            img_src = _url_imagem_segura(image_to_base64(imagem_url))
                            if img_src:
                                img_src_seguro = html.escape(img_src, quote=True)
                                st.markdown(
                                    f"""
                                    <div class="lightbox-wrapper">
                                        <label style="cursor: zoom-in; width: 100%; display: flex; flex-direction: column; align-items: center;">
                                            <input type="checkbox" class="lightbox-toggle">
                                            <img src="{img_src_seguro}" class="lightbox-image" alt="Foto de {cesta_nome_seguro}" title="Clique para ampliar a foto da cesta">
                                            <div class="lightbox-modal">
                                                <img src="{img_src_seguro}" alt="Foto ampliada de {cesta_nome_seguro}">
                                            </div>
                                        </label>
                                        <div class="imagem-legenda">👆 Toque na foto para ampliar</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )


                        # NOTA: 'fotos_adicionais' não existe na tabela `cestas` do schema atual
                        # (colunas: id, nome, descricao, imagem, preco, ativa, created_at, ordem,
                        # secao_vitrine). Esse bloco nunca é preenchido hoje — deixei como está
                        # (é inofensivo) mas é código morto até essa coluna existir de fato.
                        fotos_extras = cesta.get("fotos_adicionais", [])
                        if isinstance(fotos_extras, list) and len(fotos_extras) > 0:
                            st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 6px; text-transform: uppercase;'>📸 Outros ângulos:</div>", unsafe_allow_html=True)
                            cols_extras = st.columns(min(len(fotos_extras), 3))
                            for f_idx, f_url in enumerate(fotos_extras[:3]):
                                if f_url and str(f_url).strip():
                                    with cols_extras[f_idx]:
                                        st.image(str(f_url).strip(), use_container_width=True)

                    with col_text:
                        st.markdown(f'<div class="card-cesta-titulo">{cesta_nome_seguro}</div>', unsafe_allow_html=True)

                        if cesta.get("descricao") and str(cesta["descricao"]).strip():
                            descricao_txt = html.escape(str(cesta["descricao"])).replace("\n", "<br>")
                            st.markdown(f'<div class="card-cesta-desc">{descricao_txt}</div>', unsafe_allow_html=True)

                        try:
                            valor = float(cesta.get("preco", 0))
                            valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                            st.markdown(f'<div class="card-cesta-preco">{valor_fmt}</div>', unsafe_allow_html=True)
                        except:
                            st.markdown('<div class="card-cesta-preco">Preço sob consulta</div>', unsafe_allow_html=True)

                        st.write("")
                        # Botão que redireciona para o checkout com o ID salvo
                        if st.button("🛒 Quero Montar Esta Cesta", key=f"cesta_btn_{cesta['id']}", use_container_width=True):
                            st.session_state["cesta_selecionada_home"] = cesta["id"]
                            st.switch_page("pages/01_Inicio.py")

# ==========================================================
# APRESENTAÇÃO DOS ADICIONAIS (GRID PREMIUM ORIGINAL)
# ==========================================================
if produtos_adicionais:
    cards_html = ""
    for prod in produtos_adicionais:
        nome_p = str(prod.get("nome") or "")
        nome_p_seguro = html.escape(nome_p)
        preco_p = prod.get("preco")
        imagem_p = prod.get("imagem")

        if preco_p is not None and str(preco_p).strip() != "":
            try:
                val_f = float(preco_p)
                texto_preco = f'R$ {val_f:,.2f}'.replace(",", "X").replace(".", ",").replace("X",".")
                span_preco = f'<span class="adicional-preco-fixo">{texto_preco}</span>'
            except:
                span_preco = '<span class="adicional-preco-consulta">Consulta</span>'
        else:
            span_preco = '<span class="adicional-preco-consulta">Consulta</span>'

        img_src = _url_imagem_segura(image_to_base64(imagem_p)) if imagem_p and str(imagem_p).strip() else ""
        if img_src:
            img_src_seguro = html.escape(img_src, quote=True)
            img_html = f'<label style="cursor: zoom-in; display: inline-block; margin-bottom: 6px;"><input type="checkbox" class="lightbox-toggle"><img src="{img_src_seguro}" class="adicional-img-small" alt="{nome_p_seguro}" title="Clique para ampliar"><div class="lightbox-modal"><img src="{img_src_seguro}" alt="{nome_p_seguro}"></div></label>'
        else:
            icone = "📷" if "polaroid" in nome_p.lower() else "🎀"
            img_html = f'<div class="adicional-img-placeholder" style="margin-bottom: 6px;">{icone}</div>'

        cards_html += f'<div class="adicional-item-box">{img_html}<div class="adicional-nome">{nome_p_seguro}</div><div>{span_preco}</div></div>'

    st.markdown(
        f"""
        <div class="adicionais-hero-card">
            <div class="adicionais-hero-title">
                🎀 Incremente seu presente com nossos Adicionais:
                <span style="font-size: 13px; font-weight: 500; color: #888; display: block; margin-top: 6px;">
                    👉 Você poderá escolher os adicionais na próxima tela de montagem. (Toque na foto para ampliar).
                </span>
            </div>
            <div class="adicionais-grid-css">
                {cards_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# SEÇÃO DE CONTATOS E RODAPÉ
# ==========================================================
st.markdown(
    """
    <div class="footer-container">
        <div class="footer-title">Fale Conosco</div>
        <div class="footer-text">
            Ficou com alguma dúvida sobre entregas, prazos ou quer fazer uma encomenda corporativa?<br>
            Nossa equipe está pronta para te atender.
        </div>
        <div class="social-btn-box">
            <a href="https://wa.me/5561999759079?text=Olá!%20Gostaria%20de%20tirar%20dúvidas%20sobre%20as%20cestas." target="_blank" class="btn-whatsapp">
                💬 (61) 99975-9079
            </a>
            <a href="https://instagram.com/docecestabrasilia" target="_blank" class="btn-instagram">
                📸 @docecestabrasilia
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.divider()

# Link discreto para a Área Administrativa no rodapé
st.page_link(
    "pages/99_Admin.py",
    label="Acesso Restrito Administrativo",
    icon="🔒"
)
