import streamlit as st

from services.cesta_service import (
    listar_cestas,
    cadastrar_cesta,
    excluir_cesta,
    alterar_status_cesta
)

st.set_page_config(
    page_title="Cestas",
    page_icon="🎁",
    layout="wide"
)

st.title("🎁 Cadastro de Cestas")

st.divider()

# =====================================================
# NOVA CESTA
# =====================================================

st.subheader("➕ Nova Cesta")

with st.form("nova_cesta"):

    nome = st.text_input(
        "Nome da Cesta"
    )

    descricao = st.text_area(
        "Descrição"
    )

    preco = st.number_input(
        "Preço (R$)",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

    imagem = st.text_input(
        "Imagem (URL)"
    )

    salvar = st.form_submit_button(
        "💾 Cadastrar Cesta",
        use_container_width=True
    )

if salvar:

    if nome.strip() == "":

        st.error("Informe o nome da cesta.")

    else:

        try:

            cadastrar_cesta(
                nome.strip(),
                descricao.strip(),
                preco,
                imagem.strip()
            )

            st.success(
                "Cesta cadastrada com sucesso!"
            )

            st.rerun()

        except Exception as erro:

            st.error(
                f"Erro ao cadastrar cesta: {erro}"
            )

st.divider()

# =====================================================
# CARREGA CESTAS
# =====================================================

try:

    cestas = listar_cestas()

except Exception as erro:

    st.error(
        f"Erro ao carregar cestas: {erro}"
    )

    st.stop()

st.subheader("📋 Cestas Cadastradas")
