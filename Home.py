import streamlit as st
import base64
from pathlib import Path

from services.cesta_service import listar_cestas


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Doce Cesta Brasília | Vitrine de Cestas",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# CSS MODERNO E RESPONSIVO (MOBILE FIRST)
# ==========================================================

st.markdown(
"""
<style>
/* Remoção dos elementos padrão e barra lateral */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { visibility: hidden !important; height: 0px !important; }
footer { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

/* Margens gerais da página */
.block-container {
    max-width: 1100px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Banner de Cabeçalho */
.header-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin-bottom: 1rem;
    width: 100%;
}

.header-logo {
    width: 65px;
    height: auto;
    object-fit: contain;
    flex-shrink: 0;
}

.header-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: left;
}

.header-title {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #5a3b28 !important;
    margin: 0 !important;
    line-height: 1.15 !important;
}

.header-subtitle {
    font-size: 13px !important;
    color: #775a46 !important;
    margin-top: 2px !important;
    margin-bottom: 0 !important;
}

/* Estilização dos Cards do Catálogo */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 16px !important;
    padding: 14px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 3px 10px rgba(90, 59, 40, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
    box-shadow: 0 6px 16px rgba(90, 59, 40, 0.08);
}

.card-cesta-titulo {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-top: 6px !important;
    margin-bottom: 4px !important;
}

.card-cesta-desc {
    font-size: 13px !important;
    color: #666 !important;
    line-height: 1.4 !important;
    margin-bottom: 8px !important;
}

.card-cesta-preco {
    font-size: 18px !important;
    font-weight: 800 !important;
    color: #2e7d32 !important;
    margin-bottom: 10px !important;
}

/* Botão Personalizar Cesta */
div[data-testid="stButton"] button {
    background: #5a3b28 !important;
    color: white !important;
    border-radius: 10px !important;
    height: 44px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 3px 8px rgba(90, 59, 40, 0.12) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] button:hover {
    background: #42291d !important;
    color: white !important;
}

/* Ajustes Exclusivos para Celulares */
@media (max-width: 640px) {
    .block-container {
        padding-top: 0.5rem !important;
    }
    .header-logo {
        width: 80px !important;
    }
    .header-title {
        font-size: 18px !important;
    }
    .header-subtitle {
        font-size: 11px !important;
    }
    .card-cesta-titulo {
        font-size: 16px !important;
    }
    .card-cesta-preco {
        font-size: 16px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)


# ==========================================================
# CABEÇALHO DA MARCA
# ==========================================================

logo_path = Path("assets/logo.webp")
logo_html = ""

if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    logo_html = f'<img src="data:image/webp;base64,{encoded_logo}" class="header-logo" alt="Logo">'

st.markdown(
    f"""
    <div class="header-banner">
        {logo_html}
        <div class="header-text">
            <h1 class="header-title">Doce Cesta Brasília</h1>
            <p class="header-subtitle">Cestas personalizadas para momentos especiais 💝</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")


# ==========================================================
# CATÁLOGO DE CESTAS DINÂMICO
# ==========================================================

st.markdown("### 🎁 Nossos Modelos de Cestas")
st.caption("Escolha a cesta perfeita abaixo para personalizar os itens e fazer seu pedido.")

try:
    cestas = listar_cestas()
    cestas = [c for c in cestas if c.get("ativa", True)]
except Exception as erro:
    st.error(f"Erro ao carregar cestas: {erro}")
    cestas = []

if not cestas:
    st.info("Nenhuma cesta cadastrada no momento.")
else:
    colunas = st.columns(2)

    for idx, cesta in enumerate(cestas):
        coluna = colunas[idx % 2]

        with coluna:
            with st.container(border=True):
                # Imagem da Cesta
                if cesta.get("imagem"):
                    st.image(cesta["imagem"], use_container_width=True)

                # Detalhes
                st.markdown(f'<div class="card-cesta-titulo">{cesta["nome"]}</div>', unsafe_allow_html=True)

                if cesta.get("descricao"):
                    desc = cesta["descricao"]
                    if len(desc) > 110:
                        desc = desc[:110] + "..."
                    st.markdown(f'<div class="card-cesta-desc">{desc}</div>', unsafe_allow_html=True)

                # Preço
                try:
                    valor = float(cesta.get("preco", 0))
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f'<div class="card-cesta-preco">{valor_fmt}</div>', unsafe_allow_html=True)
                except:
                    st.markdown('<div class="card-cesta-preco">Preço sob consulta</div>', unsafe_allow_html=True)

                # Ação de Seleção -> Redireciona para o formulário no app.py
                if st.button("✨ Monte sua Cesta", key=f"cesta_btn_{cesta['id']}", use_container_width=True):
                    st.session_state["cesta_selecionada_home"] = cesta["id"]
                    st.switch_page("app.py")


# ==========================================================
# RODAPÉ E LINK ADMIN
# ==========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; font-size:12px; color:#888; padding:10px;">
    Doce Cesta Brasília © 2026
    </div>
    """,
    unsafe_allow_html=True
)

st.page_link(
    "pages/99_Admin.py",
    label="Área Administrativa",
    icon="🔒"
)
