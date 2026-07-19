import streamlit as st

from services.cesta_service import (
    buscar_cesta,
    atualizar_cesta
)

st.set_page_config(
    page_title="Editar Cesta",
    page_icon="✏️",
    layout="wide"
)

# =====================================================
# VERIFICA SE EXISTE CESTA SELECIONADA
# =====================================================

if "cesta_editar" not in st.session_state:

    st.error("Nenhuma cesta selecionada.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/04_Cestas.py")

    st.stop()

cesta_id = st.session_state["cesta_editar"]

# =====================================================
# CARREGA DADOS
# =====================================================

try:

    cesta = buscar_cesta(cesta_id)

except Exception as erro:

    st.error(erro)

    st.stop()

st.title("✏️ Editar Cesta")

st.divider()

# =====================================================
# FORMULÁRIO
# =====================================================

with st.form("form_editar_cesta"):

    nome = st.text_input(
        "Nome da Cesta",
        value=cesta["nome"]
    )

    descricao = st.text_area(
        "Descrição",
        value=cesta["descricao"] or ""
    )

    preco = st.number_input(
        "Preço (R$)",
        min_value=0.0,
        value=float(cesta["preco"]),
        step=1.0
    )

    imagem = st.text_input(
        "Imagem (URL)",
        value=cesta["imagem"] or ""
    )

    ativa = st.checkbox(
        "Cesta ativa",
        value=cesta["ativa"]
    )

    col1, col2 = st.columns(2)

    with col1:

        salvar = st.form_submit_button(
            "💾 Salvar Alterações",
            use_container_width=True
        )

    with col2:

        cancelar = st.form_submit_button(
            "❌ Cancelar",
            use_container_width=True
        )

# =====================================================
# BOTÕES
# =====================================================

if cancelar:

    st.session_state.pop("cesta_editar", None)

    st.switch_page("pages/04_Cestas.py")


if salvar:

    if nome.strip() == "":

        st.error("Informe o nome da cesta.")

    else:

        try:

            atualizar_cesta(
                cesta_id,
                nome.strip(),
                descricao.strip(),
                preco,
                imagem.strip(),
                ativa
            )

            st.success("Cesta atualizada com sucesso!")

            st.session_state.pop("cesta_editar", None)

            st.switch_page("pages/04_Cestas.py")

        except Exception as erro:

            st.error(erro)
