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

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CSS COMPACTO E ISOLADO
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}

h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-top: 12px !important;
    margin-bottom: 8px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CARDS DE RESUMO FINANCEIRO (KPIs)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.kpi-title {
    font-size: 12px !important;
    font-weight: 700;
    color: #775a46;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 20px !important;
    font-weight: 700;
    color: #2e7d32;
}

.kpi-value-neutral {
    font-size: 20px !important;
    font-weight: 700;
    color: #5a3b28;
}

/* Ajustes direcionados de tabelas */
div[data-testid="stDataFrame"] {
    border: 1px solid #e8ddd3 !important;
    border-radius: 8px !important;
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

st.title("💰 Financeiro")
st.caption("Controle de faturamento, vendas e resultados.")
st.divider()


# =====================================================
# CARREGAR PEDIDOS E ADICIONAIS
# =====================================================

@st.cache_data(ttl=60)
def carregar_pedidos():
    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .execute()
    )
    return resposta.data or []


@st.cache_data(ttl=60)
def carregar_adicionais():
    resposta = (
        supabase
        .table("pedido_adicionais")
        .select(
            """
            pedido_id,
            nome_produto,
            quantidade,
            valor_unitario
            """
        )
        .execute()
    )
    return resposta.data or []


# =====================================================
# BUSCA DOS DADOS
# =====================================================

try:
    pedidos = carregar_pedidos()
    adicionais = carregar_adicionais()
except Exception as erro:
    st.error(f"Erro ao carregar dados financeiros: {erro}")
    st.stop()

if not pedidos:
    st.warning("Nenhum pedido encontrado.")
    st.stop()

df = pd.DataFrame(pedidos)
df_adicionais = pd.DataFrame(adicionais)


# =====================================================
# TRATAMENTO DOS DADOS
# =====================================================

if "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
else:
    df["created_at"] = pd.Timestamp.now()

df["valor_total"] = pd.to_numeric(df.get("valor_total", 0), errors="coerce").fillna(0)
df["valor_frete"] = pd.to_numeric(df.get("valor_frete", 0), errors="coerce").fillna(0)
df["desconto"] = pd.to_numeric(df.get("desconto", 0), errors="coerce").fillna(0)

status_financeiro = ["Pago", "Entregue"]
df = df[df["status"].isin(status_financeiro)]

df["ano"] = df["created_at"].dt.year
df["mes"] = df["created_at"].dt.month


# =====================================================
# FORMATAÇÃO DE MOEDA
# =====================================================

def moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X",".")
    )


# =====================================================
# FILTROS
# =====================================================

st.subheader("🔎 Filtros")

with st.container(border=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        anos = sorted(df["ano"].dropna().unique(), reverse=True)
        ano_selecionado = st.selectbox("Ano", ["Todos"] + list(anos))

    with col2:
        meses = {
            1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril",
            5:"Maio", 6:"Junho", 7:"Julho", 8:"Agosto",
            9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"
        }
        mes_selecionado = st.selectbox("Mês", ["Todos"] + list(meses.values()))

    with col3:
        status_lista = sorted(df["status"].dropna().unique().tolist())
        status_selecionado = st.selectbox("Status", ["Todos"] + status_lista)


# =====================================================
# APLICA FILTROS
# =====================================================

df_filtrado = df.copy()

if ano_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["ano"] == ano_selecionado]

if mes_selecionado != "Todos":
    numero_mes = [chave for chave, valor in meses.items() if valor == mes_selecionado][0]
    df_filtrado = df_filtrado[df_filtrado["mes"] == numero_mes]

if status_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status"] == status_selecionado]


# =====================================================
# RESUMO FINANCEIRO
# =====================================================

st.subheader("📊 Resumo financeiro (Pedidos Pagos e Entregues)")

col1, col2, col3, col4 = st.columns(4)

faturamento = df_filtrado["valor_total"].sum()
total_fretes = df_filtrado["valor_frete"].sum()
quantidade_pedidos = len(df_filtrado)
ticket_medio = faturamento / quantidade_pedidos if quantidade_pedidos > 0 else 0

with col1:
    with st.container(border=True):
        st.markdown('<div class="kpi-title">💰 Faturamento</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value">{moeda(faturamento)}</div>', unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown('<div class="kpi-title">🚚 Fretes</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value-neutral">{moeda(total_fretes)}</div>', unsafe_allow_html=True)

with col3:
    with st.container(border=True):
        st.markdown('<div class="kpi-title">📋 Pedidos</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value-neutral">{quantidade_pedidos}</div>', unsafe_allow_html=True)

with col4:
    with st.container(border=True):
        st.markdown('<div class="kpi-title">🎯 Ticket Médio</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value-neutral">{moeda(ticket_medio)}</div>', unsafe_allow_html=True)


st.divider()


# =====================================================
# FATURAMENTO POR MÊS
# =====================================================

st.subheader("📅 Faturamento mensal")

if not df_filtrado.empty:
    faturamento_mes = (
        df_filtrado
        .groupby(df_filtrado["created_at"].dt.strftime("%m/%Y"))["valor_total"]
        .sum()
        .reset_index()
    )
    faturamento_mes.columns = ["Mês", "Faturamento"]
    faturamento_mes["Faturamento"] = faturamento_mes["Faturamento"].apply(moeda)

    st.dataframe(faturamento_mes, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum dado para o período selecionado.")


st.divider()


# =====================================================
# CESTAS VENDIDAS
# =====================================================

st.subheader("🧺 Cestas vendidas")

if "cesta_nome" in df_filtrado.columns:
    cestas = (
        df_filtrado
        .groupby("cesta_nome")
        .size()
        .reset_index(name="Quantidade vendida")
        .sort_values("Quantidade vendida", ascending=False)
    )
    cestas.columns = ["Cesta", "Quantidade vendida"]
    st.dataframe(cestas, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma informação de cesta encontrada.")


st.divider()


# =====================================================
# ADICIONAIS VENDIDOS
# =====================================================

st.subheader("🎀 Adicionais vendidos")

if not df_adicionais.empty:
    pedidos_filtrados_ids = df_filtrado["id"].tolist()
    adicionais_filtrados = df_adicionais[df_adicionais["pedido_id"].isin(pedidos_filtrados_ids)].copy()

    if not adicionais_filtrados.empty:
        adicionais_filtrados["quantidade"] = pd.to_numeric(adicionais_filtrados["quantidade"], errors="coerce").fillna(1)
        adicionais_filtrados["valor_unitario"] = pd.to_numeric(adicionais_filtrados["valor_unitario"], errors="coerce").fillna(0)
        adicionais_filtrados["total"] = adicionais_filtrados["quantidade"] * adicionais_filtrados["valor_unitario"]

        resumo_adicionais = (
            adicionais_filtrados
            .groupby("nome_produto")
            .agg(Quantidade=("quantidade", "sum"), Faturamento=("total", "sum"))
            .reset_index()
        )
        resumo_adicionais.columns = ["Adicional", "Quantidade vendida", "Faturamento"]
        resumo_adicionais["Faturamento"] = resumo_adicionais["Faturamento"].apply(moeda)
        resumo_adicionais = resumo_adicionais.sort_values("Quantidade vendida", ascending=False)

        st.dataframe(resumo_adicionais, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum adicional encontrado para o período.")
else:
    st.info("Nenhum adicional vendido.")


st.divider()


# =====================================================
# VALORES POR STATUS
# =====================================================

st.subheader("📌 Resumo por status")

if "status" in df_filtrado.columns:
    resumo_status = (
        df_filtrado
        .groupby("status")
        .agg(Quantidade=("id", "count"), Valor=("valor_total", "sum"))
        .reset_index()
    )
    resumo_status.columns = ["Status", "Quantidade", "Valor"]
    resumo_status["Valor"] = resumo_status["Valor"].apply(moeda)

    st.dataframe(resumo_status, use_container_width=True, hide_index=True)


# =====================================================
# DETALHAMENTO FINANCEIRO
# =====================================================

st.divider()
st.subheader("📋 Detalhamento financeiro dos pedidos")

colunas_detalhamento = [
    "created_at", "cliente_nome", "cliente_telefone",
    "cesta_nome", "status", "valor_frete", "desconto", "valor_total"
]

colunas_existentes = [coluna for coluna in colunas_detalhamento if coluna in df_filtrado.columns]

detalhamento = (
    df_filtrado[colunas_existentes]
    .sort_values("created_at", ascending=False)
    .copy()
)

if "created_at" in detalhamento.columns:
    detalhamento["created_at"] = detalhamento["created_at"].dt.strftime("%d/%m/%Y %H:%M")

for coluna in ["valor_frete", "desconto", "valor_total"]:
    if coluna in detalhamento.columns:
        detalhamento[coluna] = detalhamento[coluna].apply(moeda)

detalhamento = detalhamento.rename(
    columns={
        "created_at": "Data",
        "cliente_nome": "Cliente",
        "cliente_telefone": "Telefone",
        "cesta_nome": "Cesta",
        "status": "Status",
        "valor_frete": "Frete",
        "desconto": "Desconto",
        "valor_total": "Valor Total"
    }
)

st.dataframe(detalhamento, use_container_width=True, hide_index=True)


# =====================================================
# CONFERÊNCIA DE VALORES
# =====================================================

st.divider()
st.subheader("🔎 Conferência de valores")
st.caption(
    """
O valor apresentado abaixo utiliza o campo **valor_total** salvo no pedido.

Esse valor é atualizado:
✅ Inicialmente pelo formulário do cliente  
✅ Depois pelo atendimento administrativo em Detalhes do Pedido  
✅ Considerando frete, descontos e adicionais sob consulta
"""
)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown('<div class="kpi-title">Pedidos Analisados</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value-neutral">{len(df_filtrado)}</div>', unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown('<div class="kpi-title">Total Vendido</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value">{moeda(df_filtrado["valor_total"].sum())}</div>', unsafe_allow_html=True)

with col3:
    with st.container(border=True):
        st.markdown('<div class="kpi-title">Média por Pedido</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-value-neutral">{moeda(df_filtrado["valor_total"].mean() if len(df_filtrado) > 0 else 0)}</div>', unsafe_allow_html=True)


# =====================================================
# AVISO DE PEDIDOS SEM VALOR
# =====================================================

pedidos_sem_valor = df_filtrado[df_filtrado["valor_total"] <= 0]

if not pedidos_sem_valor.empty:
    st.warning(f"⚠️ Existem {len(pedidos_sem_valor)} pedido(s) sem valor total definido.")
