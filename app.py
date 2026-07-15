import streamlit as st
from pathlib import Path
from services.pedido_service import salvar_pedido
from services.foto_service import salvar_fotos

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================
# CSS
# ==========================
st.markdown("""
<style>

/* Esconde menu lateral */
section[data-testid="stSidebar"]{
    display:none;
}

/* Esconde botão do menu */
[data-testid="collapsedControl"]{
    display:none;
}

/* Cabeçalho */
header{
    visibility:hidden;
}

/* Rodapé */
footer{
    visibility:hidden;
}

/* Menu Streamlit */
#MainMenu{
    visibility:hidden;
}

/* Centraliza conteúdo */
.block-container{
    max-width:850px;
    padding-top:20px;
}

/* Botão */
.stButton > button{
    background:#8B5A2B;
    color:white;
    border-radius:12px;
    height:55px;
    font-size:18px;
    font-weight:bold;
}

/* Rodapé */
.rodape{
    text-align:center;
    color:#777;
    margin-top:50px;
}

</style>
""", unsafe_allow_html=True)
# ==========================
# LOGO
# ==========================

logo = Path("assets/logo.webp")

if logo.exists():

    col1,col2,col3 = st.columns([2,1,2])

    with col2:

        st.image(str(logo), width=180)

st.markdown(
    "<h1 style='text-align:center;color:#8B5A2B;'>Doce Cesta Brasília</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Cestas personalizadas para momentos especiais 💝</p>",
    unsafe_allow_html=True
)
# ==========================
# FORMULÁRIO DE PEDIDOS
# ==========================

st.header("📝 Formulário de Pedido")

with st.form("pedido"):


    st.subheader("👤 Dados do Cliente")

    nome = st.text_input(
        "Nome Completo *"
    )

    cpf = st.text_input(
        "CPF *",
        placeholder="000.000.000-00"
    )

    telefone = st.text_input(
        "Telefone *",
        placeholder="(61) 99999-9999"
    )

    st.subheader("🎁 Escolha da Cesta")

    cesta = st.selectbox(
        "Nome da Cesta",
        [
            "Selecione...",
            "Cesta Romântica",
            "Cesta Premium",
            "Cesta Luxo"
        ]
    )

    tipo_pao = st.radio(
        "Tipo de Pão",
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

    # ============================================
    # ADICIONAIS
    # ============================================

    st.subheader("🎀 Adicionais")

    col1, col2 = st.columns(2)

    with col1:
        caneca = st.checkbox("☕ Caneca")
        polaroid = st.checkbox("📷 Polaroid")
        balao = st.checkbox("🎈 Balão")

    with col2:
        mini_buque = st.checkbox("💐 Mini Buquê")
        mini_buque_flores = st.checkbox("🌸 Mini Buquê Flores Secas")

    # ============================================
    # FOTOS
    # ============================================

    fotos = []

    if polaroid:

        st.info(
            "Selecione uma ou mais fotos que serão impressas e colocadas na cesta."
        )

        fotos = st.file_uploader(
            "Enviar Fotos",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True
        )

    # ============================================
    # PAGAMENTO
    # ============================================

    st.subheader("💳 Forma de Pagamento")

    pagamento = st.radio(
        "",
        [
            "Pix",
            "Cartão de Crédito"
        ],
        horizontal=True
    )

    # ============================================
    # MENSAGEM
    # ============================================

    st.subheader("💌 Mensagem")

    mensagem = st.text_area(
        "",
        height=120,
        placeholder="Digite aqui a mensagem que acompanhará a cesta..."
    )

    # ============================================
    # ENTREGA
    # ============================================

    st.subheader("📍 Endereço de Entrega")

    endereco = st.text_area(
        "",
        height=120,
        placeholder="Rua, número, complemento, bairro, cidade..."
    )

    # ============================================
    # DATA E HORÁRIO
    # ============================================

    col1, col2 = st.columns(2)

    with col1:
        data_entrega = st.date_input(
            "📅 Data da Entrega"
        )

    with col2:
        horario_entrega = st.time_input(
            "🕒 Horário"
        )

    st.divider()

    enviar = st.form_submit_button(
        "🛒 ENVIAR PEDIDO",
        use_container_width=True
    )

if enviar:

    # ============================
    # VALIDAÇÕES
    # ============================

    if nome.strip() == "":
        st.error("Informe o nome do cliente.")

    elif cpf.strip() == "":
        st.error("Informe o CPF.")

    elif telefone.strip() == "":
        st.error("Informe o telefone.")

    elif cesta == "Selecione...":
        st.error("Escolha uma cesta.")

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

        dados = {

            "cliente_nome": nome,

            "cliente_cpf": cpf,

            "cliente_telefone": telefone,

            "cesta_nome": cesta,

            "pao": tipo_pao,

            "espalhavel": espalhavel,

            "bebida": bebida,

            "adicionais": ", ".join(adicionais),

            "pagamento": pagamento,

            "mensagem": mensagem,

            "endereco": endereco,

            "data_entrega": str(data_entrega),

            "horario_entrega": str(horario_entrega),

            "status": "Recebido",

            "valor_frete": 0,

            "valor_total": 0

        }

        sucesso, pedido_id = salvar_pedido(dados)

if sucesso:

    # Salva as fotos (caso existam)
    if polaroid and fotos:
        try:
            salvar_fotos(pedido_id, fotos)
        except Exception as erro:
            st.warning(f"As fotos não puderam ser enviadas: {erro}")

    st.success("🎉 Pedido enviado com sucesso!")

    st.info("""
Obrigado por escolher a **Doce Cesta Brasília** ❤️

Recebemos seu pedido com sucesso.

Nossa equipe entrará em contato o mais rápido possível para informar:

✅ Valor do frete

✅ Valor final da cesta

✅ Confirmação da entrega.

Muito obrigado pela preferência!
""")

else:

    st.error(f"Erro ao salvar o pedido: {pedido_id}")
