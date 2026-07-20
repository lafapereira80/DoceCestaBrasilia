import streamlit as st
import pandas as pd
from datetime import datetime

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
# CSS - REMOVER MENU STREAMLIT
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

    return pd.DataFrame(resposta.data)



# =====================================================
# TÍTULO
# =====================================================

st.title("💰 Financeiro")

st.divider()


# =====================================================
# CARREGAMENTO
# =====================================================

df = carregar_pedidos()
st.write("Colunas encontradas no Supabase:")
st.write(df.columns.tolist())

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


df["ano"] = df["created_at"].dt.year


df["mes"] = df["created_at"].dt.month



df["valor_total"] = pd.to_numeric(
    df["valor_total"],
    errors="coerce"
).fillna(0)



# =====================================================
# FILTROS
# =====================================================

st.subheader("🔎 Filtros")


col1, col2 = st.columns(2)


with col1:

    anos = sorted(
        df["ano"].unique(),
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
        df_filtrado["ano"] == ano_selecionado
    ]



if mes_selecionado != "Todos":

    numero_mes = [
        chave
        for chave, valor in meses.items()
        if valor == mes_selecionado
    ][0]


    df_filtrado = df_filtrado[
        df_filtrado["mes"] == numero_mes
    ]



st.divider()



# =====================================================
# INDICADORES
# =====================================================

st.subheader("📊 Resumo financeiro")


col1, col2, col3 = st.columns(3)



with col1:

    faturamento = df_filtrado[
        "valor_total"
    ].sum()


    st.metric(
        "Faturamento",
        f"R$ {faturamento:,.2f}"
    )



with col2:

    pedidos = len(df_filtrado)


    st.metric(
        "Pedidos realizados",
        pedidos
    )



with col3:

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
# FATURAMENTO POR PERÍODO
# =====================================================

st.subheader(
    "📅 Faturamento por mês"
)


faturamento_mes = (
    df_filtrado
    .groupby(
        df_filtrado["created_at"].dt.strftime("%m/%Y")
    )["valor_total"]
    .sum()
    .reset_index()
)


faturamento_mes.columns = [
    "Mês",
    "Valor"
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



if "cesta" in df_filtrado.columns:


    cestas = (
        df_filtrado
        .groupby("cesta")
        .size()
        .reset_index(
            name="Quantidade"
        )
        .sort_values(
            "Quantidade",
            ascending=False
        )
    )


    st.dataframe(
        cestas,
        use_container_width=True
    )

else:

    st.info(
        "Campo cesta não encontrado."
    )



st.divider()



# =====================================================
# ADICIONAIS VENDIDOS
# =====================================================

st.subheader(
    "🎁 Adicionais vendidos"
)



if "adicionais" in df_filtrado.columns:


    lista_adicionais = []


    for item in df_filtrado["adicionais"]:

        if item:

            if isinstance(item, list):

                lista_adicionais.extend(item)

            else:

                partes = str(item).split(",")

                lista_adicionais.extend(
                    [
                        p.strip()
                        for p in partes
                    ]
                )



    if lista_adicionais:


        adicionais = pd.DataFrame(
            lista_adicionais,
            columns=["Adicional"]
        )


        adicionais = (
            adicionais
            .groupby("Adicional")
            .size()
            .reset_index(
                name="Quantidade"
            )
            .sort_values(
                "Quantidade",
                ascending=False
            )
        )


        st.dataframe(
            adicionais,
            use_container_width=True
        )


    else:

        st.info(
            "Nenhum adicional vendido."
        )


else:

    st.info(
        "Campo adicionais não encontrado."
    )



st.divider()



# =====================================================
# DETALHAMENTO DOS PEDIDOS
# =====================================================

st.subheader(
    "📋 Detalhamento financeiro"
)


colunas = [
    "created_at",
    "nome",
    "cesta",
    "valor_total"
]


colunas_existentes = [
    c for c in colunas
    if c in df_filtrado.columns
]


st.dataframe(
    df_filtrado[
        colunas_existentes
    ].sort_values(
        "created_at",
        ascending=False
    ),
    use_container_width=True
)
