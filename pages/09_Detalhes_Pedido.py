import streamlit as st
import pandas as pd
import requests
import re
import uuid
from datetime import datetime, date
import streamlit.components.v1 as components

from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.produto_service import listar_produtos_por_categoria_id
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Detalhes e Edição de Pedido", page_icon="🔍", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# =====================================================
# CSS PREMIUM (PADRÃO DE BLOCOS / DASHBOARD)
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 4rem !important; max-width: 1400px !important; }

/* TOPO DO DASHBOARD */
.dash-header { 
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 18px 25px; 
    border-radius: 16px; border: 1px solid #e8ddd3; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03); 
    margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; 
}
.dash-title { font-family: 'Dancing Script', cursive !important; font-size: 36px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1; }
.dash-subtitle { font-size: 13px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 3px !important; }

/* ESTILIZAÇÃO DOS CONTAINERS (CAIXAS NATIVAS) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important; border: 1px solid #e8ddd3 !important; border-radius: 16px !important;
    padding: 20px !important; margin-bottom: 18px !important; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02) !important;
}

/* TICKET DE RESUMO INTERNO NA CAIXA */
.ticket-title { font-size: 15px; font-weight: 800; color: #137333; margin-bottom: 12px; text-align: center; border-bottom: 2px solid #ceead6; padding-bottom: 6px;}
.ticket-line { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12.5px; color: #5a3b28; }
.ticket-line strong { font-weight: 700; color: #2c1e14; text-align: right;}
.ticket-total { display: flex; justify-content: space-between; font-size: 20px; font-weight: 800; color: #137333; margin-top: 12px; padding-top: 10px; border-top: 2px dashed #137333; }

/* CHECKBOXES E EXTRAS */
div[data-testid="stCheckbox"] { background: #faf7f3; border: 1px solid #e8ddd3; padding: 6px 10px; border-radius: 8px; margin-bottom: 6px; }

/* BOTÃO DE AÇÃO PRINCIPAL */
div[data-testid="stButton"] button[kind="primary"] { 
    background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; 
    border-radius: 12px !important; font-weight: 800 !important; border: none !important; 
    box-shadow: 0 6px 20px rgba(19, 115, 51, 0.25) !important; font-size: 15px !important; padding: 16px !important; width: 100% !important; 
}
div[data-testid="stButton"] button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(19, 115, 51, 0.35) !important;}

@media print {
    header, footer, section[data-testid="stSidebar"], div[data-testid="stButton"] { display: none !important; }
}
</style>
""", unsafe_allow_html=True)

# Pega o ID da sessão
pedido_id = st.session_state.get('pedido_detalhe_id')

if not pedido_id:
    st.warning("Nenhum pedido selecionado.")
    if st.button("⬅️ Voltar aos Pedidos"):
        st.switch_page("pages/02_Pedidos.py")
    st.stop()

# Carrega os dados do pedido do Supabase
def obter_detalhe(p_id):
    res = supabase.table("pedidos").select("*").eq("id", p_id).execute()
    return res.data[0] if res.data else None

pedido = obter_detalhe(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()

# =====================================================
# FUNÇÕES E CACHES OTIMIZADOS
# =====================================================
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data(ttl=300, show_spinner=False)
def obter_cestas_admin():
    try:
        cestas = listar_cestas()
        return sorted([c for c in cestas if c.get("ativa", True)], key=lambda x: x.get("nome", ""))
    except: return []

@st.cache_data(ttl=300, show_spinner=False)
def obter_adicionais_admin():
    try:
        categorias = supabase.table("categorias").select("*").execute().data or []
        cat_add = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)
        if cat_add:
            produtos_add = listar_produtos_por_categoria_id(cat_add["id"])
            return sorted([p for p in produtos_add if p.get("ativo", True)], key=lambda x: x.get("nome", ""))
        return []
    except: return []

@st.cache_data(ttl=300, show_spinner=False)
def carregar_config_cesta_cached(cesta_id):
    try: return carregar_configuracao_cesta(cesta_id)
    except: return []

cestas_disponiveis = obter_cestas_admin()
adicionais_disponiveis = obter_adicionais_admin()

# ESTADOS DA SESSÃO DE EDIÇÃO
if "edit_inicializado" not in st.session_state or st.session_state.get("edit_pedido_id_atual") != pedido_id:
    st.session_state.edit_pedido_id_atual = pedido_id
    st.session_state.edit_nome = pedido.get('cliente_nome', '')
    st.session_state.edit_tel = pedido.get('cliente_telefone', '')
    st.session_state.edit_cpf = pedido.get('cliente_cpf', '')
    st.session_state.edit_dest_nome = pedido.get('destinatario_nome', '')
    st.session_state.edit_dest_tel = pedido.get('destinatario_telefone', '')
    st.session_state.edit_motivo = pedido.get('motivo_homenagem', '')
    st.session_state.edit_mensagem = pedido.get('mensagem', '')
    st.session_state.edit_endereco = pedido.get('endereco', '')
    st.session_state.edit_status = pedido.get('status', 'Recebido')
    st.session_state.edit_pagamento = pedido.get('pagamento', 'Pix')
    st.session_state.edit_frete = float(pedido.get('valor_frete', 0) or 0)
    
    add_texto_banco = pedido.get('adicionais', '')
    desc_extraido = 0.0
    if "Desconto de" in add_texto_banco:
        try:
            match = re.search(r'Desconto de ([\d\.]+)%', add_texto_banco)
            if match: desc_extraido = float(match.group(1))
        except: pass
    st.session_state.edit_desconto = desc_extraido

    try: st.session_state.edit_data = datetime.strptime(str(pedido.get('data_entrega', date.today()))[:10], "%Y-%m-%d").date()
    except: st.session_state.edit_data = date.today()
    st.session_state.edit_periodo = pedido.get('periodo_entrega', '')

    lista_itens_carregados = []
    cesta_id_banco = pedido.get('cesta_id')
    cesta_banco_obj = next((c for c in cestas_disponiveis if c["id"] == cesta_id_banco), None)
    
    if cesta_banco_obj:
        lista_itens_carregados.append({
            "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_banco_obj["id"], "nome": cesta_banco_obj["nome"],
            "preco_unitario": tratar_preco(cesta_banco_obj.get("preco")), "quantidade": 1, "descricao": pedido.get("produtos", "")
        })
    else:
        lista_itens_carregados.append({
            "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": None, "nome": pedido.get("cesta_nome", "Produto Base"),
            "preco_unitario": float(pedido.get("valor_total", 0) or 0), "quantidade": 1, "descricao": pedido.get("produtos", "")
        })
    
    if add_texto_banco:
        for linha in add_texto_banco.split("\n"):
            if "x " in linha and "(R$" in linha:
                try:
                    partes = linha.split(" (R$")
                    nome_extra = partes[0].replace("🎀", "").replace("▪️", "").strip()
                    if "x " in nome_extra: nome_extra = nome_extra.split("x ", 1)[1]
                    preco_extra = float(partes[1].replace(")", "").replace(",", ".").strip())
                    lista_itens_carregados.append({
                        "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": nome_extra,
                        "preco_unitario": preco_extra, "quantidade": 1, "descricao": ""
                    })
                except: pass

    st.session_state.edit_itens = lista_itens_carregados

if "edit_extras_avulsos" not in st.session_state: st.session_state.edit_extras_avulsos = []

# =====================================================
# CABEÇALHO DO PAINEL DE EDIÇÃO
# =====================================================
c_head, c_btn = st.columns([6, 1], vertical_alignment="center")
with c_head:
    st.markdown(f"""
    <div class="dash-header">
        <div>
            <h1 class="dash-title">Editar Pedido #{pedido['id']}</h1>
            <p class="dash-subtitle">Modifique cestas, adicione extras, atualize dados cadastrais e altere o status ✏️</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c_btn:
    if st.button("⬅️ Voltar", use_container_width=True):
        st.switch_page("pages/02_Pedidos.py")

st.write("")

# =====================================================
# BLOCOS DE EDIÇÃO (2 COLUNAS LARGAS)
# =====================================================
col_bloco1, col_bloco2 = st.columns([1, 1], gap="medium")

with col_bloco1:
    # 1. DADOS DO COMPRADOR
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 2px dashed #f5eee6; padding-bottom: 6px; text-transform: uppercase;'>👤 1. Dados do Comprador</div>", unsafe_allow_html=True)
        st.session_state.edit_nome = st.text_input("Nome Completo *", value=st.session_state.edit_nome)
        c_cpf, c_tel = st.columns(2)
        with c_cpf: st.session_state.edit_cpf = st.text_input("CPF / CNPJ", value=st.session_state.edit_cpf)
        with c_tel: st.session_state.edit_tel = st.text_input("WhatsApp *", value=st.session_state.edit_tel)

    # 2. SELEÇÃO DE PRODUTOS E CESTAS
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 2px dashed #f5eee6; padding-bottom: 6px; text-transform: uppercase;'>🎁 2. Trocar ou Adicionar Produtos</div>", unsafe_allow_html=True)
        
        cesta_troca = st.selectbox("Substituir / Inserir Cesta Base", [None] + cestas_disponiveis, format_func=lambda x: f"{x['nome']} (R$ {tratar_preco(x.get('preco')):.2f})" if x else "Selecione uma Cesta...", key="sel_troca_cesta")
        
        selecoes_cesta_edit = {}
        if cesta_troca:
            cfg = carregar_config_cesta_cached(cesta_troca["id"])
            if cfg and any(grp.get("produtos") for grp in cfg):
                st.markdown("<div style='font-size: 11.5px; font-weight: 700; color: #137333; margin-top: 5px;'>🍓 Opções da Cesta:</div>", unsafe_allow_html=True)
                for grp in cfg:
                    cat = grp.get("categoria", "Geral")
                    prods = grp.get("produtos", [])
                    maximo = grp.get("max_escolhas", 1)
                    if not prods: continue
                    if maximo == 1:
                        esc = st.selectbox(f"{cat}", prods, format_func=lambda p: p["nome"], key=f"edit_rad_{cesta_troca['id']}_{cat}")
                        if esc: selecoes_cesta_edit[cat] = [esc]
                    else:
                        escs = st.multiselect(f"{cat} (Máx: {maximo})", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"edit_mul_{cesta_troca['id']}_{cat}")
                        selecoes_cesta_edit[cat] = escs

        if st.button("➕ Inserir Cesta no Pedido", use_container_width=True):
            if cesta_troca:
                itens_sel_str = ""
                if selecoes_cesta_edit:
                    opcoes_str = " | ".join([f"{cat}: {', '.join([i['nome'] for i in itens])}" for cat, itens in selecoes_cesta_edit.items() if itens])
                    if opcoes_str: itens_sel_str = f"Itens: {opcoes_str}"

                st.session_state.edit_itens.append({
                    "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_troca["id"], "nome": cesta_troca["nome"], 
                    "preco_unitario": tratar_preco(cesta_troca.get("preco")), "quantidade": 1, "descricao": itens_sel_str
                })
                st.rerun()

    # 3. DESTINATÁRIO E CARTÃO
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 2px dashed #f5eee6; padding-bottom: 6px; text-transform: uppercase;'>💌 3. Destinatário e Cartão</div>", unsafe_allow_html=True)
        cd1, cd2 = st.columns(2)
        with cd1: st.session_state.edit_dest_nome = st.text_input("Nome Homenageado *", value=st.session_state.edit_dest_nome)
        with cd2: st.session_state.edit_dest_tel = st.text_input("Tel. Destinatário", value=st.session_state.edit_dest_tel)
        st.session_state.edit_motivo = st.text_input("Ocasião", value=st.session_state.edit_motivo)
        st.session_state.edit_mensagem = st.text_area("Mensagem do Cartão", height=70, value=st.session_state.edit_mensagem)

with col_bloco2:
    # 4. ADICIONAIS E EXTRAS
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 2px dashed #f5eee6; padding-bottom: 6px; text-transform: uppercase;'>🎀 4. Adicionais e Extras</div>", unsafe_allow_html=True)
        
        if adicionais_disponiveis:
            st.markdown("<div style='font-size: 12px; font-weight: 700; color: #5a3b28; margin-bottom: 6px;'>✨ Catálogo de Adicionais</div>", unsafe_allow_html=True)
            col_ad1, col_ad2 = st.columns(2)
            for idx, p_ad in enumerate(adicionais_disponiveis):
                preco_ad = tratar_preco(p_ad.get("preco"))
                txt_preco = f"(+ R$ {preco_ad:.2f})" if preco_ad > 0 else "(Sob Consulta)"
                col_alvo = col_ad1 if idx % 2 == 0 else col_ad2
                with col_alvo:
                    if st.checkbox(f"{p_ad['nome']} {txt_preco}", key=f"edit_chk_ad_{p_ad['id']}"):
                        if not any(it.get("nome") == p_ad["nome"] for it in st.session_state.edit_itens):
                            st.session_state.edit_itens.append({
                                "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": p_ad["id"], "nome": p_ad["nome"],
                                "preco_unitario": preco_ad, "quantidade": 1, "descricao": ""
                            })

        st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 12px 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 12px; font-weight: 700; color: #5a3b28; margin-bottom: 4px;'>✍️ Extra Personalizado</div>", unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns([2, 1, 1])
        with cm1: extra_nome_man = st.text_input("Nome", placeholder="Ex: Balão", key="edit_extra_nome", label_visibility="collapsed")
        with cm2: extra_preco_man = st.number_input("Valor", min_value=0.0, step=5.0, value=0.0, key="edit_extra_preco", label_visibility="collapsed")
        with cm3:
            if st.button("➕ Add", use_container_width=True):
                if extra_nome_man.strip():
                    st.session_state.edit_itens.append({
                        "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": extra_nome_man.strip(),
                        "preco_unitario": extra_preco_man, "quantidade": 1, "descricao": ""
                    })
                    st.rerun()

    # 5. ENDEREÇO E ENTREGA
    with st.container(border=True):
        st.markdown("<div style='font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 2px dashed #f5eee6; padding-bottom: 6px; text-transform: uppercase;'>📍 5. Endereço e Entrega</div>", unsafe_allow_html=True)
        st.session_state.edit_endereco = st.text_area("Endereço Completo de Entrega *", value=st.session_state.edit_endereco, height=75)
        ce1, ce2 = st.columns(2)
        with ce1: st.session_state.edit_data = st.date_input("Data Entrega", value=st.session_state.edit_data, format="DD/MM/YYYY")
        with ce2: st.session_state.edit_periodo = st.text_input("Horário / Período", value=st.session_state.edit_periodo)

# =====================================================
# CARRINHO / ITENS ATUAIS DO PEDIDO
# =====================================================
st.write("")
with st.container(border=True):
    st.markdown("<div style='font-size: 15px; font-weight: 800; color: #c5721f; margin-bottom: 12px; border-bottom: 2px solid #e8ddd3; padding-bottom: 6px;'>🛒 ITENS DO PEDIDO (EDITE QUANTIDADES OU REMOVA)</div>", unsafe_allow_html=True)
    
    total_bruto = 0
    if st.session_state.edit_itens:
        h1, h2, h3, h4, h5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
        h1.markdown("<div style='color:#775a46; font-size:12px; font-weight:700;'>Descrição</div>", unsafe_allow_html=True)
        h2.markdown("<div style='color:#775a46; font-size:12px; font-weight:700;'>Valor Un. (R$)</div>", unsafe_allow_html=True)
        h3.markdown("<div style='color:#775a46; font-size:12px; font-weight:700;'>Qtd</div>", unsafe_allow_html=True)
        h4.markdown("<div style='color:#775a46; font-size:12px; font-weight:700;'>Subtotal</div>", unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state.edit_itens):
            c1, c2, c3, c4, c5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
            with c1:
                icone = "📦" if item["tipo"] == "Cesta" else "✨"
                st.markdown(f"<div style='margin-top:6px; font-weight:700; font-size:13.5px; color:#4a2e1b;'>{icone} {item['nome']}</div>", unsafe_allow_html=True)
                if item.get("descricao"): st.caption(item["descricao"])
            with c2:
                novo_preco = st.number_input("Valor", value=float(item["preco_unitario"]), min_value=0.0, step=1.0, format="%.2f", key=f"edit_p_{item['id']}", label_visibility="collapsed")
                st.session_state.edit_itens[i]["preco_unitario"] = novo_preco
            with c3:
                nova_qtd = st.number_input("Qtd", value=int(item["quantidade"]), min_value=1, step=1, key=f"edit_q_{item['id']}", label_visibility="collapsed")
                st.session_state.edit_itens[i]["quantidade"] = nova_qtd
            with c4:
                sub_linha = novo_preco * nova_qtd
                total_bruto += sub_linha
                st.markdown(f"<div style='margin-top:8px; font-weight:800; font-size:15px; color:#137333;'>R$ {formatar_moeda(sub_linha)}</div>", unsafe_allow_html=True)
            with c5:
                if st.button("🗑️", key=f"edit_d_{item['id']}"):
                    st.session_state.edit_itens.pop(i)
                    st.rerun()
    else:
        st.info("Nenhum item inserido no pedido.")

# =====================================================
# TICKET DE RESUMO & FECHAMENTO
# =====================================================
with st.container(border=True):
    st.markdown("<div class='ticket-title'>📋 TICKET DE RESUMO & FECHAMENTO</div>", unsafe_allow_html=True)
    
    t_cf1, t_cf2, t_cf3 = st.columns(3)
    with t_cf1: st.session_state.edit_pagamento = st.selectbox("Pagamento", ["Pix", "Cartão de Crédito", "Faturamento (Boleto)", "Transferência Bancária"], index=["Pix", "Cartão de Crédito", "Faturamento (Boleto)", "Transferência Bancária"].index(st.session_state.edit_pagamento) if st.session_state.edit_pagamento in ["Pix", "Cartão de Crédito", "Faturamento (Boleto)", "Transferência Bancária"] else 0)
    with t_cf2: st.session_state.edit_status = st.selectbox("Status", ["Recebido", "Pendente", "Pago", "Em Produção", "Em Rota de Entrega", "Entregue", "Desistência"], index=["Recebido", "Pendente", "Pago", "Em Produção", "Em Rota de Entrega", "Entregue", "Desistência"].index(st.session_state.edit_status) if st.session_state.edit_status in ["Recebido", "Pendente", "Pago", "Em Produção", "Em Rota de Entrega", "Entregue", "Desistência"] else 0)
    with t_cf3: st.session_state.edit_frete = st.number_input("Frete (R$)", min_value=0.0, step=5.0, value=st.session_state.edit_frete)
    
    st.session_state.edit_desconto = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=st.session_state.edit_desconto)
    
    valor_desconto = total_bruto * (st.session_state.edit_desconto / 100)
    total_liquido = total_bruto - valor_desconto + st.session_state.edit_frete

    st.markdown("<hr style='border: none; border-top: 1px dashed #ceead6; margin: 12px 0;'>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="ticket-total">
        <span>TOTAL LÍQUIDO:</span> 
        <span>R$ {formatar_moeda(total_liquido)}</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("💾 SALVAR TODAS AS ALTERAÇÕES DO PEDIDO", type="primary"):
        if not st.session_state.edit_nome: st.error("Informe o nome do comprador."); st.stop()
        if not st.session_state.edit_itens: st.error("O pedido precisa ter ao menos um item."); st.stop()
        if not st.session_state.edit_endereco: st.error("Informe o endereço de entrega."); st.stop()

        lista_cestas = [it for it in st.session_state.edit_itens if it["tipo"] == "Cesta"]
        lista_extras = [it for it in st.session_state.edit_itens if it["tipo"] == "Extra"]
        
        lista_str_produtos = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})\n{it.get('descricao','')}".strip() for it in lista_cestas]
        lista_str_extras = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_extras]
        
        nome_cesta_princ = lista_cestas[0]["nome"] if lista_cestas else "Pedido Personalizado"
        cesta_id_princ = lista_cestas[0]["cesta_id"] if lista_cestas else None
            
        msg_adicionais = f"Desconto de {st.session_state.edit_desconto}% aplicado." if st.session_state.edit_desconto > 0 else ""
        if lista_str_extras:
            msg_adicionais += ("\n\n" if msg_adicionais else "") + "EXTRAS E ADICIONAIS:\n" + "\n".join(lista_str_extras)

        dados_atualizacao = {
            "cliente_nome": st.session_state.edit_nome.strip(),
            "cliente_telefone": re.sub(r'\D', '', st.session_state.edit_tel),
            "cliente_cpf": re.sub(r'\D', '', st.session_state.edit_cpf),
            "destinatario_nome": st.session_state.edit_dest_nome.strip(),
            "destinatario_telefone": st.session_state.edit_dest_tel.strip(),
            "motivo_homenagem": st.session_state.edit_motivo.strip() or "Atualizado",
            "cesta_id": cesta_id_princ,
            "cesta_nome": nome_cesta_princ,
            "produtos": "\n\n".join(lista_str_produtos),
            "adicionais": msg_adicionais,
            "pagamento": st.session_state.edit_pagamento,
            "mensagem": st.session_state.edit_mensagem.strip(),
            "endereco": st.session_state.edit_endereco.strip(),
            "data_entrega": st.session_state.edit_data.strftime("%Y-%m-%d"),
            "periodo_entrega": st.session_state.edit_periodo.strip() or "A combinar",
            "status": st.session_state.edit_status,
            "valor_frete": st.session_state.edit_frete,
            "valor_total": total_liquido
        }
        
        with st.spinner("Atualizando pedido no sistema..."):
            try:
                supabase.table("pedidos").update(dados_atualizacao).eq("id", pedido_id).execute()
                st.success("✅ Pedido alterado e atualizado com sucesso!")
                time.sleep(1)
                st.switch_page("pages/02_Pedidos.py")
            except Exception as e:
                st.error(f"❌ Erro ao atualizar pedido: {e}")

# =====================================================
# BOTÕES DE AÇÃO INFERIORES
# =====================================================
st.write("")
c_imp, c_exc = st.columns(2)
with c_imp:
    if st.button("🖨️ Imprimir Ficha", use_container_width=True):
        components.html("<script>window.print();</script>", height=0)
with c_exc:
    if st.button("🗑️ Excluir Pedido", use_container_width=True):
        try:
            supabase.table("pedidos").delete().eq("id", pedido_id).execute()
            st.session_state['pedido_detalhe_id'] = None
            st.switch_page("pages/02_Pedidos.py")
        except Exception as e:
            st.error(f"Erro ao excluir: {e}")
