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
            value=False
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
        "💾 Salvar categoria"
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


    with st.container(border=True):


        col1, col2 = st.columns(
            [3,1]
        )


        with col1:


            status = (
                "🟢 Ativa"
                if ativo
                else
                "🔴 Inativa"
            )


            st.markdown(
                f"""
**{nome}**

{status} | 
Preço: {"Sim" if possui_preco else "Não"} | 
Pedido: {"Sim" if exibir_pedido else "Não"}
"""
            )



        with col2:


            if ativo:


                texto_status = "🔴 Desativar"


            else:


                texto_status = "🟢 Ativar"



            if st.button(

                texto_status,

                key=f"status_{categoria_id}"

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



        # =================================================
        # BOTÕES DE AÇÃO
        # =================================================


        col1, col2, col3 = st.columns(3)



        with col1:


            editar = st.button(

                "✏️ Editar",

                key=f"editar_{categoria_id}"

            )



        with col2:


            excluir = st.button(

                "🗑️ Excluir",

                key=f"excluir_{categoria_id}"

            )



        with col3:


            st.write("")



        # =================================================
        # EDITAR
        # =================================================


        if editar:


            with st.form(

                key=f"form_edit_{categoria_id}"

            ):


                novo_nome = st.text_input(

                    "Nome",

                    value=nome

                )


                col1, col2 = st.columns(2)


                with col1:


                    novo_preco = st.checkbox(

                        "Possui preço",

                        value=possui_preco,

                        key=f"preco_{categoria_id}"

                    )


                with col2:


                    novo_exibir = st.checkbox(

                        "Exibir no pedido",

                        value=exibir_pedido,

                        key=f"pedido_{categoria_id}"

                    )



                nova_ordem = st.number_input(

                    "Ordem",

                    min_value=0,

                    value=categoria.get(
                        "ordem",
                        0
                    ),

                    key=f"ordem_{categoria_id}"

                )



                salvar = st.form_submit_button(

                    "💾 Salvar alterações"

                )



                if salvar:


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

                            "Categoria atualizada!"

                        )


                        st.rerun()



                    except Exception as erro:


                        st.error(

                            f"Erro ao atualizar: {erro}"

                        )



        # =================================================
        # EXCLUIR
        # =================================================


        if excluir:


            try:


                excluir_categoria(

                    categoria_id

                )


                st.success(

                    "Categoria excluída!"

                )


                st.rerun()



            except Exception as erro:


                st.error(

                    f"Erro ao excluir: {erro}"

                )
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
