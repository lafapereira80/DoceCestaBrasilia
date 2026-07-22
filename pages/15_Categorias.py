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
    administrador
)



# =====================================================
# CONFIGURAÇÃO
# =====================================================

configurar_pagina(
    "Categorias"
)

menu_lateral()


administrador()



# =====================================================
# TÍTULO
# =====================================================

st.markdown(
"""
<h2 style="
color:#8B5A2B;
">
📂 Categorias de Produtos
</h2>
""",
unsafe_allow_html=True
)



st.caption(
    "Cadastre e organize as categorias utilizadas nas cestas e pedidos."
)



# =====================================================
# CARREGAR CATEGORIAS
# =====================================================

try:

    categorias = listar_categorias()


except Exception as erro:

    st.error(
        f"Erro ao carregar categorias: {erro}"
    )

    categorias = []





# =====================================================
# NOVA CATEGORIA
# =====================================================

with st.expander(
    "➕ Nova categoria",
    expanded=False
):


    col1,col2,col3 = st.columns(
        [2,1,1]
    )


    with col1:

        nome = st.text_input(
            "Nome da categoria"
        )


    with col2:

        possui_preco = st.checkbox(
            "Possui preço",
            value=False
        )


    with col3:

        ordem = st.number_input(
            "Ordem",
            min_value=0,
            value=0
        )



    exibir_no_pedido = st.checkbox(
        "Exibir no pedido do cliente",
        value=True
    )



    if st.button(
        "💾 Salvar categoria",
        use_container_width=True
    ):


        if not nome.strip():

            st.error(
                "Informe o nome da categoria."
            )


        else:

            try:


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



            except Exception as erro:


                st.error(
                    f"Erro ao cadastrar: {erro}"
                )



# =====================================================
# LISTAGEM
# =====================================================

st.divider()


st.markdown(
"### 📋 Categorias cadastradas"
)
# =====================================================
# EXIBIÇÃO DAS CATEGORIAS
# =====================================================


if not categorias:


    st.info(
        "Nenhuma categoria cadastrada."
    )


else:


    for categoria in categorias:


        with st.container(border=True):


            col1,col2,col3,col4 = st.columns(
                [3,1,1,1]
            )


            # -----------------------------------------
            # NOME
            # -----------------------------------------

            with col1:


                st.markdown(
                    f"""
**{categoria['nome']}**

"""
                )


                detalhes = []


                if categoria.get(
                    "possui_preco"
                ):

                    detalhes.append(
                        "💰 Possui preço"
                    )

                else:

                    detalhes.append(
                        "🎁 Incluso na cesta"
                    )



                if categoria.get(
                    "exibir_no_pedido"
                ):

                    detalhes.append(
                        "👁️ Aparece no pedido"
                    )

                else:

                    detalhes.append(
                        "🚫 Oculta do pedido"
                    )



                st.caption(

                    " | ".join(detalhes)

                )



            # -----------------------------------------
            # STATUS
            # -----------------------------------------

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




            # -----------------------------------------
            # ALTERAR STATUS
            # -----------------------------------------

            with col3:


                texto_status = (

                    "Desativar"
                    if ativo
                    else
                    "Ativar"

                )


                if st.button(

                    f"🔄 {texto_status}",

                    key=f"status_{categoria['id']}",

                    use_container_width=True

                ):


                    try:


                        alterar_status_categoria(

                            categoria["id"],

                            not ativo

                        )


                        st.success(

                            "Status alterado!"

                        )


                        st.rerun()



                    except Exception as erro:


                        st.error(

                            f"Erro ao alterar status: {erro}"

                        )





            # -----------------------------------------
            # EXCLUIR
            # -----------------------------------------

            with col4:


                if st.button(

                    "🗑️",

                    key=f"excluir_{categoria['id']}",

                    use_container_width=True

                ):


                    try:


                        excluir_categoria(

                            categoria["id"]

                        )


                        st.success(

                            "Categoria excluída!"

                        )


                        st.rerun()



                    except Exception as erro:


                        st.error(

                            f"Erro ao excluir: {erro}"

                        )



            # -----------------------------------------
            # ÁREA DE EDIÇÃO
            # -----------------------------------------

            with st.expander(
                "✏️ Editar categoria"
            ):


                col1,col2,col3 = st.columns(
                    [2,1,1]
                )


                with col1:


                    novo_nome = st.text_input(

                        "Nome",

                        value=categoria["nome"],

                        key=f"nome_{categoria['id']}"

                    )



                with col2:


                    nova_ordem = st.number_input(

                        "Ordem",

                        min_value=0,

                        value=categoria.get(
                            "ordem",
                            0
                        ),

                        key=f"ordem_{categoria['id']}"

                    )



                with col3:


                    novo_ativo = st.checkbox(

                        "Ativo",

                        value=categoria.get(
                            "ativo",
                            False
                        ),

                        key=f"ativo_{categoria['id']}"

                    )



                col4,col5 = st.columns(2)



                with col4:


                    novo_preco = st.checkbox(

                        "Possui preço",

                        value=categoria.get(
                            "possui_preco",
                            False
                        ),

                        key=f"preco_{categoria['id']}"

                    )



                with col5:


                    novo_exibir = st.checkbox(

                        "Exibir no pedido",

                        value=categoria.get(
                            "exibir_no_pedido",
                            True
                        ),

                        key=f"pedido_{categoria['id']}"

                    )




                if st.button(

                    "💾 Salvar alterações",

                    key=f"salvar_{categoria['id']}",

                    use_container_width=True

                ):


                    try:


                        atualizar_categoria(

                            categoria["id"],

                            novo_nome,

                            novo_preco,

                            novo_exibir,

                            novo_ativo,

                            nova_ordem

                        )


                        st.success(

                            "Categoria atualizada!"

                        )


                        st.rerun()



                    except Exception as erro:


                        st.error(

                            f"Erro ao atualizar: {erro}"

                        )
                        # =====================================================
# AJUSTES FINAIS
# =====================================================


st.divider()



st.markdown(
"""
<div style="
text-align:center;
font-size:12px;
color:#777;
padding:15px;
">

Doce Cesta Brasília - Administração

</div>
""",
unsafe_allow_html=True
)
