import streamlit as st
import pandas as pd


from config.supabase import supabase


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
    page_title="Financeiro",
    page_icon="💰",
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
    "💰 Financeiro"
)


st.divider()



# =====================================================
# BUSCAR PEDIDOS
# =====================================================

@st.cache_data(ttl=60)
def carregar_pedidos():


    resposta = (

        supabase

        .table("pedidos")

        .select("*")

        .execute()

    )


    return pd.DataFrame(
        resposta.data
    )



# =====================================================
# CARREGAMENTO
# =====================================================

try:


    df = carregar_pedidos()



except Exception as erro:


    st.error(
        f"Erro ao carregar pedidos: {erro}"
    )

    st.stop()



if df.empty:


    st.warning(
        "Nenhum pedido encontrado."
    )

    st.stop()



# =====================================================
# TRATAMENTO DOS DADOS
# =====================================================

df["created_at"] = pd.to_datetime(
    df["created_at"]
)



df["ano"] = (
    df["created_at"]
    .dt.year
)



df["mes"] = (
    df["created_at"]
    .dt.month
)



df["valor_total"] = pd.to_numeric(

    df["valor_total"],

    errors="coerce"

).fillna(0)



df["valor_frete"] = pd.to_numeric(

    df["valor_frete"],

    errors="coerce"

).fillna(0)




# =====================================================
# FILTROS
# =====================================================

st.subheader(
    "🔎 Filtros"
)



col1, col2 = st.columns(2)



with col1:


    anos = sorted(

        df["ano"]

        .unique(),

        reverse=True

    )


    ano_selecionado = st.selectbox(

        "Ano",

        ["Todos"] + list(anos)

    )



with col2:


    meses = {

        1:"Janeiro",

        2:"Fevereiro",

        3:"Março",

        4:"Abril",

        5:"Maio",

        6:"Junho",

        7:"Julho",

        8:"Agosto",

        9:"Setembro",

        10:"Outubro",

        11:"Novembro",

        12:"Dezembro"

    }



    mes_selecionado = st.selectbox(

        "Mês",

        ["Todos"] + list(meses.values())

    )



df_filtrado = df.copy()



if ano_selecionado != "Todos":


    df_filtrado = df_filtrado[

        df_filtrado["ano"]

        ==

        ano_selecionado

    ]



if mes_selecionado != "Todos":


    numero_mes = [

        chave

        for chave, valor in meses.items()

        if valor == mes_selecionado

    ][0]



    df_filtrado = df_filtrado[

        df_filtrado["mes"]

        ==

        numero_mes

    ]



st.divider()



# =====================================================
# RESUMO
# =====================================================

st.subheader(
    "📊 Resumo financeiro"
)



col1, col2, col3, col4 = st.columns(4)



with col1:


    faturamento = (

        df_filtrado["valor_total"]

        .sum()

    )


    st.metric(

        "Faturamento",

        f"R$ {faturamento:,.2f}"

    )



with col2:


    fretes = (

        df_filtrado["valor_frete"]

        .sum()

    )


    st.metric(

        "Fretes",

        f"R$ {fretes:,.2f}"

    )



with col3:


    pedidos = len(
        df_filtrado
    )


    st.metric(

        "Pedidos",

        pedidos

    )



with col4:


    ticket = (

        faturamento / pedidos

        if pedidos > 0

        else 0

    )


    st.metric(

        "Ticket médio",

        f"R$ {ticket:,.2f}"

    )



st.divider()



# =====================================================
# FATURAMENTO POR MÊS
# =====================================================

st.subheader(
    "📅 Faturamento mensal"
)



faturamento_mes = (

    df_filtrado

    .groupby(

        df_filtrado["created_at"]

        .dt.strftime("%m/%Y")

    )

    ["valor_total"]

    .sum()

    .reset_index()

)



faturamento_mes.columns = [

    "Mês",

    "Faturamento"

]



st.dataframe(

    faturamento_mes,

    use_container_width=True

)



st.divider()



# =====================================================
# CESTAS VENDIDAS
# =====================================================

st.subheader(
    "🧺 Cestas vendidas"
)



if "cesta_nome" in df_filtrado.columns:


    cestas = (

        df_filtrado

        .groupby(
            "cesta_nome"
        )

        .size()

        .reset_index(

            name="Quantidade vendida"

        )

        .sort_values(

            "Quantidade vendida",

            ascending=False

        )

    )


    cestas.columns = [

        "Cesta",

        "Quantidade vendida"

    ]


    st.dataframe(

        cestas,

        use_container_width=True

    )


else:


    st.warning(

        "Campo cesta_nome não encontrado."

    )



st.divider()



# =====================================================
# ADICIONAIS
# =====================================================

st.subheader(
    "🎁 Adicionais vendidos"
)



if "adicionais" in df_filtrado.columns:


    lista_adicionais = []



    for adicional in df_filtrado["adicionais"]:


        if adicional:


            texto = str(adicional)


            itens = texto.split(",")



            for item in itens:


                lista_adicionais.append(

                    item.strip()

                )



    if lista_adicionais:


        tabela_adicionais = (

            pd.DataFrame(

                lista_adicionais,

                columns=["Adicional"]

            )

            .groupby(

                "Adicional"

            )

            .size()

            .reset_index(

                name="Quantidade vendida"

            )

            .sort_values(

                "Quantidade vendida",

                ascending=False

            )

        )


        st.dataframe(

            tabela_adicionais,

            use_container_width=True

        )


    else:


        st.info(

            "Nenhum adicional vendido."

        )



st.divider()



# =====================================================
# DETALHAMENTO
# =====================================================

st.subheader(
    "📋 Detalhamento financeiro"
)



colunas = [

    "created_at",

    "cliente_nome",

    "cesta_nome",

    "valor_frete",

    "valor_total",

    "status"

]



colunas_existentes = [

    coluna

    for coluna in colunas

    if coluna in df_filtrado.columns

]



st.dataframe(

    df_filtrado[

        colunas_existentes

    ]

    .sort_values(

        "created_at",

        ascending=False

    ),

    use_container_width=True

)
