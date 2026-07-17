import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Administrador",
    page_icon="🔒",
    layout="wide"
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------

st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.card{
    background:#ffffff;
    border-radius:12px;
    padding:20px;
    border:1px solid #e5e5e5;
    text-align:center;
    margin-bottom:15px;
}

.titulo{
    text-align:center;
    font-size:34px;
    font-weight:bold;
    color:#8B5A2B;
}

.sub{
    text-align:center;
    color:#777;
    margin-bottom:30px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOGO
# ---------------------------------------------------

logo = Path("assets/logo.webp")

col1,col2,col3 = st.columns([2,1,2])

with col2:

    if logo.exists():
        st.image(str(logo), width=140)

st.markdown(
    "<div class='titulo'>Painel Administrativo</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='sub'>Doce Cesta Brasília</div>",
    unsafe_allow_html=True
)

st.divider()

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

if not st.session_state.admin_logado:

    senha = st.text_input(
        "Senha do Administrador",
        type="password"
    )

    if st.button(
        "Entrar",
        use_container_width=True
    ):

        if senha == "admin123":

            st.session_state.admin_logado = True
            st.rerun()

        else:

            st.error("Senha incorreta.")

    st.stop()

# ---------------------------------------------------
# MENU
# ---------------------------------------------------

st.success("Administrador conectado.")

st.subheader("📂 Módulos do Sistema")

col1, col2, col3 = st.columns(3)

with col1:

    st.page_link(
        "pages/02_Pedidos.py",
        label="📋 Pedidos",
        icon="📋"
    )

with col2:

    st.page_link(
        "pages/03_Clientes.py",
        label="👥 Clientes",
        icon="👥"
    )

with col3:

    st.page_link(
        "pages/07_Dashboard.py",
        label="📊 Dashboard",
        icon="📊"
    )

col1, col2, col3 = st.columns(3)

with col1:

    st.page_link(
        "pages/04_Cestas.py",
        label="🎁 Cestas",
        icon="🎁"
    )

with col2:

    st.page_link(
        "pages/05_Produtos.py",
        label="🛒 Produtos",
        icon="🛒"
    )

with col3:

    st.page_link(
        "pages/06_Financeiro.py",
        label="💰 Financeiro",
        icon="💰"
    )

st.divider()

st.info("Selecione um módulo para começar.")
