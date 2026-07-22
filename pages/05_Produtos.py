import streamlit as st


from services.produto_service import (
    listar_produtos,
    cadastrar_produto,
    excluir_produto,
    listar_categorias,
    alterar_status_produto
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
# CSS
# =====================================================

st.markdown(
"""
<style>

.block-container{
    padding-top:1rem;
}


h1{
    font-size:26px !important;
}


h2{
    font-size:18px !important;
}


p, div, span{
    font-size:13px;
}


.stButton button{
    height:32px;
    font-size:13px;
    border-radius:8px;
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
    "Gerenciamento de produtos por categoria dinâmica."
)



st.divider()



# =====================================================
# CARREGAR CATEGORIAS
# =====================================================

try:


    categorias = listar_categorias()



except Exception as erro:


    st.error(
        f"Erro ao carregar categorias: {erro}"
    )


    categorias = []



# =====================================================
# CADASTRO DE PRODUTO
# =====================================================

if usuario["perfil"] == "Administrador":


    st.subheader(
        "➕ Novo Produto"
    )



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

            format_func=lambda x: x["nome"]

        )


    else:


        categoria = None


        st.warning(

            "Nenhuma categoria cadastrada."

        )



    # =================================================
    # REGRA DINÂMICA DE PREÇO
    #
    # Categoria define se possui preço
    # =================================================


    if categoria:


        categoria_possui_preco = categoria.get(

            "possui_preco",

            False

        )


    else:


        categoria_possui_preco = False





    if categoria_possui_preco:



        tipo_preco = st.radio(

            "Tipo de preço",

            [

                "Preço definido",

                "Preço sob consulta"

            ],

            horizontal=True

        )



        if tipo_preco == "Preço sob consulta":



            preco = None



            st.info(

                "O valor será definido no fechamento do pedido."

            )



        else:



            preco = st.number_input(

                "Preço (R$)",

                min_value=0.0,

                value=0.0,

                step=0.50,

                format="%.2f"

            )



    else:



        tipo_preco = "Incluso na cesta"


        preco = None



        st.info(

            "Este produto será incluso automaticamente na composição da cesta."

        )





    ativo = st.checkbox(

        "Produto ativo",

        value=True

    )





    salvar = st.button(

        "💾 Cadastrar Produto",

        use_container_width=True

    )





else:


    salvar = False


    st.info(

        "Modo consulta. Apenas Administradores podem cadastrar produtos."

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
    # VALIDA PREÇO
    # SOMENTE CATEGORIAS COM PREÇO
    # =================================================


    if (

        categoria.get("possui_preco")

        and

        tipo_preco == "Preço definido"

        and

        preco <= 0

    ):


        st.error(

            "Informe o valor do produto."

        )


        st.stop()





    try:



        cadastrar_produto(

            categoria_id=categoria["id"],

            nome=nome.strip(),

            descricao=descricao.strip(),

            preco=preco,

            ativo=ativo,

            tipo_preco=tipo_preco

        )



        st.success(

            "Produto cadastrado com sucesso!"

        )


        st.rerun()





    except Exception as erro:


        st.error(

            f"Erro ao cadastrar produto: {erro}"

        )
        # =====================================================
# FUNÇÃO EXIBIR PRODUTO
# =====================================================

def exibir_produto(
    produto,
    categoria
):


    with st.container(border=True):


        col1, col2, col3, col4 = st.columns(
            [5, 2, 1.2, 2]
        )



        # =============================================
        # NOME / DESCRIÇÃO
        # =============================================

        with col1:


            st.write(

                f"**{produto.get('nome','-')}**"

            )



            if produto.get("descricao"):


                st.caption(

                    produto["descricao"]

                )





        # =============================================
        # PREÇO
        # REGRA DINÂMICA
        # =============================================

        with col2:


            possui_preco = categoria.get(

                "possui_preco",

                False

            )



            if possui_preco:



                tipo = str(

                    produto.get(

                        "tipo_preco",

                        "Preço definido"

                    )

                ).strip()



                if tipo.lower() == "preço sob consulta":



                    st.info(

                        "Sob consulta"

                    )



                else:



                    valor = produto.get(

                        "preco"

                    )



                    if valor is not None:



                        valor_formatado = (

                            f"R$ {float(valor):,.2f}"

                            .replace(",", "X")

                            .replace(".", ",")

                            .replace("X",".")

                        )



                        st.write(

                            valor_formatado

                        )



                    else:



                        st.info(

                            "Sob consulta"

                        )



            else:



                st.success(

                    "Incluso"

                )





        # =============================================
        # STATUS
        # =============================================

        with col3:


            if produto.get(

                "ativo",

                True

            ):


                st.success(

                    "🟢"

                )


            else:


                st.error(

                    "🔴"

                )





        # =============================================
        # AÇÕES
        # =============================================

        with col4:



            b1,b2,b3 = st.columns(3)



            with b1:


                editar = st.button(

                    "✏️",

                    key=f"editar_{produto['id']}",

                    help="Editar produto"

                )



            with b2:


                status = st.button(

                    "🔴"

                    if produto.get(

                        "ativo",

                        True

                    )

                    else

                    "🟢",

                    key=f"status_{produto['id']}",

                    help="Alterar status"

                )



            with b3:


                excluir = st.button(

                    "🗑️",

                    key=f"excluir_{produto['id']}",

                    help="Excluir produto"

                )




    return editar, status, excluir






# =====================================================
# LISTAGEM DOS PRODUTOS
# =====================================================


st.divider()



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





if not produtos:


    st.info(

        "Nenhum produto cadastrado."

    )


    st.stop()





# =====================================================
# ORGANIZA CATEGORIAS DINAMICAMENTE
# =====================================================

categorias_dict = {


    categoria["id"]:

        categoria

    for categoria in categorias

}






produtos_agrupados = {}




for produto in produtos:



    categoria_id = produto.get(

        "categoria_id"

    )



    categoria = categorias_dict.get(

        categoria_id

    )



    if categoria:



        nome_categoria = categoria.get(

            "nome",

            "Sem Categoria"

        )


    else:


        nome_categoria = "Sem Categoria"



    if nome_categoria not in produtos_agrupados:



        produtos_agrupados[nome_categoria] = {


            "categoria": categoria,

            "produtos": []

        }



    produtos_agrupados[nome_categoria]["produtos"].append(

        produto

    )





# =====================================================
# ORDENA PELA ORDEM DA CATEGORIA
# =====================================================


categorias_ordenadas = sorted(

    produtos_agrupados.items(),

    key=lambda x:

        x[1]["categoria"].get(

            "ordem",

            999

        )

        if x[1]["categoria"]

        else 999

)





# =====================================================
# EXIBIÇÃO
# =====================================================


for categoria_nome, dados in categorias_ordenadas:



    categoria = dados["categoria"]



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
        ">
        📂 {categoria_nome}
        </div>
        """,

        unsafe_allow_html=True

    )





    for produto in dados["produtos"]:



        editar, status, excluir = exibir_produto(

            produto,

            categoria

        )



        # =============================================
        # EDITAR
        # =============================================


        if editar:


            st.session_state[

                "produto_editar"

            ] = produto["id"]



            st.switch_page(

                "pages/10_Editar_Produto.py"

            )



        # =============================================
        # ALTERAR STATUS
        # =============================================


        if status:



            novo_status = not produto.get(

                "ativo",

                True

            )



            try:



                alterar_status_produto(

                    produto["id"],

                    novo_status

                )



                st.rerun()



            except Exception as erro:



                st.error(

                    f"Erro ao alterar status: {erro}"

                )



        # =============================================
        # EXCLUIR
        # =============================================


        if excluir:



            try:



                excluir_produto(

                    produto["id"]

                )



                st.success(

                    "Produto excluído com sucesso."

                )


                st.rerun()



            except Exception as erro:



                st.error(

                    f"Erro ao excluir produto: {erro}"

                )



        st.write("")
        # =====================================================
# RODAPÉ
# =====================================================

st.divider()



st.caption(

    "🛒 Cadastro de produtos - Doce Cesta Brasília"

)
