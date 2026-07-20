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
    administrador
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

administrador()



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



produto_id = st.session_state[
    "produto_editar"
]



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


st.divider()



# =====================================================
# FORMULÁRIO
# =====================================================

indice_categoria = 0



for i, categoria in enumerate(categorias):


    if categoria["id"] == produto["categoria_id"]:


        indice_categoria = i

        break




with st.form(
    "form_editar_produto"
):


    categoria = st.selectbox(

        "Categoria",

        categorias,

        index=indice_categoria,

        format_func=lambda c: c["nome"]

    )



    nome = st.text_input(

        "Nome do Produto",

        value=produto["nome"]

    )



    preco = st.number_input(

        "Preço",

        min_value=0.0,

        value=float(
            produto["preco"]
        ),

        step=1.0

    )



    ativo = st.checkbox(

        "Produto ativo",

        value=produto["ativo"]

    )



    col1,col2 = st.columns(2)



    with col1:


        salvar = st.form_submit_button(

            "💾 Salvar Alterações",

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
