import streamlit as st


from services.cesta_service import (
    listar_cestas
)


from services.produto_service import (
    listar_produtos,
    listar_categorias
)


from services.cesta_produto_service import (
    listar_produtos_da_cesta
)


from services.configuracao_cesta_service import (
    salvar_configuracao_cesta
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

    page_title="Configurar Cesta",

    page_icon="⚙️",

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

font-size:26px !important;

}


h2{

font-size:20px !important;

}


.stButton button{

border-radius:10px;

}


</style>
""",
unsafe_allow_html=True
)



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "⚙️ Configurar Cesta"
)


st.caption(
    "Defina quais produtos estarão disponíveis e quantas opções o cliente poderá escolher."
)


st.divider()



# =====================================================
# CARREGAMENTO
# =====================================================

try:


    cestas = listar_cestas()

    produtos = listar_produtos()

    categorias = listar_categorias()



except Exception as erro:


    st.error(
        f"Erro ao carregar dados: {erro}"
    )

    st.stop()



if not cestas:


    st.warning(
        "Nenhuma cesta cadastrada."
    )

    st.stop()



if not produtos:


    st.warning(
        "Nenhum produto cadastrado."
    )

    st.stop()



# =====================================================
# ESCOLHA DA CESTA
# =====================================================


cesta = st.selectbox(

    "🎁 Escolha a cesta para configurar",

    cestas,

    format_func=lambda x:
        x["nome"]

)



if not cesta:


    st.stop()



cesta_id = cesta["id"]



st.divider()

# =====================================================
# PRODUTOS JÁ CONFIGURADOS
# =====================================================

try:

    produtos_vinculados = listar_produtos_da_cesta(
        cesta_id
    )


except Exception:

    produtos_vinculados = []



produtos_marcados = [

    item["produto_id"]

    for item in produtos_vinculados

]



# =====================================================
# ORGANIZA PRODUTOS POR CATEGORIA
# =====================================================


categorias_dict = {


    categoria["id"]:

        categoria["nome"]


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
# CONFIGURAÇÃO
# =====================================================


st.subheader(
    "📦 Produtos disponíveis"
)


st.info(
    "Selecione os produtos que farão parte desta cesta e defina quantas opções o cliente poderá escolher."
)



configuracoes = []



ordem_categorias = [


    "Pães",

    "Bebidas",

    "Espalháveis",

    "Adicionais"


]



# adiciona categorias extras caso existam

for categoria in produtos_por_categoria:


    if categoria not in ordem_categorias:

        ordem_categorias.append(
            categoria
        )



for categoria_nome in ordem_categorias:



    if categoria_nome not in produtos_por_categoria:

        continue



    lista_produtos = produtos_por_categoria[
        categoria_nome
    ]



    if not lista_produtos:

        continue



    with st.container(border=True):


        st.markdown(
            f"### 📦 {categoria_nome}"
        )



        col1,col2 = st.columns(2)



        with col1:


            minimo = st.number_input(

                "Mínimo de escolhas",

                min_value=0,

                value=1,

                step=1,

                key=f"min_{categoria_nome}"

            )



        with col2:


            maximo = st.number_input(

                "Máximo de escolhas",

                min_value=1,

                value=1,

                step=1,

                key=f"max_{categoria_nome}"

            )



        if maximo < minimo:


            st.warning(

                "O máximo não pode ser menor que o mínimo."

            )



        selecionados_categoria = []



        for produto in lista_produtos:



            marcado = produto["id"] in produtos_marcados



            escolhido = st.checkbox(

                produto["nome"],

                value=marcado,

                key=f"{categoria_nome}_{produto['id']}"

            )



            if escolhido:


                selecionados_categoria.append(

                    produto["id"]

                )



        if selecionados_categoria:



            configuracoes.append({


                "categoria": categoria_nome,


                "min_escolhas": minimo,


                "max_escolhas": maximo,


                "produtos": selecionados_categoria


            })



    st.divider()

# =====================================================
# CONFIGURAÇÃO DE ESCOLHAS POR CATEGORIA
# =====================================================


st.divider()


st.subheader(
    "⚙️ Limites de escolha por categoria"
)



st.info(
    "Defina quantos itens o cliente poderá escolher dentro de cada categoria."
)



configuracoes = []



for categoria_nome, produtos_categoria in produtos_por_categoria.items():


    with st.container(border=True):


        st.markdown(
            f"### 📦 {categoria_nome}"
        )


        st.write(
            "Produtos disponíveis:"
        )


        lista_produtos = []


        for produto in produtos_categoria:


            lista_produtos.append(
                produto["id"]
            )


            st.write(
                f"• {produto['nome']}"
            )



        col1, col2 = st.columns(2)



        with col1:


            min_escolhas = st.number_input(

                "Mínimo de escolhas",

                min_value=0,

                value=1,

                step=1,

                key=f"min_{categoria_nome}"

            )



        with col2:


            max_escolhas = st.number_input(

                "Máximo de escolhas",

                min_value=1,

                value=1,

                step=1,

                key=f"max_{categoria_nome}"

            )



        if max_escolhas < min_escolhas:


            st.warning(

                "O máximo não pode ser menor que o mínimo."

            )



        configuracoes.append({

            "categoria":

                categoria_nome,


            "produtos":

                lista_produtos,


            "min_escolhas":

                min_escolhas,


            "max_escolhas":

                max_escolhas

        })



# =====================================================
# BOTÕES
# =====================================================


st.divider()



col1, col2 = st.columns(2)



with col1:


    salvar = st.button(

        "💾 Salvar Configuração",

        use_container_width=True

    )



with col2:


    voltar = st.button(

        "⬅ Voltar",

        use_container_width=True

    )



# =====================================================
# VOLTAR
# =====================================================


if voltar:


    st.session_state.pop(

        "cesta_configurar",

        None

    )


    st.switch_page(

        "pages/04_Cestas.py"

    )



# =====================================================
# SALVAR
# =====================================================


if salvar:


    try:


        salvar_configuracao_cesta(

            cesta_id,

            configuracoes

        )


        st.success(

            "Configuração da cesta salva com sucesso!"

        )


        st.session_state.pop(

            "cesta_configurar",

            None

        )


        st.switch_page(

            "pages/04_Cestas.py"

        )



    except Exception as erro:


        st.error(

            f"Erro ao salvar configuração: {erro}"

        )
        # =====================================================
# RESUMO DA CONFIGURAÇÃO
# =====================================================


st.divider()



st.subheader(
    "📋 Resumo da configuração"
)



if configuracoes:


    for item in configuracoes:


        with st.container(border=True):


            st.write(
                f"**{item['categoria']}**"
            )


            st.write(

                f"Mínimo: {item['min_escolhas']} | "
                f"Máximo: {item['max_escolhas']}"

            )


            st.write(

                f"Produtos vinculados: {len(item['produtos'])}"

            )


else:


    st.info(

        "Nenhuma configuração criada."

    )



# =====================================================
# RODAPÉ
# =====================================================


st.divider()



st.caption(

    "Doce Cesta Brasília - Configuração de Cestas"

)



# =====================================================
# GARANTE LIMPEZA DE ESTADO
# =====================================================


if "limpar_configuracao" in st.session_state:


    del st.session_state["limpar_configuracao"]
