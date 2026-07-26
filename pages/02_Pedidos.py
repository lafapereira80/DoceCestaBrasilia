import streamlit as st
import pandas as pd
from datetime import datetime

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
    # Se a seleção mudar, limpa o PDF antigo da memória
    st.session_state["pdf_gerado"] = None
    
    chave = f"imprimir_{pedido_id}"
    if st.session_state.get(chave):
        if pedido_id not in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].append(pedido_id)
    else:
        if pedido_id in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].remove(pedido_id)


# =====================================================
# FORMATADOR DE DATA BRASILEIRO (DD/MM/AAAA)
# =====================================================

def formatar_data(data_str):
    if not data_str:
        return "-"
    try:
        dt = pd.to_datetime(data_str)
        if pd.isna(dt):
            return str(data_str)
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(data_str)


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
   CONTAINERS DOS PEDIDOS E REVISÃO
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

.preview-impressao {
    background-color: #fffbf7;
    border-left: 4px solid #b06000 !important;
}

/* =========================================
   BADGES DE STATUS VISUAL E LABELS
========================================== */
.badge-status {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px !important;
    text-align: center;
}

.badge-pago { background-color: #e6f4ea; color: #137333; }
.badge-recebido { background-color: #fef7e0; color: #b06000; }
.badge-desistencia { background-color: #fce8e6; color: #c5221f; }

.info-label {
    font-weight: 800;
    color: #9d7d65;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
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

/* Botões da Tabela */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] button {
    font-size: 14px !important;
    padding: 2px !important;
    border-radius: 8px !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
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
st.caption("Acompanhamento do fluxo completo de compras.")
st.divider()


# =====================================================
# CARREGA PEDIDOS
# =====================================================

try:
    pedidos = listar_pedidos_ativos()
except Exception as erro:
    st.error(f"Erro ao carregar pedidos: {erro}")
    pedidos = []

df = pd.DataFrame(pedidos) if pedidos else pd.DataFrame(columns=["id", "cliente_nome", "status", "created_at"])


# =====================================================
# ORDENAÇÃO E PESQUISA
# =====================================================

if not df.empty and "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at", ascending=False)

st.subheader("🔍 Pesquisar cliente")
pesquisa = st.text_input("", placeholder="Digite o nome do cliente...")

if pesquisa.strip() and not df.empty:
    df = df[df["cliente_nome"].fillna("").str.contains(pesquisa, case=False)]


# =====================================================
# STATUS VISUAL
# =====================================================

def status_visual_html(status):
    status_str = str(status).strip().capitalize()
    if status_str == "Pago":
        return '<span class="badge-status badge-pago">🟢 Pago</span>'
    elif status_str == "Recebido":
        return '<span class="badge-status badge-recebido">🟡 Recebido</span>'
    elif status_str == "Desistência" or status_str == "Desistencia":
        return '<span class="badge-status badge-desistencia">🔴 Desistência</span>'
    return f'<span class="badge-status">{status}</span>'


# =====================================================
# FUNÇÃO DE RENDERIZAÇÃO DA LISTA DE PEDIDOS
# =====================================================

def mostrar_lista(titulo, status_filtro, permitir_exclusao=False, permitir_impressao=False):
    st.subheader(titulo)

    if df.empty or "status" not in df.columns:
        st.info(f"Nenhum pedido registrado em '{titulo.replace('📥 ', '').replace('💰 ', '').replace('❌ ', '')}'.")
        return

    pedidos_status = df[df["status"].astype(str).str.strip().str.capitalize() == status_filtro.capitalize()]

    if pedidos_status.empty:
        st.info(f"Nenhum pedido nesta etapa no momento.")
        return

    for _, pedido in pedidos_status.iterrows():
        try:
            pedido_atualizado = buscar_pedido(pedido["id"])
            if pedido_atualizado:
                pedido = pedido_atualizado
        except Exception:
            pass

        with st.container(border=True):
            if permitir_impressao:
                col_check, col_info1, col_info2, col_status, col_valor, col_acoes = st.columns([1.2, 3.2, 2.8, 1.8, 1.8, 1.5])
            else:
                col_info1, col_info2, col_status, col_valor, col_acoes = st.columns([3.8, 3.0, 2.0, 2.0, 1.5])

            if permitir_impressao:
                with col_check:
                    st.checkbox(
                        "🖨️",
                        key=f"imprimir_{pedido['id']}",
                        on_change=atualizar_selecao_impressao,
                        args=(pedido["id"],),
                        help="Selecionar para impressão"
                    )

            with col_info1:
                nome_cliente = str(pedido.get("cliente_nome", "-")).strip()
                nome_cliente = " ".join(nome_cliente.split())
                st.markdown(f'<div class="cliente-nome">{nome_cliente}</div>', unsafe_allow_html=True)
                st.caption(f"📱 {pedido.get('cliente_telefone', '-')}")

            with col_info2:
                st.write(f"🎁 **{pedido.get('cesta_nome','-')}**")
                data_formatada = formatar_data(pedido.get('data_entrega'))
                st.caption(f"🗓️ Entrega: {data_formatada}")

            with col_status:
                st.markdown(status_visual_html(pedido.get("status", "-")), unsafe_allow_html=True)

            with col_valor:
                valor = float(pedido.get("valor_total", 0) or 0)
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                st.markdown(f'<div class="valor-pedido">{valor_formatado}</div>', unsafe_allow_html=True)

            with col_acoes:
                if permitir_exclusao:
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        if st.button("👁️", key=f"abrir_{pedido['id']}", help="Abrir pedido", use_container_width=True):
                            st.session_state["pedido_aberto"] = pedido["id"]
                            st.switch_page("pages/09_Detalhes_Pedido.py")
                    with sub_col2:
                        if st.button("🗑️", key=f"excluir_{pedido['id']}", help="Excluir pedido", use_container_width=True):
                            sucesso, mensagem = excluir_pedido_completo(pedido["id"])
                            if sucesso:
                                st.success(mensagem)
                                st.rerun()
                            else:
                                st.error(mensagem)
                else:
                    if st.button("👁️", key=f"abrir_{pedido['id']}", help="Abrir pedido", use_container_width=True):
                        st.session_state["pedido_aberto"] = pedido["id"]
                        st.switch_page("pages/09_Detalhes_Pedido.py")


# =====================================================
# FLUXO COMPLETO DE PEDIDOS NA TELA
# =====================================================

mostrar_lista("📥 Pedidos Recebidos", "Recebido")
mostrar_lista("💰 Pedidos Pagos", "Pago", permitir_impressao=True)
mostrar_lista("❌ Desistências", "Desistência", permitir_exclusao=(usuario.get("perfil") == "Administrador"))


# =====================================================
# IMPRESSÃO DOS PEDIDOS SELECIONADOS (NOVO LAYOUT)
# =====================================================

if st.session_state["pedidos_impressao"]:
    st.divider()
    st.subheader("🖨️ Impressão de Pedidos")

    # Resgata os dados completos apenas dos pedidos marcados no Checkbox
    pedidos_selecionados_dados = []
    for pid in st.session_state["pedidos_impressao"]:
        pedido_completo = buscar_pedido(pid)
        if pedido_completo:
            pedidos_selecionados_dados.append(pedido_completo)

    quantidade = len(pedidos_selecionados_dados)
    st.success(f"✅ {quantidade} pedido(s) selecionado(s) e pronto(s) para impressão.")

    # --- PAINEL DE REVISÃO DOS PEDIDOS ---
    st.markdown("#### 🛒 Revisão dos Pedidos Selecionados")
    for ped in pedidos_selecionados_dados:
        # Pega as variáveis e trata valores nulos
        nome_comprador = ped.get('cliente_nome', '-')
        tel_comprador = ped.get('cliente_telefone', '-')
        nome_homenageado = ped.get('destinatario_nome', '-')
        tel_homenageado = ped.get('destinatario_telefone', '-')
        nome_cesta = ped.get('cesta_nome', '-')
        data_entrega = formatar_data(ped.get('data_entrega'))
        periodo = ped.get('periodo_entrega', '-')
        horario = ped.get('horario_combinado', '')
        horario_str = f" ({horario})" if horario else ""

        # Monta um Card visual para cada pedido
        st.markdown(
            f"""
            <div data-testid="stVerticalBlockBorderWrapper" class="preview-impressao">
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px;">
                        <div class="info-label">👤 Comprador</div>
                        <div style="font-weight: 600; color: #333;">{nome_comprador}</div>
                        <div style="font-size: 12px; color: #666;">📱 {tel_comprador}</div>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <div class="info-label">💝 Homenageado</div>
                        <div style="font-weight: 600; color: #333;">{nome_homenageado}</div>
                        <div style="font-size: 12px; color: #666;">📱 {tel_homenageado}</div>
                    </div>
                    <div style="flex: 1.5; min-width: 250px;">
                        <div class="info-label">🚚 Cesta e Entrega</div>
                        <div style="font-weight: 600; color: #333;">🎁 {nome_cesta}</div>
                        <div style="font-size: 12px; color: #666;">🗓️ {data_entrega} | 🕒 {periodo}{horario_str}</div>
                    </div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.write("") # Quebra de linha suave

    # --- BOTÕES E GERAÇÃO DE PDF ---
    formato_impressao = st.radio(
        "Formato do PDF",
        ["📄 Folha A4 - 12 pedidos por página", "🧾 Individual 7x10 cm"],
        horizontal=True
    )

    if st.button("📄 Gerar PDF Definitivo", use_container_width=True, type="primary"):
        if pedidos_selecionados_dados:
            pdf = gerar_pdf_pedidos(pedidos_selecionados_dados, formato_impressao)
            st.session_state["pdf_gerado"] = pdf
            st.success("✅ PDF gerado com sucesso! Clique no botão abaixo para salvar o arquivo.")

    if st.session_state.get("pdf_gerado"):
        st.download_button(
            "⬇️ Baixar PDF",
            st.session_state["pdf_gerado"],
            file_name=f"pedidos_producao_{datetime.now().strftime('%d%m%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption(f"Total de pedidos ativos no painel: {len(df)}")
