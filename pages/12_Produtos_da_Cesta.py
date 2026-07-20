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
# ORGANIZA PRODUTOS POR CATEGORIA
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


    nome_categoria = categorias_dict.get(

        produto["categoria_id"],

        "Sem Categoria"

    )



    produtos_por_categoria.setdefault(

        nome_categoria,

        []

    ).append(produto)



# =====================================================
# PRODUTOS JÁ VINCULADOS
# =====================================================

produtos_marcados = [

    item["produto_id"]

    for item in produtos_da_cesta

]



# =====================================================
# CHECKBOXES
# =====================================================

selecionados = []



ordem = [

    "Pães",

    "Bebidas",

    "Espalháveis",

    "Adicionais"

]



for categoria in ordem:



    if categoria not in produtos_por_categoria:

        continue



    st.subheader(

        f"📦 {categoria}"

    )



    for produto in produtos_por_categoria[categoria]:


        marcado = produto["id"] in produtos_marcados



        escolhido = st.checkbox(

            produto["nome"],

            value=marcado,

            key=f"produto_{produto['id']}"

        )



        if escolhido:


            selecionados.append(

                produto["id"]

            )



    st.divider()



# =====================================================
# BOTÕES
# =====================================================

col1,col2 = st.columns(2)



with col1:


    if st.button(

        "💾 Salvar Produtos da Cesta",

        use_container_width=True

    ):


        try:


            salvar_produtos_da_cesta(

                cesta_id,

                selecionados

            )



            st.success(

                "Produtos da cesta atualizados com sucesso!"

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
