import streamlit as st

from services.pedido_service import (
    buscar_pedido,
    atualizar_pedido
)

from services.foto_service import listar_fotos

st.set_page_config(
    page_title="Pedido",
    page_icon="📋",
    layout="wide"
)

# =====================================================
# VERIFICA SE VEIO DA LISTA DE PEDIDOS
# =====================================================

if "pedido_aberto" not in st.session_state:

    st.error("Nenhum pedido foi selecionado.")

    if st.button("⬅ Voltar"):

        st.switch_page("pages/02_Pedidos.py")

    st.stop()

pedido_id = st.session_state["pedido_aberto"]

# =====================================================
# BUSCA O PEDIDO
# =====================================================

try:

    pedido = buscar_pedido(pedido_id)

except Exception as erro:

    st.error(erro)

    st.stop()

# =====================================================
# CABEÇALHO
# =====================================================

st.title(f"📋 Pedido #{pedido['id']}")

st.caption(f"Status atual: {pedido['status']}")

st.divider()

# =====================================================
# DADOS DO CLIENTE
# =====================================================

st.subheader("👤 Cliente")

col1, col2, col3 = st.columns(3)

with col1:

    st.write("**Nome**")

    st.write(pedido["cliente_nome"])
with col2:

    st.write("**CPF**")

    st.write(pedido["cliente_cpf"])

with col3:

    st.write("**Telefone**")

    st.write(pedido["cliente_telefone"])

st.divider()

# =====================================================
# INFORMAÇÕES DO PEDIDO
# =====================================================

st.subheader("🎁 Informações do Pedido")
col1, col2, col3 = st.columns(3)

with col1:
st.write("**Cesta**")
st.write(pedido["cesta_nome"])
with col2:
st.write("**Pagamento**")
st.write(pedido["pagamento"])
with col3:
st.write("**Status**")
st.write(pedido["status"])

st.divider()

st.subheader("🛒 Produtos Escolhidos")

produtos = pedido.get("produtos", "")

if produtos:

    for linha in produtos.split("\n"):

        st.write("• " + linha)

else:

    st.info("Nenhum produto registrado.")

st.divider()

st.subheader("✨ Pedidos Especiais")

pedido_especial = pedido.get("pedido_especial", "")

if pedido_especial:

    st.text_area(

        "Pedidos especiais",

        value=pedido_especial,

        disabled=True,

        height=120,

        key="pedido_especial"

    )

else:

    st.info("Nenhum pedido especial.")

# =====================================================
# ADICIONAIS
# =====================================================

st.subheader("🎀 Adicionais")

adicionais = pedido.get("adicionais", "")

if adicionais:

    st.success(adicionais)

else:

    st.info("Nenhum adicional escolhido.")

st.divider()

# =====================================================
# MENSAGEM
# =====================================================

st.subheader("💌 Mensagem")

mensagem = pedido.get("mensagem", "")

if mensagem:

   st.text_area(
    "Mensagem",
    value=mensagem,
    disabled=True,
    height=120,
    key="mensagem_pedido"
)
else:

    st.info("Nenhuma mensagem cadastrada.")

st.divider()

# =====================================================
# ENTREGA
# =====================================================

st.subheader("📍 Entrega")

st.write("**Endereço**")

st.text_area(
    "Endereço",
    value=pedido.get("endereco", ""),
    disabled=True,
    height=120,
    key="endereco_pedido"
)

col1, col2 = st.columns(2)

with col1:

    st.write("**Data**")
    st.write(pedido["data_entrega"])

with col2:

    st.write("**Período**")
st.write(pedido.get("periodo_entrega", ""))

st.divider()

# =====================================================
# FOTOS DA POLAROID
# =====================================================

st.subheader("📷 Fotos da Polaroid")

try:

    fotos = listar_fotos(pedido["id"])

    if fotos:

        colunas = st.columns(3)

        for indice, foto in enumerate(fotos):

            with colunas[indice % 3]:

                st.image(
    foto["url_publica"],
    caption=foto.get("nome_original", "Foto"),
    use_container_width=True
)

    else:

        st.info("Este pedido não possui fotos.")

except Exception as erro:

    st.error(f"Erro ao carregar as fotos: {erro}")

st.divider()

# =====================================================
# ATENDIMENTO
# =====================================================

st.subheader("🚚 Atendimento")

col1, col2 = st.columns(2)

with col1:

    valor_frete = st.number_input(
        "Valor do Frete (R$)",
        min_value=0.0,
        value=float(pedido.get("valor_frete", 0) or 0),
        step=1.0,
        key="valor_frete"
    )

with col2:

    valor_total = st.number_input(
        "Valor Final (R$)",
        min_value=0.0,
        value=float(pedido.get("valor_total", 0) or 0),
        step=1.0,
        key="valor_total"
    )

status = st.selectbox(
    "Status do Pedido",
    [
        "Recebido",
        "Pago",
        "Desistência",
        "Entregue"
    ],
    index=[
        "Recebido",
        "Pago",
        "Desistência",
        "Entregue"
    ].index(
        pedido.get("status", "Recebido")
    ),
    key="status_pedido"
)

if st.button(
    "💾 Salvar Atendimento",
    use_container_width=True,
    key="salvar_atendimento"
):

    atualizar_pedido(
        pedido["id"],
        status,
        valor_frete,
        valor_total
    )

    st.success("✅ Atendimento atualizado com sucesso!")

    st.rerun()

st.divider()

if st.button(
    "⬅ Voltar para Pedidos",
    key="voltar_pedidos"
):

    st.switch_page("pages/02_Pedidos.py")
