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
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.caption(f"Total de pedidos: {len(df)}")
