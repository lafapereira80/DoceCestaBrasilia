import streamlit as st


from services.produto_service import (
    listar_produtos,
    listar_categorias
)


from services.cesta_produto_service import (
    listar_produtos_da_cesta,
    salvar_produtos_da_cesta
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

    page_title="Produtos da Cesta",

    page_icon="📦",

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

font-size:17px !important;

margin-top:8px;

margin-bottom:5px;

}


p, div, span {

font-size:13px;

}


label {

font-size:13px !important;

}


.stCheckbox {

margin-bottom:-8px;

}


.stButton button {

height:34px;

font-size:13px;

padding:4px 10px;

}


.block-container {

padding-top:1rem;

padding-bottom:1rem;

}


hr {

margin-top:8px;

margin-bottom:8px;

}


</style>
""",
unsafe_allow_html=True
)



# =====================================================
# VERIFICA CESTA SELECIONADA
# =====================================================

if "cesta_produtos" not in st.session_state:


    st.error(
        "Nenhuma cesta selecionada."
    )


    if st.button(
        "⬅ Voltar"
    ):


        st.switch_page(
            "pages/04_Cestas.py"
        )


    st.stop()



cesta_id = st.session_state["cesta_produtos"]



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "📦 Produtos da Cesta"
)


st.caption(
    "Selecione os produtos que fazem parte desta cesta."
)


st.divider()



# =====================================================
# CARREGA DADOS
# =====================================================

try:


    categorias = listar_categorias()


    produtos = listar_produtos()


    produtos_da_cesta = listar_produtos_da_cesta(

        cesta_id

    )


except Exception as erro:


    st.error(

        f"Erro ao carregar dados: {erro}"

    )


    st.stop()



# =====================================================
# ORGANIZA CATEGORIAS DINAMICAMENTE
# =====================================================

categorias_dict = {


    categoria["id"]: categoria["nome"]


    for categoria in categorias

}



produtos_por_categoria = {}



for categoria in categorias:


    produtos_por_categoria[

        categoria["nome"]

    ] = []



for produto in produtos:


    # ---------------------------------------------
    # Ignora produtos inativos
    # ---------------------------------------------

    if (

        "ativo" in produto

        and not produto["ativo"]

    ):

        continue



    nome_categoria = categorias_dict.get(

        produto.get("categoria_id"),

        "Sem Categoria"

    )



    produtos_por_categoria.setdefault(

        nome_categoria,

        []

    ).append(

        produto

    )



# =====================================================
# REMOVE CATEGORIAS SEM PRODUTOS
# =====================================================

produtos_por_categoria = {


    categoria: lista


    for categoria, lista in produtos_por_categoria.items()


    if lista

}



# =====================================================
# ORDENAÇÃO DINÂMICA
# =====================================================

categorias_ordenadas = sorted(

    produtos_por_categoria.keys(),

    key=lambda x: x.lower()

)
# =====================================================
# PRODUTOS VINCULADOS À CESTA
# =====================================================

produtos_marcados = [


    item["produto_id"]


    for item in produtos_da_cesta

]



# =====================================================
# SELEÇÃO DINÂMICA DOS PRODUTOS
# =====================================================

selecionados = []



for categoria in categorias_ordenadas:



    st.subheader(

        f"📦 {categoria}"

    )



    produtos_lista = produtos_por_categoria[

        categoria

    ]



    col1, col2 = st.columns(2)



    for index, produto in enumerate(produtos_lista):


        marcado = produto["id"] in produtos_marcados



        with col1 if index % 2 == 0 else col2:



            escolhido = st.checkbox(

                produto["nome"],

                value=marcado,

                key=f"produto_{produto['id']}"

            )



            if escolhido:


                selecionados.append(

                    produto["id"]

                )



    st.write("")





# =====================================================
# BOTÕES
# =====================================================

st.divider()



col1, col2 = st.columns(2)



with col1:



    if st.button(

        "💾 Salvar Produtos",

        use_container_width=True

    ):


        try:



            salvar_produtos_da_cesta(

                cesta_id,

                selecionados

            )



            st.success(

                "Produtos da cesta atualizados!"

            )



            st.rerun()



        except Exception as erro:



            st.error(

                f"Erro ao salvar: {erro}"

            )





with col2:



    if st.button(

        "⬅ Voltar",

        use_container_width=True

    ):



        st.session_state.pop(

            "cesta_produtos",

            None

        )



        st.switch_page(

            "pages/04_Cestas.py"

        )
