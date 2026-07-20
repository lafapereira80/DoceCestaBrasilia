import streamlit as st
from config.supabase import supabase

st.set_page_config(
    page_title="Histórico do Cliente",
    page_icon="👤",
    layout="wide"
)

# =====================================================
# VERIFICA SE VEIO DA TELA CLIENTES
# =====================================================

if "cliente_cpf" not in st.session_state:

    st.error("Nenhum cliente selecionado.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/03_Clientes.py")

    st.stop()

cpf = st.session_state["cliente_cpf"]

# =====================================================
# BUSCA TODOS OS PEDIDOS DO CLIENTE
# =====================================================

try:

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("cliente_cpf", cpf)
        .eq("status", "Entregue")
        .order("created_at", desc=True)
        .execute()
    )

    pedidos = resposta.data or []

except Exception as erro:

    st.error(f"Erro ao carregar histórico: {erro}")

    st.stop()


st.write("Quantidade de pedidos encontrados:", len(pedidos))

for pedido in pedidos:
    st.write(
        "ID:",
        pedido["id"],
        "| CPF:",
        pedido["cliente_cpf"],
        "| Status:",
        pedido["status"],
        "| Data:",
        pedido["created_at"]
    )

except Exception as erro:

    st.error(f"Erro ao carregar histórico: {erro}")
    st.stop()
    
if not pedidos:

    st.warning("Cliente sem pedidos.")

    st.stop()

cliente = pedidos[0]

st.title("👤 Histórico do Cliente")

st.divider()

# =====================================================
# RESUMO DO CLIENTE
# =====================================================

total_pedidos = len(pedidos)

valor_total = sum(
    float(p.get("valor_total") or 0)
    for p in pedidos
)

ticket_medio = (
    valor_total / total_pedidos
    if total_pedidos > 0
    else 0
)

ultima_compra = pedidos[0].get("data_entrega", "-")

st.subheader("👤 Dados do Cliente")

col1, col2 = st.columns(2)

with col1:

    st.write("**Nome**")
    st.write(cliente["cliente_nome"])

    st.write("**CPF**")
    st.write(cliente["cliente_cpf"])

with col2:

    st.write("**Telefone**")
    st.write(cliente["cliente_telefone"])

st.divider()

st.subheader("📊 Resumo")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Pedidos",
        total_pedidos
    )

with c2:

    st.metric(
        "Valor Gasto",
        f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with c3:

    st.metric(
        "Ticket Médio",
        f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with c4:

    st.metric(
        "Última Compra",
        str(ultima_compra)
    )

st.divider()

# =====================================================
# HISTÓRICO DOS PEDIDOS
# =====================================================

st.subheader("📋 Histórico de Compras")

st.write("Total no histórico:", len(pedidos))

for i, pedido in enumerate(pedidos):

    st.write("Pedido número:", i + 1)

    with st.container(border=True):

    with st.container(border=True):

        st.markdown(
            f"## 🎁 {pedido.get('cesta_nome','-')}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write("**Data da entrega**")
            st.write(pedido.get("data_entrega","-"))

        with col2:

            st.write("**Status**")
            st.write(pedido.get("status","-"))

        with col3:

            st.write("**Pagamento**")
            st.write(pedido.get("pagamento","-"))

        st.divider()

        # ==========================================
        # PRODUTOS ESCOLHIDOS
        # ==========================================

        st.write("### 📦 Produtos da Cesta")

        produtos = pedido.get("produtos","")

        if produtos:

            st.code(produtos)

        else:

            st.info("Nenhum produto registrado.")

        # ==========================================

        st.write("### 🎀 Adicionais")

        adicionais = pedido.get("adicionais","")

        if adicionais:

            st.success(adicionais)

        else:

            st.info("Nenhum adicional.")

        # ==========================================

        st.write("### 💌 Mensagem")

        mensagem = pedido.get("mensagem","")

        if mensagem:

            st.text_area(

                "Mensagem",

                value=mensagem,

                disabled=True,

                height=90,

                key=f"msg_{pedido['id']}",

                label_visibility="collapsed"

            )

        else:

            st.info("Sem mensagem.")

        # ==========================================

        st.write("### ✨ Pedido Especial")

        especial = pedido.get("pedido_especial","")

        if especial:

            st.text_area(

                "Pedido Especial",

                value=especial,

                disabled=True,

                height=90,

                key=f"esp_{pedido['id']}",

                label_visibility="collapsed"

            )

        else:

            st.info("Nenhum pedido especial.")

        # ==========================================

        st.write("### 📍 Endereço")

        st.text_area(

            "Endereço",

            value=pedido.get("endereco",""),

            disabled=True,

            height=90,

            key=f"end_{pedido['id']}",

            label_visibility="collapsed"

        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(

                "Frete",

                f"R$ {float(pedido.get('valor_frete') or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")

            )

        with col2:

            st.metric(

                "Valor Total",

                f"R$ {float(pedido.get('valor_total') or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")

            )

        # ==========================================

        st.write("### 📷 Fotos")

        if pedido.get("foto_excluida"):

            st.success(
                "Fotos removidas automaticamente após a conclusão do pedido."
            )

        else:

            st.info(
                "Fotos ainda disponíveis."
            )

    st.divider()
# =====================================================
# VOLTAR
# =====================================================

if st.button(
    "⬅ Voltar para Clientes",
    use_container_width=True,
    key="voltar_clientes"
):

    st.session_state.pop(
        "cliente_cpf",
        None
    )

    st.switch_page(
        "pages/03_Clientes.py"
    )
