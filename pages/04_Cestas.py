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

# =====================================================
# LISTAGEM DAS CESTAS
# =====================================================

if not cestas:

    st.info("Nenhuma cesta cadastrada.")

else:

    for cesta in cestas:

        ativa = cesta.get("ativa", True)

        with st.container(border=True):

            col1, col2, col3, col4, col5, col6 = st.columns(
                [5, 2, 1, 1, 1, 1]
            )

            with col1:

                st.write(f"**{cesta['nome']}**")

                if cesta["descricao"]:

                    st.caption(cesta["descricao"])

            with col2:

                st.write(
                    f"R$ {float(cesta['preco']):.2f}"
                )

            with col3:

                if ativa:

                    st.success("Ativa")

                else:

                    st.error("Inativa")

            # =======================================
            # EDITAR
            # =======================================

            with col4:

                if st.button(
                    "✏️",
                    key=f"editar_{cesta['id']}"
                ):

                    st.session_state["cesta_editar"] = cesta["id"]

                    st.switch_page(
                        "pages/11_Editar_Cesta.py"
                    )

            # =======================================
            # PRODUTOS DA CESTA
            # =======================================

            with col5:

                if st.button(
                    "📦",
                    key=f"produtos_{cesta['id']}"
                ):

                    st.session_state["cesta_produtos"] = cesta["id"]

                    st.switch_page(
                        "pages/12_Produtos_da_Cesta.py"
                    )

            # =======================================
            # EXCLUIR
            # =======================================

            with col6:

                if st.button(
                    "🗑️",
                    key=f"excluir_{cesta['id']}"
                ):

                    excluir_cesta(cesta["id"])

                    st.success("Cesta excluída.")

                    st.rerun()

        st.divider()
        
