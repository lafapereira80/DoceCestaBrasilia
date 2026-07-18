import streamlit as st

from services.cesta_service import (
    listar_cestas,
    cadastrar_cesta,
    excluir_cesta
)

st.set_page_config(
    page_title="Cestas",
    page_icon="🧺",
    layout="wide"
)

st.title("🧺 Cadastro de Cestas")

st.divider()
# =====================================================
# FORMULÁRIO
# =====================================================

st.subheader("➕ Nova Cesta")

with st.form("form_cesta"):

    nome = st.text_input(
        "Nome da Cesta"
    )

    descricao = st.text_area(
        "Descrição",
        height=100
    )

    preco = st.number_input(
        "Valor da Cesta (R$)",
        min_value=0.0,
        value=0.0,
        step=1.0
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
                nome,
                descricao,
                preco
            )

            st.success(
                "Cesta cadastrada com sucesso!"
            )

            st.rerun()

        except Exception as erro:

            st.error(erro)

# =====================================================
# LISTA DE CESTAS
# =====================================================

st.subheader("📋 Cestas Cadastradas")

try:

    cestas = listar_cestas()

except Exception as erro:

    st.error(erro)

    st.stop()

if not cestas:

    st.info("Nenhuma cesta cadastrada.")

else:

    for cesta in cestas:

        st.markdown(f"## 🧺 {cesta['nome']}")

        st.write(
            f"**Valor:** R$ {float(cesta['preco']):.2f}"
        )

        if cesta["descricao"]:

            st.caption(cesta["descricao"])

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:

            if st.button(
                "✏️ Dados",
                key=f"dados_{cesta['id']}"
            ):

                st.session_state["editar_cesta"] = cesta["id"]

                st.info(
                    "Edição da cesta será implementada na próxima etapa."
                )

        with col2:

            if st.button(
                "🍞 Pães",
                key=f"paes_{cesta['id']}"
            ):

                st.session_state["configurar_cesta"] = cesta["id"]

                st.session_state["categoria"] = "Pães"

                st.rerun()

        with col3:

            if st.button(
                "🥤 Bebidas",
                key=f"bebidas_{cesta['id']}"
            ):

                st.session_state["configurar_cesta"] = cesta["id"]

                st.session_state["categoria"] = "Bebidas"

                st.rerun()

        with col4:

            if st.button(
                "🍯 Espalháveis",
                key=f"espalhaveis_{cesta['id']}"
            ):

                st.session_state["configurar_cesta"] = cesta["id"]

                st.session_state["categoria"] = "Espalháveis"

                st.rerun()

        with col5:

            if st.button(
                "🗑️",
                key=f"excluir_{cesta['id']}"
            ):

                excluir_cesta(cesta["id"])

                st.success("Cesta excluída.")

                st.rerun()

        st.divider()



st.divider()
