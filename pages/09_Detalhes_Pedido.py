import streamlit as st

from services.pedido_service import (
    buscar_pedido,
    atualizar_pedido
)

from services.foto_service import listar_fotos


st.set_page_config(
    page_title="Detalhes Pedido",
    page_icon="📋",
    layout="wide"
)


# =====================================================
# VALIDA PEDIDO
# =====================================================

if "pedido_aberto" not in st.session_state:

    st.error(
        "Nenhum pedido selecionado."
    )

    if st.button("⬅ Voltar"):

        st.switch_page(
            "pages/02_Pedidos.py"
        )

    st.stop()



pedido_id = st.session_state["pedido_aberto"]



# =====================================================
# BUSCA PEDIDO
# =====================================================

try:

    pedido = buscar_pedido(
        pedido_id
    )

except Exception as erro:

    st.error(
        erro
    )

    st.stop()



# =====================================================
# CABEÇALHO
# =====================================================

st.title("📋 Detalhes do Pedido")

st.caption(
    f"Status atual: {pedido.get('status','-')}"
)


# =====================================================
# CLIENTE
# =====================================================

st.subheader("👤 Cliente")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Nome",
        pedido.get(
            "cliente_nome",
            "-"
        )
    )


with col2:

    st.metric(
        "CPF",
        pedido.get(
            "cliente_cpf",
            "-"
        )
    )


with col3:

    st.metric(
        "Telefone",
        pedido.get(
            "cliente_telefone",
            "-"
        )
    )



# =====================================================
# PEDIDO
# =====================================================

st.subheader("🎁 Pedido")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Cesta",
        pedido.get(
            "cesta_nome",
            "-"
        )
    )


with col2:

    st.metric(
        "Pagamento",
        pedido.get(
            "pagamento",
            "-"
        )
    )


with col3:

    st.metric(
        "Entrega",
        pedido.get(
            "data_entrega",
            "-"
        )
    )


with col4:

    st.metric(
        "Período",
        pedido.get(
            "periodo_entrega",
            "-"
        )
    )



# =====================================================
# PRODUTOS E ADICIONAIS
# =====================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "🛒 Produtos"
    )

    produtos = pedido.get(
        "produtos",
        ""
    )


    if produtos:

        for item in produtos.split("\n"):

            st.write(
                "• " + item
            )

    else:

        st.info(
            "Nenhum produto."
        )



with col2:

    st.subheader(
        "🎀 Adicionais"
    )


    adicionais = pedido.get(
        "adicionais",
        ""
    )


    if adicionais:

        st.success(
            adicionais
        )

    else:

        st.info(
            "Nenhum adicional."
        )



# =====================================================
# MENSAGENS
# =====================================================

col1, col2 = st.columns(2)



with col1:

    st.subheader(
        "💌 Mensagem"
    )


    st.text_area(
        "",
        value=pedido.get(
            "mensagem",
            ""
        ),
        disabled=True,
        height=100,
        key="mensagem_view"
    )



with col2:

    st.subheader(
        "✨ Pedido Especial"
    )


    st.text_area(
        "",
        value=pedido.get(
            "pedido_especial",
            ""
        ),
        disabled=True,
        height=100,
        key="especial_view"
    )



# =====================================================
# ENTREGA
# =====================================================

st.subheader(
    "📍 Endereço de Entrega"
)


st.text_area(
    "",
    value=pedido.get(
        "endereco",
        ""
    ),
    disabled=True,
    height=80,
    key="endereco_view"
)



# =====================================================
# FOTOS
# =====================================================

st.subheader(
    "📷 Fotos da Polaroid"
)


try:

    fotos = listar_fotos(
        pedido["id"]
    )


    if fotos:

        colunas = st.columns(4)


        for i, foto in enumerate(fotos):

            with colunas[i % 4]:

                st.image(
                    foto.get("url"),
                    caption=foto.get(
                        "nome_original",
                        "Foto"
                    ),
                    use_container_width=True
                )


    else:

        st.info(
            "Nenhuma foto cadastrada."
        )


except Exception as erro:

    st.error(
        f"Erro nas fotos: {erro}"
    )



# =====================================================
# ATENDIMENTO
# =====================================================

st.subheader(
    "🚚 Atendimento"
)


col1, col2, col3 = st.columns(3)


with col1:

    valor_frete = st.number_input(
        "Frete",
        min_value=0.0,
        value=float(
            pedido.get(
                "valor_frete",
                0
            )
            or 0
        ),
        step=1.0
    )


with col2:

    valor_total = st.number_input(
        "Valor Final",
        min_value=0.0,
        value=float(
            pedido.get(
                "valor_total",
                0
            )
            or 0
        ),
        step=1.0
    )


with col3:

    status_opcoes = [
        "Recebido",
        "Pago",
        "Desistência",
        "Entregue"
    ]


    status_atual = pedido.get(
        "status",
        "Recebido"
    )


    if status_atual not in status_opcoes:

        status_atual = "Recebido"



    status = st.selectbox(
        "Status",
        status_opcoes,
        index=status_opcoes.index(
            status_atual
        )
    )



if st.button(
    "💾 Salvar Atendimento",
    use_container_width=True
):


    atualizar_pedido(
        pedido["id"],
        status,
        valor_frete,
        valor_total
    )


    st.success(
        "✅ Pedido atualizado!"
    )


    st.rerun()



# =====================================================
# VOLTAR
# =====================================================

if st.button(
    "⬅ Voltar para Pedidos",
    use_container_width=True
):

    st.switch_page(
        "pages/02_Pedidos.py"
    )
