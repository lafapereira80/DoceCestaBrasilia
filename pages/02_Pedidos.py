import streamlit as st
import pandas as pd

from services.pedido_service import (
    listar_pedidos_ativos,
    excluir_pedido_completo,
    buscar_pedido
)

from utils.menu import (
    configurar_pagina,
    menu_lateral
)

from utils.permissao import (
    administrador_operador
)

from utils.impressao_pedido import (
    gerar_pdf_pedidos
)


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Pedidos",
    page_icon="📋",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CONTROLE DE IMPRESSÃO
# =====================================================

if "pedidos_impressao" not in st.session_state:
    st.session_state["pedidos_impressao"] = []

if "pdf_gerado" not in st.session_state:
    st.session_state["pdf_gerado"] = None


# =====================================================
# FUNÇÃO CHECKBOX IMPRESSÃO
# =====================================================

def atualizar_selecao_impressao(pedido_id):
    chave = f"imprimir_{pedido_id}"
    if st.session_state.get(chave):
        if pedido_id not in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].append(pedido_id)
    else:
        if pedido_id in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].remove(pedido_id)


# =====================================================
# CSS COMPACTO E ISOLADO
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}

h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-top: 15px !important;
    margin-bottom: 8px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINERS DOS PEDIDOS (CARDS LINHA)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 6px 12px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.08);
}

/* =========================================
   BADGES DE STATUS VISUAL
========================================== */
.badge-status {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px !important;
    text-align: center;
}

.badge-pago {
    background-color: #e6f4ea;
    color: #137333;
}

.badge-recebido {
    background-color: #fef7e0;
    color: #b06000;
}

.badge-desistencia {
    background-color: #fce8e6;
    color: #c5221f;
}

/* =========================================
   ELEMENTOS DE TEXTO E VALORES
========================================== */
.cliente-nome {
    font-weight: 700;
    color: #333;
    font-size: 14px !important;
}

.valor-pedido {
    font-weight: 700;
    color: #2e7d32;
    font-size: 14px !important;
}

.cabecalho-tabela {
    font-weight: 700;
    color: #775a46;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

/* Botões da Tabela */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 13px !important;
    padding: 2px 8px !important;
    border-radius: 8px !important;
    min-height: 32px !important;
}

div[data-testid="stCheckbox"] {
    margin-top: 4px;
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# TÍTULO
# =====================================================

st.title("📋 Gestão de Pedidos")
st.caption("Controle dos pedidos em andamento.")
st.divider()


# =====================================================
# CARREGA PEDIDOS
# =====================================================

try:
    pedidos = listar_pedidos_ativos()
except Exception as erro:
    st.error(f"Erro ao carregar pedidos: {erro}")
    st.stop()

if not pedidos:
    st.info("Nenhum pedido em andamento.")
    st.stop()

df = pd.DataFrame(pedidos)


# =====================================================
# ORDENAÇÃO
# =====================================================

if "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at", ascending=False)


# =====================================================
# PESQUISA
# =====================================================

st.subheader("🔍 Pesquisar cliente")
pesquisa = st.text_input("", placeholder="Digite o nome do cliente...")

if pesquisa.strip():
    df = df[
        df["cliente_nome"]
        .fillna("")
        .str.contains(pesquisa, case=False)
    ]


# =====================================================
# STATUS VISUAL (TAGS ENCAPSULADAS)
# =====================================================

def status_visual_html(status):
    if status == "Pago":
        return '<span class="badge-status badge-pago">🟢 Pago</span>'
    if status == "Recebido":
        return '<span class="badge-status badge-recebido">🟡 Recebido</span>'
    if status == "Desistência":
        return '<span class="badge-status badge-desistencia">🔴 Desistência</span>'
    return f'<span class="badge-status">{status}</span>'


# =====================================================
# LISTAGEM
# =====================================================

def mostrar_lista(
    titulo,
    status_filtro,
    permitir_exclusao=False,
    permitir_impressao=False
):
    pedidos_status = df[df["status"] == status_filtro]

    if pedidos_status.empty:
        return

    st.subheader(titulo)

    for _, pedido in pedidos_status.iterrows():
        # Busca dados atualizados
        try:
            pedido_atualizado = buscar_pedido(pedido["id"])
            if pedido_atualizado:
                pedido = pedido_atualizado
        except Exception:
            pass

        with st.container(border=True):
            col_check, col_info1, col_info2, col_status, col_valor, col_acoes = st.columns(
                [1.2, 3.2, 2.8, 1.8, 1.8, 1.2] if permitir_impressao else [3.8, 3.0, 2.0, 2.0, 1.2]
            )

            # Seleção de Impressão
            if permitir_impressao:
                with col_check:
                    st.checkbox(
                        "🖨️",
                        key=f"imprimir_{pedido['id']}",
                        on_change=atualizar_selecao_impressao,
                        args=(pedido["id"],),
                        help="Selecionar para impressão"
                    )

            # Coluna 1: Cliente & Telefone
            col_c1 = col_info1 if permitir_impressao else col_check
            with col_c1:
                nome_cliente = str(pedido.get("cliente_nome", "-")).strip()
                nome_cliente = " ".join(nome_cliente.split())
                st.markdown(f'<div class="cliente-nome">{nome_cliente}</div>', unsafe_allow_html=True)
                st.caption(f"📱 {pedido.get('cliente_telefone', '-')}")

            # Coluna 2: Cesta & Data de Entrega
            col_c2 = col_info2 if permitir_impressao else col_info1
            with col_c2:
                st.write(f"🎁 **{pedido.get('cesta_nome','-')}**")
                st.caption(f"🗓️ Entrega: {pedido.get('data_entrega','-')}")

            # Coluna 3: Status
            col_c3 = col_status if permitir_impressao else col_info2
            with col_c3:
                st.markdown(
                    status_visual_html(pedido.get("status", "-")),
                    unsafe_allow_html=True
                )

            # Coluna 4: Valor
            col_c4 = col_valor if permitir_impressao else col_status
            with col_c4:
                valor = float(pedido.get("valor_total", 0) or 0)
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                st.markdown(f'<div class="valor-pedido">{valor_formatado}</div>', unsafe_allow_html=True)

            # Coluna 5: Botões de Ação
            col_c5 = col_acoes if permitir_impressao else col_valor
            with col_c5:
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    if st.button("👁️", key=f"abrir_{pedido['id']}", help="Abrir pedido", use_container_width=True):
                        st.session_state["pedido_aberto"] = pedido["id"]
                        st.switch_page("pages/09_Detalhes_Pedido.py")

                if permitir_exclusao:
                    with sub_col2:
                        if st.button("🗑️", key=f"excluir_{pedido['id']}", help="Excluir pedido", use_container_width=True):
                            sucesso, mensagem = excluir_pedido_completo(pedido["id"])
                            if sucesso:
                                st.success(mensagem)
                                st.rerun()
                            else:
                                st.error(mensagem)


# =====================================================
# ORDEM DOS PEDIDOS
# =====================================================

mostrar_lista("📥 Pedidos Recebidos", "Recebido")

mostrar_lista("💰 Pedidos Pagos", "Pago", permitir_impressao=True)

mostrar_lista(
    "❌ Desistências",
    "Desistência",
    permitir_exclusao=(usuario.get("perfil") == "Administrador")
)


# =====================================================
# IMPRESSÃO DOS PEDIDOS SELECIONADOS
# =====================================================

if st.session_state["pedidos_impressao"]:
    st.divider()
    st.subheader("🖨️ Impressão de Pedidos")

    quantidade = len(st.session_state["pedidos_impressao"])
    st.success(f"{quantidade} pedido(s) selecionado(s) para impressão.")

    formato_impressao = st.radio(
        "Formato do PDF",
        [
            "📄 Folha A4 - 12 pedidos por página",
            "🧾 Individual 7x10 cm"
        ],
        horizontal=True
    )

    if st.button("📄 Gerar PDF", use_container_width=True, type="primary"):
        pedidos_pdf = []
        for pedido_id in st.session_state["pedidos_impressao"]:
            pedido = buscar_pedido(pedido_id)
            if pedido:
                pedidos_pdf.append(pedido)

        if pedidos_pdf:
            pdf = gerar_pdf_pedidos(pedidos_pdf, formato_impressao)
            st.session_state["pdf_gerado"] = pdf
            st.success("✅ PDF gerado com sucesso!")

    if st.session_state["pdf_gerado"]:
        st.download_button(
            "⬇️ Baixar PDF",
            st.session_state["pdf_gerado"],
            file_name="pedidos_producao.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# =====================================================
# TOTAL
# =====================================================

st.divider()
st.caption(f"Total de pedidos ativos: {len(df)}")
