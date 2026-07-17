import streamlit as st
import pandas as pd

from services.pedido_service import listar_pedidos

st.set_page_config(
    page_title="Pedidos",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Pedidos")

st.write("Todos os pedidos recebidos pelo sistema.")

st.divider()

# ==========================================================
# CARREGA PEDIDOS
# ==========================================================

try:

    pedidos = listar_pedidos()

except Exception as erro:

    st.error(f"Erro ao carregar pedidos: {erro}")
    st.stop()

# ==========================================================
# SEM PEDIDOS
# ==========================================================

if not pedidos:

    st.info("Nenhum pedido foi encontrado.")
    st.stop()

# ==========================================================
# TABELA
# ==========================================================

df = pd.DataFrame(pedidos)

# ==========================================================
# FILTROS
# ==========================================================

st.subheader("🔍 Pesquisar Pedidos")

col1, col2 = st.columns([3, 1])

with col1:

    pesquisa = st.text_input(
        "Nome do cliente",
        placeholder="Digite o nome..."
    )

with col2:

    status_lista = ["Todos"]

    if "status" in df.columns:
        status_lista.extend(
            sorted(df["status"].dropna().unique().tolist())
        )

    status = st.selectbox(
        "Status",
        status_lista
    )

# ==========================================================
# FILTRO NOME
# ==========================================================

if pesquisa.strip():

    df = df[
        df["cliente_nome"]
        .fillna("")
        .str.contains(
            pesquisa,
            case=False
        )
    ]

# ==========================================================
# FILTRO STATUS
# ==========================================================

if status != "Todos":

    df = df[
        df["status"] == status
    ]

# ==========================================================
# COLUNAS
# ==========================================================

colunas = [
    "id",
    "cliente_nome",
    "cliente_telefone",
    "cesta_nome",
    "status",
    "data_entrega"
]

colunas = [c for c in colunas if c in df.columns]

df = df[colunas]
st.subheader("📋 Lista de Pedidos")

for _, pedido in df.iterrows():

    col1, col2, col3, col4, col5, col6 = st.columns(
        [1, 3, 2, 2, 2, 1]
    )

    with col1:
        st.write(f"**#{pedido['id']}**")

    with col2:
        st.write(pedido["cliente_nome"])

    with col3:
        st.write(pedido["cesta_nome"])

    with col4:
        st.write(pedido["status"])

    with col5:
        st.write(str(pedido["data_entrega"]))

    with col6:

        if st.button(
            "👁️",
            key=f"abrir_{pedido['id']}",
            help="Abrir pedido"
        ):

            st.session_state["pedido_aberto"] = pedido["id"]

            st.switch_page("pages/08_Admin.py")

st.divider()

st.caption(f"Total de pedidos: {len(df)}")
