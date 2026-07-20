import streamlit as st
import pandas as pd

from config.supabase import supabase


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Financeiro",
    page_icon="💰",
    layout="wide"
)


# =====================================================
# REMOVER ELEMENTOS STREAMLIT
# =====================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)



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
# TÍTULO
# =====================================================

st.title("💰 Financeiro")

st.divider()



# =====================================================
# CARREGAR DADOS
# =====================================================

df = carregar_pedidos()



if df.empty:

    st.warning(
        "Nenhum pedido encontrado."
    )

    st.stop()



# =====================================================
# TRATAMENTO
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
        df["ano"].unique(),
        reverse=True
    )


    ano = st.selectbox(
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


    mes = st.selectbox(
        "Mês",
        ["Todos"] + list(meses.values())
    )



df_filtrado = df.copy()



if ano != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["ano"] == ano
    ]



if mes != "Todos":

    numero_mes = [
        k for k,v in meses.items()
        if v == mes
    ][0]


    df_filtrado = df_filtrado[
        df_filtrado["mes"] == numero_mes
    ]



st.divider()



# =====================================================
# INDICADORES
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

    frete = (
        df_filtrado["valor_frete"]
        .sum()
    )


    st.metric(
        "Fretes recebidos",
        f"R$ {frete:,.2f}"
    )



with col3:

    quantidade = len(
        df_filtrado
    )


    st.metric(
        "Pedidos",
        quantidade
    )



with col4:

    ticket = (
        faturamento / quantidade
        if quantidade > 0
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



st.divider()



# =====================================================
# ADICIONAIS
# =====================================================

st.subheader(
    "🎁 Adicionais vendidos"
)



if "adicionais" in df_filtrado.columns:


    lista = []


    for item in df_filtrado["adicionais"]:


        if item:

            texto = str(item)


            partes = texto.split(",")


            for p in partes:

                lista.append(
                    p.strip()
                )



    if lista:


        adicionais = (

            pd.DataFrame(
                lista,
                columns=[
                    "Adicional"
                ]
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
            adicionais,
            use_container_width=True
        )


    else:

        st.info(
            "Nenhum adicional encontrado."
        )



st.divider()



# =====================================================
# DETALHAMENTO
# =====================================================

st.subheader(
    "📋 Detalhamento dos pedidos"
)



colunas = [

    "created_at",
    "cliente_nome",
    "cesta_nome",
    "valor_frete",
    "valor_total",
    "status"

]



colunas_ok = [

    c for c in colunas
    if c in df_filtrado.columns

]



st.dataframe(

    df_filtrado[
        colunas_ok
    ]

    .sort_values(
        "created_at",
        ascending=False
    ),

    use_container_width=True

)
