import streamlit as st
from pathlib import Path

from services.pedido_service import salvar_pedido
from services.foto_service import salvar_fotos
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

/* Esconde menu lateral */
section[data-testid="stSidebar"]{
    display:none;
}

/* Esconde botão do menu */
[data-testid="collapsedControl"]{
    display:none;
}

/* Cabeçalho */
header{
    visibility:hidden;
}

/* Rodapé */
footer{
    visibility:hidden;
}

/* Menu Streamlit */
#MainMenu{
    visibility:hidden;
}

/* Centraliza conteúdo */
.block-container{
    max-width:850px;
    padding-top:20px;
}

/* Botões */
.stButton > button{
    background:#8B5A2B;
    color:white;
    border-radius:12px;
    height:55px;
    font-size:18px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# LOGO
# ==========================================================

logo = Path("assets/logo.webp")

if logo.exists():

    col1, col2, col3 = st.columns([2,1,2])

    with col2:

        st.image(str(logo), width=180)

st.markdown(
    "<h1 style='text-align:center;color:#8B5A2B;'>Doce Cesta Brasília</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Cestas personalizadas para momentos especiais 💝</p>",
    unsafe_allow_html=True
)

# ==========================================================
# FORMULÁRIO DE PEDIDOS
# ==========================================================

st.header("📝 Formulário de Pedido")

# ==========================================================
# DADOS DO CLIENTE
# ==========================================================

st.subheader("👤 Dados do Cliente")

nome = st.text_input(
    "Nome Completo *"
)

cpf = st.text_input(
    "CPF *",
    placeholder="000.000.000-00"
)

telefone = st.text_input(
    "Telefone *",
    placeholder="(61) 99999-9999"
)

st.divider()

# ==========================================================
# CARREGA CESTAS
# ==========================================================

try:

    cestas = listar_cestas()

except Exception as erro:

    st.error(f"Erro ao carregar as cestas: {erro}")
    st.stop
