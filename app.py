import streamlit as st
import base64
from pathlib import Path

from services.cesta_service import listar_cestas
from services.categoria_service import listar_categorias_pedido
from services.produto_service import listar_produtos_por_categoria_id


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
# CSS MODERNO, HARMONIOSO E RESPONSIVO (MOBILE FIRST)
# ==========================================================

st.markdown(
"""
<style>
/* Remoção de elementos padrão do Streamlit */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { visibility: hidden !important; height: 0px !important; }
footer { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

/* Container Principal */
.block-container {
    max-width: 1080px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Banner / Cabeçalho Principal */
.header-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-bottom: 1.2rem;
    width: 100%;
    background: #ffffff;
    padding: 16px 20px;
    border-radius: 18px;
    border: 1px solid #e8ddd3;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.04);
}

.header-logo {
    width: 75px;
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
    font-size: 13.5px !important;
    color: #775a46 !important;
    margin-top: 3px !important;
    margin-bottom: 0 !important;
}

/* Section Destaque dos Adicionais */
.adicionais-hero-card {
    background: linear-gradient(135deg, #ffffff 0%, #faf5f0 100%);
    border: 1px solid #e2d2c3;
    border-radius: 16px;
    padding: 16px 20px;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 3px 10px rgba(90, 59, 40, 0.03);
}

.adicionais-hero-title {
    font-size: 15px;
    font-weight: 700;
    color: #5a3b28;
    margin-bottom: 10px;
}

.adicional-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #ffffff;
    border: 1px solid #dfcdbb;
    border-radius: 20px;
    padding: 6px 12px;
    margin-right: 6px;
    margin-bottom: 8px;
    font-size: 12.5px;
    color: #4a3222;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.adicional-preco-fixo {
    color: #2e7d32;
    font-weight: 700;
}

.adicional-preco-consulta {
    color: #c5721f;
    font-weight: 700;
    background: #fff8ef;
    padding: 1px 6px;
    border-radius: 10px;
    font-size: 11px;
}

/* Cards das Cestas */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 18px !important;
    padding: 16px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.04);
    transition: all 0.25s ease !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #cbab92 !important;
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08);
}

.card-cesta-titulo {
    font-size: 19px !important;
    font-weight: 800 !important;
    color: #5a3b28 !important;
    margin-top: 4px !important;
    margin-bottom: 6px !important;
}

/* Texto de Descrição Justificado */
.card-cesta-desc {
    font-size: 13px !important;
    color: #4d3e35 !important;
    line-height: 1.55 !important;
    text-align: justify !important;
    margin-bottom: 12px !important;
    background: #fcf9f5;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid #f0e6dc;
}

.card-cesta-preco {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #2e7d32 !important;
    margin-bottom: 12px !important;
}

/* Botão Personalizar Cesta / CTA */
div[data-testid="stButton"] button {
    background: #5a3b28 !important;
    color: white !important;
    border-radius: 12px !important;
    height: 46px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(90, 59, 40, 0.15) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] button:hover {
    background: #42291d !important;
    color: white !important;
}

/* Seção de Contatos e Rodapé */
.footer-container {
    background: #ffffff;
    border: 1px solid #e8ddd3;
    border-radius: 18px;
    padding: 22px;
    text-align: center;
    margin-top: 1.5rem;
    box-shadow: 0 2px 8px rgba(90, 59, 40, 0.03);
}

.footer-title {
    font-size: 16px;
    font-weight: 700;
    color: #5a3b28;
    margin-bottom: 8px;
}

.footer-text {
    font-size: 13px;
    color: #666;
    margin-bottom: 14px;
}

.whatsapp-btn-box a {
    display: inline-block;
    background: #25d366 !important;
    color: white !important;
    padding: 11px 22px;
    border-radius: 12px;
    font-weight: 700;
    text-decoration: none;
    font-size: 14px;
    box-shadow: 0 3px 8px rgba(37, 211, 102, 0.22);
    transition: all 0.2s ease;
}

/* Ajustes Responsivos Exclusivos para Celulares */
@media (max-width: 640px) {
    .block-container {
        padding-top: 0.5rem !important;
    }
    .header-banner {
        padding: 12px;
        gap: 10px;
    }
    .header-logo {
        width: 60px !important;
    }
    .header-title {
        font-size: 20px !important;
    }
    .header-subtitle {
        font-size: 11px !important;
    }
    .card-cesta-titulo {
        font-size: 17px !important;
    }
    .card-cesta-preco {
        font-size: 18px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)


# ==========================================================
# CABEÇALHO / LOGO DA MARCA
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
            <p class="header-subtitle">Cestas personalizadas para momentos inesquecíveis 💝</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# TÍTULO PRINCIPAL DO CATÁLOGO
# ==========================================================

st.markdown("<h3 style='color:#5a3b28; margin-top:0; margin-bottom:4px;'>🎁 Nossos Modelos de Cestas</h3>", unsafe_allow_html=True)
st.caption("Escolha a cesta perfeita, confira os itens detalhados e personalize do seu jeito.")


# ==========================================================
# CATÁLOGO DE CESTAS DINÂMICO
# ==========================================================

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

                # 1. TRATAMENTO DE FOTO PRINCIPAL
                imagem_url = cesta.get("imagem")
                if imagem_url and str(imagem_url).strip():
                    st.image(str(imagem_url).strip(), use_container_width=True)

                # 2. TRATAMENTO DE FOTOS EXTRAS
                fotos_extras = cesta.get("fotos_adicionais", [])
                if isinstance(fotos_extras, list) and len(fotos_extras) > 0:
                    st.caption("📸 Outros ângulos desta cesta:")
                    cols_extras = st.columns(min(len(fotos_extras), 4))
                    for f_idx, f_url in enumerate(fotos_extras):
                        if f_url and str(f_url).strip():
                            with cols_extras[f_idx % 4]:
                                st.image(str(f_url).strip(), use_container_width=True)

                # 3. TÍTULO DA CESTA
                st.markdown(f'<div class="card-cesta-titulo">{cesta["nome"]}</div>', unsafe_allow_html=True)

                # 4. DESCRIÇÃO COMPLETA E JUSTIFICADA
                if cesta.get("descricao") and str(cesta["descricao"]).strip():
                    st.markdown(f'<div class="card-cesta-desc">{cesta["descricao"]}</div>', unsafe_allow_html=True)

                # 5. PREÇO FORMATADO
                try:
                    valor = float(cesta.get("preco", 0))
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f'<div class="card-cesta-preco">{valor_fmt}</div>', unsafe_allow_html=True)
                except:
                    st.markdown('<div class="card-cesta-preco">Preço sob consulta</div>', unsafe_allow_html=True)

                # 6. BOTÃO DE AÇÃO -> Direciona para o formcompra.py em pages/
                if st.button("✨ Monte sua Cesta", key=f"cesta_btn_{cesta['id']}", use_container_width=True):
                    st.session_state["cesta_selecionada_home"] = cesta["id"]
                    st.switch_page("pages/formcompra.py")


# ==========================================================
# APRESENTAÇÃO DOS ADICIONAIS (APÓS AS CESTAS CADASTRADAS)
# ==========================================================

produtos_adicionais = []
try:
    categorias = listar_categorias_pedido()
    cat_adicionais = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)
    if cat_adicionais:
        produtos_adicionais = listar_produtos_por_categoria_id(cat_adicionais["id"])
except:
    produtos_adicionais = []

if produtos_adicionais:
    pills_html = ""
    for prod in produtos_adicionais:
        nome_p = prod.get("nome", "")
        preco_p = prod.get("preco")

        if preco_p is not None and str(preco_p).strip() != "":
            try:
                val_f = float(preco_p)
                texto_preco = f'<span class="adicional-preco-fixo">R$ {val_f:,.2f}</span>'.replace(",", "X").replace(".", ",").replace("X",".")
            except:
                texto_preco = '<span class="adicional-preco-consulta">Sob Consulta</span>'
        else:
            texto_preco = '<span class="adicional-preco-consulta">Sob Consulta</span>'

        pills_html += f"""<div class="adicional-pill"><span>✨ {nome_p}</span>{texto_preco}</div>"""

    st.markdown(
        f"""
        <div class="adicionais-hero-card">
            <div class="adicionais-hero-title">
                🎀 Personalize qualquer cesta com nossos Adicionais Especialmente Escolhidos:
            </div>
            <div style="display: flex; flex-wrap: wrap; align-items: center;">
                {pills_html}
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
        <div class="footer-title">📞 Fale Conosco & Atendimento</div>
        <div class="footer-text">
            Dúvidas sobre entregas, prazos ou encomendas corporativas? Fale diretamente com nossa equipe!<br>
            📍 <b>Brasília - DF</b> | 🕒 Atendimento de Segunda a Sábado
        </div>
        <div class="whatsapp-btn-box">
            <a href="https://wa.me/5561999759079?text=Olá!%20Gostaria%20de%20tirar%20dúvidas%20sobre%20as%20cestas." target="_blank">
                💬 Chamar no WhatsApp (61) 99975-9079
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# Link discreto para a Área Administrativa
st.page_link(
    "pages/99_Admin.py",
    label="Área Administrativa",
    icon="🔒"
)
