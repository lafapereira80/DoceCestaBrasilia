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
# CSS
# =====================================================

st.markdown(
"""
<style>

.block-container{

    padding-top:1rem;

}


h1{

    font-size:24px !important;

}


p,span,div,label{

    font-size:13px;

}


.stButton button{

    height:34px;

    border-radius:8px;

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


    if st.button(
        "⬅ Voltar"
    ):


        st.switch_page(
            "pages/05_Produtos.py"
        )


    st.stop()



produto_id = st.session_state["produto_editar"]



# =====================================================
# BUSCAR DADOS
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



if not produto:


    st.error(
        "Produto não encontrado."
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
# IDENTIFICA CATEGORIA ATUAL
# =====================================================

indice_categoria = 0


for i, categoria in enumerate(categorias):


    if categoria["id"] == produto["categoria_id"]:


        indice_categoria = i

        break
        # =====================================================
# FORMULÁRIO DE EDIÇÃO
# =====================================================


categoria = st.selectbox(

    "Categoria",

    categorias,

    index=indice_categoria,

    format_func=lambda c: c["nome"]

)



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



# =====================================================
# REGRA DE PREÇO
# SOMENTE ADICIONAIS POSSUEM VALOR
# =====================================================


categoria_nome = (

    categoria["nome"]

    .strip()

    .lower()

)



if categoria_nome == "adicionais":



    tipo_atual = produto.get(

        "tipo_preco",

        "Preço definido"

    )



    tipo_preco = st.radio(

        "Tipo de preço",

        [

            "Preço definido",

            "Preço sob consulta"

        ],

        index=(

            1

            if tipo_atual == "Preço sob consulta"

            else 0

        ),

        horizontal=True

    )



    if tipo_preco == "Preço sob consulta":



        preco = None



        st.info(

            "Produto sem valor definido. O preço será informado no pedido."

        )



    else:



        preco = st.number_input(

            "Preço (R$)",

            min_value=0.0,

            value=float(

                produto.get(

                    "preco",

                    0

                )

                or 0

            ),

            step=0.50,

            format="%.2f"

        )



else:



    tipo_preco = "Incluso na cesta"


    preco = None



    st.info(

        "Produto incluso na composição da cesta. Não possui preço individual."

    )




# =====================================================
# STATUS
# =====================================================


ativo = st.checkbox(

    "Produto ativo",

    value=produto.get(

        "ativo",

        True

    )

)



st.divider()



col1, col2 = st.columns(2)



with col1:


    salvar = st.button(

        "💾 Salvar alterações",

        use_container_width=True

    )



with col2:


    cancelar = st.button(

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
# SALVAR ALTERAÇÕES
# =====================================================

if salvar:



    if not nome.strip():


        st.error(

            "Informe o nome do produto."

        )

        st.stop()





    # =================================================
    # VALIDAÇÃO DE PREÇO
    # =================================================


    if (

        categoria_nome == "adicionais"

        and

        tipo_preco == "Preço definido"

        and

        preco <= 0

    ):


        st.error(

            "Informe o valor do adicional."

        )

        st.stop()





    try:



        atualizar_produto(


            produto_id,


            categoria["id"],


            nome.strip(),


            descricao.strip(),


            preco,


            ativo,


            tipo_preco


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
        # =====================================================
# RODAPÉ
# =====================================================

st.divider()


st.caption(

    "✏️ Edição de produtos - Doce Cesta Brasília"

)
