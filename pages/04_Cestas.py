import streamlit as st

from services.cesta_service import (
    listar_cestas,
    cadastrar_cesta,
    excluir_cesta,
    upload_imagem_cesta
)

from utils.menu import (
    configurar_pagina,
    menu_lateral
)

from utils.permissao import (
    administrador_operador
)


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Cestas",
    page_icon="🎁",
    layout="wide"
)


# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CSS COMPACTO
# =====================================================

st.markdown(
"""
<style>

h1 {
    font-size:24px !important;
    margin-bottom:5px;
}

h2 {
    font-size:18px !important;
    margin-top:8px;
    margin-bottom:8px;
}

h3 {
    font-size:15px !important;
}

p, div, span {
    font-size:13px;
}

.stCaption {
    font-size:11px !important;
}

input, textarea {
    font-size:13px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    padding-top:8px;
    padding-bottom:8px;
    margin-bottom:6px;
}

.block-container {
    padding-top:1rem;
    padding-bottom:1rem;
}

hr {
    margin-top:8px;
    margin-bottom:8px;
}

</style>
""",
unsafe_allow_html=True
)


# =====================================================
# TÍTULO
# =====================================================

st.title("🎁 Cestas")
st.divider()


# =====================================================
# NOVA CESTA
# =====================================================

if usuario["perfil"] == "Administrador":

    st.subheader("➕ Nova Cesta")

    with st.form("nova_cesta"):

        nome = st.text_input("Nome da Cesta")

        descricao = st.text_area(
            "Descrição",
            height=70
        )

        preco = st.number_input(
            "Preço (R$)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f"
        )

        imagem_arquivo = st.file_uploader(
            "📷 Foto da Cesta",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ]
        )

        if imagem_arquivo:
            st.image(
                imagem_arquivo,
                width=220
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
                imagem_url = None

                if imagem_arquivo:
                    imagem_url = upload_imagem_cesta(
                        imagem_arquivo
                    )

                cadastrar_cesta(
                    nome.strip(),
                    descricao.strip(),
                    preco,
                    imagem_url
                )

                st.success("Cesta cadastrada com sucesso!")
                st.rerun()

            except Exception as erro:
                st.error(f"Erro ao cadastrar cesta: {erro}")

    st.divider()

else:
    st.info("Modo consulta. Apenas Administradores podem cadastrar novas cestas.")


# =====================================================
# CARREGA CESTAS
# =====================================================

try:
    cestas = listar_cestas()

except Exception as erro:
    st.error(f"Erro ao carregar cestas: {erro}")
    st.stop()


st.subheader("📋 Cestas Cadastradas")


# =====================================================
# LISTAGEM
# =====================================================

if not cestas:

    st.info("Nenhuma cesta cadastrada.")

else:

    for cesta in cestas:

        ativa = cesta.get(
            "ativa",
            True
        )

        with st.container(border=True):

            col1, col2, col3, col4, col5, col6, col7 = st.columns(
                [5, 2, 1, 1, 1, 1, 1]
            )

            # ===========================
            # DADOS DA CESTA
            # ===========================

            with col1:

                st.write(f"**{cesta['nome']}**")

                if cesta.get("descricao"):

                    descricao = cesta["descricao"]

                    if len(descricao) > 90:
                        descricao = descricao[:90] + "..."

                    st.caption(descricao)

                if cesta.get("imagem"):

                    st.image(
                        cesta["imagem"],
                        width=120
                    )

            # ===========================
            # PREÇO
            # ===========================

            with col2:

                try:
                    valor = float(
                        cesta.get(
                            "preco",
                            0
                        )
                    )

                    st.write(f"R$ {valor:.2f}")

                except:
                    st.write("Sem preço")

            # ===========================
            # STATUS
            # ===========================

            with col3:

                if ativa:
                    st.success("✓ Ativa")
                else:
                    st.error("✕ Inativa")

            # ===========================
            # EDITAR
            # ===========================

            with col4:

                if st.button("✏️", key=f"editar_{cesta['id']}", help="Editar Cesta"):

                    st.session_state["cesta_editar"] = cesta["id"]

                    st.switch_page("pages/11_Editar_Cesta.py")

            # ===========================
            # PRODUTOS DA CESTA
            # ===========================

            with col5:

                if st.button("📦", key=f"produtos_{cesta['id']}", help="Produtos da Cesta"):

                    st.session_state["cesta_produtos"] = cesta["id"]

                    st.switch_page("pages/12_Produtos_da_Cesta.py")

            # ===========================
            # CONFIGURAR CESTA
            # ===========================

            with col6:

                if st.button("⚙️", key=f"config_{cesta['id']}", help="Configurar Cesta"):

                    st.session_state["cesta_configurar"] = cesta["id"]

                    st.switch_page("pages/14_Configurar_Cesta.py")

            # ===========================
            # EXCLUIR
            # ===========================

            with col7:

                if st.button("🗑️", key=f"excluir_{cesta['id']}", help="Excluir Cesta"):

                    try:
                        excluir_cesta(cesta["id"])

                        st.success("Cesta excluída.")
                        st.rerun()

                    except Exception as erro:
                        st.error(f"Erro ao excluir cesta: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("Doce Cesta Brasília - Cadastro de Cestas")
