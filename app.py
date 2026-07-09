import streamlit as st

# ==========================
# CONFIGURAÇÃO DA PÁGINA
# ==========================
st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="wide"
)

# ==========================
# TÍTULO
# ==========================
st.title("🎁 Doce Cesta Brasília")

st.subheader("Bem-vindo ao sistema de pedidos")

st.write("""
Este sistema está sendo desenvolvido especialmente para a
**Doce Cesta Brasília**.

Em breve será possível:

✅ Fazer pedidos

✅ Enviar fotos para Polaroid

✅ Escolher cestas

✅ Acompanhar pedidos

✅ Área administrativa completa
""")

st.success("Primeira versão criada com sucesso!")
