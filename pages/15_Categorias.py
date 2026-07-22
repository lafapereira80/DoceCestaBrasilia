import streamlit as st


from services.categoria_service import (

    listar_categorias,

    cadastrar_categoria,

    atualizar_categoria,

    excluir_categoria,

    alterar_status_categoria

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

st.set_page_config(

    page_title="Categorias",

    page_icon="📂",

    layout="wide"

)



# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()



# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>

.block-container{

    padding-top:1rem;

}


.stButton button{

    height:32px;

    border-radius:8px;

    font-size:13px;

}


</style>

""",

unsafe_allow_html=True

)



# =====================================================
# TÍTULO
# =====================================================

st.title(

    "📂 Categorias"

)


st.caption(

    "Gerenciamento das categorias do sistema"

)


st.divider()



# =====================================================
# NOVA CATEGORIA
# =====================================================

st.subheader(

    "➕ Nova Categoria"

)



with st.form(

    "nova_categoria"

):


    nome = st.text_input(

        "Nome da Categoria"

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


        ativo = st.checkbox(

            "Categoria ativa",

            value=True

        )

    ordem = st.number_input(

        "Ordem de exibição",

        min_value=0,

        value=0,

        step=1

    )



    salvar = st.form_submit_button(

        "💾 Salvar Categoria",

        use_container_width=True

    )





# =====================================================
# SALVAR NOVA CATEGORIA
# =====================================================

if salvar:


    if not nome.strip():


        st.error(

            "Informe o nome da categoria."

        )

        st.stop()



    try:


        cadastrar_categoria(

            nome.strip(),

            possui_preco,

            exibir_no_pedido,

            ativo,

            ordem

        )


        st.success(

            "Categoria criada com sucesso!"

        )


        st.rerun()



    except Exception as erro:


        st.error(

            f"Erro ao criar categoria: {erro}"

        )





# =====================================================
# LISTAGEM DE CATEGORIAS
# =====================================================

st.divider()


st.subheader(

    "📋 Categorias cadastradas"

)



try:


    categorias = listar_categorias()



except Exception as erro:


    st.error(

        f"Erro ao carregar categorias: {erro}"

    )


    categorias = []




if not categorias:


    st.info(

        "Nenhuma categoria cadastrada."

    )


else:


    for categoria in categorias:


        with st.container(border=True):


            col1, col2, col3, col4 = st.columns(

                [4,2,2,2]

            )



            with col1:


                st.write(

                    f"**{categoria['nome']}**"

                )


                st.caption(

                    f"Ordem: {categoria.get('ordem',0)}"

                )



                if categoria.get(

                    "exibir_no_pedido",

                    True

                ):


                    st.caption(

                        "📦 Aparece no pedido"

                    )


                else:


                    st.caption(

                        "🚫 Oculta no pedido"

                    )



            with col2:


                if categoria.get(

                    "possui_preco",

                    False

                ):


                    st.success(

                        "💰 Possui preço"

                    )


                else:


                    st.info(

                        "Incluso"

                    )



            with col3:


                if categoria.get(

                    "ativo",

                    True

                ):


                    st.success(

                        "🟢 Ativa"

                    )


                else:


                    st.error(

                        "🔴 Inativa"

                    )



            with col4:


                b1, b2, b3 = st.columns(3)



                with b1:


                    editar = st.button(

                        "✏️",

                        key=f"editar_{categoria['id']}",

                        help="Editar categoria"

                    )


                with b2:


                    alterar = st.button(

                        "🔄",

                        key=f"status_{categoria['id']}",

                        help="Alterar status"

                    )


                with b3:


                    excluir = st.button(

                        "🗑️",

                        key=f"excluir_{categoria['id']}",

                        help="Excluir categoria"

                    )

            # =====================================================
            # EDITAR CATEGORIA
            # =====================================================

            if editar:


                st.session_state["categoria_editar"] = categoria["id"]


                st.rerun()





            # =====================================================
            # ALTERAR STATUS
            # =====================================================

            if alterar:


                novo_status = not categoria.get(

                    "ativo",

                    True

                )


                try:


                    alterar_status_categoria(

                        categoria["id"],

                        novo_status

                    )


                    st.success(

                        "Status alterado com sucesso!"

                    )


                    st.rerun()



                except Exception as erro:


                    st.error(

                        f"Erro ao alterar status: {erro}"

                    )





            # =====================================================
            # EXCLUIR CATEGORIA
            # =====================================================

            if excluir:


                try:


                    excluir_categoria(

                        categoria["id"]

                    )


                    st.success(

                        "Categoria excluída com sucesso!"

                    )


                    st.rerun()



                except Exception as erro:


                    st.error(

                        f"Erro ao excluir categoria: {erro}"

                    )



            st.write("")





# =====================================================
# FORMULÁRIO DE EDIÇÃO
# =====================================================

if "categoria_editar" in st.session_state:


    categoria_id = st.session_state["categoria_editar"]



    categoria_edicao = None



    for item in categorias:


        if item["id"] == categoria_id:


            categoria_edicao = item

            break



    if categoria_edicao:


        st.divider()


        st.subheader(

            "✏️ Editar Categoria"

        )



        with st.form(

            "editar_categoria"

        ):


            nome_editado = st.text_input(

                "Nome da Categoria",

                value=categoria_edicao["nome"]

            )



            col1,col2,col3 = st.columns(3)



            with col1:


                possui_preco_editado = st.checkbox(

                    "Possui preço",

                    value=categoria_edicao.get(

                        "possui_preco",

                        False

                    )

                )



            with col2:


                exibir_editado = st.checkbox(

                    "Exibir no pedido",

                    value=categoria_edicao.get(

                        "exibir_no_pedido",

                        True

                    )

                )



            with col3:


                ativo_editado = st.checkbox(

                    "Categoria ativa",

                    value=categoria_edicao.get(

                        "ativo",

                        True

                    )

                )



            ordem_editada = st.number_input(

                "Ordem",

                min_value=0,

                value=categoria_edicao.get(

                    "ordem",

                    0

                )

            )



            col1,col2 = st.columns(2)



            with col1:


                salvar_edicao = st.form_submit_button(

                    "💾 Atualizar",

                    use_container_width=True

                )



            with col2:


                cancelar_edicao = st.form_submit_button(

                    "❌ Cancelar",

                    use_container_width=True

                )
                     # =====================================================
        # SALVAR EDIÇÃO
        # =====================================================

        if salvar_edicao:


            if not nome_editado.strip():


                st.error(

                    "Informe o nome da categoria."

                )

                st.stop()



            try:


                atualizar_categoria(

                    categoria_id,

                    nome_editado.strip(),

                    possui_preco_editado,

                    exibir_editado,

                    ativo_editado,

                    ordem_editada

                )


                st.success(

                    "Categoria atualizada com sucesso!"

                )


                st.session_state.pop(

                    "categoria_editar",

                    None

                )


                st.rerun()



            except Exception as erro:


                st.error(

                    f"Erro ao atualizar categoria: {erro}"

                )





        # =====================================================
        # CANCELAR EDIÇÃO
        # =====================================================

        if cancelar_edicao:


            st.session_state.pop(

                "categoria_editar",

                None

            )


            st.rerun()





# =====================================================
# RODAPÉ
# =====================================================

st.divider()



st.caption(

    "📂 Gerenciamento de categorias - Doce Cesta Brasília"

)   
