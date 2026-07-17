import streamlit as st

from services.pedido_service import buscar_pedido

st.set_page_config(
    page_title="Pedido",
    page_icon="📋",
    layout="wide"
)

# =====================================================
# VERIFICA SE VEIO DA LISTA DE PEDIDOS
# =====================================================

if "pedido_aberto" not in st.session_state:

    st.error("Nenhum pedido foi selecionado.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/02_Pedidos.py")

    st.stop()

pedido_id = st.session_state["pedido_aberto"]

# =====================================================
# BUSCA O PEDIDO
# =====================================================

try:

    pedido = buscar_pedido(pedido_id)

except Exception as erro:

    st.error(erro)

    st.stop()

# =====================================================
# CABEÇALHO
# =====================================================

st.title(f"📋 Pedido #{pedido['id']}")

st.caption(f"Status atual: {pedido['status']}")

st.divider()

# =====================================================
# DADOS DO CLIENTE
# =====================================================

st.subheader("👤 Cliente")

col1, col2 = st.columns(2)

with col1:

    st.write("**Nome**")

    st.write(pedido["cliente_nome"])

    st.write("**CPF**")

    st.write(pedido["cliente_cpf"])

with col2:

    st.write("**Telefone**")

    st.write(pedido["cliente_telefone"])

st.divider()

# =====================================================
# BOTÃO VOLTAR
# =====================================================

if st.button("⬅ Voltar para Pedidos"):

    st.switch_page("pages/02_Pedidos.py")
