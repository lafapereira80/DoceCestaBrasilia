import streamlit as st
import pandas as pd
import requests
import re
import uuid
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

/* Painel de Resumo Financeiro Real-Time */
.resumo-financeiro {
    background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 12px; padding: 15px 20px;
    display: flex; justify-content: space-between; align-items: center; margin-top: 15px;
}
.resumo-item { text-align: center; }
.resumo-label { font-size: 12px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; }
.resumo-valor { font-size: 20px; font-weight: 800; color: #4a2e1b; }
.resumo-destaque { font-size: 24px; font-weight: 800; color: #137333; }

/* Botões Nativos */
div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 800 !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(19, 115, 51, 0.2) !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background: linear-gradient(135deg, #0f5c28 0%, #093818) !important; transform: translateY(-2px) !important; }

/* Remove paddings desnecessários nos inputs da lista */
div[data-testid="stNumberInput"] label { display: none !important; }

@media print {
    header, footer, section[data-testid="stSidebar"], .stAppDeployMenu, 
    div[data-testid="stButton"], .header-banner, .stTabs > div[role="tablist"],
    div[data-testid="stCheckbox"], div[data-baseweb="select"], input, .corp-card {
        display: none !important;
    }
    .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important;}
    .proposta-preview { box-shadow: none !important; border: none !important; padding: 0 !important; }
    body { background-color: white !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Vendas Corporativas (B2B)</h1>
    <p class="header-subtitle">Monte orçamentos vivos, edite preços, gere PDFs e confirme os pedidos 🏢</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES E CACHES
# =====================================================
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

@st.cache_data(ttl=60, show_spinner=False)
def obter_cestas_admin():
    cestas = listar_cestas()
    return sorted([c for c in cestas if c.get("ativa", True)], key=lambda x: x.get("nome", ""))

@st.cache_data(ttl=60, show_spinner=False)
def obter_adicionais_admin():
    try:
        res = supabase.table("produtos").select("*").execute()
        ativos = [p for p in (res.data or []) if p.get("ativo", True)]
        return sorted(ativos, key=lambda x: x.get("nome", ""))
    except:
        return []

@st.cache_data(ttl=15, show_spinner=False)
def carregar_pedidos_b2b():
    try:
        res = supabase.table("pedidos").select("*").ilike("cliente_nome", "%[B2B]%").execute()
        return res.data or []
    except:
        return []

def buscar_cnpj_api(cnpj_str):
    cnpj_limpo = re.sub(r'\D', '', cnpj_str)
    if len(cnpj_limpo) != 14: return False, "CNPJ inválido. Digite 14 números."
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200: return True, r.json()
        else: return False, "CNPJ não encontrado."
    except Exception as e: return False, "Erro de conexão."

cestas_disponiveis = obter_cestas_admin()
adicionais_disponiveis = obter_adicionais_admin()

# Sessões do sistema
if "corp_cnpj" not in st.session_state: st.session_state.corp_cnpj = ""
if "corp_nome" not in st.session_state: st.session_state.corp_nome = ""
if "corp_tel" not in st.session_state: st.session_state.corp_tel = ""
if "corp_end" not in st.session_state: st.session_state.corp_end = ""
if "itens_orcamento" not in st.session_state: st.session_state["itens_orcamento"] = []

# =====================================================
# ABAS DO MÓDULO
# =====================================================
aba_proposta, aba_empresas = st.tabs(["📝 Novo Orçamento / Pedido", "🤝 Histórico de Vendas B2B"])

# =====================================================
# ABA 1: GERADOR E CADASTRO DE PEDIDO CORPORATIVO
# =====================================================
with aba_proposta:
    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    st.markdown('<div class="corp-title">⚙️ 1. Dados da Empresa e Negociação</div>', unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([2, 1, 3])
    with col_c1:
        cnpj_input = st.text_input("Consulta Rápida por CNPJ", value=st.session_state.corp_cnpj, placeholder="Somente números")
    with col_c2:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Buscar Dados", use_container_width=True):
            if cnpj_input:
                sucesso, dados = buscar_cnpj_api(cnpj_input)
                if sucesso:
                    st.session_state.corp_cnpj = cnpj_input
                    st.session_state.corp_nome = dados.get("nome_fantasia") or dados.get("razao_social", "")
                    st.session_state.corp_tel = dados.get("ddd_telefone_1", "")
                    
                    log = dados.get('logradouro', '')
                    num = dados.get('numero', '')
                    bairro = dados.get('bairro', '')
                    cidade = dados.get('municipio', '')
                    uf = dados.get('uf', '')
                    st.session_state.corp_end = f"{log}, {num} - {bairro}, {cidade}-{uf}"
                    
                    st.toast("✅ Dados importados da Receita Federal com sucesso!")
                    st.rerun()
                else:
                    st.error(dados)
            else:
                st.warning("Digite um CNPJ para buscar.")

    st.write("")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        empresa_nome = st.text_input("Nome da Empresa Cliente *", value=st.session_state.corp_nome, placeholder="Ex: Sicoob, Tribunal de Justiça, etc.")
        telefone_empresa = st.text_input("WhatsApp / Telefone da Empresa", value=st.session_state.corp_tel, placeholder="Ex: (61) 99999-9999")
        contato_nome = st.text_input("A/C (Nome do Contato)", placeholder="Ex: Ana Clara - Coord. de RH")
    with col_e2:
        validade = st.date_input("Validade da Proposta", value=datetime.now() + timedelta(days=7), format="DD/MM/YYYY")
        motivo = st.text_input("Motivo / Evento", placeholder="Ex: Brindes de Fim de Ano, Dia da Mulher")
        data_entrega = st.date_input("Data Acordada para Entrega", value=date.today(), format="DD/MM/YYYY")

    # ===================================================================
    # 2. SISTEMA DE ADIÇÃO AO CARRINHO VIVO (SEM "FECHAR PACOTE")
    # ===================================================================
    st.markdown("#### 🎁 2. Adicionar Itens ao Contrato (Pacotes e Extras)")
    
    col_add1, col_add2, col_add3 = st.columns(3)
    
    with col_add1:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>📦 Pacotes (Cestas Base)</div>", unsafe_allow_html=True)
        cesta_sel = st.selectbox("Cestas", [None] + cestas_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione uma Cesta...", label_visibility="collapsed")
        if st.button("➕ Inserir Cesta", use_container_width=True):
            if cesta_sel:
                st.session_state["itens_orcamento"].append({
                    "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_sel["id"], "nome": cesta_sel["nome"], 
                    "preco_unitario": tratar_preco(cesta_sel.get("preco")), "quantidade": 1, "descricao": cesta_sel.get("descricao", "")
                })
                st.rerun()

    with col_add2:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✨ Extras do Catálogo</div>", unsafe_allow_html=True)
        adc_sel = st.selectbox("Extras", [None] + adicionais_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione um Adicional...", label_visibility="collapsed")
        if st.button("➕ Inserir Extra", use_container_width=True):
            if adc_sel:
                st.session_state["itens_orcamento"].append({
                    "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": adc_sel["nome"], 
                    "preco_unitario": tratar_preco(adc_sel.get("preco")), "quantidade": 1, "descricao": ""
                })
                st.rerun()

    with col_add3:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✍️ Extra Personalizado</div>", unsafe_allow_html=True)
        txt_man = st.text_input("Extra Manual", placeholder="Digite o nome do item...", label_visibility="collapsed")
        if st.button("➕ Inserir Manual", use_container_width=True):
            if txt_man.strip():
                st.session_state["itens_orcamento"].append({
                    "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": txt_man.strip(), 
                    "preco_unitario": 0.0, "quantidade": 1, "descricao": ""
                })
                st.rerun()


    # ===================================================================
    # 3. CARRINHO DE COMPRAS EDITÁVEL (AO VIVO)
    # ===================================================================
    total_bruto = 0
    
    if st.session_state["itens_orcamento"]:
        st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 25px 0;'>", unsafe_allow_html=True)
        st.markdown("### 🛒 Resumo do Contrato (Edite Preços e Quantidades)")
        st.info("💡 Você pode alterar o **Valor Unitário** (especialmente para itens sob consulta) e a **Quantidade** diretamente na lista abaixo. O sistema calculará o Subtotal e o Total automaticamente.")
        
        # Cabeçalhos da Tabela Customizada
        h1, h2, h3, h4, h5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
        h1.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Descrição do Item</div>", unsafe_allow_html=True)
        h2.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Valor Un. (R$)</div>", unsafe_allow_html=True)
        h3.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Qtd</div>", unsafe_allow_html=True)
        h4.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Subtotal</div>", unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state["itens_orcamento"]):
            c1, c2, c3, c4, c5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
            
            with c1:
                icone = "📦" if item["tipo"] == "Cesta" else "✨"
                st.markdown(f"<div style='margin-top:8px; font-weight:700; font-size:14px; color:#4a2e1b;'>{icone} {item['nome']}</div>", unsafe_allow_html=True)
                
            with c2:
                # O número digitado aqui atualiza o dict do session_state automaticamente
                novo_preco = st.number_input("Valor", value=float(item["preco_unitario"]), min_value=0.0, step=1.0, format="%.2f", key=f"p_{item['id']}")
                st.session_state["itens_orcamento"][i]["preco_unitario"] = novo_preco
                
            with c3:
                # O número digitado aqui atualiza a quantidade instantaneamente
                nova_qtd = st.number_input("Qtd", value=int(item["quantidade"]), min_value=1, step=1, key=f"q_{item['id']}")
                st.session_state["itens_orcamento"][i]["quantidade"] = nova_qtd
                
            with c4:
                # O subtotal real-time é calculado multiplicando os valores da tela
                subtotal_linha = novo_preco * nova_qtd
                total_bruto += subtotal_linha
                st.markdown(f"<div style='margin-top:10px; font-weight:800; font-size:16px; color:#137333;'>R$ {subtotal_linha:,.2f}</div>", unsafe_allow_html=True)
                
            with c5:
                st.markdown("<div style='margin-top:2px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"d_{item['id']}", help="Remover do Contrato"):
                    st.session_state["itens_orcamento"].pop(i)
                    st.rerun()

        st.write("")
        if st.button("🧹 Limpar Todo o Contrato"):
            st.session_state["itens_orcamento"] = []
            st.rerun()

    st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 💰 4. Condições Comerciais e Logística")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        desconto_perc = st.number_input("Desconto de Lote (%)", min_value=0.0, max_value=100.0, step=1.0)
    with col_d2:
        frete_lote = st.number_input("Frete Único Logístico (R$)", min_value=0.0, step=10.0)
    with col_d3:
        prazo_pagamento = st.selectbox("Condição de Pagamento", ["Pix", "Cartão de Crédito", "Faturamento (Boleto)", "Transferência Bancária"])

    endereco_empresa = st.text_input("📍 Endereço de Entrega da Empresa", value=st.session_state.corp_end, placeholder="Ex: SQS 101, Bloco A, Ed. Comercial")

    # Cálculos Financeiros Dinâmicos
    valor_desconto = total_bruto * (desconto_perc / 100)
    total_liquido = total_bruto - valor_desconto + frete_lote

    # Exibição do Valor Total Dinâmico na Tela
    st.markdown(f"""
    <div class="resumo-financeiro">
        <div class="resumo-item">
            <div class="resumo-label">Subtotal (Cestas + Extras)</div>
            <div class="resumo-valor">R$ {total_bruto:,.2f}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">Desconto Aplicado</div>
            <div class="resumo-valor" style="color: #c5221f;">- R$ {valor_desconto:,.2f}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">Logística</div>
            <div class="resumo-valor">R$ {frete_lote:,.2f}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">VALOR TOTAL B2B</div>
            <div class="resumo-destaque">R$ {total_liquido:,.2f}</div>
        </div>
    </div>
    """.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        ver_preview = st.checkbox("👁️ Montar Documento de Orçamento (PDF / WhatsApp)", value=False)
        
    with col_btn2:
        if st.button("✅ SALVAR PEDIDO B2B COMO VENDA CONFIRMADA", type="primary", use_container_width=True):
            if not empresa_nome: st.error("Informe o Nome da Empresa."); st.stop()
            if not st.session_state["itens_orcamento"]: st.error("Adicione itens ao contrato."); st.stop()
            if not endereco_empresa: st.error("Informe o Endereço de Entrega para a logística."); st.stop()
                
            # Organiza os itens para o banco de dados (Cestas em produtos, Extras em adicionais)
            lista_cestas = [it for it in st.session_state["itens_orcamento"] if it["tipo"] == "Cesta"]
            lista_extras = [it for it in st.session_state["itens_orcamento"] if it["tipo"] == "Extra"]
            
            lista_str_produtos = [f"{it['quantidade']}x {it['nome']} (R$ {it['preco_unitario']:.2f})" for it in lista_cestas]
            lista_str_extras = [f"{it['quantidade']}x {it['nome']} (R$ {it['preco_unitario']:.2f})" for it in lista_extras]
            
            # Identifica a cesta principal para a tag
            nome_da_cesta_principal = "Lote Corporativo"
            cesta_id_principal = None
            if lista_cestas:
                nome_da_cesta_principal = lista_cestas[0]["nome"]
                cesta_id_principal = lista_cestas[0]["cesta_id"]
            elif lista_extras:
                nome_da_cesta_principal = "Itens Corporativos Extras"
                
            # Se só existirem extras (ex: cliente comprou 50 canecas avulsas), coloca eles no campo produtos
            if not lista_cestas and lista_extras:
                lista_str_produtos = lista_str_extras
                msg_adicionais = f"Desconto de {desconto_perc}% aplicado."
            else:
                msg_adicionais = f"Desconto de {desconto_perc}% aplicado."
                if lista_str_extras:
                    msg_adicionais += "\n\nEXTRAS E ADICIONAIS INCLUSOS:\n" + "\n".join(lista_str_extras)

            cnpj_formatado = re.sub(r'\D', '', st.session_state.corp_cnpj) if st.session_state.corp_cnpj else "00000000000"

            dados_b2b = {
                "cliente_nome": f"[B2B] {empresa_nome.strip()}",
                "cliente_telefone": telefone_empresa.strip() or "00000000000",
                "cliente_cpf": cnpj_formatado,
                "destinatario_nome": contato_nome.strip() or "Colaboradores",
                "destinatario_telefone": telefone_empresa.strip(),
                "motivo_homenagem": f"B2B: {motivo.strip()}",
                "cesta_id": cesta_id_principal,
                "cesta_nome": nome_da_cesta_principal,
                "produtos": "\n".join(lista_str_produtos),
                "adicionais": msg_adicionais,
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
                st.session_state.corp_cnpj = ""
                st.session_state.corp_nome = ""
                st.session_state.corp_tel = ""
                st.session_state.corp_end = ""
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
            st.info("🖨️ **Dica de Ouro:** Pressione `Ctrl + P` (ou clique com botão direito e vá em Imprimir) e mude o destino para **Salvar como PDF**.")
            
            linhas_html = ""
            for item in st.session_state["itens_orcamento"]:
                # Se for Cesta tem a descrição original, se for Extra fica vazio
                desc_curta = (item['descricao'][:150] + '...') if item['descricao'] and len(item['descricao']) > 150 else (item['descricao'] or '')
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
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e8ddd3;">Descrição dos Itens do Contrato</th>
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
        st.info("Nenhuma venda corporativa registrada ainda.")
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
