import streamlit as st
from config.supabase import supabase

st.set_page_config(
    page_title="Histórico do Cliente",
    page_icon="👤",
    layout="wide"
)

# =====================================================
# VERIFICA SE VEIO DA TELA CLIENTES
# =====================================================

if "cliente_cpf" not in st.session_state:

    st.error("Nenhum cliente selecionado.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/03_Clientes.py")

    st.stop()

cpf = st.session_state["cliente_cpf"]

# =====================================================
# BUSCA TODOS OS PEDIDOS DO CLIENTE
# =====================================================

try:

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("cliente_cpf", cpf)
        .order("created_at", desc=True)
        .execute()
    )

    pedidos = resposta.data or []

except Exception as erro:

    st.error(f"Erro ao carregar histórico: {erro}")

    st.stop()

if not pedidos:

    st.warning("Cliente sem pedidos.")

    st.stop()

cliente = pedidos[0]

st.title("👤 Histórico do Cliente")

st.divider()
