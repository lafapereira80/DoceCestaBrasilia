import streamlit as st
from pathlib import Path

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

/* Esconde o menu de navegação das páginas */
[data-testid="stSidebarNav"]{
    display:none;
}

/* Esconde a barra lateral inteira */
section[data-testid="stSidebar"]{
    display:none;
}

/* Esconde o botão >> */
[data-testid="stSidebarCollapsedControl"]{
    display:none;
}

/* Esconde o cabeçalho */
header{
    visibility:hidden;
}

/* Esconde menu */
#MainMenu{
    visibility:hidden;
}

/* Esconde rodapé */
footer{
    visibility:hidden;
}

/* Centraliza a página */
.block-container{
    max-width:900px;
    padding-top:20px;
}

/* Título */
.titulo{
    text-align:center;
    color:#8B5A2B;
    font-size:42px;
    font-weight:bold;
}

/* Subtítulo */
.subtitulo{
    text-align:center;
    color:#666;
    font-size:18px;
    margin-bottom:30px;
}

</style>
""", unsafe_allow_html=True)
# ==========================
# LOGO
# ==========================

logo = Path("assets/logo.webp")

if logo.exists():

    c1,c2,c3 = st.columns([1,2,1])

    with c2:

    st.image(str(logo), width=180)
    
st.markdown(
    "<div class='titulo'>Doce Cesta Brasília</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitulo'>Cestas personalizadas para momentos especiais 💝</div>",
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
        type=["jpg","jpeg","png","webp"],
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
# DATA
# ============================================

col1,col2 = st.columns(2)

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

    st.success("🎉 Pedido enviado com sucesso!")

    st.info("""

Obrigado por escolher a **Doce Cesta Brasília** ❤️

Recebemos seu pedido.

Nossa equipe entrará em contato o mais rápido possível para informar:

✅ Valor do frete

✅ Valor final da cesta

✅ Confirmação da entrega.

Muito obrigado pela preferência!

""")

st.divider()

st.caption("© Doce Cesta Brasília")

st.page_link(
    "pages/99_Admin.py",
    label="🔒 Área Administrativa",
    icon="🔒"
)
