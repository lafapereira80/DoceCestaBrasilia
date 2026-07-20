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
# CONFIGURAÇÃO DA PÁGINA
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

}



p, div, span {

font-size:13px;

}



label {

font-size:13px !important;

}



.stButton button {

height:34px;

font-size:13px;

padding:4px 10px;

}



input {

font-size:13px !important;

}



.block-container {

padding-top:1rem;

padding-bottom:1rem;

}


</style>
""",
unsafe_allow_html=True
)



# =====================================================
# VERIFICA PRODUTO SELECIONADO
# =====================================================

if "produto_editar" not in st.session_state:


    st.error(
        "Nenhum produto selecionado."
    )


    if st.button(
        "⬅ Voltar"
    ):


        st.switch_page(
            "pages/05_Produtos.py"
        )


    st.stop()



produto_id = st.session_state["produto_editar"]



# =====================================================
# CARREGA DADOS
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



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "✏️ Editar Produto"
)


st.caption(
    "Atualize as informações do produto."
)


st.divider()



# =====================================================
# IDENTIFICA CATEGORIA
# =====================================================

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

            value=produto["nome"]

        )



    col1,col2 = st.columns(2)



    with col1:


        preco = st.number_input(

            "Preço (R$)",

            min_value=0.0,

            value=float(
                produto["preco"]
            ),

            step=1.0

        )



    with col2:


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


    if nome.strip() == "":


        st.error(

            "Informe o nome do produto."

        )


    else:


        try:



            atualizar_produto(

                produto_id,

                categoria["id"],

                nome.strip(),

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
