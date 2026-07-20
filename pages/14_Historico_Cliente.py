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

# =====================================================
# RESUMO DO CLIENTE
# =====================================================

total_pedidos = len(pedidos)

valor_total = sum(
    float(p.get("valor_total") or 0)
    for p in pedidos
)

ticket_medio = (
    valor_total / total_pedidos
    if total_pedidos > 0
    else 0
)

ultima_compra = pedidos[0].get("data_entrega", "-")

st.subheader("👤 Dados do Cliente")

col1, col2 = st.columns(2)

with col1:

    st.write("**Nome**")
    st.write(cliente["cliente_nome"])

    st.write("**CPF**")
    st.write(cliente["cliente_cpf"])

with col2:

    st.write("**Telefone**")
    st.write(cliente["cliente_telefone"])

st.divider()

st.subheader("📊 Resumo")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Pedidos",
        total_pedidos
    )

with c2:

    st.metric(
        "Valor Gasto",
        f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with c3:

    st.metric(
        "Ticket Médio",
        f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with c4:

    st.metric(
        "Última Compra",
        str(ultima_compra)
    )

st.divider()
