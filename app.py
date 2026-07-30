import streamlit as st
import base64
from pathlib import Path
from config.supabase import supabase

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA (VITRINE)
# ==========================================================
st.set_page_config(
    page_title="Doce Cesta Brasília | Presentes Inesquecíveis",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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

@st.cache_data(show_spinner=False)
def carregar_logo_base64():
    logo_path = Path("assets/logo.webp")
    if logo_path.exists():
        with open(logo_path, "rb") as img_file:
            encoded_logo = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/webp;base64,{encoded_logo}" class="header-logo" alt="Logo">'
    return "🎁"

# ==========================================================
# CSS PREMIUM ULTRA MODERNO (DESIGN E-COMMERCE)
# ==========================================================
st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

/* Ocultar elementos padrão do Streamlit */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { visibility: hidden !important; height: 0px !important; }
footer { visibility: hidden !important; }
.stAppDeployMenu { display: none !important; }

/* Corpo e Container Principal */
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { max-width: 900px !important; padding-top: 1.5rem !important; padding-bottom: 4rem !important; }

/* Banner da Loja */
.header-banner {
    display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 30px 20px;
    border-radius: 24px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
    margin-bottom: 2rem;
}
.header-logo { width: 110px; height: auto; object-fit: contain; margin-bottom: 12px; filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.06)); }
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 46px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; }
.header-subtitle { font-size: 15px !important; color: #775a46 !important; font-weight: 500 !important; margin-top: 8px !important; }

/* Estilização das Abas (Tabs) */
div[data-testid="stTabs"] button {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important; font-size: 16px !important; color: #8c7362 !important; padding-bottom: 10px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] { color: #c5721f !important; border-bottom-color: #c5721f !important; }

/* =========================================
   CARDS DE PRODUTOS (CESTAS) NATIVOS E BLINDADOS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important; border: 1px solid #e8ddd3 !important; border-radius: 20px !important;
    padding: 16px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; height: 100%;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #d2bfae !important; box-shadow: 0 10px 25px rgba(90, 59, 40, 0.08) !important; transform: translateY(-4px);
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    height: 100%; display: flex; flex-direction: column; justify-content: space-between;
}

.card-content { display: flex; flex-direction: column; flex-grow: 1; }
.produto-img-container { width: 100%; border-radius: 14px; overflow: hidden; margin-bottom: 14px; background: #faf7f3; display: flex; align-items: center; justify-content: center; aspect-ratio: 1 / 1; }
.produto-img-container img { width: 100%; height: 100%; object-fit: cover; }
.produto-titulo { font-family: 'Dancing Script', cursive !important; font-size: 28px !important; font-weight: 700; color: #c5721f; margin-bottom: 8px; line-height: 1.1; }
.produto-desc { font-size: 13.5px; color: #775a46; line-height: 1.5; margin-bottom: 15px; text-align: justify; flex-grow: 1; }
.produto-preco { font-size: 20px; font-weight: 800; color: #137333; margin-bottom: 8px; }

/* Botões Nativos Streamlit dentro do Card Principal */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #137333 0%, #0d4e22 100%) !important; color: white !important;
    border-radius: 12px !important; height: 46px !important; font-size: 14px !important;
    font-weight: 800 !important; border: none !important; width: 100% !important;
    box-shadow: 0 4px 12px rgba(19, 115, 51, 0.2) !important; transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important; box-shadow: 0 6px 16px rgba(19, 115, 51, 0.35) !important;
}

/* =========================================
   CARDS DE ADICIONAIS (MIMOS EXTRAS COM FOTOS)
========================================== */
.addon-section-title {
    font-family: 'Dancing Script', cursive !important; font-size: 38px !important; 
    font-weight: 700 !important; color: #c5721f !important; text-align: center; margin-top: 40px; margin-bottom: 5px;
}
.addon-section-subtitle { text-align: center; color: #775a46; font-size: 14px; font-weight: 500; margin-bottom: 25px; }

.addon-card {
    background: #ffffff; border: 1px solid #dfcdbb; border-radius: 16px; padding: 12px;
    display: flex; flex-direction: column; align-items: center; justify-content: flex-start; text-align: center;
    height: 100%; box-shadow: 0 4px 10px rgba(90, 59, 40, 0.03); transition: all 0.2s ease;
}
.addon-card:hover { border-color: #c5721f; transform: translateY(-3px); box-shadow: 0 8px 20px rgba(90, 59, 40, 0.06); }
.addon-img-container {
    width: 100%; aspect-ratio: 1 / 1; border-radius: 12px; overflow: hidden; margin-bottom: 12px;
    background: #faf7f3; display: flex; align-items: center; justify-content: center;
}
.addon-img-container img { width: 100%; height: 100%; object-fit: cover; }
.addon-icone { font-size: 38px; opacity: 0.6; }
.addon-nome { font-size: 14.5px; font-weight: 800; color: #4a2e1b; line-height: 1.2; margin-bottom: 6px; }
.addon-preco { font-size: 15px; font-weight: 800; color: #137333; margin-top: auto; }

/* Responsividade Mobile */
@media (max-width: 640px) {
    .header-title { font-size: 38px !important; }
    .produto-titulo { font-size: 26px !important; }
    .addon-section-title { font-size: 32px !important; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# INICIALIZAÇÃO DA SESSÃO
# ==========================================================
if "cesta_selecionada_home" not in st.session_state:
    st.session_state["cesta_selecionada_home"] = None

# ==========================================================
# CABEÇALHO DA LOJA
# ==========================================================
st.markdown(f"""
<div class="header-banner">
    {carregar_logo_base64()}
    <h1 class="header-title">Doce Cesta Brasília</h1>
    <p class="header-subtitle">Monte e personalize o presente perfeito 💝</p>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# CARREGAMENTO DOS DADOS (SEÇÕES, CESTAS E ADICIONAIS)
# ==========================================================
with st.spinner("Preparando a vitrine..."):
    secoes, cestas = obter_vitrine_oficial()
    adicionais = obter_adicionais_vitrine()

if not cestas:
    st.info("Nossos presentes estão sendo preparados e o catálogo será atualizado em breve. Volte mais tarde! 🎀")
    st.stop()

# ==========================================================
# 1. VITRINE DE CESTAS (COM DESCRIÇÃO COMPLETA E BOTÃO NATIVO)
# ==========================================================
nomes_secoes = [sec["nome"] for sec in secoes]

if len(nomes_secoes) > 1:
    abas = st.tabs(nomes_secoes)
else:
    abas = [st.container()]

for i, aba in enumerate(abas):
    secao_atual = nomes_secoes[i]
    
    with aba:
        st.write("") # Respiro
        
        cestas_da_aba = [c for c in cestas if c.get("secao_vitrine", "Cestas de Café") == secao_atual]
        
        if not cestas_da_aba:
            st.write(f"*(Nenhuma opção disponível no momento em {secao_atual})*")
            continue

        # Renderiza os cards em 2 colunas
        colunas = st.columns(2)
        
        for idx, cesta in enumerate(cestas_da_aba):
            with colunas[idx % 2]:
                with st.container(border=True): # Card delimitador oficial do Streamlit
                    
                    imagem_html = f'<img src="{cesta["imagem"]}" alt="{cesta["nome"]}">' if cesta.get("imagem") else '<div style="height:100%; width:100%; display:flex; align-items:center; justify-content:center; color:#ccc; background:#f5eee6;">Sem Imagem</div>'
                    
                    # Exibe a DESCRIÇÃO COMPLETA, formatando quebras de linha para HTML
                    descricao_txt = str(cesta.get("descricao", "")).replace("\n", "<br>")
                        
                    valor = float(cesta.get("preco", 0))
                    preco_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    
                    # Informações do produto injetadas diretamente na caixa
                    st.markdown(f"""
                    <div class="card-content">
                        <div class="produto-img-container">
                            {imagem_html}
                        </div>
                        <div class="produto-titulo">{cesta['nome']}</div>
                        <div class="produto-desc">{descricao_txt}</div>
                        <div class="produto-preco">{preco_fmt}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # O botão "Monte sua cesta" renderizado logo abaixo do conteúdo, ancorado perfeitamente na caixa
                    if st.button("🎁 Monte sua cesta", key=f"comprar_{cesta['id']}", use_container_width=True):
                        st.session_state["cesta_selecionada_home"] = cesta["id"]
                        st.switch_page("pages/01_Inicio.py")

# ==========================================================
# 2. SEÇÃO DE MIMOS EXTRAS E ADICIONAIS (AGORA COM FOTOS)
# ==========================================================
if adicionais:
    st.markdown("<hr style='border: none; border-top: 2px dashed #e8ddd3; margin-top: 40px;'>", unsafe_allow_html=True)
    st.markdown('<div class="addon-section-title">🎀 Mimos Extras & Adicionais</div>', unsafe_allow_html=True)
    st.markdown('<div class="addon-section-subtitle">Surpreenda ainda mais adicionando estes itens na próxima etapa!</div>', unsafe_allow_html=True)
    
    # Exibe adicionais em grid responsivo (3 colunas)
    cols_add = st.columns(3)
    for i, add in enumerate(adicionais):
        with cols_add[i % 3]:
            # Lógica de Imagem: Puxa a foto do banco, se não existir coloca o Ícone
            imagem_add = add.get("imagem")
            if imagem_add:
                midia_html = f'<img src="{imagem_add}" alt="{add["nome"]}">'
            else:
                icone = "📷" if "polaroid" in str(add.get("nome", "")).lower() else "✨"
                midia_html = f'<div class="addon-icone">{icone}</div>'
                
            preco_add = add.get("preco")
            txt_preco = f"R$ {float(preco_add):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if preco_add else "Sob Consulta"
            
            st.markdown(f"""
            <div class="addon-card">
                <div class="addon-img-container">
                    {midia_html}
                </div>
                <div class="addon-nome">{add['nome']}</div>
                <div class="addon-preco">{txt_preco}</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("") # Respiro entre as linhas

# ==========================================================
# RODAPÉ E ACESSO RESTRITO
# ==========================================================
st.write("")
st.divider()
st.markdown('<div style="text-align:center; font-size:13px; color:#888; font-weight: 500;">Doce Cesta Brasília © 2026<br>Feito com amor e carinho 💖</div>', unsafe_allow_html=True)

# Botão discreto para painel admin no rodapé
col_esp1, col_btn, col_esp2 = st.columns([4, 1, 4])
with col_btn:
    st.page_link("pages/99_Admin.py", label="🔒 Painel", icon="🔑")
