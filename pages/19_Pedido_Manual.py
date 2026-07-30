import streamlit as st
import pandas as pd
import requests
import re
import uuid
from datetime import datetime, date

from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.produto_service import listar_produtos_por_categoria_id
from services.pedido_service import salvar_pedido
from services.pedido_adicional_service import salvar_adicionais_pedido
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
# CSS PREMIUM E RESPONSIVO
# =====================================================
st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1100px; }
h1, h2, h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-bottom: 8px !important; letter-spacing: -0.3px; }

/* CABEÇALHO COM BOTÃO */
.header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.header-banner {
    flex-grow: 1; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 6px; 
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 25px 20px;
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
}
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; text-align: center;}
.header-subtitle { font-size: 14px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 0px !important; text-align: center;}

/* CARDS PADRÃO B2B */
.corp-card {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 24px;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.02); margin-bottom: 15px;
}
.corp-title { font-size: 18px; font-weight: 800; color: #c5721f; margin-bottom: 15px; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px;}

/* PREVIEW WHATSAPP/PDF */
.proposta-preview {
    background: #ffffff; border: 1px solid #dfcdbb; border-radius: 12px; padding: 30px;
    font-family: 'Arial', sans-serif; color: #333; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
.proposta-header { text-align: center; border-bottom: 3px solid #c5721f; padding-bottom: 15px; margin-bottom: 25px; }
.proposta-total { font-size: 22px; font-weight: bold; color: #c5721f; text-align: right; margin-top: 20px; border-top: 2px solid #e8ddd3; padding-top: 15px;}

/* RESUMO FINANCEIRO */
.resumo-financeiro {
    background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 12px; padding: 15px 20px;
    display: flex; justify-content: space-between; align-items: center; margin-top: 15px; flex-wrap: wrap; gap: 10px;
}
.resumo-item { text-align: center; flex: 1; min-width: 120px;}
.resumo-label { font-size: 12px; font-weight: 700; color: #775a46; text-transform: uppercase; letter-spacing: 0.5px; }
.resumo-valor { font-size: 20px; font-weight: 800; color: #4a2e1b; }
.resumo-destaque { font-size: 24px; font-weight: 800; color: #137333; }

.polaroid-box { background: #fff8f8; border: 2px dashed #ffb6c1; border-radius: 12px; padding: 15px; margin-top: 15px;}

/* BOTÕES MODERNOS */
div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 800 !important; transition: all 0.2s ease !important; }
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #c5721f 0%, #a65d14) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(197, 114, 31, 0.2) !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background: linear-gradient(135deg, #a65d14 0%, #874c10) !important; transform: translateY(-2px) !important; }

/* OCULTAR LABELS DOS NUMBERS NA LISTA */
div[data-testid="stNumberInput"] label { display: none !important; }

/* RESPONSIVIDADE MOBILE */
@media (max-width: 768px) {
    .header-container { flex-direction: column; gap: 15px; }
    .header-banner { width: 100%; padding: 20px 15px; }
    .corp-card { padding: 16px; }
    .resumo-financeiro { flex-direction: column; text-align: left; align-items: flex-start; }
    .resumo-item { text-align: left; display: flex; justify-content: space-between; width: 100%; border-bottom: 1px solid #f5eee6; padding-bottom: 8px;}
}
</style>
""", unsafe_allow_html=True)

# CABEÇALHO COM BOTÃO DE VOLTAR
c_head, c_btn = st.columns([4, 1], vertical_alignment="center")
with c_head:
    st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">Cadastrar Pedido Varejo (PF)</h1>
        <p class="header-subtitle">Monte pedidos, adicione extras vivos e envie para a produção 🛍️</p>
    </div>
    """, unsafe_allow_html=True)
with c_btn:
    if st.button("⬅️ Voltar ao Mural", use_container_width=True):
        st.switch_page("pages/02_Pedidos.py")

# =====================================================
# FUNÇÕES, CACHES E BLINDAGENS
# =====================================================
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def buscar_cep_api(cep_str):
    cep_limpo = re.sub(r'\D', '', cep_str)
    if len(cep_limpo) != 8: return False, "CEP inválido."
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        if r.status_code == 200 and "erro" not in r.json(): return True, r.json()
    except: pass
    return False, "CEP não encontrado."

@st.cache_data(ttl=60, show_spinner=False)
def obter_secoes_e_cestas():
    try:
        res_secoes = supabase.table("vitrine_secoes").select("nome").eq("ativa", True).order("ordem").execute()
        secoes = [s["nome"] for s in (res_secoes.data or [])]
        if not secoes: secoes = ["Cestas de Café"]
        cestas = [c for c in listar_cestas() if c.get("ativa", True)]
        return secoes, sorted(cestas, key=lambda x: x.get("nome", ""))
    except: return ["Cestas de Café"], []

@st.cache_data(ttl=60, show_spinner=False)
def obter_adicionais_catalogo():
    try:
        res = supabase.table("produtos").select("*").execute()
        ativos = [p for p in (res.data or []) if p.get("ativo", True) and "adicional" in p.get("categoria", "").strip().lower()]
        return sorted(ativos, key=lambda x: x.get("nome", ""))
    except: return []

secoes_disponiveis, cestas_ativas = obter_secoes_e_cestas()
adicionais_disponiveis = obter_adicionais_catalogo()

# Sessões do sistema
if "itens_pedido" not in st.session_state: st.session_state["itens_pedido"] = []
for key in ["pf_cep", "pf_rua", "pf_num", "pf_comp", "pf_bairro", "pf_cidade", "pf_uf", "pf_ult_cep"]:
    if key not in st.session_state: st.session_state[key] = ""

# =====================================================
# 1. DADOS DO CLIENTE E HOMENAGEADO
# =====================================================
st.markdown('<div class="corp-card">', unsafe_allow_html=True)
st.markdown('<div class="corp-title">👤 1. Comprador e Homenageado</div>', unsafe_allow_html=True)

col_e1, col_e2 = st.columns(2)
with col_e1:
    cliente_nome = st.text_input("Nome do Cliente (Comprador) *", placeholder="Ex: Maria da Silva")
    cliente_tel = st.text_input("Telefone / WhatsApp *", placeholder="Ex: (61) 99999-9999")
with col_e2:
    dest_nome = st.text_input("Nome do Destinatário (Quem vai receber) *", placeholder="Repita se for a mesma pessoa")
    dest_tel = st.text_input("Telefone do Destinatário", placeholder="(Opcional)")
st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 2. SELEÇÃO DE PRODUTOS E EXTRAS (ESTILO B2B)
# =====================================================
st.markdown('<div class="corp-card">', unsafe_allow_html=True)
st.markdown('<div class="corp-title">🎁 2. Adicionar Itens ao Pedido (Pacotes e Extras)</div>', unsafe_allow_html=True)

col_add1, col_add2, col_add3 = st.columns(3)

with col_add1:
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>📦 Catálogo e Cestas</div>", unsafe_allow_html=True)
    secao_sel = st.selectbox("Seção", secoes_disponiveis, label_visibility="collapsed")
    cestas_filtradas = [c for c in cestas_ativas if (c.get("secao_vitrine") or "Cestas de Café").strip().lower() == secao_sel.strip().lower()]
    cesta_sel = st.selectbox("Cestas", [None] + cestas_filtradas, format_func=lambda x: x["nome"] if x else "Selecione uma Cesta...", label_visibility="collapsed")
    
    opcoes_str = ""
    if cesta_sel:
        cfg = carregar_configuracao_cesta(cesta_sel["id"])
        if cfg and any(grp.get("produtos") for grp in cfg):
            opcoes_str = st.text_input("Especifique (Sabores/Bebidas)", placeholder="Ex: Bolo de Choc, Vinho Suave...")

    if st.button("➕ Inserir Produto", use_container_width=True):
        if cesta_sel:
            desc = cesta_sel.get("descricao", "")
            if opcoes_str: desc += f" | Opções: {opcoes_str}"
            st.session_state["itens_pedido"].append({
                "id": str(uuid.uuid4()), "tipo": "Cesta", "produto_id": cesta_sel["id"], "nome": cesta_sel["nome"], 
                "preco_unitario": tratar_preco(cesta_sel.get("preco")), "quantidade": 1, "descricao": desc
            })
            st.rerun()

with col_add2:
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✨ Adicionais Oficiais</div>", unsafe_allow_html=True)
    adc_sel = st.selectbox("Extras", [None] + adicionais_disponiveis, format_func=lambda x: x["nome"] if x else "Selecione um Adicional...", label_visibility="collapsed")
    if st.button("➕ Inserir Adicional", use_container_width=True):
        if adc_sel:
            st.session_state["itens_pedido"].append({
                "id": str(uuid.uuid4()), "tipo": "Extra", "produto_id": adc_sel["id"], "nome": adc_sel["nome"], 
                "preco_unitario": tratar_preco(adc_sel.get("preco")), "quantidade": 1, "descricao": ""
            })
            st.rerun()

with col_add3:
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #775a46;'>✍️ Extra Personalizado</div>", unsafe_allow_html=True)
    txt_man = st.text_input("Extra Manual", placeholder="Ex: Balão Metalizado", label_visibility="collapsed")
    if st.button("➕ Inserir Manual", use_container_width=True):
        if txt_man.strip():
            st.session_state["itens_pedido"].append({
                "id": str(uuid.uuid4()), "tipo": "Extra", "produto_id": None, "nome": txt_man.strip(), 
                "preco_unitario": 0.0, "quantidade": 1, "descricao": ""
            })
            st.rerun()

# -----------------------------------------------------
# CARRINHO VIVO (EDIÇÃO DE VALORES E QTD)
# -----------------------------------------------------
total_bruto = 0

if st.session_state["itens_pedido"]:
    st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("### 🛒 Resumo dos Itens (Edite Preços e Quantidades)")
    
    h1, h2, h3, h4, h5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
    h1.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Descrição do Item</div>", unsafe_allow_html=True)
    h2.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Valor Un. (R$)</div>", unsafe_allow_html=True)
    h3.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Qtd</div>", unsafe_allow_html=True)
    h4.markdown("<div style='color:#775a46; font-size:12px; font-weight:700; text-transform:uppercase;'>Subtotal</div>", unsafe_allow_html=True)
    
    for i, item in enumerate(st.session_state["itens_pedido"]):
        c1, c2, c3, c4, c5 = st.columns([3.5, 1.5, 1.5, 1.5, 0.5])
        
        with c1:
            icone = "📦" if item["tipo"] == "Cesta" else "🎀"
            st.markdown(f"<div style='margin-top:8px; font-weight:700; font-size:14px; color:#4a2e1b;'>{icone} {item['nome']}</div>", unsafe_allow_html=True)
            
        with c2:
            novo_preco = st.number_input("Valor", value=float(item["preco_unitario"]), min_value=0.0, step=1.0, format="%.2f", key=f"p_{item['id']}", label_visibility="collapsed")
            st.session_state["itens_pedido"][i]["preco_unitario"] = novo_preco
            
        with c3:
            nova_qtd = st.number_input("Qtd", value=int(item["quantidade"]), min_value=1, step=1, key=f"q_{item['id']}", label_visibility="collapsed")
            st.session_state["itens_pedido"][i]["quantidade"] = nova_qtd
            
        with c4:
            subtotal_linha = novo_preco * nova_qtd
            total_bruto += subtotal_linha
            st.markdown(f"<div style='margin-top:10px; font-weight:800; font-size:16px; color:#c5721f;'>R$ {formatar_moeda(subtotal_linha)}</div>", unsafe_allow_html=True)
            
        with c5:
            st.markdown("<div style='margin-top:2px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"d_{item['id']}", help="Remover"):
                st.session_state["itens_pedido"].pop(i)
                st.rerun()

    st.write("")
    if st.button("🧹 Esvaziar Carrinho"):
        st.session_state["itens_pedido"] = []
        st.rerun()

# -----------------------------------------------------
# INTELIGÊNCIA POLAROID
# -----------------------------------------------------
tem_polaroid = any("polaroid" in item["nome"].lower() or "foto" in item["nome"].lower() for item in st.session_state["itens_pedido"])
fotos_upload = []

if tem_polaroid:
    st.markdown("""
    <div class="polaroid-box">
        <h4 style="color: #d1476a; margin-top: 0; margin-bottom: 5px;">📸 Upload de Fotos Polaroid</h4>
        <p style="font-size: 13px; color: #5a3b28;">O sistema identificou polaroids! Anexe as imagens enviadas pelo cliente. Elas serão salvas no Supabase (bucket pedido_fotos) para a produção.</p>
    </div>
    """, unsafe_allow_html=True)
    fotos_upload = st.file_uploader("Selecione as fotos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 3. ENDEREÇO, LOGÍSTICA E CARTÃO
# =====================================================
st.markdown('<div class="corp-card">', unsafe_allow_html=True)
st.markdown('<div class="corp-title">📍 3. Endereço, Logística e Mensagem</div>', unsafe_allow_html=True)

# Busca CEP
cx1, cx2, cx3 = st.columns([1.5, 1, 3])
with cx1:
    cep_in = st.text_input("CEP de Entrega", max_chars=8, placeholder="Somente números", value=st.session_state.pf_cep)
    if len(re.sub(r'\D', '', cep_in)) == 8 and st.session_state.pf_ult_cep != re.sub(r'\D', '', cep_in):
        ok, d_cep = buscar_cep_api(cep_in)
        if ok:
            st.session_state.pf_rua = d_cep.get("logradouro", "")
            st.session_state.pf_bairro = d_cep.get("bairro", "")
            st.session_state.pf_cidade = f"{d_cep.get('localidade', '')}-{d_cep.get('uf', '')}"
            st.session_state.pf_cep = cep_in
        st.session_state.pf_ult_cep = re.sub(r'\D', '', cep_in)
        st.rerun()

with cx2:
    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
    if st.button("🔍 Buscar", use_container_width=True): pass

c_r1, c_r2, c_r3 = st.columns([3, 1, 2])
rua = c_r1.text_input("Rua/Logradouro *", value=st.session_state.pf_rua)
num = c_r2.text_input("Nº *", value=st.session_state.pf_num)
comp = c_r3.text_input("Complemento", value=st.session_state.pf_comp)

c_b1, c_b2 = st.columns(2)
bairro = c_b1.text_input("Bairro *", value=st.session_state.pf_bairro)
cidade = c_b2.text_input("Cidade-UF *", value=st.session_state.pf_cidade)

st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 15px 0;'>", unsafe_allow_html=True)

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1: dt_entrega = st.date_input("Data de Entrega", value=date.today(), format="DD/MM/YYYY")
with col_d2: horario = st.text_input("Horário Combinado", placeholder="Ex: 09h às 10h")
with col_d3: motivo = st.text_input("Ocasião (Opcional)", placeholder="Ex: Dia das Mães")

mensagem = st.text_area("💌 Mensagem do Cartão", height=80, placeholder="Texto exato que irá impresso no cartão de presentes.")
st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 4. PAGAMENTO, RESUMO E FECHAMENTO
# =====================================================
st.markdown('<div class="corp-card">', unsafe_allow_html=True)
st.markdown('<div class="corp-title">💰 4. Pagamento e Fechamento</div>', unsafe_allow_html=True)

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    prazo_pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito"])
with col_p2:
    frete_val = st.number_input("Frete / Entrega (R$)", min_value=0.0, step=5.0, value=0.0)
with col_p3:
    desc_perc = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0)

# CÁLCULOS FINAIS
valor_desconto = total_bruto * (desc_perc / 100)
total_liquido = total_bruto - valor_desconto + frete_val

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
        <div class="resumo-valor">R$ {formatar_moeda(frete_val)}</div>
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
    ver_preview = st.checkbox("👁️ Gerar Espelho para Conferência", value=False)
    
with col_btn2:
    if st.button("✅ REGISTRAR PEDIDO", type="primary", use_container_width=True):
        if not cliente_nome: st.error("Informe o Nome do Cliente."); st.stop()
        if not st.session_state["itens_pedido"]: st.error("Adicione itens ao pedido (Passo 2)."); st.stop()
        if not rua or not num or not bairro: st.error("Preencha o Endereço de Entrega corretamente."); st.stop()

        # UPLOAD DAS POLAROIDS
        links_polaroid = []
        if tem_polaroid and fotos_upload:
            with st.spinner("📦 Salvando fotos no banco de dados (Supabase)..."):
                for foto in fotos_upload:
                    ext = foto.name.split('.')[-1]
                    file_name = f"polaroid_{uuid.uuid4().hex}.{ext}"
                    try:
                        supabase.storage.from_("pedido_fotos").upload(file_name, foto.read(), {"content-type": foto.type})
                        url = supabase.storage.from_("pedido_fotos").get_public_url(file_name)
                        links_polaroid.append(url)
                    except Exception as e:
                        st.warning(f"Erro ao subir foto para o bucket pedido_fotos: {e}")

        # SEPARA CESTAS E EXTRAS PARA O BANCO DE DADOS
        lista_cestas = [it for it in st.session_state["itens_pedido"] if it["tipo"] == "Cesta"]
        lista_extras = [it for it in st.session_state["itens_pedido"] if it["tipo"] == "Extra"]
        
        lista_str_produtos = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})\n{it.get('descricao','')}".strip() for it in lista_cestas]
        lista_str_extras = [f"{it['quantidade']}x {it['nome']} (R$ {formatar_moeda(it['preco_unitario'])})" for it in lista_extras]
        
        nome_cesta_principal = lista_cestas[0]["nome"] if lista_cestas else "Itens Avulsos"
        cesta_id_principal = lista_cestas[0]["produto_id"] if lista_cestas else None
            
        msg_adicionais = f"Desconto de {desc_perc}% aplicado." if desc_perc > 0 else "Sem desconto."
        if lista_str_extras:
            msg_adicionais += "\n\nADICIONAIS:\n" + "\n".join(lista_str_extras)

        if links_polaroid:
            msg_adicionais += "\n\n📸 LINKS FOTOS POLAROID (Acesso p/ Impressão):\n" + "\n".join(links_polaroid)

        cep_final = f" (CEP: {cep_in})" if cep_in.strip() else ""
        end_final = f"{rua}, {num} - {comp} - {bairro}, {cidade}{cep_final}"

        dados_pf = {
            "cliente_nome": cliente_nome.strip(),
            "cliente_telefone": cliente_tel.strip() or "00000000000",
            "cliente_cpf": "00000000000",
            "destinatario_nome": dest_nome.strip() or cliente_nome.strip(),
            "destinatario_telefone": dest_tel.strip(),
            "motivo_homenagem": motivo.strip() or "Varejo",
            "cesta_id": cesta_id_principal,
            "cesta_nome": nome_cesta_principal,
            "produtos": "\n\n".join(lista_str_produtos) if lista_str_produtos else "\n".join(lista_str_extras),
            "adicionais": msg_adicionais,
            "pagamento": prazo_pagamento,
            "mensagem": mensagem.strip(),
            "endereco": end_final,
            "data_entrega": dt_entrega.strftime("%Y-%m-%d"),
            "periodo_entrega": horario.strip() or "A combinar",
            "status": "Recebido",
            "valor_frete": frete_val,
            "valor_total": total_liquido,
            "cesta_montada": False
        }
        
        with st.spinner("Registrando pedido..."):
            sucesso, p_id = salvar_pedido(dados_pf)
            if sucesso:
                if lista_extras:
                    adicionais_bd = [{"produto_id": e.get("produto_id"), "nome": e["nome"], "preco": e["preco_unitario"]} for e in lista_extras]
                    salvar_adicionais_pedido(p_id, adicionais_bd)
                
                st.success(f"🎉 Pedido gerado! Você será redirecionado em instantes...")
                st.session_state["itens_pedido"] = []
                for k in ["pf_cep", "pf_rua", "pf_num", "pf_comp", "pf_bairro", "pf_cidade", "pf_ult_cep"]: st.session_state[k] = ""
                time.sleep(2)
                st.switch_page("pages/02_Pedidos.py")
            else:
                st.error("Erro ao registrar o pedido no banco de dados.")

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# ESPELHO (PREVIEW)
# =====================================================
if st.session_state["itens_pedido"] and cliente_nome and ver_preview:
    st.markdown("### 👁️ Espelho do Pedido")
    aba_pdf, aba_whats = st.tabs(["📄 Resumo Visual", "📱 Copiar para WhatsApp"])

    with aba_pdf:
        linhas_html = ""
        for item in st.session_state["itens_pedido"]:
            linhas_html += f"""<tr>
            <td style="padding: 10px; border-bottom: 1px solid #f5eee6;"><b>{item['nome']}</b></td>
            <td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: center;">{item['quantidade']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: right;">R$ {formatar_moeda(item['preco_unitario'])}</td>
            <td style="padding: 10px; border-bottom: 1px solid #f5eee6; text-align: right;">R$ {formatar_moeda(item['preco_unitario'] * item['quantidade'])}</td>
            </tr>"""

        st.markdown(f"""<div class="proposta-preview">
        <div class="proposta-header">
        <h2 style="color: #c5721f; margin-bottom: 5px; font-weight: 800;">RESUMO DO PEDIDO VAREJO</h2>
        <p style="margin: 0; color: #555; font-size: 14px;">Doce Cesta Brasília</p>
        </div>
        <table style="width: 100%; border: none; margin-bottom: 25px;"><tr><td style="width: 60%; vertical-align: top;"><p style="margin:2px 0;"><b>Cliente:</b> {cliente_nome}</p><p style="margin:2px 0;"><b>Para:</b> {dest_nome or cliente_nome}</p></td><td style="width: 40%; vertical-align: top; text-align: right;"><p style="margin:2px 0;"><b>Entrega:</b> {dt_entrega.strftime("%d/%m/%Y")} ({horario})</p></td></tr></table>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;"><tr style="background-color: #faf7f3;"><th style="padding: 12px; text-align: left; border-bottom: 2px solid #e8ddd3;">Item</th><th style="padding: 12px; text-align: center; border-bottom: 2px solid #e8ddd3;">Qtd</th><th style="padding: 12px; text-align: right; border-bottom: 2px solid #e8ddd3;">Un.</th><th style="padding: 12px; text-align: right; border-bottom: 2px solid #e8ddd3;">Subtotal</th></tr>{linhas_html}</table>
        <div style="margin-top: 25px; text-align: right; font-size: 15px;"><p style="margin: 4px 0;">Subtotal: R$ {formatar_moeda(total_bruto)}</p><p style="margin: 4px 0; color: #c5221f;">Desconto: - R$ {formatar_moeda(valor_desconto)}</p><p style="margin: 4px 0;">Frete: R$ {formatar_moeda(frete_val)}</p></div>
        <div class="proposta-total">TOTAL: R$ {formatar_moeda(total_liquido)}</div>
        </div>""", unsafe_allow_html=True)

    with aba_whats:
        linhas_wpp = "".join([f"▪️ {i['quantidade']}x *{i['nome']}* (R$ {formatar_moeda(i['preco_unitario'])})\n" for i in st.session_state["itens_pedido"]])
        st.code(f"""*RESUMO DO PEDIDO - DOCE CESTA BRASÍLIA* 🎁\n\n👤 *Cliente:* {cliente_nome}\n📦 *Para:* {dest_nome or cliente_nome}\n📅 *Entrega:* {dt_entrega.strftime("%d/%m/%Y")} ({horario})\n\n*ITENS SELECIONADOS:*\n{linhas_wpp}\n*RESUMO FINANCEIRO:*\n💰 Subtotal: R$ {formatar_moeda(total_bruto)}\n🔻 Desconto: - R$ {formatar_moeda(valor_desconto)}\n🚚 Frete: R$ {formatar_moeda(frete_val)}\n━━━━━━━━━━━━━━━━━━━━\n*TOTAL: R$ {formatar_moeda(total_liquido)}*\n\n💳 *Pagamento:* {prazo_pagamento}""", language="markdown")
