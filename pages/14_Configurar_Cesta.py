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
    "Configure os produtos base e limites de escolha da cesta."
)


st.divider()




# =====================================================
# CARREGAMENTO
# =====================================================

try:


    cestas = listar_cestas()

    produtos = listar_produtos()

    categorias = listar_categorias()



    categorias_dict = {

        categoria["id"]:
            categoria["nome"]

        for categoria in categorias

    }



    # Remove adicionais
    produtos = [

        produto

        for produto in produtos

        if categorias_dict.get(
            produto["categoria_id"]
        )
        != "Adicionais"

    ]



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
        "Nenhum produto disponível."
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
# PRODUTOS CONFIGURADOS
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
# PRODUTOS POR CATEGORIA
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
# CATEGORIAS COM LIMITE
# =====================================================

categorias_com_limite = [

    "Pães",

    "Bebidas",

    "Espalháveis"

]





# =====================================================
# PRODUTOS DISPONÍVEIS
# =====================================================

st.subheader(
    "📦 Produtos disponíveis"
)



st.info(
"""
Selecione os produtos que fazem parte desta cesta.

Regras:

🍞 Pães  
🥤 Bebidas  
🍓 Espalháveis  

Essas categorias possuem limite de escolha.

Exemplo:

- Escolher 1 pão
- Escolher até 2 bebidas
- Escolher até 2 espalháveis


🎀 Adicionais

São disponibilizados automaticamente para todas as cestas
e não precisam ser configurados aqui.
"""
)



configuracoes = []



ordem_categorias = [

    "Pães",

    "Bebidas",

    "Espalháveis"

]



for categoria in produtos_por_categoria:


    if categoria not in ordem_categorias:

        ordem_categorias.append(categoria)




ordem = 1




# =====================================================
# EXIBIÇÃO
# =====================================================

for categoria_nome in ordem_categorias:


    if categoria_nome not in produtos_por_categoria:

        continue



    lista_produtos = produtos_por_categoria[categoria_nome]



    with st.container(border=True):


        st.markdown(
            f"### 📦 {categoria_nome}"
        )



        if categoria_nome in categorias_com_limite:


            col1, col2 = st.columns(2)


            with col1:

                minimo = st.number_input(

                    "Mínimo de escolhas",

                    min_value=0,

                    max_value=20,

                    value=1,

                    key=f"min_{categoria_nome}"

                )



            with col2:

                maximo = st.number_input(

                    "Máximo de escolhas",

                    min_value=1,

                    max_value=20,

                    value=1,

                    key=f"max_{categoria_nome}"

                )



        else:


            minimo = 0

            maximo = 99




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



                escolhido = st.checkbox(

                    produto["nome"],

                    value=marcado,

                    key=f"produto_{produto['id']}"

                )



                if escolhido:


                    selecionados.append(

                        produto["id"]

                    )




        if selecionados:


            configuracoes.append({

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
# RESUMO
# =====================================================

st.divider()


st.subheader(
    "📋 Resumo da configuração"
)



if configuracoes:


    for item in configuracoes:


        with st.container(border=True):


            st.markdown(
                f"### {item['categoria']}"
            )


            st.write(
                f"Produtos selecionados: {len(item['produtos'])}"
            )


            st.write(
                f"Escolha do cliente: "
                f"{item['min_escolhas']} até "
                f"{item['max_escolhas']}"
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
            "Configuração salva com sucesso!"
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
