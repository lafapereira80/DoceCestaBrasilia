import streamlit as st
from pathlib import Path

from services.pedido_service import salvar_pedido
from services.foto_service import salvar_fotos
from services.cesta_service import listar_cestas
from services.cesta_produto_service import listar_produtos_da_cesta
#from services.configuracao_cesta_service import carregar_configuracao_cesta

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

/* Sidebar */
section[data-testid="stSidebar"]{
    display:none;
}

/* Botão menu */
[data-testid="collapsedControl"]{
    display:none;
}

/* Cabeçalho */
header{
    visibility:hidden;
}

/* Rodapé Streamlit */
footer{
    visibility:hidden;
}

/* Menu */
#MainMenu{
    visibility:hidden;
}

/* Centraliza conteúdo */
.block-container{
    max-width:850px;
    padding-top:20px;
}

/* Botões */
.stButton>button{
    background:#8B5A2B;
    color:white;
    border-radius:12px;
    height:55px;
    font-size:18px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# LOGO
# ==========================================================

logo = Path("assets/logo.webp")

if logo.exists():

    c1, c2, c3 = st.columns([2,1,2])

    with c2:

        st.image(str(logo), width=180)

st.markdown(
    "<h1 style='text-align:center;color:#8B5A2B;'>Doce Cesta Brasília</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Cestas personalizadas para momentos especiais 💝</p>",
    unsafe_allow_html=True
)

# ==========================================================
# FORMULÁRIO
# ==========================================================

st.header("📝 Formulário de Pedido")

# ==========================================================
# DADOS DO CLIENTE
# ==========================================================

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

st.divider()

# ==========================================================
# CARREGA CESTAS
# ==========================================================

try:

    cestas = listar_cestas()

except Exception as erro:

    st.error(f"Erro ao carregar as cestas: {erro}")

    st.stop()

if not cestas:

    st.warning("Nenhuma cesta cadastrada.")

    st.stop()

# ==========================================================
# ESCOLHA DA CESTA
# ==========================================================

st.subheader("🎁 Escolha sua Cesta")

cesta = st.selectbox(

    "Selecione uma cesta",

    cestas,

    format_func=lambda c: c["nome"]

)

st.divider()

# ==========================================================
# INFORMAÇÕES DA CESTA
# ==========================================================

if cesta:

    if cesta.get("imagem"):

        st.image(
            cesta["imagem"],
            use_container_width=True
        )

    if cesta.get("descricao"):

        st.info(cesta["descricao"])

    st.markdown(
        """
### 🍓 Personalize sua cesta

Escolha abaixo os produtos disponíveis para esta cesta.
"""
    )

st.divider()

# ==========================================================
# PRODUTOS DA CESTA
# ==========================================================

configuracao = carregar_configuracao_cesta(cesta["cesta_id"])

selecoes_cliente = {}

if not configuracao:

    st.warning(
        "Esta cesta ainda não possui produtos configurados."
    )

else:

    for grupo in configuracao:

        categoria = grupo["categoria"]

        quantidade = grupo["quantidade"]

        produtos = grupo["produtos"]

        st.subheader(f"📦 {categoria}")

        if quantidade == 1:

            escolhido = st.radio(

                "Escolha uma opção",

                produtos,

                format_func=lambda p: p["nome"],

                key=f"radio_{categoria}"

            )

            selecoes_cliente[categoria] = [escolhido]

        else:

            escolhidos = st.multiselect(

                f"Escolha até {quantidade} itens",

                produtos,

                format_func=lambda p: p["nome"],

                max_selections=quantidade,

                key=f"multi_{categoria}"

            )

            selecoes_cliente[categoria] = escolhidos

        st.divider()

# ==========================================================
# ADICIONAIS
# ==========================================================

st.subheader("🎀 Adicionais")

col1, col2 = st.columns(2)

with col1:

    caneca = st.checkbox("☕ Caneca")

    polaroid = st.checkbox("📷 Polaroid")

    balao = st.checkbox("🎈 Balão")

with col2:

    mini_buque = st.checkbox("💐 Mini Buquê")

    mini_buque_flores = st.checkbox(
        "🌸 Mini Buquê Flores Secas"
    )

st.divider()

# ==========================================================
# FOTOS DA POLAROID
# ==========================================================

st.subheader("📷 Fotos para Polaroid")

if polaroid:

    fotos = st.file_uploader(

        "Selecione as fotos",

        type=["jpg", "jpeg", "png", "webp"],

        accept_multiple_files=True

    )

else:

    fotos = []

    st.info(
        "Marque Polaroid para habilitar o envio das fotos."
    )

st.divider()

# ==========================================================
# PAGAMENTO
# ==========================================================

st.subheader("💳 Forma de Pagamento")

pagamento = st.radio(

    "",

    [

        "Pix",

        "Cartão de Crédito"

    ],

    horizontal=True

)

st.divider()

# ==========================================================
# MENSAGEM
# ==========================================================

st.subheader("💌 Mensagem")

mensagem = st.text_area(

    "Mensagem que acompanhará a cesta",

    height=120

)

# ==========================================================
# PEDIDOS ESPECIAIS
# ==========================================================

st.subheader("✨ Pedidos Especiais")

pedido_especial = st.text_area(

    "Deseja solicitar algo especial?",

    height=120

)

st.divider()

# ==========================================================
# ENTREGA
# ==========================================================

st.subheader("📍 Endereço de Entrega")

endereco = st.text_area(

    "Endereço",

    height=120

)

col1, col2 = st.columns(2)

with col1:

    data_entrega = st.date_input(
        "📅 Data da Entrega"
    )

with col2:

    periodo_entrega = st.selectbox(

        "🕘 Período",

        [

            "Manhã",

            "Tarde",

            "Noite"

        ]

    )

st.divider()

# ==========================================================
# BOTÃO ENVIAR
# ==========================================================

enviar = st.button(

    "🛒 ENVIAR PEDIDO",

    use_container_width=True,

    type="primary"

)

# ==========================================================
# ENVIO
# ==========================================================

if enviar:

    if nome.strip() == "":

        st.error("Informe o nome do cliente.")

        st.stop()

    if cpf.strip() == "":

        st.error("Informe o CPF.")

        st.stop()

    if telefone.strip() == "":

        st.error("Informe o telefone.")

        st.stop()

    # ==========================================
    # ADICIONAIS
    # ==========================================

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

    # ==========================================
    # PRODUTOS ESCOLHIDOS
    # ==========================================

    produtos_escolhidos = []

    for categoria, itens in selecoes_cliente.items():

        for item in itens:

            produtos_escolhidos.append(
                f"{categoria}: {item['nome']}"
            )

    # ==========================================
    # DADOS
    # ==========================================

    dados = {

        "cliente_nome": nome,

        "cliente_cpf": cpf,

        "cliente_telefone": telefone,

        "cesta_id": cesta["id"],

        "cesta_nome": cesta["nome"],

        "produtos": "\n".join(produtos_escolhidos),

        "adicionais": ", ".join(adicionais),

        "pagamento": pagamento,

        "mensagem": mensagem,

        "pedido_especial": pedido_especial,

        "endereco": endereco,

        "data_entrega": str(data_entrega),

        "periodo_entrega": periodo_entrega,

        "status": "Recebido",

        "valor_frete": 0,

        "valor_total": 0

    }

    sucesso, pedido_id = salvar_pedido(dados)

    if sucesso:

        if polaroid and fotos:

            try:

                salvar_fotos(
                    pedido_id,
                    fotos
                )

            except Exception as erro:

                st.warning(
                    f"As fotos não puderam ser enviadas: {erro}"
                )

        st.success("🎉 Pedido enviado com sucesso!")

        st.info("""

Obrigado por escolher a **Doce Cesta Brasília** ❤️

Recebemos seu pedido com sucesso.

Nossa equipe entrará em contato para informar:

✅ Valor do frete

✅ Valor final

✅ Confirmação da entrega

""")

    else:

        st.error(
            f"Erro ao salvar pedido: {pedido_id}"
        )

# ==========================================================
# RODAPÉ
# ==========================================================

st.divider()

st.markdown(

    """

<div style="text-align:center;padding:20px;">

© 2026 Doce Cesta Brasília

</div>

""",

    unsafe_allow_html=True

)

st.page_link(

    "pages/99_Admin.py",

    label="Área Administrativa",

    icon="🔒"

)
