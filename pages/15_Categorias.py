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

st.set_page_config(

    page_title="Categorias",

    page_icon="📂",

    layout="wide"

)



configurar_pagina()

menu_lateral()

administrador_operador()



# =====================================================
# CONTROLE DE EDIÇÃO
# =====================================================

if "categoria_editando" not in st.session_state:

    st.session_state["categoria_editando"] = None



# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>

h1{
font-size:26px !important;
}

h2{
font-size:18px !important;
}

p,div,span{
font-size:13px;
}

.stButton button{
font-size:12px;
padding:4px 10px;
}

[data-testid="stVerticalBlockBorderWrapper"]{
padding:10px;
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
    "Gerencie as categorias de produtos da Doce Cesta Brasília"
)



st.divider()



# =====================================================
# NOVA CATEGORIA
# =====================================================

with st.expander(
    "➕ Nova Categoria"
):


    nome_categoria = st.text_input(
        "Nome da categoria"
    )


    col1,col2,col3 = st.columns(3)



    with col1:

        possui_preco = st.checkbox(
            "Possui preço"
        )


    with col2:

        exibir_no_pedido = st.checkbox(
            "Exibir no pedido"
        )


    with col3:

        ativo = st.checkbox(
            "Ativa",
            value=True
        )


    ordem = st.number_input(

        "Ordem de exibição",

        min_value=0,

        value=0

    )



    if st.button(
        "💾 Salvar categoria",
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



try:

    categorias = listar_categorias()


except Exception as erro:

    st.error(
        f"Erro ao carregar categorias: {erro}"
    )

    st.stop()



if not categorias:

    st.info(
        "Nenhuma categoria cadastrada."
    )

    st.stop()
    # =====================================================
# LISTAGEM DAS CATEGORIAS
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


        status_texto = (

            "🟢 Ativa"

            if ativo

            else

            "🔴 Inativa"

        )


        st.markdown(

            f"""
### {nome}

{status_texto} | Preço: {"Sim" if possui_preco else "Não"} | Pedido: {"Sim" if exibir_pedido else "Não"} | Ordem: {ordem_atual}

"""

        )



        col_status, col_editar, col_excluir = st.columns(3)



        # =====================================================
        # ALTERAR STATUS
        # =====================================================

        with col_status:


            texto_botao = (

                "🔴 Desativar"

                if ativo

                else

                "🟢 Ativar"

            )


            if st.button(

                texto_botao,

                key=f"status_{categoria_id}",

                use_container_width=True

            ):


                try:


                    alterar_status_categoria(

                        categoria_id,

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



        # =====================================================
        # EDITAR
        # =====================================================

        with col_editar:


            if st.button(

                "✏️ Editar",

                key=f"editar_{categoria_id}",

                use_container_width=True

            ):


                st.session_state["categoria_editando"] = categoria_id


                st.rerun()



        # =====================================================
        # EXCLUIR
        # =====================================================

        with col_excluir:


            excluir = st.button(

                "🗑️ Excluir",

                key=f"excluir_{categoria_id}",

                use_container_width=True

            )



        # =====================================================
        # FORMULÁRIO DE EDIÇÃO
        # =====================================================

        if st.session_state["categoria_editando"] == categoria_id:



            st.markdown(
                "#### ✏️ Editando categoria"
            )



            with st.form(

                key=f"form_edicao_{categoria_id}"

            ):


                novo_nome = st.text_input(

                    "Nome da categoria",

                    value=nome

                )



                col1,col2 = st.columns(2)



                with col1:


                    novo_preco = st.checkbox(

                        "Possui preço",

                        value=possui_preco,

                        key=f"preco_edit_{categoria_id}"

                    )



                with col2:


                    novo_exibir = st.checkbox(

                        "Exibir no pedido",

                        value=exibir_pedido,

                        key=f"pedido_edit_{categoria_id}"

                    )



                col3,col4 = st.columns(2)



                with col3:


                    novo_ativo = st.checkbox(

                        "Categoria ativa",

                        value=ativo,

                        key=f"ativo_edit_{categoria_id}"

                    )



                with col4:


                    nova_ordem = st.number_input(

                        "Ordem de exibição",

                        min_value=0,

                        value=int(ordem_atual),

                        step=1,

                        key=f"ordem_edit_{categoria_id}"

                    )



                col_salvar,col_cancelar = st.columns(2)



                with col_salvar:


                    salvar = st.form_submit_button(

                        "💾 Salvar alterações",

                        use_container_width=True

                    )



                with col_cancelar:


                    cancelar = st.form_submit_button(

                        "❌ Cancelar",

                        use_container_width=True

                    )



                if salvar:


                    if not novo_nome.strip():


                        st.error(
                            "Informe o nome da categoria."
                        )


                    else:


                        try:


                            resultado = atualizar_categoria(

                                categoria_id,

                                novo_nome,

                                novo_preco,

                                novo_exibir,

                                novo_ativo,

                                nova_ordem

                            )


                            st.session_state["categoria_editando"] = None


                            st.success(

                                f"Categoria atualizada! Ordem salva: {nova_ordem}"

                            )


                            st.rerun()



                        except Exception as erro:


                            st.error(

                                f"Erro ao atualizar: {erro}"

                            )



                if cancelar:


                    st.session_state["categoria_editando"] = None


                    st.rerun()
                            # =====================================================
        # CONFIRMAÇÃO DE EXCLUSÃO
        # =====================================================

        if excluir:


            st.warning(

                f"Deseja realmente excluir a categoria **{nome}**?"

            )


            col_confirmar, col_cancelar = st.columns(2)



            with col_confirmar:


                if st.button(

                    "✅ Confirmar exclusão",

                    key=f"confirmar_excluir_{categoria_id}",

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


                            st.session_state["categoria_editando"] = None


                            st.rerun()



                    except Exception as erro:


                        st.error(

                            f"Erro ao excluir: {erro}"

                        )



            with col_cancelar:


                if st.button(

                    "❌ Cancelar",

                    key=f"cancelar_excluir_{categoria_id}",

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
