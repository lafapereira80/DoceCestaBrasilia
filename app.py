import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="wide"
)

# Carrega o CSS
css_path = Path("assets/style.css")
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Logo
logo = Path("assets/logo.webp")
if logo.exists():
    st.image(str(logo), width=250)

# Título
st.markdown("<div class='main-title'>Doce Cesta Brasília</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Cestas personalizadas para momentos especiais 💝</div>", unsafe_allow_html=True)

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='card'>
        <h3>🎁</h3>
        <b>Escolha sua cesta</b>
        <p>Diversas opções para cada ocasião.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='card'>
        <h3>🍞</h3>
        <b>Personalize</b>
        <p>Escolha pão, bebida e espalháveis.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='card'>
        <h3>📷</h3>
        <b>Polaroid</b>
        <p>Envie várias fotos para impressão.</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='card'>
        <h3>🚚</h3>
        <b>Entrega</b>
        <p>Receba no endereço escolhido.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

col_esq, col_centro, col_dir = st.columns([1,2,1])

with col_centro:
    if st.button("🛒 FAZER PEDIDO", use_container_width=True):
        st.switch_page("pages/02_Pedidos.py")

st.markdown(
    "<div class='footer'>© Doce Cesta Brasília - Todos os direitos reservados.</div>",
    unsafe_allow_html=True
)