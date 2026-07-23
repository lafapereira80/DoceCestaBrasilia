import streamlit as st
from pathlib import Path

from services.pedido_service import salvar_pedido
from services.foto_service import salvar_fotos
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.categoria_service import listar_categorias_pedido
from services.produto_service import listar_produtos_por_categoria_id
from services.pedido_adicional_service import salvar_adicionais_pedido


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# CSS MODERNO E RESPONSIVO
# ==========================================================

st.markdown(
"""
<style>
/* =========================================
   REMOÇÃO DE ELEMENTOS PADRÃO E SIDEBAR
========================================== */
section[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

header {
    visibility: hidden !important;
    height: 0px !important;
}

footer {
    visibility: hidden !important;
}

#MainMenu {
    visibility: hidden !important;
}

/* =========================================
   CONTAINER PRINCIPAL E ESPAÇAMENTOS
========================================== */
.block-container {
    max-width: 680px !important;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.6rem !important;
}

/* =========================================
   TYPOGRAPHY
========================================== */
h1 {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #5a3b28 !important;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-top: 8px !important;
    margin-bottom: 6px !important;
}

p, label, span, div {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CARDS DE SEÇÃO (BORDER WRAPPER)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.03);
}

.secao-titulo {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-bottom: 8px !important;
}

/* =========================================
   CUSTOMIZAÇÃO DO UPLOADER (DROPZONE)
========================================== */
div[data-testid="stFileUploader"] {
    width: 100% !important;
}

div[data-testid="stFileUploader"] section {
    background-color: #faf7f3 !important;
    border: 2px dashed #dfcdbb !important;
    border-radius: 12px !important;
    padding: 10px !important;
    text-align: center !important;
}

div[data-testid="stFileUploader"] section button {
    background-color: #ffffff !important;
    border: 1px solid #dfcdbb !important;
    color: #5a3b28 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}

div[data-testid="stFileUploader"] section button span {
    display: none !important;
}

div[data-testid="stFileUploader"] section button::after {
    content: "📁 Selecionar Fotos" !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

/* =========================================
   BOTÃO PRINCIPAL DE ENVIO (CTA)
========================================== */
.stButton button {
    background: #5a3b28 !important;
    color: white !important;
    border-radius: 12px !important;
    height: 48px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(90, 59, 40, 0.15) !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    background: #42291d !important;
    color: white !important;
}

.imagem-cesta img {
    border-radius: 12px;
    object-fit: cover;
    max-width: 100%;
}

/* =========================================
   AJUSTES RESPONSIVOS (MOBILE)
========================================== */
@media (max-width: 640px) {
    .block-container {
        padding-top: 0.5rem !important;
    }
    
    h1 {
        font-size: 22px !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 10px 12px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)


# ==========================================================
# LOGO E CABEÇALHO
# ==========================================================

logo = Path("assets/logo.webp")

if logo.exists():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(str(logo), width=120)

st.markdown("<h1 style='text-align:center;'>Doce Cesta Brasília</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#775a46; margin-bottom:12px;'>Cestas personalizadas para momentos especiais 💝</p>", unsafe_allow_html=True)


# ==========================================================
# CLIENTE (SEUS DADOS)
# ==========================================================

with st.container(border=True):
    st.markdown('<div class="secao-titulo">👤 Seus Dados</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome completo *", placeholder="Digite seu nome")
    with col2:
        telefone = st.text_input("Telefone *", placeholder="(61) 99999-9999")

    cpf = st.text_input("CPF *", placeholder="000.000.000-00")


# ==========================================================
# CESTAS
# ==========================================================

with st.container(border=True):
    st.markdown('<div class="secao-titulo">🎁 Escolha sua Cesta</div>', unsafe_allow_html=True)

    try:
        cestas = listar_cestas()
    except Exception as erro:
        st.error(f"Erro ao carregar cestas: {erro}")
        cestas = []

    cesta = None

    if cestas:
        opcoes_cestas = [{"id": None, "nome": "Selecione..."}] + cestas

        cesta_selecionada = st.selectbox(
            "Selecione a cesta",
            opcoes_cestas,
            format_func=lambda c: c["nome"],
            index=0
        )

        if cesta_selecionada["id"]:
            cesta = cesta_selecionada
    else:
        st.warning("Nenhuma cesta cadastrada.")


# ==========================================================
# INFORMAÇÕES VISUAIS DA CESTA
# ==========================================================

if cesta:
    with st.container(border=True):
        col1, col2 = st.columns([1, 1.8])

        with col1:
            if cesta.get("imagem"):
                st.markdown('<div class="imagem-cesta">', unsafe_allow_html=True)
                st.image(cesta["imagem"], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Imagem da cesta não cadastrada.")

        with col2:
            if cesta.get("descricao"):
                st.info(cesta["descricao"])

            if cesta.get("preco") is not None:
                try:
                    valor = float(cesta["preco"])
                    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f"**🎁 Valor da cesta:** <span style='font-size:16px; color:#2e7d32; font-weight:bold;'>{valor_formatado}</span>", unsafe_allow_html=True)
                except:
                    pass


# ==========================================================
# PERSONALIZAÇÃO DA CESTA
# ==========================================================

st.markdown("### 🍓 Personalize sua cesta")

selecoes_cliente = {}
configuracao_cesta = []

if cesta:
    configuracao_cesta = carregar_configuracao_cesta(cesta["id"])

    if configuracao_cesta:
        for grupo in configuracao_cesta:
            categoria = grupo.get("categoria", "Sem categoria")
            produtos = grupo.get("produtos", [])
            minimo = grupo.get("min_escolhas", 0)
            maximo = grupo.get("max_escolhas", 1)

            if not produtos:
                continue

            with st.container(border=True):
                st.markdown(f"**📦 {categoria}**")

                if maximo == 1:
                    escolhido = st.radio(
                        "Escolha uma opção",
                        produtos,
                        format_func=lambda p: p["nome"],
                        key=f"radio_{cesta['id']}_{categoria}"
                    )
                    if escolhido:
                        selecoes_cliente[categoria] = [escolhido]
                else:
                    escolhidos = st.multiselect(
                        f"Escolha entre {minimo} e {maximo} opções",
                        produtos,
                        format_func=lambda p: p["nome"],
                        max_selections=maximo,
                        key=f"multi_{cesta['id']}_{categoria}"
                    )
                    selecoes_cliente[categoria] = escolhidos
    else:
        st.info("Esta cesta ainda não possui produtos configurados.")
else:
    st.info("Escolha uma cesta para visualizar os produtos disponíveis.")


# ==========================================================
# COMPLEMENTOS (ADICIONAIS)
# ==========================================================

st.markdown("### 🎀 Complementos")
st.caption("Escolha itens adicionais para complementar sua cesta.")

adicionais_selecionados = []
polaroid = False

try:
    categorias_pedido = listar_categorias_pedido()
except Exception as erro:
    categorias_pedido = []
    st.error(f"Erro ao carregar complementos: {erro}")


categoria_adicionais = None
for categoria_item in categorias_pedido:
    nome_cat = categoria_item.get("nome", "").strip()
    if nome_cat.lower() == "adicionais":
        categoria_adicionais = categoria_item
        break

categorias_exibir = []
if categoria_adicionais:
    categorias_exibir.append(categoria_adicionais)


for categoria_item in categorias_exibir:
    nome_categoria = categoria_item.get("nome", "")
    produtos_categoria = listar_produtos_por_categoria_id(categoria_item["id"])

    if not produtos_categoria:
        continue

    with st.container(border=True):
        st.markdown(f"**{nome_categoria}**")
        colunas = st.columns(2)

        for indice, produto in enumerate(produtos_categoria):
            coluna = colunas[indice % 2]

            with coluna:
                preco = produto.get("preco")

                if preco is None:
                    texto_valor = "Consultar valor"
                else:
                    valor = float(preco)
                    texto_valor = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")

                label_produto = f"{produto['nome']} | {texto_valor}"

                marcado = st.checkbox(
                    label_produto,
                    key=f"complemento_{produto['id']}"
                )

                if marcado:
                    adicionais_selecionados.append({
                        "produto_id": produto["id"],
                        "nome": produto["nome"],
                        "preco": produto.get("preco"),
                        "categoria": nome_categoria
                    })

                    if produto["nome"].lower().strip() == "polaroid":
                        polaroid = True


# ==========================================================
# FOTOS POLAROID
# ==========================================================

if polaroid:
    with st.container(border=True):
        st.markdown('<div class="secao-titulo">📷 Fotos da Polaroid</div>', unsafe_allow_html=True)
        fotos = st.file_uploader(
            "Selecione as imagens",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="upload_polaroid"
        )
else:
    fotos = []


# ==========================================================
# PAGAMENTO
# ==========================================================

with st.container(border=True):
    st.markdown('<div class="secao-titulo">💳 Pagamento</div>', unsafe_allow_html=True)
    pagamento = st.radio(
        "Forma de pagamento",
        ["Pix", "Cartão de Crédito"],
        horizontal=True,
        key="forma_pagamento"
    )


# ==========================================================
# MENSAGEM & PEDIDO ESPECIAL
# ==========================================================

with st.container(border=True):
    st.markdown('<div class="secao-titulo">💌 Mensagem do Cartão</div>', unsafe_allow_html=True)
    mensagem = st.text_area(
        "Mensagem que acompanhará a cesta",
        height=80,
        placeholder="Digite uma mensagem especial para o destinatário...",
        key="mensagem_cliente"
    )

with st.container(border=True):
    st.markdown('<div class="secao-titulo">✨ Pedido Especial</div>', unsafe_allow_html=True)
    pedido_especial = st.text_area(
        "Alguma solicitação especial?",
        height=70,
        placeholder="Exemplo: entregar preferencialmente até as 09:00...",
        key="pedido_especial"
    )


# ==========================================================
# ENTREGA
# ==========================================================

with st.container(border=True):
    st.markdown('<div class="secao-titulo">📍 Entrega</div>', unsafe_allow_html=True)
    endereco = st.text_area(
        "Endereço de entrega",
        height=80,
        placeholder="Informe o endereço completo (Rua, Número, Bairro, Ponto de Referência)...",
        key="endereco"
    )

    col1, col2 = st.columns(2)
    with col1:
        data_entrega = st.date_input("📅 Data de entrega", format="DD/MM/YYYY")
    with col2:
        periodo_entrega = st.selectbox("🕘 Período", ["Manhã", "Tarde", "Noite"])


# ==========================================================
# CÁLCULO DOS VALORES
# ==========================================================

valor_cesta = 0
valor_adicionais = 0
tem_adicional_consulta = False

if cesta:
    try:
        valor_cesta = float(cesta.get("preco", 0))
    except:
        valor_cesta = 0

for item in adicionais_selecionados:
    if item["preco"] is None:
        tem_adicional_consulta = True
        continue
    try:
        valor_adicionais += float(item["preco"])
    except:
        pass

valor_estimado = valor_cesta + valor_adicionais


# ==========================================================
# RESUMO DO PEDIDO
# ==========================================================

if cesta:
    with st.container(border=True):
        st.markdown('<div class="secao-titulo">💰 Resumo do Pedido</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.caption("🎁 Valor da cesta")
            st.markdown(f"**R$ {valor_cesta:,.2f}**".replace(",", "X").replace(".", ",").replace("X","."))
        with col2:
            st.caption("🎀 Complementos")
            st.markdown(f"**R$ {valor_adicionais:,.2f}**".replace(",", "X").replace(".", ",").replace("X","."))

        st.divider()

        val_fmt = f"R$ {valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
        st.success(f"💝 Valor estimado: **{val_fmt}**")

        if tem_adicional_consulta:
            st.warning("⚠️ Existem itens com valor sob consulta. Nossa equipe confirmará o valor final.")


# ==========================================================
# BOTÃO ENVIO
# ==========================================================

st.write("")

enviar = st.button(
    "🎁 ENVIAR PEDIDO",
    use_container_width=True,
    type="primary",
    key="enviar_pedido"
)


# ==========================================================
# PROCESSAMENTO
# ==========================================================

if enviar:
    if not nome.strip():
        st.error("Informe o nome do cliente.")
        st.stop()

    if not cpf.strip():
        st.error("Informe o CPF.")
        st.stop()

    if not telefone.strip():
        st.error("Informe o telefone.")
        st.stop()

    if not cesta:
        st.error("Selecione uma cesta.")
        st.stop()

    produtos_escolhidos = []
    for cat_nome, itens in selecoes_cliente.items():
        for item in itens:
            produtos_escolhidos.append(f"{cat_nome}: {item['nome']}")

    complementos_texto = []
    for item in adicionais_selecionados:
        if item["preco"] is None:
            complementos_texto.append(f"{item['nome']} (Preço sob consulta)")
        else:
            complementos_texto.append(item["nome"])

    dados = {
        "cliente_nome": nome,
        "cliente_cpf": cpf,
        "cliente_telefone": telefone,
        "cesta_id": cesta["id"],
        "cesta_nome": cesta["nome"],
        "produtos": "\n".join(produtos_escolhidos),
        "adicionais": ", ".join(complementos_texto),
        "pagamento": pagamento,
        "mensagem": mensagem,
        "pedido_especial": pedido_especial,
        "endereco": endereco,
        "data_entrega": data_entrega.strftime("%Y-%m-%d"),
        "periodo_entrega": periodo_entrega,
        "status": "Recebido",
        "valor_frete": 0,
        "valor_total": valor_estimado
    }

    try:
        sucesso, pedido_id = salvar_pedido(dados)
    except Exception as erro:
        st.error(f"Erro ao salvar pedido: {erro}")
        st.stop()

    if sucesso:
        if adicionais_selecionados:
            salvar_adicionais_pedido(pedido_id, adicionais_selecionados)

        if polaroid and fotos:
            salvar_fotos(pedido_id, fotos)

        st.success("🎉 Pedido enviado com sucesso!")

        st.info(
"""
❤️ Obrigado por escolher a **Doce Cesta Brasília**!

Recebemos seu pedido.

Nossa equipe entrará em contato para confirmar:
✅ Valores dos itens sob consulta  
✅ Valor do frete  
✅ Valor final do pedido  
✅ Detalhes da entrega
"""
        )
    else:
        st.error(f"Erro ao salvar pedido: {pedido_id}")


# ==========================================================
# RODAPÉ E LINK ADMIN
# ==========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; font-size:12px; color:#888; padding:10px;">
    Doce Cesta Brasília © 2026
    </div>
    """,
    unsafe_allow_html=True
)

st.page_link(
    "pages/99_Admin.py",
    label="Área Administrativa",
    icon="🔒"
)
