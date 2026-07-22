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
    "Gerencie as categorias de produtos da Doce Cesta Brasília"
)



# =====================================================
# CADASTRAR NOVA CATEGORIA
# =====================================================

with st.expander(
    "➕ Nova Categoria",
    expanded=False
):


    nome_categoria = st.text_input(
        "Nome da categoria",
        key="nova_categoria_nome"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        possui_preco = st.checkbox(
            "Possui preço",
            value=False,
            key="nova_categoria_preco"
        )


    with col2:

        exibir_no_pedido = st.checkbox(
            "Exibir no pedido",
            value=False,
            key="nova_categoria_pedido"
        )


    with col3:

        ativo = st.checkbox(
            "Ativa",
            value=True,
            key="nova_categoria_ativa"
        )


    ordem = st.number_input(
        "Ordem de exibição",
        min_value=0,
        value=0,
        key="nova_categoria_ordem"
    )



    if st.button(
        "💾 Salvar categoria",
        key="salvar_nova_categoria",
        use_container_width=True
    ):


        if not nome_categoria.strip():

            st.error(
                "Informe o nome da categoria."
            )


        else:

            try:

                cadastrar_categoria(

                    nome_categoria,

                    possui_preco,

                    exibir_no_pedido,

                    ativo,

                    ordem

                )


                st.success(
                    "Categoria cadastrada com sucesso!"
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


st.subheader(
    "Categorias cadastradas"
)


categorias = listar_categorias()



if not categorias:

    st.info(
        "Nenhuma categoria cadastrada."
    )

    st.stop()



# =====================================================
# EXIBIÇÃO DAS CATEGORIAS
# =====================================================


for categoria in categorias:


    categoria_id = categoria["id"]


    nome = categoria.get(
        "nome",
        ""
    )


    ativo = categoria.get(
        "ativo",
        False
    )


    possui_preco = categoria.get(
        "possui_preco",
        False
    )


    exibir_pedido = categoria.get(
        "exibir_no_pedido",
        False
    )


    ordem_atual = categoria.get(
        "ordem",
        0
    )



    with st.container(border=True):


        status = (
            "🟢 Ativa"
            if ativo
            else
            "🔴 Inativa"
        )


        st.markdown(
            f"""
### {nome}

{status} |  Preço: {"Sim" if possui_preco else "Não"} |  Pedido: {"Sim" if exibir_pedido else "Não"} | Ordem: {ordem_atual}
"""
        )
  
        # =====================================================
        # BOTÕES DE AÇÃO
        # =====================================================


        col_status, col_editar, col_excluir = st.columns(
            [1, 1, 1]
        )


        # =====================================================
        # ALTERAR STATUS
        # =====================================================

        with col_status:


            texto_status = (
                "🔴 Desativar"
                if ativo
                else
                "🟢 Ativar"
            )


            if st.button(

                texto_status,

                key=f"categoria_status_{categoria_id}",

                use_container_width=True

            ):


                try:


                    alterar_status_categoria(

                        categoria_id,

                        not ativo

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
        # EDITAR
        # =====================================================

        with col_editar:


            editar = st.button(

                "✏️ Editar",

                key=f"categoria_editar_{categoria_id}",

                use_container_width=True

            )



        # =====================================================
        # EXCLUIR
        # =====================================================

        with col_excluir:


            excluir = st.button(

                "🗑️ Excluir",

                key=f"categoria_excluir_{categoria_id}",

                use_container_width=True

            )



        # =====================================================
        # FORMULÁRIO DE EDIÇÃO
        # =====================================================

        if editar:


            with st.form(

                key=f"form_categoria_{categoria_id}"

            ):


                novo_nome = st.text_input(

                    "Nome da categoria",

                    value=nome,

                    key=f"categoria_nome_{categoria_id}"

                )



                col1, col2 = st.columns(2)



                with col1:


                    novo_preco = st.checkbox(

                        "Possui preço",

                        value=possui_preco,

                        key=f"categoria_preco_{categoria_id}"

                    )



                with col2:


                    novo_exibir = st.checkbox(

                        "Exibir no pedido",

                        value=exibir_pedido,

                        key=f"categoria_pedido_{categoria_id}"

                    )



                nova_ordem = st.number_input(

                    "Ordem de exibição",

                    min_value=0,

                    value=ordem_atual,

                    key=f"categoria_ordem_{categoria_id}"

                )



                salvar_edicao = st.form_submit_button(

                    "💾 Salvar alterações",

                    use_container_width=True

                )



                if salvar_edicao:


                    if not novo_nome.strip():

                        st.error(
                            "Informe o nome da categoria."
                        )


                    else:


                        try:


                            atualizar_categoria(

                                categoria_id,

                                novo_nome,

                                novo_preco,

                                novo_exibir,

                                ativo,

                                nova_ordem

                            )


                            st.success(

                                "Categoria atualizada com sucesso!"

                            )


                            st.rerun()



                        except Exception as erro:


                            st.error(

                                f"Erro ao atualizar: {erro}"

                            )



        # =====================================================
        # CONFIRMAÇÃO DE EXCLUSÃO
        # =====================================================

        if excluir:


            confirmar = st.warning(
                f"Deseja realmente excluir a categoria **{nome}**?"
            )


            col_confirmar, col_cancelar = st.columns(2)



            with col_confirmar:


                if st.button(

                    "✅ Confirmar exclusão",

                    key=f"confirmar_exclusao_{categoria_id}",

                    use_container_width=True

                ):


                    try:


                        resultado = excluir_categoria(

                            categoria_id

                        )


                        if resultado is False:


                            st.error(

                                "Não foi possível excluir a categoria."

                            )


                        else:


                            st.success(

                                "Categoria excluída com sucesso!"

                            )


                            st.rerun()



                    except Exception as erro:


                        st.error(

                            f"Erro ao excluir: {erro}"

                        )



            with col_cancelar:


                if st.button(

                    "❌ Cancelar",

                    key=f"cancelar_exclusao_{categoria_id}",

                    use_container_width=True

                ):


                    st.rerun()
# =====================================================
# RODAPÉ
# =====================================================

st.divider()


st.markdown(
    """
    <div style="
        text-align:center;
        font-size:12px;
        padding:15px;
    ">

    © 2026 Doce Cesta Brasília

    </div>
    """,
    unsafe_allow_html=True
)
