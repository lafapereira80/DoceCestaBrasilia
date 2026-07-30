import streamlit as st
import pandas as pd
import requests
import re
import uuid
from datetime import datetime, date
from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.pedido_service import salvar_pedido
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

st.set_page_config(page_title="Novo Pedido (Varejo)", page_icon="🛍️", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# =====================================================
# CSS PREMIUM
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }
h1, h2, h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-bottom: 8px !important; letter-spacing: -0.3px; }

.header-banner { background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 25px 20px; border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04); margin-bottom: 2rem; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 6px; }
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; text-align: center;}
.header-subtitle { font-size: 14px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 0px !important; text-align: center;}

.corp-card { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 24px; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.02); margin-bottom: 15px; }
.corp-title { font-size: 18px; font-weight: 800; color: #c5721f; margin-bottom: 15px; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px;}

.resumo-financeiro { background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 12px; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; margin-top: 15px; }
.resumo-item { text-align: center; }
.resumo-label { font-size: 12px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; }
.resumo-valor { font-size: 20px; font-weight: 800; color: #4a2e1b; }
.resumo-destaque { font-size: 24px; font-weight: 800; color: #137333; }

.polaroid-box { background: #fff8f8; border: 2px dashed #ffb6c1; border-radius: 12px; padding: 15px; margin-top: 15px;}
div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 800 !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #c5721f 0%, #a65d14) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(197, 114, 31, 0.2) !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background: linear-gradient(135deg, #a65d14 0%, #874c10) !important; transform: translateY(-2px) !important; }

div[data-testid="stNumberInput"] label { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Varejo (Pessoa Física)</h1>
    <p class="header-subtitle">Monte pedidos completos, selecione opções de cestas, suba polaroids e feche vendas 🛍️</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES E CACHES (INTEGRAÇÃO SUPABASE E VIA CEP)
# =====================================================
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def buscar_cep_api(cep_str):
    cep_limpo = re.sub(r'\D', '', cep_str)
    if len(cep_limpo) != 8: return False, "CEP inválido. Digite 8 números."
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        if r.status_code == 200:
            dados = r.json()
            if "erro" in dados: return False, "CEP não encontrado."
            return True, dados
        return False, "CEP não encontrado."
    except: return False, "Erro de conexão ao buscar o CEP."

@st.cache_data(ttl=60, show_spinner=False)
def obter_cestas_admin():
    cestas = listar_cestas()
    return sorted([c for c in cestas if c.get("ativa", True)], key=lambda x: x.get("nome", ""))

@st.cache_data(ttl=60, show_spinner=False)
def obter_adicionais_admin():
    try:
        res = supabase.table("produtos").select("*").execute()
        ativos = [p for p in (res.data or []) if p.get("ativo", True) and p.get("categoria", "").strip().lower() in ["adicionais", "adicional"]]
        return sorted(ativos, key=lambda x: x.get("nome", ""))
    except: return []

def obter_itens_da_cesta(cesta_id):
    try:
        res = supabase.table("produtos").select("*").eq("cesta_id", cesta_id).eq("ativo", True).execute()
        if res.data: return res.data
    except: pass
    return []

cestas_disponiveis = obter_cestas_admin()
adicionais_disponiveis = obter_adicionais_admin()

if "itens_varejo" not in st.session_state: st.session_state["itens_varejo"] = []
if "cep" not in st.session_state: st.session_state.cep = ""
if "rua" not in st.session_state: st.session_state.rua = ""
if "num" not in st.session_state: st.session_state.num = ""
if "comp" not in st.session_state: st.session_state.comp = ""
if "bairro" not in st.session_state: st.session_state.bairro = ""
if "cidade" not in st.session_state: st.session_state.cidade = ""
if "uf" not in st.session_state: st.session_state.uf = ""

# =====================================================
# GERADOR DE PEDIDO
# =====================================================
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

st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown('<div class="corp-title">🎁 2. Montagem do Pedido</div>', unsafe_allow_html=True)

st.markdown("<div style='font-size: 14px; font-weight: 700; color: #775a46; margin-bottom: 5px;'>📦 Escolha a Cesta Base</div>", unsafe_allow_html=True)
cesta_sel = st.selectbox("Cestas", [None] + cestas_disponiveis, format_func=lambda x: f"{x['nome']} (R$ {tratar_preco(x.get('preco')):.2f})" if x else "Selecione uma Cesta...", label_visibility="collapsed")

opcoes_selecionadas_cesta = []
if cesta_sel:
    st.info(f"📝 **Descrição da Cesta:** {cesta_sel.get('descricao', 'Sem descrição cadastrada.')}")
    
    itens_vinculados = obter_itens_da_cesta(cesta_sel["id"])
    if itens_vinculados:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #c5721f; margin-top: 10px;'>Selecione as opções da cesta (Sabores, Bebidas, etc):</div>", unsafe_allow_html=True)
        opcoes_selecionadas_cesta = st.multiselect("Opções", itens_vinculados, format_func=lambda x: x["nome"], label_visibility="collapsed")

if st.button("➕ Adicionar Cesta ao Pedido", use_container_width=True):
    if cesta_sel:
        desc_final = cesta_sel.get("descricao", "")
        if opcoes_selecionadas_cesta:
            nomes_opcoes = [op["nome"] for op in opcoes_selecionadas_cesta]
            desc_final += f" | Opções escolhidas: {', '.join(nomes_opcoes)}"
            
        st.session_state["itens_varejo"].append({
            "id": str(uuid.uuid4()), "tipo": "Cesta", "cesta_id": cesta_sel["id"], "nome": cesta_sel["nome"], 
            "preco_unitario": tratar_preco(cesta_sel.get("preco")), "quantidade": 1, "descricao": desc_final
        })
        st.rerun()

st.write("")
col_add2, col_add3 = st.columns(2)
with col_add2:
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✨ Adicionais Globais do Catálogo</div>", unsafe_allow_html=True)
    adc_sel = st.selectbox("Extras Globais", [None] + adicionais_disponiveis, format_func=lambda x: f"{x['nome']} (+ R$ {tratar_preco(x.get('preco')):.2f})" if x else "Selecione um Adicional...", label_visibility="collapsed")
    if st.button("➕ Inserir Adicional", use_container_width=True):
        if adc_sel:
            st.session_state["itens_varejo"].append({
                "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": adc_sel["nome"], 
                "preco_unitario": tratar_preco(adc_sel.get("preco")), "quantidade": 1, "descricao": ""
            })
            st.rerun()

with col_add3:
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✍️ Extra Personalizado Manual</div>", unsafe_allow_html=True)
    txt_man = st.text_input("Extra Manual", placeholder="Ex: Fotos Polaroid", label_visibility="collapsed")
    if st.button("➕ Inserir Manual", use_container_width=True):
        if txt_man.strip():
            st.session_state["itens_varejo"].append({
                "id": str(uuid.uuid4()), "tipo": "Extra", "cesta_id": None, "nome": txt_man.strip(), 
                "preco_unitario": 0.0, "quantidade": 1, "descricao": ""
            })
            st.rerun()

# CARRINHO DE COMPRAS EDITÁVEL
total_bruto = 0
if st.session_state["itens_varejo"]:
    st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("### 🛒 Resumo do Pedido (Edite Preços e Quantidades)")
    
    h1, h2, h3, h4, h5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
    h1.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Descrição</div>", unsafe_allow_html=True)
    h2.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Valor Un. (R$)</div>", unsafe_allow_html=True)
    h3.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Qtd</div>", unsafe_allow_html=True)
    h4.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Subtotal</div>", unsafe_allow_html=True)
    
    for i, item in enumerate(st.session_state["itens_varejo"]):
        c1, c2, c3, c4, c5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
        with c1:
            icone = "📦" if item["tipo"] == "Cesta" else "✨"
            st.markdown(f"<div style='margin-top:8px; font-weight:700; font-size:14px; color:#4a2e1b;'>{icone} {item['nome']}</div>", unsafe_allow_html=True)
        with c2:
            novo_preco = st.number_input("Valor", value=float(item["preco_unitario"]), min_value=0.0, step=1.0, format="%.2f", key=f"p_{item['id']}", label_visibility="collapsed")
            st.session_state["itens_varejo"][i]["preco_unitario"] = novo_preco
        with c3:
            nova_qtd = st.number_input("Qtd", value=int(item["quantidade"]), min_value=1, step=1, key=f"q_{item['id']}", label_visibility="collapsed")
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

# UPLOAD REAL DE POLAROIDS PARA O SUPABASE BUCKET
tem_polaroid = any("polaroid" in item["nome"].lower() or "foto" in item["nome"].lower() for item in st.session_state["itens_varejo"])
fotos_enviadas = []
if tem_polaroid:
    st.markdown("""
    <div class="polaroid-box">
        <h4 style="color: #d1476a; margin-top: 0; margin-bottom: 5px;">📸 Upload de Fotos Polaroid</h4>
        <p style="font-size: 13px; color: #5a3b28; margin-bottom: 15px;">O sistema detectou fotos no pedido! Faça o upload das imagens. Elas serão salvas no <b>Supabase Storage (Bucket 'pedido_fotos')</b> e os links irão automaticamente para a ficha técnica da cozinha.</p>
    </div>
    """, unsafe_allow_html=True)
    fotos_enviadas = st.file_uploader("Selecione as fotos (PNG, JPG, JPEG)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown('<div class="corp-title">💌 3. Mensagem do Cartão</div>', unsafe_allow_html=True)
mensagem_cartao = st.text_area("Texto do Cartão (Opcional)", height=100, placeholder="Ex: Feliz aniversário, meu amor! Com carinho, João.")

st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown('<div class="corp-title">📍 4. Endereço de Entrega (Busca por CEP)</div>', unsafe_allow_html=True)

col_cep1, col_cep2, col_cep3 = st.columns([2, 1, 3])
with col_cep1:
    cep_input = st.text_input("Digite o CEP", value=st.session_state.cep, placeholder="Apenas números")
with col_cep2:
    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
    if st.button("🔍 Buscar CEP", use_container_width=True):
        if cep_input:
            sucesso, dados_cep = buscar_cep_api(cep_input)
            if sucesso:
                st.session_state.cep = cep_input
                st.session_state.rua = dados_cep.get("logradouro", "")
                st.session_state.bairro = dados_cep.get("bairro", "")
                st.session_state.cidade = dados_cep.get("localidade", "")
                st.session_state.uf = dados_cep.get("uf", "")
                st.rerun()
            else:
                st.error(dados_cep)
        else:
            st.warning("Digite um CEP válido.")
            
st.write("")
col_end1, col_end2, col_end3 = st.columns([3, 1, 2])
with col_end1:
    rua_input = st.text_input("Rua / Logradouro *", value=st.session_state.rua)
with col_end2:
    num_input = st.text_input("Número *", value=st.session_state.num)
with col_end3:
    comp_input = st.text_input("Complemento", value=st.session_state.comp, placeholder="Ex: Apto 101")
    
col_end4, col_end5, col_end6 = st.columns([2, 2, 1])
with col_end4:
    bairro_input = st.text_input("Bairro *", value=st.session_state.bairro)
with col_end5:
    cidade_input = st.text_input("Cidade *", value=st.session_state.cidade)
with col_end6:
    uf_input = st.text_input("UF", value=st.session_state.uf)

endereco_completo = ""
if rua_input and num_input and bairro_input:
    comp_str = f" - {comp_input}" if comp_input else ""
    endereco_completo = f"{rua_input}, {num_input}{comp_str} - {bairro_input}, {cidade_input}-{uf_input}"

st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown('<div class="corp-title">💰 5. Logística, Fechamento e Valores</div>', unsafe_allow_html=True)

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    data_entrega = st.date_input("Data de Entrega", value=date.today(), format="DD/MM/YYYY")
with col_d2:
    horario = st.text_input("Horário Acordado", placeholder="Ex: 09h às 10h")
with col_d3:
    prazo_pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Dinheiro", "Link de Pagamento"])
    
st.write("")
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.markdown("<div style='font-size: 14px; font-weight: 700; color: #4a2e1b;'>🚚 Valor do Frete / Entrega (R$)</div>", unsafe_allow_html=True)
    frete_lote = st.number_input("Frete", min_value=0.0, step=5.0, value=0.0, label_visibility="collapsed")
with col_f2:
    st.markdown("<div style='font-size: 14px; font-weight: 700; color: #c5221f;'>🔻 Desconto Concedido (%)</div>", unsafe_allow_html=True)
    desconto_perc = st.number_input("Desconto", min_value=0.0, max_value=100.0, step=1.0, value=0.0, label_visibility="collapsed")

valor_desconto = total_bruto * (desconto_perc / 100)
total_liquido = total_bruto - valor_desconto + frete_lote

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
        <div class="resumo-label">Frete (Entrega)</div>
        <div class="resumo-valor">R$ {formatar_moeda(frete_lote)}</div>
    </div>
    <div class="resumo-item">
        <div class="resumo-label">TOTAL A PAGAR</div>
        <div class="resumo-destaque">R$ {formatar_moeda(total_liquido)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
if st.button("✅ REGISTRAR PEDIDO DE VAREJO", type="primary", use_container_width=True):
    if not cliente_nome: st.error("Informe o Nome do Cliente."); st.stop()
    if not st.session_state["itens_varejo"]: st.error("Adicione itens ao carrinho."); st.stop()
    if not endereco_completo: st.error("Faça a busca do CEP e complete o Endereço."); st.stop()
    
    links_polaroid = []
    if tem_polaroid and fotos_enviadas:
        with st.spinner("📦 Salvando fotos no banco de dados (Supabase)..."):
            for foto in fotos_enviadas:
                ext = foto.name.split('.')[-1]
                file_name = f"polaroid_{uuid.uuid4().hex}.{ext}"
                try:
                    # Upload para o bucket pedido_fotos
                    supabase.storage.from_("pedido_fotos").upload(file_name, foto.read(), {"content-type": foto.type})
                    url = supabase.storage.from_("pedido_fotos").get_public_url(file_name)
                    links_polaroid.append(url)
                except Exception as e:
                    st.warning(f"Erro ao subir foto: O bucket 'pedido_fotos' existe e é público no Supabase? Erro técnico: {e}")

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
        
    msg_adicionais = f"Desconto de {desconto_perc}% aplicado."
    if lista_str_extras:
        msg_adicionais += "\n\nADICIONAIS:\n" + "\n".join(lista_str_extras)

    if links_polaroid:
        msg_adicionais += "\n\n📸 LINKS DAS FOTOS POLAROID (Baixar para Produção):\n" + "\n".join(links_polaroid)

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
        "endereco": endereco_completo,
        "data_entrega": data_entrega.strftime("%Y-%m-%d"),
        "periodo_entrega": horario.strip() or "A combinar",
        "status": "Recebido",
        "valor_frete": frete_lote,
        "valor_total": total_liquido,
        "cesta_montada": False
    }
    
    sucesso, p_id = salvar_pedido(dados_pf)
    if sucesso:
        st.success(f"🎉 Pedido de Varejo para {cliente_nome} registrado! Aguardando pagamento no Mural.")
        st.session_state["itens_varejo"] = []
        st.session_state.cep = ""
        st.session_state.rua = ""
        st.session_state.num = ""
        st.session_state.comp = ""
        st.session_state.bairro = ""
        st.session_state.cidade = ""
        st.session_state.uf = ""
    else:
        st.error("Erro ao registrar o pedido no banco de dados.")

st.markdown('</div>', unsafe_allow_html=True)
