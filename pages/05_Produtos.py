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
# TÍTULO
# =====================================================

st.title(
    "🛒 Cadastro de Produtos"
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


        categoria = st.selectbox(

            "Categoria",

            categorias,

            format_func=lambda c: c["nome"]

        )


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

            "💾 Cadastrar Produto",

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
                    "Produto cadastrado com sucesso!"
                )


                st.rerun()



            except Exception as erro:


                st.error(
                    f"Erro ao cadastrar produto: {erro}"
                )


else:


    st.info(
        "Modo consulta. Apenas Administradores podem alterar produtos."
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
# ORGANIZA PRODUTOS POR CATEGORIA
# =====================================================

categorias_dict = {}


for categoria in categorias:

    categorias_dict[
        categoria["id"]
    ] = categoria["nome"]



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


    if nome_categoria not in produtos_por_categoria:


        produtos_por_categoria[
            nome_categoria
        ] = []



    produtos_por_categoria[
        nome_categoria
    ].append(produto)



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
# EXIBE PRODUTOS
# =====================================================

for nome_categoria in ordem_categorias:


    if nome_categoria not in produtos_por_categoria:

        continue



    st.subheader(
        f"📦 {nome_categoria}"
    )



    lista = produtos_por_categoria[
        nome_categoria
    ]



    if len(lista) == 0:


        st.info(
            "Nenhum produto cadastrado."
        )

        continue



    for produto in lista:


        ativo = produto.get(
            "ativo",
            True
        )



        with st.container(border=True):


            if usuario["perfil"] == "Administrador":


                col1, col2, col3, col4, col5, col6 = st.columns(

                    [5,2,2,1,1,1]

                )


            else:


                col1, col2, col3 = st.columns(

                    [5,2,2]

                )



            # ==========================================
            # Nome
            # ==========================================

            with col1:


                st.write(
                    f"**{produto['nome']}**"
                )



            # ==========================================
            # Preço
            # ==========================================

            with col2:


                st.write(

                    f"R$ {float(produto['preco']):.2f}"

                )



            # ==========================================
            # Status
            # ==========================================

            with col3:


                if ativo:


                    st.success(
                        "Ativo"
                    )


                else:


                    st.error(
                        "Inativo"
                    )



            # ==========================================
            # AÇÕES ADMIN
            # ==========================================

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

                            "Produto excluído com sucesso!"

                        )


                        st.rerun()



    st.divider()
