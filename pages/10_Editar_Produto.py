import streamlit as st


from services.produto_service import (
    listar_categorias,
    buscar_produto,
    atualizar_produto
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

    page_title="Editar Produto",

    page_icon="✏️",

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

h1{

font-size:24px !important;

}


p,div,span,label{

font-size:13px;

}


.stButton button{

height:34px;

font-size:13px;

}


</style>
""",
unsafe_allow_html=True
)




# =====================================================
# VALIDA PRODUTO
# =====================================================

if "produto_editar" not in st.session_state:


    st.error(
        "Nenhum produto selecionado."
    )


    if st.button("⬅ Voltar"):


        st.switch_page(
            "pages/05_Produtos.py"
        )


    st.stop()




produto_id = st.session_state["produto_editar"]




# =====================================================
# BUSCA DADOS
# =====================================================

try:


    produto = buscar_produto(

        produto_id

    )


    categorias = listar_categorias()



except Exception as erro:


    st.error(

        f"Erro ao carregar produto: {erro}"

    )


    st.stop()




st.title(
    "✏️ Editar Produto"
)


st.caption(
    "Atualize as informações do produto."
)


st.divider()




indice_categoria = 0


for i,categoria in enumerate(categorias):


    if categoria["id"] == produto["categoria_id"]:


        indice_categoria = i

        break

# =====================================================
# FORMULÁRIO
# =====================================================

with st.form(
    "form_editar_produto"
):


    col1,col2 = st.columns(2)



    with col1:


        categoria = st.selectbox(

            "Categoria",

            categorias,

            index=indice_categoria,

            format_func=lambda c:c["nome"]

        )



    with col2:


        nome = st.text_input(

            "Nome do Produto",

            value=produto.get(

                "nome",

                ""

            )

        )



    descricao = st.text_area(

        "Descrição",

        value=produto.get(

            "descricao",

            ""

        ) or "",

        height=80

    )



    st.divider()



    # =================================================
    # PREÇO
    # =================================================


    preco_atual = produto.get(

        "preco"

    )



    preco_consulta_atual = (

        preco_atual is None

    )



    preco_consulta = False



    if categoria["nome"].lower().strip() == "adicionais":


        preco_consulta = st.checkbox(

            "☐ Preço sob consulta",

            value=preco_consulta_atual,

            help="Produto sem valor definido. O preço será informado no pedido."

        )


    else:


        preco_consulta = False





    if preco_consulta:



        preco = None



        st.info(

            "Produto configurado como: Preço sob consulta."

        )


    else:



        preco = st.number_input(

            "Preço (R$)",

            min_value=0.0,

            value=float(

                preco_atual or 0

            ),

            step=0.50,

            format="%.2f"

        )





    ativo = st.checkbox(

        "Produto ativo",

        value=produto.get(

            "ativo",

            True

        )

    )



    st.divider()



    col1,col2 = st.columns(2)



    with col1:


        salvar = st.form_submit_button(

            "💾 Salvar",

            use_container_width=True

        )



    with col2:


        cancelar = st.form_submit_button(

            "❌ Cancelar",

            use_container_width=True

        )





# =====================================================
# CANCELAR
# =====================================================

if cancelar:


    st.session_state.pop(

        "produto_editar",

        None

    )


    st.switch_page(

        "pages/05_Produtos.py"

    )





# =====================================================
# SALVAR
# =====================================================

if salvar:



    if not nome.strip():


        st.error(

            "Informe o nome do produto."

        )

        st.stop()





    try:



        atualizar_produto(


            produto_id,


            categoria["id"],


            nome.strip(),


            descricao.strip(),


            preco,


            ativo


        )



        st.success(

            "Produto atualizado com sucesso!"

        )



        st.session_state.pop(

            "produto_editar",

            None

        )



        st.switch_page(

            "pages/05_Produtos.py"

        )



    except Exception as erro:


        st.error(

            f"Erro ao atualizar produto: {erro}"

        )
