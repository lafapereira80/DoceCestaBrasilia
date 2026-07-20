import streamlit as st


from services.cesta_service import (
    listar_cestas,
    cadastrar_cesta,
    excluir_cesta
)


from utils.menu import (
    configurar_pagina,
    menu_lateral
)


from utils.permissao import (
    administrador_operador
)



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
# TÍTULO
# =====================================================

st.title(
    "🎁 Cadastro de Cestas"
)


st.divider()



# =====================================================
# NOVA CESTA
# =====================================================

if usuario["perfil"] == "Administrador":


    st.subheader(
        "➕ Nova Cesta"
    )



    with st.form(
        "nova_cesta"
    ):


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


            st.error(
                "Informe o nome da cesta."
            )


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



else:


    st.info(
        "Modo consulta. Apenas Administradores podem alterar cestas."
    )



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



st.subheader(
    "📋 Cestas Cadastradas"
)



# =====================================================
# LISTAGEM
# =====================================================

if not cestas:


    st.info(
        "Nenhuma cesta cadastrada."
    )



else:


    for cesta in cestas:



        ativa = cesta.get(
            "ativa",
            True
        )



        with st.container(border=True):


            if usuario["perfil"] == "Administrador":


                col1, col2, col3, col4, col5, col6, col7 = st.columns(
                    [5,2,1,1,1,1,1]
                )


            else:


                col1, col2, col3 = st.columns(
                    [5,2,1]
                )



            # ===========================
            # DADOS
            # ===========================


            with col1:


                st.write(
                    f"**{cesta['nome']}**"
                )



                if cesta.get("descricao"):


                    st.caption(
                        cesta["descricao"]
                    )



            with col2:


                st.write(

                    f"R$ {float(cesta['preco']):.2f}"

                )



            with col3:


                if ativa:


                    st.success(
                        "Ativa"
                    )


                else:


                    st.error(
                        "Inativa"
                    )



            # ===========================
            # AÇÕES ADMIN
            # ===========================


            if usuario["perfil"] == "Administrador":



                with col4:


                    if st.button(

                        "✏️",

                        key=f"editar_{cesta['id']}"

                    ):


                        st.session_state[
                            "cesta_editar"
                        ] = cesta["id"]



                        st.switch_page(

                            "pages/11_Editar_Cesta.py"

                        )




                with col5:


                    if st.button(

                        "📦",

                        key=f"produtos_{cesta['id']}"

                    ):


                        st.session_state[
                            "cesta_produtos"
                        ] = cesta["id"]



                        st.switch_page(

                            "pages/12_Produtos_da_Cesta.py"

                        )




                with col6:


                    if st.button(

                        "⚙️",

                        key=f"config_{cesta['id']}"

                    ):


                        st.session_state[
                            "cesta_produtos"
                        ] = cesta["id"]



                        st.switch_page(

                            "pages/13_Configurar_Cesta.py"

                        )




                with col7:


                    if st.button(

                        "🗑️",

                        key=f"excluir_{cesta['id']}"

                    ):


                        sucesso = excluir_cesta(
                            cesta["id"]
                        )


                        st.success(
                            "Cesta excluída."
                        )


                        st.rerun()



        st.divider()
