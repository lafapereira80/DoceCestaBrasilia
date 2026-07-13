import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================
# CSS
# ==========================

st.markdown("""
<style>

/* Esconde apenas a navegação lateral */
[data-testid="stSidebarNav"]{
    display:none;
}

/* Centraliza o conteúdo */
.block-container{
    max-width:850px;
    padding-top:20px;
}

/* Esconde menu */
#MainMenu{
    visibility:hidden;
}

/* Esconde footer */
footer{
    visibility:hidden;
}

.titulo{
    text-align:center;
    color:#8B5A2B;
    font-size:42px;
    font-weight:bold;
}

.subtitulo{
    text-align:center;
    color:#666;
    font-size:18px;
    margin-bottom:30px;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# LOGO
# ==========================

logo = Path("assets/logo.webp")

if logo.exists():

    c1,c2,c3 = st.columns([1,2,1])

    with c2:

        st.image(str(logo), use_container_width=True)

st.markdown(
    "<div class='titulo'>Doce Cesta Brasília</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitulo'>Cestas personalizadas para momentos especiais 💝</div>",
    unsafe_allow_html=True
)

st.success("Sistema em desenvolvimento.")

st.write("Na próxima etapa o formulário completo será colocado nesta página.")

st.divider()

st.caption("© Doce Cesta Brasília")

st.page_link(
    "pages/99_Admin.py",
    label="🔒 Área Administrativa",
    icon="🔒"
)
