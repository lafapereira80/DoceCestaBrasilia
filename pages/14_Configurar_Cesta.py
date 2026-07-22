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
# CONFIGURAÇÃO
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

h3{
    font-size:17px !important;
}

.stButton button{
    border-radius:10px;
}

[data-testid="stVerticalBlockBorderWrapper"]{
    padding:15px;
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
    "Configure os produtos e limites de escolha para cada cesta."
)


st.divider()



# =====================================================
# CARREGAMENTO DOS DADOS
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



if not categorias:


    st.warning(
        "Nenhuma categoria cadastrada."
    )

    st.stop()



# =====================================================
# MAPA DE CATEGORIAS
# =====================================================

categorias_dict = {


    categoria["id"]:
        categoria


    for categoria in categorias

}



# =====================================================
# REMOVE CATEGORIA ADICIONAIS
#
# Adicionais são gerais para todas as cestas
# e aparecem automaticamente no pedido.
#
# =====================================================

produtos_configuraveis = []



for produto in produtos:


    categoria = categorias_dict.get(

        produto["categoria_id"]

    )


    if not categoria:


        continue



    if categoria["nome"].strip().lower() == "adicionais":


        continue



    produtos_configuraveis.append(

        produto

    )



if not produtos_configuraveis:


    st.warning(
        "Nenhum produto disponível para configuração."
    )

    st.stop()



# =====================================================
# SELEÇÃO DA CESTA
# =====================================================

cesta = st.selectbox(

    "🎁 Selecione a cesta",

    cestas,

    format_func=lambda x:

        x["nome"]

)



if not cesta:


    st.stop()



cesta_id = cesta["id"]




st.divider()

# =====================================================
# PRODUTOS JÁ CONFIGURADOS NA CESTA
# =====================================================

try:


    produtos_configurados = listar_produtos_da_cesta(

        cesta_id

    )


except Exception:


    produtos_configurados = []



produtos_marcados = [

    item["produto_id"]

    for item in produtos_configurados

]




# =====================================================
# AGRUPAR PRODUTOS POR CATEGORIA
# =====================================================

produtos_por_categoria = {}



for produto in produtos_configuraveis:


    categoria = categorias_dict.get(

        produto["categoria_id"]

    )



    if not categoria:


        continue



    categoria_id = categoria["id"]


    categoria_nome = categoria["nome"]



    if categoria_id not in produtos_por_categoria:


        produtos_por_categoria[categoria_id] = {


            "nome":

                categoria_nome,


            "produtos":

                []

        }



    produtos_por_categoria[categoria_id]["produtos"].append(

        produto

    )





if not produtos_por_categoria:


    st.warning(

        "Nenhuma categoria possui produtos disponíveis."

    )

    st.stop()





# =====================================================
# CONFIGURAÇÃO DAS CATEGORIAS
# =====================================================

st.subheader(
    "📦 Produtos disponíveis"
)



st.info(
"""
Selecione quais produtos fazem parte desta cesta.

A quantidade mínima e máxima será definida
exclusivamente para esta cesta.

Exemplo:

Cesta Romântica:
Bebidas → escolher de 1 até 1

Cesta Luxo:
Bebidas → escolher de 1 até 3
"""
)



configuracoes = []



ordem = 1




# =====================================================
# EXIBIÇÃO DINÂMICA DAS CATEGORIAS
# =====================================================

for categoria_id, dados_categoria in produtos_por_categoria.items():


    categoria_nome = dados_categoria["nome"]


    lista_produtos = dados_categoria["produtos"]



    with st.container(border=True):


        st.markdown(

            f"### 📦 {categoria_nome}"

        )



        col1, col2 = st.columns(2)



        with col1:


            minimo = st.number_input(

                "Mínimo de escolhas",

                min_value=0,

                max_value=50,

                value=1,

                key=f"min_{cesta_id}_{categoria_id}"

            )



        with col2:


            maximo = st.number_input(

                "Máximo de escolhas",

                min_value=1,

                max_value=50,

                value=1,

                key=f"max_{cesta_id}_{categoria_id}"

            )



        st.divider()



        selecionados = []



        col1, col2 = st.columns(2)



        for indice, produto in enumerate(lista_produtos):


            coluna = (

                col1

                if indice % 2 == 0

                else col2

            )



            with coluna:


                marcado = produto["id"] in produtos_marcados



                selecionado = st.checkbox(

                    produto["nome"],

                    value=marcado,

                    key=f"produto_{cesta_id}_{produto['id']}"

                )



                if selecionado:


                    selecionados.append(

                        produto["id"]

                    )





        if selecionados:


            # evita limite inválido

            if maximo > len(selecionados):


                maximo = len(selecionados)



            if minimo > maximo:


                minimo = maximo



            configuracoes.append({

                "categoria_id":

                    categoria_id,


                "categoria":

                    categoria_nome,


                "produtos":

                    selecionados,


                "min_escolhas":

                    minimo,


                "max_escolhas":

                    maximo,


                "ordem":

                    ordem

            })



            ordem += 1

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


            st.markdown(

                f"### 📦 {item['categoria']}"

            )


            st.write(

                f"Produtos selecionados: "
                f"{len(item['produtos'])}"

            )


            st.write(

                f"Cliente poderá escolher: "
                f"{item['min_escolhas']} até "
                f"{item['max_escolhas']} itens"

            )


else:


    st.info(

        "Nenhum produto selecionado."

    )





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
# SALVAR CONFIGURAÇÃO
# =====================================================

if salvar:



    if not configuracoes:


        st.error(

            "Selecione pelo menos um produto."

        )

        st.stop()



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
# RODAPÉ
# =====================================================

st.divider()


st.caption(

    "Doce Cesta Brasília - Configuração de Cestas"

)

