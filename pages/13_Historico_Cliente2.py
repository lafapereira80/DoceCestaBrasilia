import streamlit as st

from config.supabase import supabase

from utils.menu import (
    configurar_pagina,
    menu_lateral
)

from utils.permissao import (
    administrador_operador
)


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Histórico do Cliente",
    page_icon="👤",
    layout="wide"
)

# CONTROLE DE ACESSO
configurar_pagina()
menu_lateral()
administrador_operador()


# =====================================================
# CSS ULTRA COMPACTO E ISOLADO
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1200px;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

h1 {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-top: 4px !important;
    margin-bottom: 4px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 12px !important;
}

/* =========================================
   CONTAINERS E CARDS COMPACTOS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.card-title {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-bottom: 6px !important;
}

.kpi-title {
    font-size: 11px !important;
    font-weight: 700;
    color: #775a46;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 2px;
}

.kpi-value {
    font-size: 16px !important;
    font-weight: 700;
    color: #2e7d32;
}

.kpi-value-neutral {
    font-size: 16px !important;
    font-weight: 700;
    color: #5a3b28;
}

/* Ajustes direcionados para botões */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 13px !important;
    border-radius: 8px !important;
    min-height: 34px !important;
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# VERIFICA CLIENTE SELECIONADO
# =====================================================

if "cliente_cpf" not in st.session_state:
    st.error("Nenhum cliente selecionado.")
    if st.button("⬅ Voltar"):
        st.switch_page("pages/03_Clientes.py")
    st.stop()

cpf = st.session_state["cliente_cpf"]


# =====================================================
# BUSCA PEDIDOS ENTREGUES
# =====================================================

try:
    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("cliente_cpf", cpf)
        .eq("status", "Entregue")
        .order("created_at", desc=True)
        .execute()
    )
    pedidos = resposta.data or []

except Exception as erro:
    st.error(f"Erro ao carregar histórico: {erro}")
    st.stop()

if not pedidos:
    st.warning("Cliente sem pedidos entregues.")
    st.stop()

cliente = pedidos[0]


# =====================================================
# FORMATAÇÃO DE MOEDA
# =====================================================

def moeda(valor):
    try:
        return (
            f"R$ {float(valor):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X",".")
        )
    except:
        return "R$ 0,00"


# =====================================================
# TÍTULO
# =====================================================

st.title("👤 Histórico do Cliente")
st.caption("Visão detalhada do perfil e compras entregues.")
st.divider()


# =====================================================
# RESUMO DO CLIENTE & METRICAS (CARD INTEGRADO)
# =====================================================

total_pedidos = len(pedidos)
valor_total = sum(float(p.get("valor_total") or 0) for p in pedidos)
ticket_medio = valor_total / total_pedidos if total_pedidos > 0 else 0
ultima_compra = pedidos[0].get("data_entrega", "-")

with st.container(border=True):
    col_info, col_kpis = st.columns([1.2, 2])

    with col_info:
        st.markdown('<div class="card-title">👤 Dados do Cliente</div>', unsafe_allow_html=True)
        st.write(f"**Nome:** {cliente.get('cliente_nome', '-')}")
        st.write(f"**CPF:** {cliente.get('cliente_cpf', '-')}")
        st.write(f"**Telefone:** 📱 {cliente.get('cliente_telefone', '-')}")

    with col_kpis:
        st.markdown('<div class="card-title">📊 Resumo Financeiro</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown('<div class="kpi-title">Pedidos</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value-neutral">{total_pedidos}</div>', unsafe_allow_html=True)
        with k2:
            st.markdown('<div class="kpi-title">Valor Gasto</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{moeda(valor_total)}</div>', unsafe_allow_html=True)
        with k3:
            st.markdown('<div class="kpi-title">Ticket Médio</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value-neutral">{moeda(ticket_medio)}</div>', unsafe_allow_html=True)
        with k4:
            st.markdown('<div class="kpi-title">Última Compra</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value-neutral">{str(ultima_compra)}</div>', unsafe_allow_html=True)


st.divider()


# =====================================================
# HISTÓRICO DE COMPRAS (COMPACTO SIDE-BY-SIDE)
# =====================================================

st.subheader(f"📋 Histórico de Compras ({len(pedidos)})")

for i, pedido in enumerate(pedidos):
    with st.container(border=True):
        st.markdown(
            f'<div class="card-title">🎁 {pedido.get("cesta_nome","-")} <span style="font-size:12px; font-weight:normal; color:#775a46;">(Pedido #{i+1})</span></div>',
            unsafe_allow_html=True
        )

        col_esq, col_dir = st.columns([1.1, 1])

        # Coluna da Esquerda: Produtos e Adicionais
        with col_esq:
            st.markdown("**📦 Produtos da Cesta**")
            produtos = pedido.get("produtos", "")
            if produtos:
                st.code(produtos, language=None)
            else:
                st.caption("Nenhum produto registrado.")

            st.markdown("**🎀 Adicionais**")
            adicionais = pedido.get("adicionais", "")
            if adicionais:
                st.success(adicionais)
            else:
                st.caption("Nenhum adicional.")

        # Coluna da Direita: Detalhes, Mensagens, Endereço e Valores
        with col_dir:
            # Info Geral em linha
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption(f"🗓️ Entrega: **{pedido.get('data_entrega','-')}**")
            with c2:
                st.caption(f"📌 Status: **{pedido.get('status','-')}**")
            with c3:
                st.caption(f"💳 Pgto: **{pedido.get('pagamento','-')}**")

            # Mensagem
            mensagem = pedido.get("mensagem", "")
            if mensagem:
                st.markdown("**💌 Mensagem:**")
                st.text_area("", value=mensagem, disabled=True, height=50, key=f"msg_{pedido['id']}")

            # Pedido Especial
            especial = pedido.get("pedido_especial", "")
            if especial:
                st.markdown("**✨ Pedido Especial:**")
                st.text_area("", value=especial, disabled=True, height=50, key=f"esp_{pedido['id']}")

            # Endereço
            st.markdown("**📍 Endereço:**")
            st.text_area("", value=pedido.get("endereco", ""), disabled=True, height=50, key=f"end_{pedido['id']}")

            # Frete e Total
            v1, v2 = st.columns(2)
            with v1:
                st.caption(f"🚚 Frete: **{moeda(pedido.get('valor_frete') or 0)}**")
            with v2:
                st.markdown(f"💰 **Total:** <span class='kpi-value'>{moeda(pedido.get('valor_total') or 0)}</span>", unsafe_allow_html=True)

            # Fotos
            if pedido.get("foto_excluida"):
                st.caption("📷 *Fotos removidas automaticamente após conclusão.*")
            else:
                st.caption("📷 *Fotos ainda disponíveis.*")


# =====================================================
# VOLTAR
# =====================================================

st.divider()

if st.button("⬅ Voltar para Clientes", use_container_width=True, key="voltar_clientes"):
    st.session_state.pop("cliente_cpf", None)
    st.switch_page("pages/03_Clientes.py")
