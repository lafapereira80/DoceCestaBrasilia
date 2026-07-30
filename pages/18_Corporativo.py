import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config.supabase import supabase
from services.cesta_service import listar_cestas
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Vendas Corporativas", page_icon="🏢", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# =====================================================
# CSS PREMIUM (PADRÃO ADMIN)
# =====================================================
st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }
h1, h2, h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-bottom: 8px !important; letter-spacing: -0.3px; }

/* Banner / Cabeçalho Luxuoso */
.header-banner {
    display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 6px; margin-bottom: 2rem;
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 25px 20px;
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
}
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; text-align: center;}
.header-subtitle { font-size: 14px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 0px !important; text-align: center;}

/* Cards do Corporativo */
.corp-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 24px;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.02); margin-bottom: 15px;
}
.corp-title { font-size: 18px; font-weight: 800; color: #c5721f; margin-bottom: 15px; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px;}

/* Proposta Preview */
.proposta-preview {
    background: #ffffff; border: 1px solid #dfcdbb; border-radius: 12px; padding: 40px;
    font-family: 'Arial', sans-serif; color: #333; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
.proposta-header { text-align: center; border-bottom: 3px solid #137333; padding-bottom: 15px; margin-bottom: 25px; }
.proposta-total { font-size: 22px; font-weight: bold; color: #137333; text-align: right; margin-top: 20px; border-top: 2px solid #e8ddd3; padding-top: 15px;}

/* Botões Nativos */
div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 800 !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(19, 115, 51, 0.2) !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background: linear-gradient(135deg, #0f5c28 0%, #093818) !important; transform: translateY(-2px) !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Vendas Corporativas (B2B)</h1>
    <p class="header-subtitle">Gestão de propostas, empresas parceiras e orçamentos em lote 🏢</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# CACHE DE CESTAS
# =====================================================
@st.cache_data(ttl=60, show_spinner=False)
def obter_cestas_admin():
    cestas = listar_cestas()
    return sorted([c for c in cestas if c.get("ativa", True)], key=lambda x: x.get("nome", ""))

cestas_disponiveis = obter_cestas_admin()

# =====================================================
# ABAS DO MÓDULO
# =====================================================
aba_proposta, aba_empresas, aba_dashboard = st.tabs(["📄 Gerador de Propostas", "🤝 Gestão de Empresas", "📊 Dashboard B2B"])

# =====================================================
# ABA 1: GERADOR DE PROPOSTAS COMERCIAIS
# =====================================================
with aba_proposta:
    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    st.markdown('<div class="corp-title">⚙️ Montar Novo Orçamento</div>', unsafe_allow_html=True)
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        empresa_nome = st.text_input("Nome da Empresa / Cliente B2B *", placeholder="Ex: Sicoob, Tribunal de Justiça, etc.")
        contato_nome = st.text_input("A/C (Nome do Contato do RH/Compras)", placeholder="Ex: Ana Clara - Coord. de RH")
    with col_e2:
        validade = st.date_input("Validade da Proposta", value=datetime.now() + timedelta(days=7))
        motivo = st.text_input("Motivo / Evento (Opcional)", placeholder="Ex: Brindes de Fim de Ano, Dia da Mulher")

    st.markdown("#### 🎁 Adicionar Itens ao Orçamento")
    
    if "itens_orcamento" not in st.session_state:
        st.session_state["itens_orcamento"] = []

    col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
    with col_i1:
        cesta_selecionada = st.selectbox("Selecione o Produto", [{"id": None, "nome": "Escolha uma cesta...", "preco": 0}] + cestas_disponiveis, format_func=lambda x: x["nome"])
    with col_i2:
        quantidade = st.number_input("Qtd", min_value=1, step=1)
    with col_i3:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Inserir Item", use_container_width=True):
            if cesta_selecionada.get("id"):
                st.session_state["itens_orcamento"].append({
                    "nome": cesta_selecionada["nome"],
                    "preco_unitario": float(cesta_selecionada.get("preco", 0)),
                    "quantidade": quantidade,
                    "descricao": cesta_selecionada.get("descricao", "")
                })
                st.rerun()

    # Tabela de Itens Adicionados
    if st.session_state["itens_orcamento"]:
        st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
        df_itens = pd.DataFrame(st.session_state["itens_orcamento"])
        df_itens["Subtotal"] = df_itens["preco_unitario"] * df_itens["quantidade"]
        
        st.write("📋 **Itens já inclusos:**")
        st.dataframe(
            df_itens[["nome", "quantidade", "preco_unitario", "Subtotal"]].style.format({"preco_unitario": "R$ {:.2f}", "Subtotal": "R$ {:.2f}"}),
            use_container_width=True, hide_index=True
        )
        
        if st.button("🧹 Limpar Todos os Itens"):
            st.session_state["itens_orcamento"] = []
            st.rerun()

    st.markdown("#### 💰 Negociação Final")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        desconto_perc = st.number_input("Desconto de Lote (%)", min_value=0.0, max_value=100.0, step=1.0)
    with col_d2:
        frete_lote = st.number_input("Logística / Frete Total (R$)", min_value=0.0, step=10.0)
    with col_d3:
        prazo_pagamento = st.selectbox("Condição de Pagamento", ["50% Sinal / 50% na Entrega", "100% Antecipado (PIX)", "Faturamento 15 dias (Boleto)", "Cartão de Crédito"])

    st.markdown('</div>', unsafe_allow_html=True)

    # =================================================
    # PREVIEW DA PROPOSTA (PDF VISUAL)
    # =================================================
    if st.session_state["itens_orcamento"] and empresa_nome:
        st.markdown("### 👁️ Preview do Documento")
        
        total_bruto = sum(item["preco_unitario"] * item["quantidade"] for item in st.session_state["itens_orcamento"])
        valor_desconto = total_bruto * (desconto_perc / 100)
        total_liquido = total_bruto - valor_desconto + frete_lote

        linhas_html = ""
        for item in st.session_state["itens_orcamento"]:
            desc_curta = (item['descricao'][:80] + '...') if item['descricao'] and len(item['descricao']) > 80 else (item['descricao'] or '')
            linhas_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #f5eee6;"><b>{item['nome']}</b><br><span style="font-size:11px; color:#666;">{desc_curta}</span></td>
                <td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: center;">{item['quantidade']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: right;">R$ {item['preco_unitario']:,.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: right;">R$ {(item['preco_unitario'] * item['quantidade']):,.2f}</td>
            </tr>
            """

        st.markdown(f"""
        <div class="proposta-preview">
            <div class="proposta-header">
                <h2 style="color: #137333; margin-bottom: 5px; font-weight: 800;">PROPOSTA COMERCIAL</h2>
                <p style="margin: 0; color: #555; font-size: 14px;">Doce Cesta Brasília - Gestão de Encantamento B2B</p>
            </div>
            
            <table style="width: 100%; border: none; margin-bottom: 25px;">
                <tr>
                    <td style="width: 60%; vertical-align: top;">
                        <p style="margin:2px 0;"><b>Para:</b> {empresa_nome}</p>
                        <p style="margin:2px 0;"><b>A/C:</b> {contato_nome}</p>
                        <p style="margin:2px 0;"><b>Ref:</b> {motivo or 'Orçamento de Produtos'}</p>
                    </td>
                    <td style="width: 40%; vertical-align: top; text-align: right;">
                        <p style="margin:2px 0;"><b>Data Emissão:</b> {datetime.now().strftime("%d/%m/%Y")}</p>
                        <p style="margin:2px 0;"><b>Validade:</b> {validade.strftime("%d/%m/%Y")}</p>
                    </td>
                </tr>
            </table>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <tr style="background-color: #faf7f3;">
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e8ddd3;">Descrição do Item</th>
                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #e8ddd3;">Qtd</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #e8ddd3;">V. Unitário</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #e8ddd3;">Subtotal</th>
                </tr>
                {linhas_html.replace(",", "X").replace(".", ",").replace("X", ".")}
            </table>
            
            <div style="margin-top: 25px; text-align: right; font-size: 15px;">
                <p style="margin: 4px 0;">Subtotal: R$ {total_bruto:,.2f}</p>
                <p style="margin: 4px 0; color: #c5221f;">Desconto ({desconto_perc}%): - R$ {valor_desconto:,.2f}</p>
                <p style="margin: 4px 0;">Logística/Frete: R$ {frete_lote:,.2f}</p>
            </div>
            
            <div class="proposta-total">
                TOTAL GERAL: R$ {total_liquido:,.2f}
            </div>
            
            <div style="margin-top: 40px; font-size: 13px; color: #666; background: #faf7f3; padding: 15px; border-radius: 8px;">
                <b style="color: #4a2e1b;">Condições Comerciais:</b><br>
                • Forma de Pagamento: {prazo_pagamento}<br>
                • O pedido só será agendado para produção após o aceite formal deste documento.<br>
                • Produtos sujeitos a alteração de marca conforme disponibilidade de estoque, mantendo a mesma qualidade.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.info("💡 Tire um print desta área (ou salve como PDF no navegador: Ctrl+P -> Salvar como PDF) e envie diretamente para o WhatsApp ou E-mail da empresa!")

# =====================================================
# ABA 2 E 3: GESTÃO E DASHBOARD B2B (FUTURO)
# =====================================================
with aba_empresas:
    st.markdown('<div class="corp-card"><div class="corp-title">🏢 Carteira de Clientes Corporativos</div><p>Em breve: Banco de dados com CNPJ, histórico de orçamentos e contato dos decisores.</p><button disabled style="padding:8px 16px; border-radius:8px;">➕ Cadastrar Empresa</button></div>', unsafe_allow_html=True)

with aba_dashboard:
    st.markdown('<div class="corp-card"><div class="corp-title">📊 Inteligência B2B</div><p>Módulo de BI exclusivo para análise de vendas por CNPJ e taxas de conversão de orçamentos.</p></div>', unsafe_allow_html=True)
