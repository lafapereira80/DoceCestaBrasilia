import streamlit as st

from services.configuracao_cesta_service import (
    buscar_configuracoes_da_cesta,
    salvar_configuracoes
)

st.set_page_config(
    page_title="Configuração da Cesta",
    page_icon="⚙️",
    layout="wide"
)

# =====================================================
# VERIFICA SE EXISTE CESTA SELECIONADA
# =====================================================

if "cesta_produtos" not in st.session_state:

    st.error("Nenhuma cesta selecionada.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/04_Cestas.py")

    st.stop()

cesta_id = st.session_state["cesta_produtos"]

st.title("⚙️ Configuração da Cesta")

st.divider()

# =====================================================
# CARREGA CONFIGURAÇÕES
# =====================================================

configuracoes = buscar_configuracoes_da_cesta(cesta_id)

config = {}

for item in configuracoes:

    config[item["categoria"]] = item["quantidade"]
# =====================================================
# FORMULÁRIO
# =====================================================

with st.form("configuracao_cesta"):

    st.subheader("🥖 Pães")

    qtd_paes = st.radio(

        "Quantidade que o cliente poderá escolher",

        [1, 2, 3],

        index=max(0, config.get("Pães", 1) - 1),

        horizontal=True

    )

    st.divider()

    st.subheader("🥤 Bebidas")

    qtd_bebidas = st.radio(

        "Quantidade que o cliente poderá escolher ",

        [1, 2, 3],

        index=max(0, config.get("Bebidas", 1) - 1),

        horizontal=True,

        key="bebidas"

    )

    st.divider()

    st.subheader("🍯 Espalháveis")

    qtd_espalhaveis = st.radio(

        "Quantidade que o cliente poderá escolher  ",

        [1, 2, 3],

        index=max(0, config.get("Espalháveis", 1) - 1),

        horizontal=True,

        key="espalhaveis"

    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        salvar = st.form_submit_button(

            "💾 Salvar Configuração",

            use_container_width=True

        )

    with col2:

        voltar = st.form_submit_button(

            "⬅ Voltar",

            use_container_width=True

        )
# =====================================================
# BOTÕES
# =====================================================

if voltar:

    st.session_state.pop(
        "cesta_produtos",
        None
    )

    st.switch_page(
        "pages/04_Cestas.py"
    )


if salvar:

    try:

        salvar_configuracoes(

            cesta_id,

            {

                "Pães": qtd_paes,

                "Bebidas": qtd_bebidas,

                "Espalháveis": qtd_espalhaveis

            }

        )

        st.success(
            "Configuração salva com sucesso!"
        )

        st.rerun()

    except Exception as erro:

        st.error(
            f"Erro ao salvar configuração: {erro}"
        )
