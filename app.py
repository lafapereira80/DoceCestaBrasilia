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
# CSS MODERNO, RESPONSIVO E ELEGANTE (MOBILE FIRST)
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
    max-width: 1050px !important;
    padding-top: 1.2rem !important;
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
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #e8ddd3;
    box-shadow: 0 2px 8px rgba(90, 59, 40, 0.03);
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
    font-size: 13px !important;
    color: #775a46 !important;
    margin-top: 3px !important;
    margin-bottom: 0 !important;
}

/* Cards das Cestas no Catálogo */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
    box-shadow: 0 6px 18px rgba(90, 59, 40, 0.1);
}

.card-cesta-titulo {
    font-size: 19px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-top: 8px !important;
    margin-bottom: 6px !important;
}

.card-cesta-desc {
    font-size: 13px !important;
    color: #555 !important;
    line-height: 1.5 !important;
    margin-bottom: 12px !important;
    background: #faf7f3;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #f2eae1;
}

.card-cesta-preco {
    font-size: 19px !important;
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
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-top: 2rem;
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
    margin-bottom: 12px;
}

/* Estilização para Links de Contato */
.whatsapp-btn-box a {
    display: inline-block;
    background: #25d366 !important;
    color: white !important;
    padding: 10px 20px;
    border-radius: 10px;
    font-weight: 700;
    text-decoration: none;
    font-size: 14px;
    box-shadow: 0 3px 8px rgba(37, 211, 102, 0.2);
    margin-top: 6px;
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
        font-size: 17px !important;
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
st.caption("Explore nossos modelos exclusivos, confira todos os itens detalhados e monte sua cesta.")

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
                # Foto Principal da Cesta
                if cesta.get("imagem"):
                    st.image(cesta["imagem"], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=Doce+Cesta+Brasília", use_container_width=True)

                # Se houver fotos adicionais salvas na cesta (ex: lista de fotos extras)
                fotos_extras = cesta.get("fotos_adicionais", [])
                if fotos_extras and isinstance(fotos_extras, list):
                    st.caption("📸 Outros ângulos da cesta:")
                    cols_extras = st.columns(len(fotos_extras))
                    for f_idx, f_url in enumerate(fotos_extras):
                        with cols_extras[f_idx]:
                            st.image(f_url, use_container_width=True)

                # Título da Cesta
                st.markdown(f'<div class="card-cesta-titulo">{cesta["nome"]}</div>', unsafe_allow_html=True)

                # Descrição COMPLETA (Sem cortes)
                if cesta.get("descricao"):
                    st.markdown(f'<div class="card-cesta-desc">{cesta["descricao"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="card-cesta-desc">Cesta completa montada com carinho e produtos selecionados.</div>', unsafe_allow_html=True)

                # Preço Formatado
                try:
                    valor = float(cesta.get("preco", 0))
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f'<div class="card-cesta-preco">{valor_fmt}</div>', unsafe_allow_html=True)
                except:
                    st.markdown('<div class="card-cesta-preco">Preço sob consulta</div>', unsafe_allow_html=True)

                # Botão de Ação -> Direciona para o formcompra.py
                if st.button("✨ Monte sua Cesta", key=f"cesta_btn_{cesta['id']}", use_container_width=True):
                    st.session_state["cesta_selecionada_home"] = cesta["id"]
                    st.switch_page("pages/formcompra.py")


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
            <a href="https://wa.me/5561999999999?text=Olá!%20Gostaria%20de%20tirar%20dúvidas%20sobre%20as%20cestas." target="_blank">
                💬 Chamar no WhatsApp (61) 99999-9999
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
