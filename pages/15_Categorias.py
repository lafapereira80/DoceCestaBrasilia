import streamlit as st


from services.categoria_service import (
    listar_categorias,
    cadastrar_categoria,
    atualizar_categoria,
    alterar_status_categoria,
    excluir_categoria
)


from utils.menu import (
    configurar_pagina,
    menu_lateral
)


from utils.permissao import (
    administrador_operador
)



# =====================================================
# CONFIGURAÇÃO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()



# =====================================================
# TÍTULO
# =====================================================

st.title("📂 Categorias")

st.caption(
    "Gerencie categorias de produtos e adicionais"
)



st.divider()



# =====================================================
# NOVA CATEGORIA
# =====================================================

with st.expander(
    "➕ Nova categoria"
):


    nome = st.text_input(
        "Nome da categoria"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        possui_preco = st.checkbox(
            "Possui preço",
            value=False
        )


    with col2:

        exibir_no_pedido = st.checkbox(
            "Exibir no pedido",
            value=True
        )


    with col3:

        ordem = st.number_input(
            "Ordem",
            min_value=0,
            value=0
        )



    if st.button(
        "Salvar categoria"
    ):


        if not nome.strip():

            st.error(
                "Informe o nome da categoria."
            )

            st.stop()



        cadastrar_categoria(

            nome,

            possui_preco,

            exibir_no_pedido,

            True,

            ordem

        )


        st.success(
            "Categoria cadastrada!"
        )


        st.rerun()



# =====================================================
# LISTAGEM
# =====================================================


st.subheader(
    "Categorias cadastradas"
)



categorias = listar_categorias()



if not categorias:


    st.info(
        "Nenhuma categoria cadastrada."
    )


    st.stop()





for categoria in categorias:



    with st.container(border=True):


        col1, col2, col3 = st.columns(
            [3,1,1]
        )



        with col1:


            st.markdown(

                f"### {categoria['nome']}"

            )


            st.write(

                f"Ordem: {categoria.get('ordem',0)}"

            )



            if categoria.get("possui_preco"):


                st.write(
                    "💰 Possui preço"
                )

            else:


                st.write(
                    "📦 Incluso na cesta"
                )



            if categoria.get(
                "exibir_no_pedido"
            ):


                st.write(
                    "👁️ Aparece no pedido"
                )


            else:


                st.write(
                    "🙈 Oculta no pedido"
                )



        with col2:



            ativo = categoria.get(
                "ativo",
                False
            )



            if ativo:


                st.success(
                    "🟢 Ativa"
                )


            else:


                st.error(
                    "🔴 Inativa"
                )



        with col3:



            if st.button(

                "🔄",

                key=f"status_{categoria['id']}",

                help="Alterar status"

            ):


                novo_status = not ativo



                resultado = alterar_status_categoria(

                    categoria["id"],

                    novo_status

                )



                if resultado:


                    st.success(

                        "Status alterado!"

                    )


                    st.rerun()


                else:


                    st.error(

                        "Erro ao alterar status."

                    )



        st.divider()



        # =================================================
        # EXCLUSÃO
        # =================================================


        confirmar = st.checkbox(

            "Confirmar exclusão",

            key=f"confirmar_{categoria['id']}"

        )



        if confirmar:


            if st.button(

                "🗑️ Excluir categoria",

                key=f"delete_{categoria['id']}"

            ):


                excluir_categoria(

                    categoria["id"]

                )


                st.success(

                    "Categoria excluída!"

                )


                st.rerun()
