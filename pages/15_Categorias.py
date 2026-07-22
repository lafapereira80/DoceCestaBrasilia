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

    administrador

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

administrador()



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
    "Gerenciamento das categorias de produtos"
)


st.divider()





# =====================================================
# CADASTRAR NOVA CATEGORIA
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
# LISTAGEM
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


                b1,b2 = st.columns(2)



                with b1:


                    alterar = st.button(

                        "🔄",

                        key=f"status_{categoria['id']}",

                        help="Alterar status"

                    )



                with b2:


                    excluir = st.button(

                        "🗑️",

                        key=f"excluir_{categoria['id']}",

                        help="Excluir categoria"

                    )





            if alterar:


                novo_status = not categoria.get(

                    "ativo",

                    True

                )


                alterar_status_categoria(

                    categoria["id"],

                    novo_status

                )


                st.rerun()





            if excluir:


                try:


                    excluir_categoria(

                        categoria["id"]

                    )


                    st.success(

                        "Categoria excluída."

                    )


                    st.rerun()



                except Exception as erro:


                    st.error(

                        f"Erro ao excluir categoria: {erro}"

                    )





# =====================================================
# RODAPÉ
# =====================================================

st.divider()


st.caption(

    "📂 Gerenciamento de categorias - Doce Cesta Brasília"

)
