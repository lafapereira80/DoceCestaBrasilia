import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, date
from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.pedido_service import salvar_pedido
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Novo Pedido (Varejo)", page_icon="🛍️", layout="wide")
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

.corp-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 24px;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.02); margin-bottom: 15px;
}
.corp-title { font-size: 18px; font-weight: 800; color: #c5721f; margin-bottom: 15px; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px;}

.proposta-preview {
    background: #ffffff; border: 1px solid #dfcdbb; border-radius: 12px; padding: 40px;
    font-family: 'Arial', sans-serif; color: #333; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
.proposta-header { text-align: center; border-bottom: 3px solid #c5721f; padding-bottom: 15px; margin-bottom: 25px; }
.proposta-total { font-size: 22px; font-weight: bold; color: #c5721f; text-align: right; margin-top: 20px; border-top: 2px solid #e8ddd3; padding-top: 15px;}

/* Painel de Resumo Financeiro Real-Time */
.resumo-financeiro {
    background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 12px; padding: 15px 20px;
    display: flex; justify-content: space-between; align-items: center; margin-top: 15px;
}
.resumo-item { text-align: center; }
.resumo-label { font-size: 12px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; }
.resumo-valor { font-size: 20px; font-weight: 800; color: #4a2e1b; }
.resumo-destaque { font-size: 24px; font-weight: 800; color: #137333; }

div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 800 !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #c5721f 0%, #a65d14) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(197, 114, 31, 0.2) !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background: linear-gradient(135deg, #a65d14 0%, #874c10) !important; transform: translateY(-2px) !important; }

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
    <h1 class="header-title">Varejo (Pessoa Física)</h1>
    <p class="header-subtitle">Monte orçamentos, insira extras, adicione cartões e registre pedidos 🛍️</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES, CACHES E BLINDAGENS
# =====================================================
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
def carregar_pedidos_varejo():
    try:
        res = supabase.table("pedidos").select("*").not_.ilike("cliente_nome", "%[B2B]%").execute()
        return res.data or []
    except:
        return []

cestas_disponiveis = obter_cestas_admin()
adicionais_disponiveis = obter_adicionais_admin()

# Sessões do sistema para Varejo
if "itens_varejo" not in st.session_state: st.session_state["itens_varejo"] = []

# =====================================================
# ABAS DO MÓDULO
# =====================================================
aba_proposta, aba_historico = st.tabs(["📝 Novo Pedido (Varejo)", "👤 Histórico de Clientes"])

# =====================================================
# ABA 1: GERADOR E CADASTRO DE PEDIDO VAREJO
# =====================================================
with aba_proposta:
    st.markdown('<div class="corp-card">', unsafe_allow_html=True)
    st.markdown('<div class="corp-title">👤 1. Dados do Cliente e Destinatário</div>', unsafe_allow_html=True)
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        cliente_nome = st.text_input("Nome do Cliente (Comprador) *", placeholder="Ex: Maria da Silva")
        cliente_tel = st.text_input("Telefone / WhatsApp *", placeholder="Ex: (61) 99999-9999")
        cliente_cpf = st.text_input("CPF (Opcional)", placeholder="Apenas números")
    with col_e2:
        dest_nome = st.text_input("Nome do Destinatário (Quem vai receber) *", placeholder="Ex: João (Repita se for a mesma pessoa)")
        dest_tel = st.text_input("Telefone do Destinatário", placeholder="Ex: (61) 98888-8888")
        motivo = st.text_input("Ocasião / Motivo", placeholder="Ex: Aniversário, Dia dos Namorados")

    st.markdown("#### 🎁 2. Adicionar Itens (Pacotes e Extras)")
    
    col_add1, col_add2, col_add3 = st.columns(3)
    with col_add1:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>📦 Cestas Base</div>", unsafe_allow_html=True)
        cesta_sel = st.selectbox("Cestas", [None] + cestas_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione uma Cesta...", label_visibility="collapsed")
        if st.button("➕ Inserir Cesta", use_container_width=True):
            if cesta_sel:
                st.session_state["itens_varejo"].append({
                    "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_sel["id"], "nome": cesta_sel["nome"], 
                    "preco_unitario": tratar_preco(cesta_sel.get("preco")), "quantidade": 1, "descricao": cesta_sel.get("descricao", "")
                })
                st.rerun()

    with col_add2:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✨ Extras do Catálogo</div>", unsafe_allow_html=True)
        adc_sel = st.selectbox("Extras", [None] + adicionais_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione um Adicional...", label_visibility="collapsed")
        if st.button("➕ Inserir Extra", use_container_width=True):
            if adc_sel:
                st.session_state["itens_varejo"].append({
                    "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": adc_sel["nome"], 
                    "preco_unitario": tratar_preco(adc_sel.get("preco")), "quantidade": 1, "descricao": ""
                })
                st.rerun()

    with col_add3:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✍️ Extra Personalizado</div>", unsafe_allow_html=True)
        txt_man = st.text_input("Extra Manual", placeholder="Ex: Balão personalizado", label_visibility="collapsed")
        if st.button("➕ Inserir Manual", use_container_width=True):
            if txt_man.strip():
                st.session_state["itens_varejo"].append({
                    "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": txt_man.strip(), 
                    "preco_unitario": 0.0, "quantidade": 1, "descricao": ""
                })
                st.rerun()

    # ===================================================================
    # 3. CARRINHO DE COMPRAS EDITÁVEL (AO VIVO)
    # ===================================================================
    total_bruto = 0
    
    if st.session_state["itens_varejo"]:
        st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 25px 0;'>", unsafe_allow_html=True)
        st.markdown("### 🛒 Resumo do Pedido (Edite Preços e Quantidades)")
        
        h1, h2, h3, h4, h5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
        h1.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Descrição do Item</div>", unsafe_allow_html=True)
        h2.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Valor Un. (R$)</div>", unsafe_allow_html=True)
        h3.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Qtd</div>", unsafe_allow_html=True)
        h4.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Subtotal</div>", unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state["itens_varejo"]):
            c1, c2, c3, c4, c5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
            
            with c1:
                icone = "📦" if item["tipo"] == "Cesta" else "✨"
                st.markdown(f"<div style='margin-top:8px; font-weight:700; font-size:14px; color:#4a2e1b;'>{icone} {item['nome']}</div>", unsafe_allow_html=True)
                
            with c2:
                novo_preco = st.number_input("Valor", value=float(item["preco_unitario"]), min_value=0.0, step=1.0, format="%.2f", key=f"p_{item['id']}")
                st.session_state["itens_varejo"][i]["preco_unitario"] = novo_preco
                
            with c3:
                nova_qtd = st.number_input("Qtd", value=int(item["quantidade"]), min_value=1, step=1, key=f"q_{item['id']}")
                st.session_state["itens_varejo"][i]["quantidade"] = nova_qtd
                
            with c4:
                subtotal_linha = novo_preco * nova_qtd
                total_bruto += subtotal_linha
                st.markdown(f"<div style='margin-top:10px; font-weight:800; font-size:16px; color:#c5721f;'>R$ {formatar_moeda(subtotal_linha)}</div>", unsafe_allow_html=True)
                
            with c5:
                st.markdown("<div style='margin-top:2px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"d_{item['id']}", help="Remover"):
                    st.session_state["itens_varejo"].pop(i)
                    st.rerun()

    st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 💌 4. Mensagem do Cartão")
    mensagem_cartao = st.text_area("Digite o texto exatamente como o cliente pediu (Opcional)", height=100, placeholder="Ex: Feliz aniversário, meu amor! Com carinho, João.")

    st.markdown("#### 💰 5. Logística e Pagamento")
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        data_entrega = st.date_input("Data de Entrega", value=date.today(), format="DD/MM/YYYY")
    with col_d2:
        periodo = st.selectbox("Período", ["Manhã", "Tarde", "Horário Marcado", "Comercial"])
    with col_d3:
        frete_lote = st.number_input("Frete (R$)", min_value=0.0, step=5.0, value=15.0)
    with col_d4:
        prazo_pagamento = st.selectbox("Forma de Pag.", ["Pix", "Cartão de Crédito", "Dinheiro", "Link de Pagamento"])
        
    desconto_perc = st.number_input("Desconto de Varejo (%)", min_value=0.0, max_value=100.0, step=1.0)
    endereco_empresa = st.text_input("📍 Endereço de Entrega", placeholder="Ex: SQS 101, Bloco A, Apto 101 - Asa Sul")

    # Cálculos Financeiros Dinâmicos
    valor_desconto = total_bruto * (desconto_perc / 100)
    total_liquido = total_bruto - valor_desconto + frete_lote

    # Exibição do Valor Total Dinâmico na Tela
    st.markdown(f"""
    <div class="resumo-financeiro">
        <div class="resumo-item">
            <div class="resumo-label">Subtotal</div>
            <div class="resumo-valor">R$ {formatar_moeda(total_bruto)}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">Desconto</div>
            <div class="resumo-valor" style="color: #c5221f;">- R$ {formatar_moeda(valor_desconto)}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">Frete</div>
            <div class="resumo-valor">R$ {formatar_moeda(frete_lote)}</div>
        </div>
        <div class="resumo-item">
            <div class="resumo-label">TOTAL DO PEDIDO</div>
            <div class="resumo-destaque">R$ {formatar_moeda(total_liquido)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        ver_preview = st.checkbox("👁️ Gerar Espelho do Pedido (PDF / WhatsApp)", value=False)
        
    with col_btn2:
        if st.button("✅ SALVAR PEDIDO NO SISTEMA", type="primary", use_container_width=True):
            if not cliente_nome: st.error("Informe o Nome do Cliente."); st.stop()
            if not st.session_state["itens_varejo"]: st.error("Adicione itens ao carrinho."); st.stop()
            if not endereco_empresa: st.error("Informe o Endereço de Entrega para a logística."); st.stop()
                
            lista_cestas = [it for it in st.session_state["itens_varejo"] if it["tipo"] == "Cesta"]
            lista_extras = [it for it in st.session_state["itens_varejo"] if it["tipo"] == "Extra"]
            
            lista_str_produtos = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_cestas]
            lista_str_extras = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_extras]
            
            nome_da_cesta_principal = "Pedido Diversos"
            cesta_id_principal = None
            if lista_cestas:
                nome_da_cesta_principal = lista_cestas[0]["nome"]
                cesta_id_principal = lista_cestas[0]["cesta_id"]
            elif lista_extras:
                nome_da_cesta_principal = "Itens Avulsos"
                
            if not lista_cestas and lista_extras:
                lista_str_produtos = lista_str_extras
                msg_adicionais = f"Desconto de {desconto_perc}% aplicado."
            else:
                msg_adicionais = f"Desconto de {desconto_perc}% aplicado."
                if lista_str_extras:
                    msg_adicionais += "\n\nADICIONAIS:\n" + "\n".join(lista_str_extras)

            dados_pf = {
                "cliente_nome": cliente_nome.strip(),
                "cliente_telefone": cliente_tel.strip(),
                "cliente_cpf": cliente_cpf.strip() or "00000000000",
                "destinatario_nome": dest_nome.strip() or cliente_nome.strip(),
                "destinatario_telefone": dest_tel.strip(),
                "motivo_homenagem": motivo.strip() or "Varejo",
                "cesta_id": cesta_id_principal,
                "cesta_nome": nome_da_cesta_principal,
                "produtos": "\n".join(lista_str_produtos),
                "adicionais": msg_adicionais,
                "pagamento": prazo_pagamento,
                "mensagem": mensagem_cartao.strip(),
                "endereco": endereco_empresa,
                "data_entrega": data_entrega.strftime("%Y-%m-%d"),
                "periodo_entrega": periodo,
                "status": "Recebido",
                "valor_frete": frete_lote,
                "valor_total": total_liquido,
                "cesta_montada": False
            }
            
            sucesso, p_id = salvar_pedido(dados_pf)
            if sucesso:
                st.success(f"🎉 Pedido de Varejo para {cliente_nome} salvo com sucesso! Vá para o Mural de Pedidos.")
                st.session_state["itens_varejo"] = []
            else:
                st.error("Erro ao registrar o pedido no banco de dados.")

    st.markdown('</div>', unsafe_allow_html=True)

    # =================================================
    # PREVIEW DA PROPOSTA (PDF E WHATSAPP)
    # =================================================
    if st.session_state["itens_varejo"] and cliente_nome and ver_preview:
        st.markdown("### 👁️ Espelho do Pedido para Conferência")
        
        aba_pdf, aba_whats = st.tabs(["📄 Documento Limpo (PDF)", "📱 Resumo WhatsApp"])

        with aba_pdf:
            st.info("🖨️ **Dica de Ouro:** Pressione `Ctrl + P` para Salvar como PDF ou Imprimir este espelho de pedido.")
            
            linhas_html = ""
            for item in st.session_state["itens_varejo"]:
                desc_curta = (item['descricao'][:150] + '...') if item['descricao'] and len(item['descricao']) > 150 else (item['descricao'] or '')
                preco_f = formatar_moeda(item['preco_unitario'])
                subtotal_f = formatar_moeda(item['preco_unitario'] * item['quantidade'])
                
                linhas_html += f"""<tr>
<td style="padding: 10px; border-bottom: 1px solid #f5eee6;"><b>{item['nome']}</b><br><span style="font-size:11px; color:#666;">{desc_curta}</span></td>
<td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: center;">{item['quantidade']}</td>
<td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: right;">R$ {preco_f}</td>
<td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: right;">R$ {subtotal_f}</td>
</tr>"""

            html_documento = f"""<div class="proposta-preview">
<div class="proposta-header">
<h2 style="color: #c5721f; margin-bottom: 5px; font-weight: 800;">ESPELHO DO PEDIDO</h2>
<p style="margin: 0; color: #555; font-size: 14px;">Doce Cesta Brasília - Encantando Pessoas</p>
</div>
<table style="width: 100%; border: none; margin-bottom: 25px;"><tr><td style="width: 60%; vertical-align: top;"><p style="margin:2px 0;"><b>Cliente:</b> {cliente_nome}</p><p style="margin:2px 0;"><b>Para:</b> {dest_nome or cliente_nome}</p><p style="margin:2px 0;"><b>Ocasião:</b> {motivo or 'Presente'}</p></td><td style="width: 40%; vertical-align: top; text-align: right;"><p style="margin:2px 0;"><b>Data Entrega:</b> {data_entrega.strftime("%d/%m/%Y")}</p><p style="margin:2px 0;"><b>Período:</b> {periodo}</p></td></tr></table>
<table style="width: 100%; border-collapse: collapse; margin-top: 10px;"><tr style="background-color: #faf7f3;"><th style="padding: 12px; text-align: left; border-bottom: 2px solid #e8ddd3;">Itens Adquiridos</th><th style="padding: 12px; text-align: center; border-bottom: 2px solid #e8ddd3;">Qtd</th><th style="padding: 12px; text-align: right; border-bottom: 2px solid #e8ddd3;">V. Unitário</th><th style="padding: 12px; text-align: right; border-bottom: 2px solid #e8ddd3;">Subtotal</th></tr>{linhas_html}</table>
<div style="margin-top: 25px; text-align: right; font-size: 15px;"><p style="margin: 4px 0;">Subtotal: R$ {formatar_moeda(total_bruto)}</p><p style="margin: 4px 0; color: #c5221f;">Desconto ({desconto_perc}%): - R$ {formatar_moeda(valor_desconto)}</p><p style="margin: 4px 0;">Frete: R$ {formatar_moeda(frete_lote)}</p></div>
<div class="proposta-total">TOTAL A PAGAR: R$ {formatar_moeda(total_liquido)}</div>
</div>"""
            st.markdown(html_documento, unsafe_allow_html=True)

        with aba_whats:
            linhas_whatsapp = ""
            for item in st.session_state["itens_varejo"]:
                linhas_whatsapp += f"▪️ {item['quantidade']}x *{item['nome']}* (R$ {formatar_moeda(item['preco_unitario'])})\n"
                
            texto_wpp = f"""*RESUMO DO PEDIDO - DOCE CESTA BRASÍLIA* 🎁
            
👤 *Cliente:* {cliente_nome}
📦 *Para:* {dest_nome or cliente_nome}
📅 *Data de Entrega:* {data_entrega.strftime("%d/%m/%Y")} ({periodo})

*ITENS SELECIONADOS:*
{linhas_whatsapp}
*RESUMO FINANCEIRO:*
💰 Subtotal: R$ {formatar_moeda(total_bruto)}
🔻 Desconto ({desconto_perc}%): - R$ {formatar_moeda(valor_desconto)}
🚚 Frete: R$ {formatar_moeda(frete_lote)}
━━━━━━━━━━━━━━━━━━━━
*TOTAL: R$ {formatar_moeda(total_liquido)}*

💳 *Forma de Pagamento:* {prazo_pagamento}
📍 *Endereço Cadastrado:* {endereco_empresa or 'A confirmar'}

Qualquer dúvida, nossa equipe está à disposição. Agradecemos a preferência! 🌻"""
            
            st.code(texto_wpp, language="markdown")

# =====================================================
# ABA 2: HISTÓRICO DE CLIENTES (VAREJO)
# =====================================================
with aba_historico:
    st.markdown('<div class="corp-card"><div class="corp-title">👤 Histórico de Pedidos de Varejo</div>', unsafe_allow_html=True)
    
    pedidos_pf = carregar_pedidos_varejo()
    
    if not pedidos_pf:
        st.info("Nenhuma venda de varejo registrada ainda.")
    else:
        df_pf = pd.DataFrame(pedidos_pf)
        df_pf["Data"] = pd.to_datetime(df_pf["created_at"]).dt.strftime("%d/%m/%Y")
        df_pf["Valor"] = pd.to_numeric(df_pf["valor_total"]).apply(lambda x: f"R$ {formatar_moeda(x)}")
        
        colunas_exibir = ["Data", "cliente_nome", "destinatario_nome", "cesta_nome", "Valor", "status", "pagamento"]
        df_display = df_pf[colunas_exibir].rename(columns={
            "cliente_nome": "Cliente",
            "destinatario_nome": "Para",
            "cesta_nome": "Pacote Vendido",
            "status": "Status",
            "pagamento": "Condição"
        })
        
        total_faturado_pf = df_pf["valor_total"].sum()
        total_clientes = df_pf["cliente_nome"].nunique()
        
        c1, c2 = st.columns(2)
        c1.metric("💰 Faturamento Varejo", f"R$ {formatar_moeda(total_faturado_pf)}")
        c2.metric("👥 Clientes Atendidos", total_clientes)
        
        st.write("")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)
