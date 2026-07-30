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
        # Busca seções ativas e ordenadas
        res_secoes = supabase.table("vitrine_secoes").select("*").eq("ativa", True).order("ordem").execute()
        secoes = res_secoes.data or []
        
        # Busca cestas ativas e ordenadas
        res_cestas = supabase.table("cestas").select("*").eq("ativa", True).order("ordem").execute()
        cestas = res_cestas.data or []
        
        # Se não houver seção cadastrada, cria uma virtual para não quebrar a loja
        if not secoes:
            secoes = [{"nome": "Cestas de Café", "ordem": 1}]
            
        return secoes, cestas
    except Exception as e:
        print(f"Erro ao carregar vitrine: {e}")
        return [{"nome": "Catálogo", "ordem": 1}], []

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

/* Estilização das Abas (Tabs) do Streamlit */
div[data-testid="stTabs"] button {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    color: #8c7362 !important;
    padding-bottom: 10px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #c5721f !important;
    border-bottom-color: #c5721f !important;
}

/* Cards de Produtos */
.produto-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 20px; padding: 16px;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    height: 100%; display: flex; flex-direction: column; justify-content: space-between;
}
.produto-card:hover {
    border-color: #d2bfae; box-shadow: 0 10px 25px rgba(90, 59, 40, 0.08); transform: translateY(-4px);
}
.produto-img-container { width: 100%; border-radius: 14px; overflow: hidden; margin-bottom: 14px; aspect-ratio: 1 / 1; background: #faf7f3; display: flex; align-items: center; justify-content: center; }
.produto-img-container img { width: 100%; height: 100%; object-fit: cover; }
.produto-titulo { font-family: 'Dancing Script', cursive !important; font-size: 28px !important; font-weight: 700; color: #c5721f; margin-bottom: 4px; line-height: 1.1; }
.produto-desc { font-size: 12.5px; color: #775a46; line-height: 1.4; flex-grow: 1; margin-bottom: 12px; }
.produto-preco { font-size: 20px; font-weight: 800; color: #137333; margin-bottom: 14px; }

/* Botões Nativos Streamlit dentro do Card */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #137333 0%, #0d4e22 100%) !important; color: white !important;
    border-radius: 12px !important; height: 46px !important; font-size: 14px !important;
    font-weight: 800 !important; border: none !important; width: 100% !important;
    box-shadow: 0 4px 12px rgba(19, 115, 51, 0.2) !important; transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important; box-shadow: 0 6px 16px rgba(19, 115, 51, 0.35) !important;
}

/* Modal / Botões Flutuantes (Admin) */
.admin-btn { position: fixed; bottom: 20px; right: 20px; background: rgba(255,255,255,0.9); backdrop-filter: blur(5px); border: 1px solid #dfcdbb; padding: 10px 15px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); z-index: 9999; font-size: 12px; font-weight: 700; color: #5a3b28; text-decoration: none; display: flex; align-items: center; gap: 6px; }

@media (max-width: 640px) {
    .header-title { font-size: 38px !important; }
    .produto-titulo { font-size: 24px !important; }
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
# CARREGAMENTO DOS DADOS (SEÇÕES E CESTAS)
# ==========================================================
with st.spinner("Preparando a vitrine..."):
    secoes, cestas = obter_vitrine_oficial()

if not cestas:
    st.info("Nossos presentes estão sendo preparados e o catálogo será atualizado em breve. Volte mais tarde! 🎀")
    st.stop()

# ==========================================================
# CRIAÇÃO DAS ABAS (TABS) DINÂMICAS
# ==========================================================
nomes_secoes = [sec["nome"] for sec in secoes]

# Se houver apenas 1 seção, não precisa criar abas. Caso contrário, cria abas.
if len(nomes_secoes) > 1:
    abas = st.tabs(nomes_secoes)
else:
    abas = [st.container()] # Container simples se for só 1

# ==========================================================
# RENDERIZAÇÃO DOS PRODUTOS
# ==========================================================
for i, aba in enumerate(abas):
    secao_atual = nomes_secoes[i]
    
    with aba:
        st.write("") # Respiro
        
        # Filtra cestas desta aba específica
        cestas_da_aba = [c for c in cestas if c.get("secao_vitrine", "Cestas de Café") == secao_atual]
        
        if not cestas_da_aba:
            st.write(f"*(Nenhuma opção disponível no momento em {secao_atual})*")
            continue

        # Renderiza os cards em 2 colunas (responsivo)
        colunas = st.columns(2)
        
        for idx, cesta in enumerate(cestas_da_aba):
            with colunas[idx % 2]:
                imagem_html = f'<img src="{cesta["imagem"]}" alt="{cesta["nome"]}">' if cesta.get("imagem") else '<div style="height:100%; display:flex; align-items:center; justify-content:center; color:#ccc;">Sem Imagem</div>'
                descricao_txt = cesta.get("descricao", "")
                if len(descricao_txt) > 85:
                    descricao_txt = descricao_txt[:85] + "..."
                    
                valor = float(cesta.get("preco", 0))
                preco_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                # Desenha o visual do Card
                st.markdown(f"""
                <div class="produto-card">
                    <div class="produto-img-container">
                        {imagem_html}
                    </div>
                    <div class="produto-titulo">{cesta['nome']}</div>
                    <div class="produto-desc">{descricao_txt}</div>
                    <div class="produto-preco">{preco_fmt}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # O botão nativo fica por cima para capturar o clique (hack de UI do Streamlit)
                # Aplicamos um margem negativa visual via container para ele encaixar dentro do card
                st.markdown("<div style='margin-top: -55px; position: relative; z-index: 10; padding: 0 16px 16px 16px;'>", unsafe_allow_html=True)
                if st.button("🎁 Montar e Comprar", key=f"comprar_{cesta['id']}", use_container_width=True):
                    st.session_state["cesta_selecionada_home"] = cesta["id"]
                    st.switch_page("pages/01_Inicio.py")
                st.markdown("</div>", unsafe_allow_html=True)

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
