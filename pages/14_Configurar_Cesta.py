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
    "Configure os produtos disponíveis e as regras de escolha do cliente."
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



if not produtos:


    st.warning(

        "Nenhum produto cadastrado."

    )

    st.stop()



# =====================================================
# ESCOLHA DA CESTA
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
# PRODUTOS JÁ VINCULADOS
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
# MAPA DE CATEGORIAS
# =====================================================

categorias_dict = {


    categoria["id"]:

        categoria["nome"]


    for categoria in categorias

}



# =====================================================
# ORGANIZA PRODUTOS POR CATEGORIA
# =====================================================

produtos_por_categoria = {}



for produto in produtos:


    categoria_nome = categorias_dict.get(

        produto["categoria_id"],

        "Sem Categoria"

    )


    if categoria_nome not in produtos_por_categoria:


        produtos_por_categoria[categoria_nome] = []



    produtos_por_categoria[categoria_nome].append(

        produto

    )



# =====================================================
# CATEGORIAS COM LIMITE DE ESCOLHA
# =====================================================

categorias_com_limite = [

    "Pães",

    "Bebidas",

    "Espalháveis"

]


# =====================================================
# CONFIGURAÇÃO DOS PRODUTOS
# =====================================================


st.subheader(
    "📦 Produtos disponíveis na cesta"
)



st.info(
    """
Selecione os produtos que farão parte da cesta.

Para:
🍞 Pães  
🥤 Bebidas  
🍓 Espalháveis  

será possível definir quantidades de escolha do cliente.

Para:
🎀 Adicionais

o cliente poderá escolher livremente.
"""
)



configuracoes = []



ordem_categorias = [

    "Pães",

    "Bebidas",

    "Espalháveis",

    "Adicionais"

]



# adiciona outras categorias se existirem

for categoria in produtos_por_categoria:


    if categoria not in ordem_categorias:


        ordem_categorias.append(

            categoria

        )



ordem = 1



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



        # =================================================
        # REGRA DE ESCOLHA
        # =================================================


        if categoria_nome in categorias_com_limite:



            col1, col2 = st.columns(2)



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



        else:



            # Adicionais não possuem limite


            minimo = 0


            maximo = 99



            if categoria_nome == "Adicionais":


                st.info(

                    "Cliente poderá escolher livremente os adicionais."

                )



        st.divider()



        produtos_selecionados = []



        for produto in lista_produtos:



            marcado = produto["id"] in produtos_marcados



            selecionado = st.checkbox(

                produto["nome"],

                value=marcado,

                key=f"{categoria_nome}_{produto['id']}"

            )



            if selecionado:


                produtos_selecionados.append(

                    produto["id"]

                )



        # =================================================
        # MONTA CONFIGURAÇÃO
        # =================================================


        if produtos_selecionados:


            for produto_id in produtos_selecionados:


                configuracoes.append({


                    "cesta_id":

                        cesta_id,


                    "produto_id":

                        produto_id,


                    "categoria":

                        categoria_nome,


                    "min_escolhas":

                        minimo,


                    "max_escolhas":

                        maximo,


                    "ordem":

                        ordem

                })


                ordem += 1



    st.divider()


# =====================================================
# RESUMO DA CONFIGURAÇÃO
# =====================================================


st.divider()



st.subheader(
    "📋 Resumo da configuração"
)



if configuracoes:



    resumo = {}



    for item in configuracoes:



        categoria = item["categoria"]



        if categoria not in resumo:


            resumo[categoria] = {

                "quantidade": 0,

                "min": item["min_escolhas"],

                "max": item["max_escolhas"]

            }



        resumo[categoria]["quantidade"] += 1





    for categoria, dados in resumo.items():


        with st.container(border=True):


            st.write(

                f"**{categoria}**"

            )


            st.write(

                f"Produtos selecionados: {dados['quantidade']}"

            )



            if categoria in categorias_com_limite:


                st.write(

                    f"Escolha do cliente: "
                    f"{dados['min']} até {dados['max']}"

                )


            else:


                st.write(

                    "Escolha livre"

                )



else:



    st.info(

        "Nenhum produto selecionado para esta cesta."

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
# SALVAR
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
