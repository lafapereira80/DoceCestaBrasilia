import streamlit as st


from services.produto_service import (

    listar_produtos,

    cadastrar_produto,

    excluir_produto,

    listar_categorias

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
# CSS
# =====================================================

st.markdown(
"""
<style>


.block-container{

    padding-top:1rem;

    padding-bottom:1rem;

}



h1{

    font-size:26px !important;

}



h2{

    font-size:20px !important;

}



h3{

    font-size:16px !important;

}



p, span, div, label{

    font-size:13px;

}



.stButton button{

    height:34px;

    font-size:13px;

    border-radius:8px;

}



input, textarea{

    font-size:13px !important;

}



[data-testid="stVerticalBlockBorderWrapper"]{

    padding:12px;

}



hr{

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


st.caption(

    "Gerenciamento de produtos por categoria"

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


    categorias = []





# =====================================================
# CADASTRO NOVO PRODUTO
# =====================================================

if usuario["perfil"] == "Administrador":



    st.subheader(

        "➕ Novo Produto"

    )



    with st.form(

        "novo_produto"

    ):



        nome = st.text_input(

            "Nome do Produto"

        )



        descricao = st.text_area(

            "Descrição",

            height=70,

            placeholder="Descrição do produto..."

        )



        if categorias:



            categoria = st.selectbox(

                "Categoria",

                categorias,

                format_func=lambda c:

                    c["nome"]

            )


        else:


            categoria = None


            st.warning(

                "Nenhuma categoria cadastrada."

            )



        # =================================================
        # PREÇO
        # =================================================


        preco_consulta = False



        if categoria:



            if categoria["nome"].lower().strip() == "adicionais":



                preco_consulta = st.checkbox(

                    "☐ Preço sob consulta",

                    help="Somente para adicionais sem valor definido."

                )



        if preco_consulta:



            preco = None



            st.info(

                "Produto será salvo como: Preço sob consulta."

            )



        else:



            preco = st.number_input(

                "Preço (R$)",

                min_value=0.0,

                value=0.0,

                step=0.50,

                format="%.2f"

            )



        ativo = st.checkbox(

            "Produto ativo",

            value=True

        )



        salvar = st.form_submit_button(

            "💾 Cadastrar Produto",

            use_container_width=True

        )

# =====================================================
# SALVAR PRODUTO
# =====================================================


if salvar:



    if not nome.strip():


        st.error(

            "Informe o nome do produto."

        )

        st.stop()





    if not categoria:


        st.error(

            "Selecione uma categoria."

        )

        st.stop()





    # =================================================
    # VALIDAÇÃO PREÇO SOB CONSULTA
    # =================================================


    if categoria["nome"].lower().strip() == "adicionais":



        if preco == 0:



            st.warning(

                "Informe um valor ou marque 'Preço sob consulta'."

            )

            st.stop()





    try:



        cadastrar_produto(



            categoria_id=categoria["id"],



            nome=nome.strip(),



            descricao=descricao.strip(),



            preco=preco,



            ativo=ativo



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

        "Modo consulta. Apenas Administradores podem cadastrar produtos."

    )





st.divider()





# =====================================================
# LISTAGEM DOS PRODUTOS
# =====================================================


st.subheader(

    "📋 Produtos Cadastrados"

)



try:


    produtos = listar_produtos()



except Exception as erro:


    st.error(

        f"Erro ao carregar produtos: {erro}"

    )


    produtos = []





# =====================================================
# AGRUPA PRODUTOS POR CATEGORIA
# =====================================================


produtos_agrupados = {}



for produto in produtos:



    categoria_produto = produto.get(

        "categorias"

    )



    if categoria_produto:



        nome_categoria = categoria_produto.get(

            "nome",

            "Sem Categoria"

        )



    else:



        nome_categoria = "Sem Categoria"




    if nome_categoria not in produtos_agrupados:



        produtos_agrupados[nome_categoria] = []



    produtos_agrupados[nome_categoria].append(

        produto

    )





# =====================================================
# EXIBIÇÃO AGRUPADA
# =====================================================


if not produtos:



    st.info(

        "Nenhum produto cadastrado."

    )

else:



    for categoria_nome, lista_produtos in produtos_agrupados.items():



        # =================================================
        # CABEÇALHO DA CATEGORIA
        # =================================================


        st.markdown(

            f"""
            <div style="
                background:#8B5A2B;
                color:white;
                padding:8px 12px;
                border-radius:10px;
                margin-top:15px;
                margin-bottom:10px;
                font-weight:bold;
                font-size:15px;
            ">
            📂 {categoria_nome}
            </div>
            """,

            unsafe_allow_html=True

        )



        for produto in lista_produtos:



            with st.container(

                border=True

            ):



                col1, col2, col3, col4 = st.columns(

                    [5,2,2,1]

                )



                # =========================================
                # NOME / DESCRIÇÃO
                # =========================================


                with col1:



                    st.write(

                        f"**{produto['nome']}**"

                    )



                    descricao = produto.get(

                        "descricao"

                    )



                    if descricao:



                        st.caption(

                            descricao

                        )





                # =========================================
                # PREÇO
                # =========================================


                with col2:



                    preco = produto.get(

                        "preco"

                    )



                    if preco is None:



                        st.warning(

                            "Sob consulta"

                        )



                    else:



                        try:



                            valor = float(

                                preco

                            )



                            valor_formatado = (

                                f"R$ {valor:,.2f}"

                                .replace(",", "X")

                                .replace(".", ",")

                                .replace("X",".")

                            )



                            st.write(

                                valor_formatado

                            )



                        except:



                            st.warning(

                                "Sob consulta"

                            )





                # =========================================
                # STATUS
                # =========================================


                with col3:



                    if produto.get(

                        "ativo",

                        True

                    ):



                        st.success(

                            "✓ Ativo"

                        )



                    else:



                        st.error(

                            "✕ Inativo"

                        )





                # =========================================
                # EXCLUIR
                # =========================================


                with col4:



                    if st.button(

                        "🗑️",

                        key=f"excluir_produto_{produto['id']}"

                    ):



                        try:



                            excluir_produto(

                                produto["id"]

                            )



                            st.success(

                                "Produto excluído."

                            )



                            st.rerun()



                        except Exception as erro:



                            st.error(

                                f"Erro ao excluir: {erro}"

                            )



            st.write("")

# =====================================================
# RODAPÉ DO MÓDULO
# =====================================================


st.divider()



st.caption(

    "🛒 Cadastro de produtos - Doce Cesta Brasília"

)
