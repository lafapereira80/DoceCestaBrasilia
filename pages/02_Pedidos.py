import streamlit as st

st.set_page_config(
    page_title="Novo Pedido",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Novo Pedido")
st.write("Preencha os dados abaixo para montar sua cesta personalizada.")

with st.form("pedido"):

    st.subheader("👤 Dados do Cliente")

    nome = st.text_input("Nome Completo *")

    cpf = st.text_input("CPF *")

    telefone = st.text_input("Telefone / WhatsApp *")

    endereco = st.text_area("Endereço de Entrega *")

    st.divider()

    st.subheader("🎁 Escolha da Cesta")

    cesta = st.selectbox(
        "Nome da Cesta",
        [
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
        ]
    )

    espalhavel = st.radio(
        "Espalhável",
        [
            "Doce de Leite",
            "Geleia",
            "Nutella"
        ]
    )

    bebida = st.radio(
        "Bebida",
        [
            "Suco de Uva",
            "Suco de Laranja",
            "Frappuccino"
        ]
    )

    st.divider()

    st.subheader("✨ Adicionais")

    adicionais = st.multiselect(
        "Escolha os adicionais",
        [
            "Caneca",
            "Polaroid",
            "Balão",
            "Mini Buquê",
            "Mini Buquê Flores Secas"
        ]
    )

    fotos = None

    if "Polaroid" in adicionais:

        fotos = st.file_uploader(
            "Envie as fotos para impressão",
            type=["jpg","jpeg","png","webp"],
            accept_multiple_files=True
        )

    st.divider()

    pagamento = st.radio(
        "Forma de Pagamento",
        [
            "Pix",
            "Cartão de Crédito"
        ]
    )

    mensagem = st.text_area(
        "Mensagem que será enviada"
    )

    enviar = st.form_submit_button(
        "📦 ENVIAR PEDIDO",
        use_container_width=True
    )

if enviar:

    if nome == "" or cpf == "" or telefone == "" or endereco == "":

        st.error("Preencha todos os campos obrigatórios.")

    else:

        st.success("🎉 Pedido enviado com sucesso!")

        st.info(
            """
Obrigado pelo seu pedido!

Recebemos sua solicitação.

Nossa equipe entrará em contato o mais rápido possível para informar:

✅ Valor do frete

✅ Valor final da cesta

✅ Confirmação da entrega
"""
        )

        with st.expander("Visualizar dados enviados"):

            st.write("**Nome:**", nome)
            st.write("**CPF:**", cpf)
            st.write("**Telefone:**", telefone)
            st.write("**Endereço:**", endereco)
            st.write("**Cesta:**", cesta)
            st.write("**Pão:**", pao)
            st.write("**Espalhável:**", espalhavel)
            st.write("**Bebida:**", bebida)
            st.write("**Adicionais:**", adicionais)
            st.write("**Pagamento:**", pagamento)
            st.write("**Mensagem:**", mensagem)

            if fotos:
                st.write(f"📷 {len(fotos)} foto(s) enviada(s)")
