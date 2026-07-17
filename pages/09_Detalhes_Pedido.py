import streamlit as st

from services.pedido_service import buscar_pedido

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

col1, col2 = st.columns(2)

with col1:

    st.write("**Nome**")

    st.write(pedido["cliente_nome"])

    st.write("**CPF**")

    st.write(pedido["cliente_cpf"])

with col2:

    st.write("**Telefone**")

    st.write(pedido["cliente_telefone"])

st.divider()

# =====================================================
# INFORMAÇÕES DO PEDIDO
# =====================================================

st.subheader("🎁 Informações do Pedido")

col1, col2 = st.columns(2)

with col1:

    st.write("**Cesta**")
    st.write(pedido["cesta_nome"])

    st.write("**Tipo de pão**")
    st.write(pedido["pao"])

    st.write("**Espalhável**")
    st.write(pedido["espalhavel"])

with col2:

    st.write("**Bebida**")
    st.write(pedido["bebida"])

    st.write("**Pagamento**")
    st.write(pedido["pagamento"])

    st.write("**Status**")
    st.write(pedido["status"])

st.divider()

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

    st.write("**Horário**")
    st.write(pedido["horario_entrega"])

st.divider()

# =====================================================
# FOTOS DA POLAROID
# =====================================================

st.subheader("📷 Fotos da Polaroid")

try:

   fotos = listar_fotos(pedido["id"])

st.write(fotos)

    if fotos:

        colunas = st.columns(3)

        for indice, foto in enumerate(fotos):

            with colunas[indice % 3]:

                st.image(
                    foto["url"],
                    caption=foto.get("nome_original", "Foto"),
                    use_container_width=True
                )

    else:

        st.info("Este pedido não possui fotos.")

except Exception as erro:

    st.error(f"Erro ao carregar as fotos: {erro}")

st.divider()

# =====================================================
# VOLTAR
# =====================================================

if st.button(
    "⬅ Voltar para Pedidos",
    key="voltar_pedidos"
):

    st.switch_page("pages/02_Pedidos.py")
