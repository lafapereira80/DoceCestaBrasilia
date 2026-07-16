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

# Exibe somente as colunas que interessam
colunas = [
    "id",
    "cliente_nome",
    "cliente_telefone",
    "cesta_nome",
    "status",
    "data_entrega"
]

# Mantém apenas as colunas existentes
colunas = [c for c in colunas if c in df.columns]

df = df[colunas]

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.caption(f"Total de pedidos: {len(df)}")
