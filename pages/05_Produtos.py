import streamlit as st


from services.produto_service import (
    listar_categorias,
    listar_produtos,
    cadastrar_produto,
    excluir_produto,
    alterar_status
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

    page_title="Produtos",

    page_icon="🛒",

    layout="wide"

)



# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()



usuario = st.session_state.usuario



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

margin-top:8px;

margin-bottom:8px;

}


p, div, span {

font-size:13px;

}


.stCaption {

font-size:11px !important;

}


.stButton button {

height:32px;

padding:2px 8px;

font-size:12px;

}


[data-testid="stVerticalBlockBorderWrapper"] {

padding-top:8px;

padding-bottom:8px;

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
# TÍTULO
# =====================================================

st.title(
    "🛒 Produtos"
)


st.divider()



# =====================================================
# CARREGA CATEGORIAS
# =====================================================

try:


    categorias = listar_categorias()



except Exception as erro:


    st.error(

        f"Erro ao carregar categorias: {erro}"

    )


    st.stop()



if not categorias:


    st.warning(

        "Nenhuma categoria cadastrada."

    )


    st.stop()



# =====================================================
# NOVO PRODUTO
# =====================================================

if usuario["perfil"] == "Administrador":


    st.subheader(
        "➕ Novo Produto"
    )



    with st.form(
        "novo_produto"
    ):


        col1,col2 = st.columns(2)



        with col1:


            categoria = st.selectbox(

                "Categoria",

                categorias,

                format_func=lambda c:c["nome"]

            )



        with col2:


            nome = st.text_input(

                "Nome do Produto"

            )



        preco = st.number_input(

            "Preço (R$)",

            min_value=0.0,

            value=0.0,

            step=1.0

        )



        salvar = st.form_submit_button(

            "💾 Cadastrar",

            use_container_width=True

        )



    if salvar:


        if nome.strip() == "":


            st.error(

                "Informe o nome do produto."

            )


        else:


            try:


                cadastrar_produto(

                    categoria["id"],

                    nome.strip(),

                    preco

                )


                st.success(

                    "Produto cadastrado!"

                )


                st.rerun()



            except Exception as erro:


                st.error(

                    f"Erro ao cadastrar produto: {erro}"

                )


else:


    st.info(

        "Modo consulta. Apenas Administradores podem cadastrar produtos."

    )



st.divider()



# =====================================================
# CARREGA PRODUTOS
# =====================================================

try:


    produtos = listar_produtos()



except Exception as erro:


    st.error(

        f"Erro ao carregar produtos: {erro}"

    )


    st.stop()



# =====================================================
# ORGANIZA CATEGORIAS
# =====================================================

categorias_dict = {


    categoria["id"]:categoria["nome"]


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



ordem_categorias = [

    "Pães",

    "Bebidas",

    "Espalháveis",

    "Adicionais"

]



st.subheader(
    "📋 Produtos Cadastrados"
)



# =====================================================
# LISTAGEM
# =====================================================

for nome_categoria in ordem_categorias:


    lista = produtos_por_categoria.get(

        nome_categoria,

        []

    )



    if not lista:

        continue



    st.subheader(

        f"📦 {nome_categoria}"

    )



    for produto in lista:


        ativo = produto.get(

            "ativo",

            True

        )



        with st.container(
            border=True
        ):


            if usuario["perfil"] == "Administrador":


                col1,col2,col3,col4,col5,col6 = st.columns(

                    [5,2,1.5,0.6,0.6,0.6]

                )


            else:


                col1,col2,col3 = st.columns(

                    [5,2,1]

                )



            with col1:


                st.write(

                    f"**{produto['nome']}**"

                )



            with col2:


                st.write(

                    f"R$ {float(produto['preco']):.2f}"

                )



            with col3:


                if ativo:


                    st.success(

                        "✓ Ativo"

                    )


                else:


                    st.error(

                        "✕ Inativo"

                    )



            if usuario["perfil"] == "Administrador":



                with col4:


                    if st.button(

                        "✏️",

                        key=f"editar_{produto['id']}"

                    ):


                        st.session_state[

                            "produto_editar"

                        ] = produto["id"]



                        st.switch_page(

                            "pages/10_Editar_Produto.py"

                        )



                with col5:


                    if st.button(

                        "🔄",

                        key=f"status_{produto['id']}"

                    ):


                        alterar_status(

                            produto["id"],

                            not ativo

                        )


                        st.rerun()



                with col6:


                    if st.button(

                        "🗑️",

                        key=f"excluir_{produto['id']}"

                    ):


                        excluir_produto(

                            produto["id"]

                        )


                        st.success(

                            "Produto excluído!"

                        )


                        st.rerun()



    st.write("")
