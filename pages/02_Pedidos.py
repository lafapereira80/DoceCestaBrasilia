import streamlit as st

from services.cesta_service import listar_cestas

st.set_page_config(
    page_title="Novo Pedido",
    page_icon="🎁",
    layout="wide"
)

st.title("🎁 Novo Pedido")

st.divider()

# =====================================================
# DADOS DO CLIENTE
# =====================================================

st.subheader("👤 Dados do Cliente")

nome = st.text_input(
    "Nome"
)

cpf = st.text_input(
    "CPF"
)

telefone = st.text_input(
    "Telefone"
)

st.divider()

# =====================================================
# ESCOLHA DA CESTA
# =====================================================

st.subheader("🎁 Escolha sua Cesta")

try:

    cestas = listar_cestas()

except Exception as erro:

    st.error(
        f"Erro ao carregar as cestas: {erro}"
    )

    st.stop()

if not cestas:

    st.warning(
        "Nenhuma cesta cadastrada."
    )

    st.stop()

cesta = st.selectbox(

    "Selecione uma cesta",

    cestas,

    format_func=lambda c: c["nome"]

)
