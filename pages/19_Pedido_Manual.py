import streamlit as st
import pandas as pd
import requests
import re
import uuid
import time
from datetime import datetime, date
from config.supabase import supabase

from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.pedido_service import salvar_pedido
from services.pedido_adicional_service import salvar_adicionais_pedido
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS PREMIUM & RESPONSIVO
# =====================================================
st.set_page_config(page_title="PDV | Novo Pedido Varejo", page_icon="🛍️", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1200px; }

/* CABEÇALHO PREMIUM */
.header-banner { 
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 30px 20px; 
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 10px 30px rgba(90, 59, 40, 0.05); 
    margin-bottom: 2rem; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 6px; 
}
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; text-align: center;}
.header-subtitle { font-size: 14px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 0px !important; text-align: center;}

/* CARDS DE ETAPAS (ESQUERDA) */
.etapa-card { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03); }
.etapa-titulo { font-size: 18px; font-weight: 800; color: #c5721f; margin-bottom: 15px; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px;}

/* PAINEL DE RESUMO (DIREITA) */
.painel-resumo { 
    background: #faf7f3; border: 2px solid #e8ddd3; border-radius: 16px; padding: 25px; 
    box-shadow: 0 8px 25px rgba(90, 59, 40, 0.06); position: sticky; top: 20px; 
}
.resumo-titulo { font-size: 20px; font-weight: 800; color: #5a3b28; margin-bottom: 15px; text-align: center; border-bottom: 2px solid #dfcdbb; padding-bottom: 10px;}
.resumo-linha { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; color: #4a2e1b; }
.resumo-linha strong { font-weight: 700; color: #2c1e14; text-align: right;}
.resumo-total-box { background: #ffffff; border: 2px solid #137333; border-radius: 12px; padding: 15px; margin-top: 20px; text-align: center;}
.resumo-total-label { font-size: 12px; font-weight: 800; color: #137333; text-transform: uppercase; letter-spacing: 0.5px;}
.resumo-total-valor { font-size: 32px; font-weight: 800; color: #137333; line-height: 1.1; margin-top: 5px;}

.polaroid-box { background: #fffcf8; border: 2px dashed #ffb6c1; border-radius: 16px; padding: 20px; margin-top: 15px;}

/* inputs */
div[data-testid="stNumberInput"] label { display: none !important; }

/* BOTÃO DE CHECKOUT */
.btn-checkout button { 
    background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; 
    border-radius: 14px !important; font-weight: 800 !important; border: none !important; 
    box-shadow: 0 6px 20px rgba(19, 115, 51, 0.3) !important; font-size: 16px !important; padding: 20px !important; width: 100% !important; margin-top: 15px;
}
.btn-checkout button:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(19, 115, 51, 0.45) !important;}

/* MEDIA QUERIES PARA MOBILE */
@media (max-width: 768px) {
    .block-container { padding-top: 1rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
    .header-title { font-size: 32px !important; }
    .etapa-card { padding: 18px !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Cadastrar Pedido (PDV Varejo)</h1>
    <p class="header-subtitle">Preencha os dados à esquerda e acompanhe o resumo do pedido ao vivo à direita 🛍️</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES E CACHES (BUSCA FIEL À "05_PRODUTOS.PY")
# =====================================================
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
def obter_adicionais_fiel():
    try:
        # Busca categorias para encontrar o ID da categoria "Adicionais"
        categorias = supabase.table("categorias").select("*").execute().data or []
        cat_add = next((c for c in categorias if c.get("nome", "").strip().lower() in ["adicionais", "adicional"]), None)
        
        if cat_add:
            # Busca produtos vinculados à categoria Adicionais
            res = supabase.table("produtos").select("*").eq("categoria_id", cat_add["id"]).eq("ativo", True).execute()
            return sorted(res.data or [], key=lambda x: x.get("nome", ""))
        return []
    except: return []

secoes_disponiveis, cestas_ativas = obter_secoes_e_cestas()
adicionais_disponiveis = obter_adicionais_fiel()

# =====================================================
# ESTADOS DA SESSÃO
# =====================================================
for key in ["man_nome", "man_cpf", "man_tel", "man_rua", "man_num", "man_comp", "man_bairro", "man_cidade", "man_cep", "ultimo_cep_man"]:
    if key not in st.session_state: st.session_state[key] = ""
if "modo_busca_cli" not in st.session_state: st.session_state.modo_busca_cli = False
if "carrinho_extras" not in st.session_state: st.session_state.carrinho_extras = [] 
if "frete_val" not in st.session_state: st.session_state.frete_val = 0.0
if "desc_val" not in st.session_state: st.session_state.desc_val = 0.0

# =====================================================
# ESTRUTURA PDV: COLUNA ESQUERDA (DADOS) | DIREITA (RESUMO)
# =====================================================
col_dados, col_resumo = st.columns([2.3, 1.2], gap="large")

with col_dados:
    # -----------------------------------------------------
    # 1. COMPRADOR
    # -----------------------------------------------------
    st.markdown('<div class="etapa-card"><div class="etapa-titulo">👤 1. Dados do Comprador</div>', unsafe_allow_html=True)
    cc1, cc_btn = st.columns([4, 1.5])
    with cc1: nome_comp = st.text_input("Nome Completo *", value=st.session_state.man_nome, key="in_nome")
    with cc_btn:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Buscar Cliente", use_container_width=True):
            st.session_state.modo_busca_cli = not st.session_state.modo_busca_cli
            st.rerun()
            
    c_cpf, c_tel = st.columns(2)
    with c_cpf: cpf_comp = st.text_input("CPF", value=st.session_state.man_cpf, key="in_cpf")
    with c_tel: tel_comp = st.text_input("Telefone / WhatsApp *", value=st.session_state.man_tel, key="in_tel")

    if st.session_state.modo_busca_cli:
        st.markdown("<div style='background: #faf7f3; padding: 15px; border-radius: 12px; margin-top: 10px; border: 1px solid #e8ddd3;'>", unsafe_allow_html=True)
        termo_busca = st.text_input("Buscar Nome ou CPF:", key="man_termo_busca")
        try:
            res_cli = supabase.table("pedidos").select("cliente_nome, cliente_cpf, cliente_telefone").not_.ilike("cliente_nome", "%[B2B]%").execute()
            cli_dict = {c.get("cliente_telefone", "").strip(): c for c in (res_cli.data or []) if c.get("cliente_telefone", "").strip()}
            lista_clientes = sorted(list(cli_dict.values()), key=lambda x: x.get("cliente_nome", ""))
        except: lista_clientes = []
        
        if termo_busca: lista_clientes = [c for c in lista_clientes if termo_busca.lower() in str(c.get("cliente_nome", "")).lower() or termo_busca in str(c.get("cliente_cpf", ""))]
        opcoes_cli = [{"cliente_nome": "--- Selecione um cliente ---", "cliente_cpf": "", "cliente_telefone": ""}] + lista_clientes
        cli_sel = st.selectbox("Resultados:", opcoes_cli, format_func=lambda x: f"{x['cliente_nome']} (Tel: {x['cliente_telefone']})", key="man_busca_dropdown")
        if cli_sel and cli_sel["cliente_nome"] != "--- Selecione um cliente ---":
            st.session_state.man_nome = cli_sel["cliente_nome"]
            st.session_state.man_cpf = cli_sel["cliente_cpf"]
            st.session_state.man_tel = cli_sel["cliente_telefone"]
            st.session_state.modo_busca_cli = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # 2. PRODUTO PRINCIPAL
    # -----------------------------------------------------
    st.markdown('<div class="etapa-card"><div class="etapa-titulo">🎁 2. Produto Principal</div>', unsafe_allow_html=True)
    selecoes_admin = {}
    
    if "man_secao_form" not in st.session_state or st.session_state["man_secao_form"] not in secoes_disponiveis:
        st.session_state["man_secao_form"] = secoes_disponiveis[0]

    def reset_cesta(): st.session_state["man_cesta_sel_id"] = None

    if len(secoes_disponiveis) > 1:
        c_sec, c_prod = st.columns(2)
        with c_sec: secao_escolhida = st.selectbox("Catálogo/Seção", secoes_disponiveis, index=secoes_disponiveis.index(st.session_state["man_secao_form"]), key="man_secao_form", on_change=reset_cesta)
    else:
        secao_escolhida = secoes_disponiveis[0]
        st.session_state["man_secao_form"] = secao_escolhida

    cestas_da_secao = [c for c in cestas_ativas if (c.get("secao_vitrine") or "Cestas de Café").strip().lower() == secao_escolhida.strip().lower()]
    opcoes_cestas = [{"id": None, "nome": "Selecione a Cesta...", "preco": 0}] + cestas_da_secao
    
    idx_cesta = 0
    if st.session_state.get("man_cesta_sel_id"):
        for i, c in enumerate(opcoes_cestas):
            if c["id"] == st.session_state["man_cesta_sel_id"]: idx_cesta = i; break

    if len(secoes_disponiveis) > 1:
        with c_prod: cesta_sel = st.selectbox("Produto Base", opcoes_cestas, format_func=lambda c: f"{c['nome']} (R$ {tratar_preco(c.get('preco')):.2f})" if c.get("id") else c["nome"], index=idx_cesta)
    else:
        cesta_sel = st.selectbox("Produto Base", opcoes_cestas, format_func=lambda c: f"{c['nome']} (R$ {tratar_preco(c.get('preco')):.2f})" if c.get("id") else c["nome"], index=idx_cesta)

    if cesta_sel and cesta_sel.get("id"):
        st.session_state["man_cesta_sel_id"] = cesta_sel["id"]
        cfg = carregar_configuracao_cesta(cesta_sel["id"])
        if cfg and any(grp.get("produtos") for grp in cfg):
            st.markdown("<div style='font-size: 13px; font-weight: 700; color: #137333; margin-top: 15px; margin-bottom: 5px;'>🍓 Escolhas da Cesta</div>", unsafe_allow_html=True)
            for grp in cfg:
                cat = grp.get("categoria", "Geral")
                prods = grp.get("produtos", [])
                maximo = grp.get("max_escolhas", 1)
                if not prods: continue
                with st.container(border=True):
                    if maximo == 1:
                        esc = st.radio(f"Opções de {cat}", prods, format_func=lambda p: p["nome"], key=f"adm_rad_{cat}")
                        if esc: selecoes_admin[cat] = [esc]
                    else:
                        escs = st.multiselect(f"Opções de {cat}", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"adm_mul_{cat}")
                        selecoes_admin[cat] = escs
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # 3. EXTRAS E ADICIONAIS (CARRINHO VIVO)
    # -----------------------------------------------------
    st.markdown('<div class="etapa-card"><div class="etapa-titulo">🎀 3. Adicionais e Extras</div>', unsafe_allow_html=True)
    
    tab_cat, tab_man = st.tabs(["📚 Inserir do Catálogo", "✍️ Inserir Extra Manual"])
    
    with tab_cat:
        adc_sel = st.selectbox("Selecione um Adicional Oficial:", [None] + adicionais_disponiveis, format_func=lambda x: f"{x['nome']} (R$ {tratar_preco(x.get('preco')):.2f})" if x else "Clique para ver a lista...")
        if st.button("➕ Adicionar ao Pedido", key="btn_add_cat"):
            if adc_sel:
                st.session_state.carrinho_extras.append({"id": str(uuid.uuid4()), "produto_id": adc_sel["id"], "nome": adc_sel["nome"], "preco": tratar_preco(adc_sel.get("preco")), "qtd": 1})
                st.rerun()

    with tab_man:
        cm1, cm2 = st.columns([2, 1])
        with cm1: nome_extra_man = st.text_input("Nome do Extra Avulso", placeholder="Ex: Balão Metálico 15 anos")
        with cm2: preco_extra_man = st.number_input("Valor Cobrado (R$)", min_value=0.0, step=5.0)
        if st.button("➕ Inserir Extra Manual", key="btn_add_man"):
            if nome_extra_man.strip():
                st.session_state.carrinho_extras.append({"id": str(uuid.uuid4()), "produto_id": None, "nome": nome_extra_man.strip(), "preco": preco_extra_man, "qtd": 1})
                st.rerun()
            else: st.warning("Digite o nome do extra.")

    polaroid = any("polaroid" in extra["nome"].lower() or "foto" in extra["nome"].lower() for extra in st.session_state.carrinho_extras)
    fotos_upload = []
    if polaroid:
        st.markdown("""
        <div class="polaroid-box">
            <h4 style="color: #d1476a; margin-top: 0; margin-bottom: 5px;">📸 Upload de Fotos Polaroid</h4>
            <p style="font-size: 13px; color: #5a3b28;">Faça o upload das imagens enviadas pelo cliente para o <b>Supabase</b>.</p>
        </div>
        """, unsafe_allow_html=True)
        fotos_upload = st.file_uploader("Anexar fotos (PNG, JPG, JPEG)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="man_upload_fotos")
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # 4. DESTINATÁRIO E CARTÃO
    # -----------------------------------------------------
    st.markdown('<div class="etapa-card"><div class="etapa-titulo">💌 4. Destinatário e Cartão</div>', unsafe_allow_html=True)
    cd1, cd2 = st.columns(2)
    with cd1: dest_nome = st.text_input("Nome do Homenageado *", key="man_dest_nome")
    with cd2: dest_tel = st.text_input("Telefone do Homenageado", key="man_dest_tel")
    motivo = st.text_input("Qual a Ocasião? (Ex: Aniversário)", key="man_motivo")
    mensagem = st.text_area("Mensagem do Cartão", height=80, key="man_msg")
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # 5. LOGÍSTICA E ENDEREÇO
    # -----------------------------------------------------
    st.markdown('<div class="etapa-card"><div class="etapa-titulo">📍 5. Logística e Endereço</div>', unsafe_allow_html=True)
    cx1, cx2, cx3 = st.columns([1.5, 1, 3])
    with cx1:
        cep_in = st.text_input("CEP", max_chars=8, placeholder="Apenas números", key="in_cep")
        cep_limpo = re.sub(r'\D', '', cep_in)
        if len(cep_limpo) == 8 and st.session_state.ultimo_cep_man != cep_limpo:
            try:
                r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
                if r.status_code == 200 and "erro" not in r.json():
                    d = r.json()
                    st.session_state.man_rua = d.get("logradouro", "")
                    st.session_state.man_bairro = d.get("bairro", "")
                    st.session_state.man_cidade = f"{d.get('localidade', '')} - {d.get('uf', '')}"
            except: pass
            st.session_state.ultimo_cep_man = cep_limpo
            st.rerun()
    with cx2:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        st.button("🔍 Buscar CEP", use_container_width=True)

    c_r1, c_r2, c_r3 = st.columns([3, 1, 2])
    with c_r1: rua = st.text_input("Rua/Logradouro *", value=st.session_state.man_rua, key="in_rua")
    with c_r2: num = st.text_input("Nº *", key="in_num")
    with c_r3: comp = st.text_input("Complemento", key="in_comp")

    c_b1, c_b2 = st.columns([1, 1])
    with c_b1: bairro = st.text_input("Bairro *", value=st.session_state.man_bairro, key="in_bairro")
    with c_b2: cidade = st.text_input("Cidade-UF *", value=st.session_state.man_cidade, key="in_cidade")

    st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 15px 0;'>", unsafe_allow_html=True)
    ce1, ce2 = st.columns(2)
    with ce1: dt_ent = st.date_input("Data da Entrega", value=date.today(), format="DD/MM/YYYY", key="man_dt")
    with ce2: per_ent = st.text_input("Horário Combinado", placeholder="Ex: Entre 08h e 10h", key="man_per")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# ESTRUTURA PDV: COLUNA DIREITA (RESUMO E PAGAMENTO)
# =====================================================
with col_resumo:
    st.markdown('<div class="painel-resumo">', unsafe_allow_html=True)
    st.markdown('<div class="resumo-titulo">📋 TICKET DO PEDIDO</div>', unsafe_allow_html=True)

    # DADOS BÁSICOS
    if nome_comp:
        st.markdown(f"<div style='font-size: 13px; color:#666; margin-bottom: 2px;'>Cliente: <b style='color:#333;'>{nome_comp}</b></div>", unsafe_allow_html=True)
    if dest_nome:
        st.markdown(f"<div style='font-size: 13px; color:#666; margin-bottom: 10px;'>Para: <b style='color:#333;'>{dest_nome}</b></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 10px 0;'>", unsafe_allow_html=True)

    # ITENS
    valor_c = float(cesta_sel.get("preco", 0)) if cesta_sel and cesta_sel.get("id") else 0.0
    nome_c_print = cesta_sel['nome'] if cesta_sel and cesta_sel.get('id') else "Nenhum produto"
    
    st.markdown(f'<div class="resumo-linha"><span>📦 {nome_c_print[:22]}...</span> <strong>R$ {formatar_moeda(valor_c)}</strong></div>', unsafe_allow_html=True)
    
    # LISTA DE EXTRAS NO TICKET
    valor_a = 0.0
    for i, extra in enumerate(st.session_state.carrinho_extras):
        sub_e = extra["preco"] * extra["qtd"]
        valor_a += sub_e
        
        c_ex1, c_ex2 = st.columns([3, 1])
        with c_ex1:
            st.markdown(f"<div style='font-size: 12px; color: #5a3b28;'>🎀 {extra['nome'][:18]}</div>", unsafe_allow_html=True)
        with c_ex2:
            if st.button("❌", key=f"del_{extra['id']}", help="Remover do carrinho"):
                st.session_state.carrinho_extras.pop(i)
                st.rerun()

    if st.session_state.carrinho_extras:
        st.markdown(f'<div class="resumo-linha" style="margin-top: 5px;"><span>🎀 Subtotal Extras</span> <strong>R$ {formatar_moeda(valor_a)}</strong></div>', unsafe_allow_html=True)

    subtotal = valor_c + valor_a

    st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 15px 0;'>", unsafe_allow_html=True)

    # CONTROLES FINANCEIROS E PAGAMENTO
    pag = st.selectbox("Pagamento", ["Pix", "Cartão de Crédito"], key="man_pag")
    status = st.selectbox("Status", ["Recebido", "Pago"], key="man_status", help="Nasce como Recebido para confirmar o pagamento depois no Mural.")
    
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    frete = st.number_input("Frete (R$)", min_value=0.0, step=5.0, value=st.session_state.frete_val, key="man_frete")
    st.session_state.frete_val = frete
    
    desc_perc = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=st.session_state.desc_val, key="man_desc")
    st.session_state.desc_val = desc_perc
    
    valor_desconto = subtotal * (desc_perc / 100)
    total_liquido = subtotal - valor_desconto + frete

    # TOTAL GIGANTE
    st.markdown(f"""
    <div class="resumo-total-box">
        <div class="resumo-total-label">Total a Cobrar</div>
        <div class="resumo-total-valor">R$ {formatar_moeda(total_liquido)}</div>
    </div>
    """, unsafe_allow_html=True)

    # BOTÃO DE CHECKOUT
    st.markdown('<div class="btn-checkout">', unsafe_allow_html=True)
    if st.button("✅ GRAVAR PEDIDO", type="primary"):
        if not nome_comp: st.error("Informe o Nome do Comprador."); st.stop()
        if not tel_comp: st.error("Informe o Telefone do Comprador."); st.stop()
        if not cesta_sel or not cesta_sel.get("id"): st.error("Selecione um Produto Base."); st.stop()
        if not dest_nome: st.error("Informe o Nome do Destinatário."); st.stop()
        if not rua or not num or not bairro: st.error("Complete Rua, Número e Bairro."); st.stop()

        links_polaroid = []
        if polaroid and fotos_upload:
            with st.spinner("📦 Enviando fotos para a nuvem..."):
                for foto in fotos_upload:
                    ext = foto.name.split('.')[-1]
                    file_name = f"polaroid_{uuid.uuid4().hex}.{ext}"
                    try:
                        supabase.storage.from_("pedido_fotos").upload(file_name, foto.read(), {"content-type": foto.type})
                        url = supabase.storage.from_("pedido_fotos").get_public_url(file_name)
                        links_polaroid.append(url)
                    except: pass

        prod_text = f"1x {cesta_sel['nome']} (R$ {formatar_moeda(valor_c)})"
        if selecoes_admin:
            prod_text += "\nOpções: " + " | ".join([f"{i['nome']}" for c, itens in selecoes_admin.items() for i in itens])
        
        adicionais_str_list = [f"1x {a['nome']} (R$ {formatar_moeda(a['preco'])})" for a in st.session_state.carrinho_extras]
        add_text = f"Desconto de {desc_perc}% aplicado." if desc_perc > 0 else ""
        if adicionais_str_list:
            add_text += ("\n\n" if add_text else "") + "ADICIONAIS E EXTRAS:\n" + "\n".join(adicionais_str_list)

        if links_polaroid:
            add_text += "\n\n📸 LINKS FOTOS POLAROID (Acesse p/ Imprimir):\n" + "\n".join(links_polaroid)

        cep_str = f" (CEP: {cep_in})" if cep_in.strip() else ""
        end_comp = f"{rua}, {num} - {comp} - {bairro}, {cidade}{cep_str}"
        
        dados_ped = {
            "cliente_nome": nome_comp.strip(),
            "cliente_cpf": re.sub(r'\D', '', cpf_comp),
            "cliente_telefone": re.sub(r'\D', '', tel_comp),
            "destinatario_nome": dest_nome.strip(),
            "destinatario_telefone": re.sub(r'\D', '', dest_tel),
            "motivo_homenagem": motivo.strip() or "Varejo/Manual",
            "cesta_id": cesta_sel["id"],
            "cesta_nome": cesta_sel["nome"],
            "produtos": prod_text,
            "adicionais": add_text,
            "pagamento": pag,
            "mensagem": mensagem,
            "pedido_especial": "",
            "endereco": end_comp,
            "data_entrega": dt_ent.strftime("%Y-%m-%d") if dt_ent else str(date.today()),
            "periodo_entrega": per_ent.strip() or "A combinar",
            "status": status,
            "valor_frete": frete,
            "valor_total": total_liquido,
            "cesta_montada": False
        }
        
        with st.spinner("Registrando pedido..."):
            suc, p_id = salvar_pedido(dados_ped)
            if suc:
                adicionais_para_banco = [{"produto_id": e["produto_id"], "nome": e["nome"], "preco": e["preco"]} for e in st.session_state.carrinho_extras]
                if adicionais_para_banco: salvar_adicionais_pedido(p_id, adicionais_para_banco)
                
                st.success(f"✅ Pedido criado com sucesso!")
                st.session_state.carrinho_extras = []
                time.sleep(1.5)
                st.switch_page("pages/02_Pedidos.py")
            else: 
                st.error("Erro ao registrar no banco de dados.")

    st.markdown('</div></div>', unsafe_allow_html=True)
