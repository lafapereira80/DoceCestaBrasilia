import streamlit as st
from datetime import datetime

from services.pedido_service import salvar_pedido

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered"
)

# ===========================
# LOGO
# ===========================

try:
    st.image("assets/logo.webp", width=220)
except:
    pass

st.markdown(
    "<h1 style='text-align:center;color:#8B5A2B;'>Doce Cesta Brasília</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Cestas personalizadas para momentos especiais 💝</p>",
    unsafe_allow_html=True
)

st.divider()

# ===========================
# FORMULÁRIO
# ===========================

with st.form("pedido"):

    st.subheader("👤 Dados do Cliente")

    nome = st.text_input("Nome *")

    cpf = st.text_input(
        "CPF *",
        placeholder="000.000.000-00"
    )

    telefone = st.text_input("Telefone *")

    st.divider()

    st.subheader("🎁 Cesta")

    cesta = st.selectbox(
        "Nome da Cesta *",
        [
            "Selecione...",
            "Cesta Básica",
            "Cesta Romântica",
            "Cesta Premium",
            "Cesta Luxo"
        ]
    )

    pao = st.radio(
        "Tipo de pão",
        [
            "Australiano",
            "Pão Doce"
        ],
        horizontal=True
    )

    espalhavel = st.radio(
        "Espalhável",
        [
            "Doce de Leite",
            "Geleia",
            "Nutella"
        ],
        horizontal=True
    )

    bebida = st.radio(
        "Bebida",
        [
            "Suco de Uva",
            "Suco de Laranja",
            "Frappuccino"
        ],
        horizontal=True
    )

    st.divider()

    st.subheader("✨ Adicionais")

    caneca = st.checkbox("Caneca")

    polaroid = st.checkbox("Polaroid")

    balao = st.checkbox("Balão")

    mini_buque = st.checkbox("Mini Buquê")

    mini_buque_flores = st.checkbox("Mini Buquê Flores Secas")

    fotos = []

    if polaroid:

        st.info("Selecione uma ou mais fotos para impressão.")

        fotos = st.file_uploader(
            "Fotos",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True
        )

    st.divider()

    st.subheader("💌 Mensagem")

    mensagem = st.text_area(
        "",
        placeholder="Digite aqui a mensagem..."
    )

    st.divider()

    st.subheader("📍 Endereço de Entrega")

    endereco = st.text_area(
        "",
        placeholder="Rua, número, complemento, bairro..."
    )

    st.divider()

    st.subheader("💳 Forma de Pagamento")

    pagamento = st.radio(
        "",
        [
            "Pix",
            "Cartão de Crédito"
        ],
        horizontal=True
    )

    enviar = st.form_submit_button(
        "📦 ENVIAR PEDIDO",
        use_container_width=True
    )

# ===========================
# SALVAR PEDIDO
# ===========================

if enviar:

    erros = []

    if nome.strip() == "":
        erros.append("Informe o nome.")

    if cpf.strip() == "":
        erros.append("Informe o CPF.")

    if telefone.strip() == "":
        erros.append("Informe o telefone.")

    if cesta == "Selecione...":
        erros.append("Escolha uma cesta.")

    if endereco.strip() == "":
        erros.append("Informe o endereço de entrega.")

    if erros:

        st.error("Corrija os itens abaixo:")

        for erro in erros:
            st.write("•", erro)

    else:

        adicionais = []

        if caneca:
            adicionais.append("Caneca")

        if polaroid:
            adicionais.append("Polaroid")

        if balao:
            adicionais.append("Balão")

        if mini_buque:
            adicionais.append("Mini Buquê")

        if mini_buque_flores:
            adicionais.append("Mini Buquê Flores Secas")

        pedido = {

            "cliente_nome": nome,

            "cliente_cpf": cpf,

            "cliente_telefone": telefone,

            "cesta_nome": cesta,

            "pao": pao,

            "espalhavel": espalhavel,

            "bebida": bebida,

            "adicionais": ", ".join(adicionais),

            "mensagem": mensagem,

            "endereco": endereco,

            "pagamento": pagamento,

            "status": "Recebido",

            "created_at": datetime.now().isoformat()

        }

        try:

            salvar_pedido(pedido)

            st.success("🎉 Pedido enviado com sucesso!")

            st.info("""
Obrigado por escolher a Doce Cesta Brasília.

Recebemos seu pedido.

Nossa equipe entrará em contato o mais rápido possível para informar:

✅ Valor do frete

✅ Valor final da cesta

✅ Confirmação da entrega
""")

        except Exception as erro:

            st.error("Erro ao salvar o pedido.")

            st.exception(erro)

st.divider()

st.markdown(
    "<p style='text-align:center;font-size:13px;'>🔒 Área Administrativa</p>",
    unsafe_allow_html=True
)
