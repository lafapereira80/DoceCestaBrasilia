import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.pedido_service import salvar_pedido
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
# CSS PREMIUM E OTIMIZAÇÃO PARA IMPRESSÃO (PDF)
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

/* Proposta Preview (Visual do PDF) */
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

/* Tabela Histórico */
div[data-testid="stDataFrame"] { border-radius: 10px !important; border: 1px solid #e8ddd3 !important; }

/* =========================================
   REGRAS DE IMPRESSÃO (CTRL+P PARA PDF)
========================================== */
@media print {
    /* Esconde botões, menus laterais, banners e abas na hora de gerar o PDF */
    header, footer, section[data-testid="stSidebar"], .stAppDeployMenu, 
    div[data-testid="stButton"], .header-banner, .stTabs > div[role="tablist"],
    div[data-testid="stCheckbox"], div[data-baseweb="select"], input, .corp-card {
        display: none !important;
    }
    
    /* Remove padding do container para ocupar a folha toda */
    .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important;}
    
    /* Tira sombra e borda redonda da proposta na hora da impressão */
    .proposta-preview {
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
    }
    
    body { background-color: white !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Vendas Corporativas (B2B)</h1>
    <p class="header-subtitle">Gere orçamentos em lote, PDF, textos para WhatsApp e registre pedidos 🏢</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# CACHE DE DADOS
# =====================================================
@st.cache_data(ttl=60, show_spinner=False)
def obter_cestas_admin():
    cestas = listar_cestas()
    return sorted([c for c in cestas if c.get("ativa", True)], key=lambda x: x.get("nome", ""))

@st.cache_data(ttl=15, show_spinner=False)
def carregar_pedidos_b2b():
    try:
        res = supabase.table("pedidos").select("*").ilike("cliente_nome", "%[B2B]%").execute()
        return res.data or []
    except:
        return []

cestas_disponiveis = obter_cestas_admin()

# =====================================================
# ABAS DO MÓDULO
# =====================================================
aba_proposta, aba_empresas = st.tabs(["📝 Novo Orçamento / Pedido", "🤝 Histórico de Vendas B2B"])

# =====================================================
# ABA 1: GERADOR E CADASTRO DE PEDIDO CORPORATIVO
# =====================================================
with aba_proposta:
    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    st.markdown('<div class="corp-title">⚙️ 1. Dados da Negociação</div>', unsafe_allow_html=True)
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        empresa_nome = st.text_input("Nome da Empresa Cliente *", placeholder="Ex: Sicoob, Tribunal de Justiça, etc.")
        telefone_empresa = st.text_input("WhatsApp / Telefone do Contato", placeholder="Ex: (61) 99999-9999")
        contato_nome = st.text_input("A/C (Nome do Contato do RH/Compras)", placeholder="Ex: Ana Clara - Coord. de RH")
    with col_e2:
        validade = st.date_input("Validade da Proposta", value=datetime.now() + timedelta(days=7))
        motivo = st.text_input("Motivo / Evento", placeholder="Ex: Brindes de Fim de Ano, Dia da Mulher")
        data_entrega = st.date_input("Data Acordada para Entrega", value=date.today())

    st.markdown("#### 🎁 2. Adicionar Itens ao Lote")
    
    if "itens_orcamento" not in st.session_state:
        st.session_state["itens_orcamento"] = []

    col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
    with col_i1:
        cesta_selecionada = st.selectbox("Selecione o Produto", [{"id": None, "nome": "Escolha uma cesta...", "preco": 0}] + cestas_disponiveis, format_func=lambda x: x["nome"])
    with col_i2:
        quantidade = st.number_input("Qtd", min_value=1, step=1)
    with col_i3:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Inserir Lote", use_container_width=True):
            if cesta_selecionada.get("id"):
                st.session_state["itens_orcamento"].append({
                    "cesta_id": cesta_selecionada["id"],
                    "nome": cesta_selecionada["nome"],
                    "preco_unitario": float(cesta_selecionada.get("preco", 0)),
                    "quantidade": quantidade,
                    "descricao": cesta_selecionada.get("descricao", "")
                })
                st.rerun()

    total_bruto = 0
    total_liquido = 0
    valor_desconto = 0

    if st.session_state["itens_orcamento"]:
        st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
        df_itens = pd.DataFrame(st.session_state["itens_orcamento"])
        df_itens["Subtotal"] = df_itens["preco_unitario"] * df_itens["quantidade"]
        
        st.write("📋 **Itens do Contrato:**")
        st.dataframe(
            df_itens[["nome", "quantidade", "preco_unitario", "Subtotal"]].style.format({"preco_unitario": "R$ {:.2f}", "Subtotal": "R$ {:.2f}"}),
            use_container_width=True, hide_index=True
        )
        
        if st.button("🧹 Limpar Itens"):
            st.session_state["itens_orcamento"] = []
            st.rerun()

    st.markdown("#### 💰 3. Condições Comerciais e Logística")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        desconto_perc = st.number_input("Desconto de Lote (%)", min_value=0.0, max_value=100.0, step=1.0)
    with col_d2:
        frete_lote = st.number_input("Frete Único (R$)", min_value=0.0, step=10.0)
    with col_d3:
        prazo_pagamento = st.selectbox("Condição de Pagamento", ["Pix", "Cartão de Crédito", "Faturamento (Boleto)", "Transferência Bancária"])

    endereco_empresa = st.text_input("📍 Endereço de Entrega da Empresa", placeholder="Ex: SQS 101, Bloco A, Ed. Comercial")

    total_bruto = sum(item["preco_unitario"] * item["quantidade"] for item in st.session_state["itens_orcamento"])
    valor_desconto = total_bruto * (desconto_perc / 100)
    total_liquido = total_bruto - valor_desconto + frete_lote

    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        ver_preview = st.checkbox("👁️ Montar Documento de Orçamento (PDF / WhatsApp)", value=False)
        
    with col_btn2:
        if st.button("✅ SALVAR PEDIDO B2B COMO VENDA CONFIRMADA", type="primary", use_container_width=True):
            if not empresa_nome: st.error("Informe o Nome da Empresa."); st.stop()
            if not st.session_state["itens_orcamento"]: st.error("Adicione ao menos um item ao pedido."); st.stop()
            if not endereco_empresa: st.error("Informe o Endereço de Entrega para a logística."); st.stop()
                
            lista_str_produtos = []
            for item in st.session_state["itens_orcamento"]:
                lista_str_produtos.append(f"{item['quantidade']}x {item['nome']} (R$ {item['preco_unitario']:.2f})")
            
            nome_da_cesta_principal = "Lote Corporativo Misto"
            if len(st.session_state["itens_orcamento"]) == 1:
                nome_da_cesta_principal = st.session_state["itens_orcamento"][0]["nome"]

            dados_b2b = {
                "cliente_nome": f"[B2B] {empresa_nome.strip()}",
                "cliente_telefone": telefone_empresa.strip() or "00000000000",
                "cliente_cpf": "00000000000",
                "destinatario_nome": contato_nome.strip() or "Colaboradores",
                "destinatario_telefone": telefone_empresa.strip(),
                "motivo_homenagem": f"B2B: {motivo.strip()}",
                "cesta_id": st.session_state["itens_orcamento"][0]["cesta_id"],
                "cesta_nome": nome_da_cesta_principal,
                "produtos": "\n".join(lista_str_produtos),
                "adicionais": f"Desconto de {desconto_perc}% aplicado.",
                "pagamento": prazo_pagamento,
                "mensagem": "Pedido corporativo gerado pelo painel B2B.",
                "endereco": endereco_empresa,
                "data_entrega": data_entrega.strftime("%Y-%m-%d"),
                "periodo_entrega": "Comercial",
                "status": "Pago",
                "valor_frete": frete_lote,
                "valor_total": total_liquido,
                "cesta_montada": False
            }
            
            sucesso, p_id = salvar_pedido(dados_b2b)
            if sucesso:
                st.success(f"🎉 Pedido corporativo {empresa_nome} salvo com sucesso! Já foi enviado para a fila de Produção.")
                st.session_state["itens_orcamento"] = []
            else:
                st.error("Erro ao registrar o pedido no banco de dados.")

    st.markdown('</div>', unsafe_allow_html=True)

    # =================================================
    # PREVIEW DA PROPOSTA (PDF E WHATSAPP)
    # =================================================
    if st.session_state["itens_orcamento"] and empresa_nome and ver_preview:
        st.markdown("### 👁️ Enviar Proposta para o Cliente")
        
        aba_pdf, aba_whats = st.tabs(["📄 Documento Formal (Salvar em PDF)", "📱 Copiar para o WhatsApp"])

        # VISÃO PDF
        with aba_pdf:
            st.info("🖨️ **Dica de Ouro:** Pressione `Ctrl + P` (ou clique com botão direito e vá em Imprimir) e mude o destino para **Salvar como PDF**. Nossa tela foi configurada para remover todos os botões na hora da impressão, gerando uma folha limpa!")
            
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
                    • Produtos sujeitos a alteração conforme disponibilidade, mantendo a mesma qualidade.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # VISÃO WHATSAPP
        with aba_whats:
            st.info("💬 **Pronto para Envio:** Passe o mouse sobre a caixa de texto abaixo e clique no ícone de cópia (no canto superior direito). Depois é só colar no WhatsApp do cliente!")
            
            linhas_whatsapp = ""
            for item in st.session_state["itens_orcamento"]:
                linhas_whatsapp += f"▪️ {item['quantidade']}x *{item['nome']}* (R$ {item['preco_unitario']:,.2f})\n"
                
            texto_wpp = f"""*PROPOSTA COMERCIAL - DOCE CESTA BRASÍLIA* 🎁
            
🏢 *Para:* {empresa_nome}
👤 *A/C:* {contato_nome}
📅 *Validade da Proposta:* {validade.strftime("%d/%m/%Y")}

*ITENS DO ORÇAMENTO:*
{linhas_whatsapp}
*RESUMO FINANCEIRO:*
💰 Subtotal: R$ {total_bruto:,.2f}
🔻 Desconto ({desconto_perc}%): - R$ {valor_desconto:,.2f}
🚚 Logística (Frete): R$ {frete_lote:,.2f}
━━━━━━━━━━━━━━━━━━━━
*TOTAL GERAL: R$ {total_liquido:,.2f}*

💳 *Condição de Pagamento:* {prazo_pagamento}
📍 *Endereço Cadastrado:* {endereco_empresa or 'A confirmar'}

Qualquer dúvida, nossa equipe está à disposição para ajudar a criar a melhor experiência para vocês! 🌻""".replace(",", "X").replace(".", ",").replace("X", ".")
            
            st.code(texto_wpp, language="markdown")


# =====================================================
# ABA 2: HISTÓRICO DE VENDAS B2B (RELAÇÃO DE CLIENTES)
# =====================================================
with aba_empresas:
    st.markdown('<div class="corp-card"><div class="corp-title">🏢 Histórico de Contratos B2B</div>', unsafe_allow_html=True)
    
    pedidos_b2b = carregar_pedidos_b2b()
    
    if not pedidos_b2b:
        st.info("Nenhuma venda corporativa registrada ainda. Os pedidos salvos na aba ao lado aparecerão aqui.")
    else:
        df_b2b = pd.DataFrame(pedidos_b2b)
        
        df_b2b["Empresa"] = df_b2b["cliente_nome"].str.replace("[B2B]", "", regex=False).str.strip()
        df_b2b["Data"] = pd.to_datetime(df_b2b["created_at"]).dt.strftime("%d/%m/%Y")
        df_b2b["Valor"] = pd.to_numeric(df_b2b["valor_total"]).apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        colunas_exibir = ["Data", "Empresa", "cesta_nome", "Valor", "status", "pagamento"]
        df_display = df_b2b[colunas_exibir].rename(columns={
            "cesta_nome": "Pacote Vendido",
            "status": "Status",
            "pagamento": "Condição"
        })
        
        total_faturado_b2b = df_b2b["valor_total"].sum()
        total_empresas = df_b2b["Empresa"].nunique()
        
        c1, c2 = st.columns(2)
        c1.metric("💰 Faturamento Total B2B", f"R$ {total_faturado_b2b:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        c2.metric("🏢 Empresas Atendidas", total_empresas)
        
        st.write("")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)
