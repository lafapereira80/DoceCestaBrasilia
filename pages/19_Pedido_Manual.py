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
from services.produto_service import listar_produtos_por_categoria_id
from services.pedido_service import salvar_pedido
from services.pedido_adicional_service import salvar_adicionais_pedido
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E DESIGN DASHBOARD PROFISSIONAL
# =====================================================
st.set_page_config(page_title="Painel PDV | Pedido Varejo", page_icon="🛍️", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 4rem !important; max-width: 1450px !important; }

/* TOPO DO DASHBOARD */
.dash-header { 
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 18px 25px; 
    border-radius: 16px; border: 1px solid #e8ddd3; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03); 
    margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; 
}
.dash-title { font-family: 'Dancing Script', cursive !important; font-size: 36px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1; }
.dash-subtitle { font-size: 13px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 3px !important; }

/* BLOCOS DE DASHBOARD (GRID MODERNO) */
.dash-box {
    background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 20px;
    box-shadow: 0 4px 12px rgba(90, 59, 40, 0.02); margin-bottom: 20px; height: 100%;
}
.dash-box-title {
    font-size: 14px; font-weight: 800; color: #c5721f; margin-bottom: 15px;
    border-bottom: 2px dashed #f5eee6; padding-bottom: 8px; display: flex; align-items: center; gap: 8px;
    text-transform: uppercase; letter-spacing: 0.5px;
}

/* CAIXA VERDE DE RESUMO E FECHAMENTO (TICKET INTEGRADO) */
.dash-ticket-verde {
    background: #f0fdf4; border: 2px solid #137333; border-radius: 16px; padding: 22px;
    box-shadow: 0 8px 25px rgba(19, 115, 51, 0.08); margin-bottom: 20px;
}
.ticket-title { font-size: 16px; font-weight: 800; color: #137333; margin-bottom: 15px; text-align: center; border-bottom: 2px solid #ceead6; padding-bottom: 8px;}
.ticket-line { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; color: #5a3b28; }
.ticket-line strong { font-weight: 700; color: #2c1e14; text-align: right;}
.ticket-total { display: flex; justify-content: space-between; font-size: 22px; font-weight: 800; color: #137333; margin-top: 15px; padding-top: 12px; border-top: 2px dashed #137333; }

/* CHECKBOXES E POLAROID */
div[data-testid="stCheckbox"] { background: #faf7f3; border: 1px solid #e8ddd3; padding: 6px 10px; border-radius: 8px; margin-bottom: 6px; }
.polaroid-box { background: #fffcf8; border: 2px dashed #ffb6c1; border-radius: 12px; padding: 15px; margin-top: 15px;}

/* BOTÃO DE AÇÃO PRINCIPAL */
div[data-testid="stButton"] button[kind="primary"] { 
    background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; 
    border-radius: 12px !important; font-weight: 800 !important; border: none !important; 
    box-shadow: 0 6px 20px rgba(19, 115, 51, 0.25) !important; font-size: 15px !important; padding: 16px !important; width: 100% !important; 
}
div[data-testid="stButton"] button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(19, 115, 51, 0.35) !important;}
</style>
""", unsafe_allow_html=True)

# CABEÇALHO DO DASHBOARD
c_head, c_btn = st.columns([6, 1], vertical_alignment="center")
with c_head:
    st.markdown("""
    <div class="dash-header">
        <div>
            <h1 class="dash-title">Painel de Vendas Varejo (PDV)</h1>
            <p class="dash-subtitle">Gestão estruturada em blocos modulares para agilizar os lançamentos 🛍️</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c_btn:
    if st.button("⬅️ Voltar", use_container_width=True):
        st.switch_page("pages/02_Pedidos.py")

# =====================================================
# FUNÇÕES E CONSULTAS AO BANCO
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
def obter_adicionais_catalogo():
    try:
        categorias = supabase.table("categorias").select("*").execute().data or []
        cat_add = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)
        if cat_add:
            produtos_add = listar_produtos_por_categoria_id(cat_add["id"])
            return sorted([p for p in produtos_add if p.get("ativo", True)], key=lambda x: x.get("nome", ""))
        return []
    except: return []

secoes_disponiveis, cestas_ativas = obter_secoes_e_cestas()
adicionais_catalogo = obter_adicionais_catalogo()

# =====================================================
# ESTADOS DA SESSÃO
# =====================================================
for key in ["man_nome", "man_cpf", "man_tel", "man_rua", "man_num", "man_comp", "man_bairro", "man_cidade", "man_cep", "ultimo_cep_man"]:
    if key not in st.session_state: st.session_state[key] = ""
if "modo_busca_cli" not in st.session_state: st.session_state.modo_busca_cli = False
if "man_extras_avulsos" not in st.session_state: st.session_state.man_extras_avulsos = [] 
if "man_cesta_sel_id" not in st.session_state: st.session_state.man_cesta_sel_id = None

# =====================================================
# ESTRUTURA EM BLOCOS DE DASHBOARD (2 COLUNAS LARGAS)
# =====================================================
col_bloco1, col_bloco2 = st.columns([1, 1], gap="medium")

# -----------------------------------------------------
# COLUNA 1: DADOS DO CLIENTE, PRODUTO E DESTINATÁRIO
# -----------------------------------------------------
with col_bloco1:
    # BLOCO 1: CLIENTE
    st.markdown('<div class="dash-box"><div class="dash-box-title">👤 1. Dados do Comprador</div>', unsafe_allow_html=True)
    cc1, cc_btn = st.columns([3, 1])
    with cc1: nome_comp = st.text_input("Nome Completo *", value=st.session_state.man_nome, key="in_nome")
    with cc_btn:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Buscar", help="Buscar cliente antigo", use_container_width=True):
            st.session_state.modo_busca_cli = not st.session_state.modo_busca_cli
            st.rerun()

    c_cpf, c_tel = st.columns(2)
    with c_cpf: cpf_comp = st.text_input("CPF", value=st.session_state.man_cpf, key="in_cpf")
    with c_tel: tel_comp = st.text_input("WhatsApp *", value=st.session_state.man_tel, key="in_tel")

    if st.session_state.modo_busca_cli:
        st.markdown("<div style='background: #faf7f3; padding: 10px; border-radius: 8px; margin-top: 8px; border: 1px solid #e8ddd3;'>", unsafe_allow_html=True)
        termo_busca = st.text_input("🔍 Digite Nome ou CPF:", key="man_termo_busca")
        try:
            res_cli = supabase.table("pedidos").select("cliente_nome, cliente_cpf, cliente_telefone").not_.ilike("cliente_nome", "%[B2B]%").execute()
            cli_dict = {c.get("cliente_telefone", "").strip(): c for c in (res_cli.data or []) if c.get("cliente_telefone", "").strip()}
            lista_clientes = sorted(list(cli_dict.values()), key=lambda x: x.get("cliente_nome", ""))
        except: lista_clientes = []
        
        if termo_busca: lista_clientes = [c for c in lista_clientes if termo_busca.lower() in str(c.get("cliente_nome", "")).lower() or termo_busca in str(c.get("cliente_cpf", ""))]
        opcoes_cli = [{"cliente_nome": "--- Selecione o cliente ---", "cliente_cpf": "", "cliente_telefone": ""}] + lista_clientes
        cli_sel = st.selectbox("Resultados:", opcoes_cli, format_func=lambda x: f"{x['cliente_nome']} ({x['cliente_telefone']})", key="man_busca_dropdown")
        
        if cli_sel and cli_sel["cliente_nome"] != "--- Selecione o cliente ---":
            st.session_state.man_nome = cli_sel["cliente_nome"]
            st.session_state.man_cpf = cli_sel["cliente_cpf"]
            st.session_state.man_tel = cli_sel["cliente_telefone"]
            st.session_state.modo_busca_cli = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # BLOCO 2: PRODUTO PRINCIPAL (SEMPRE VAZIO NO INÍCIO)
    st.markdown('<div class="dash-box"><div class="dash-box-title">🎁 2. Seleção de Produto</div>', unsafe_allow_html=True)
    selecoes_admin = {}

    if "man_secao_form" not in st.session_state or st.session_state["man_secao_form"] not in secoes_disponiveis:
        st.session_state["man_secao_form"] = secoes_disponiveis[0]

    def reset_cesta(): 
        st.session_state["man_cesta_sel_id"] = None

    if len(secoes_disponiveis) > 1:
        secao_escolhida = st.selectbox("Catálogo / Seção", secoes_disponiveis, index=secoes_disponiveis.index(st.session_state["man_secao_form"]), key="man_secao_form", on_change=reset_cesta)
    else:
        secao_escolhida = secoes_disponiveis[0]
        st.session_state["man_secao_form"] = secao_escolhida

    cestas_da_secao = [c for c in cestas_ativas if (c.get("secao_vitrine") or "Cestas de Café").strip().lower() == secao_escolhida.strip().lower()]
    opcoes_cestas = [{"id": None, "nome": "Selecione o Produto...", "preco": 0}] + cestas_da_secao
    
    idx_cesta = 0
    if st.session_state.get("man_cesta_sel_id"):
        for i, c in enumerate(opcoes_cestas):
            if c["id"] == st.session_state["man_cesta_sel_id"]: idx_cesta = i; break

    cesta_sel = st.selectbox("Produto Base", opcoes_cestas, format_func=lambda c: f"{c['nome']} (R$ {tratar_preco(c.get('preco')):.2f})" if c.get("id") else c["nome"], index=idx_cesta, key="selectbox_produto_base")

    if cesta_sel and cesta_sel.get("id"):
        st.session_state["man_cesta_sel_id"] = cesta_sel["id"]
        cfg = carregar_configuracao_cesta(cesta_sel["id"])
        if cfg and any(grp.get("produtos") for grp in cfg):
            st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 12px 0;'>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 12px; font-weight: 800; color: #137333; margin-bottom: 6px;'>🍓 Personalização da Cesta</div>", unsafe_allow_html=True)
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
    else:
        st.session_state["man_cesta_sel_id"] = None
    st.markdown('</div>', unsafe_allow_html=True)

    # BLOCO 3: DESTINATÁRIO
    st.markdown('<div class="dash-box"><div class="dash-box-title">💌 3. Destinatário e Cartão</div>', unsafe_allow_html=True)
    cd1, cd2 = st.columns(2)
    with cd1: dest_nome = st.text_input("Nome do Homenageado *", key="man_dest_nome")
    with cd2: dest_tel = st.text_input("Tel. Destinatário", key="man_dest_tel")
    motivo = st.text_input("Ocasião (Ex: Aniversário)", key="man_motivo")
    mensagem = st.text_area("Mensagem do Cartão", height=70, key="man_msg", placeholder="Texto impresso no cartão.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------
# COLUNA 2: ADICIONAIS, ENDEREÇO E TICKET VERDE INTEGRADO
# -----------------------------------------------------
with col_bloco2:
    # BLOCO 4: ADICIONAIS E EXTRAS
    adicionais_selecionados_finais = []
    st.markdown('<div class="dash-box"><div class="dash-box-title">🎀 4. Adicionais e Extras</div>', unsafe_allow_html=True)
    
    if adicionais_catalogo:
        st.markdown("<div style='font-size: 12px; font-weight: 700; color: #5a3b28; margin-bottom: 6px;'>✨ Catálogo de Adicionais</div>", unsafe_allow_html=True)
        for p_ad in adicionais_catalogo:
            preco_ad = tratar_preco(p_ad.get("preco"))
            txt_preco = f"(+ R$ {preco_ad:.2f})" if preco_ad > 0 else "(Sob Consulta)"
            if st.checkbox(f"{p_ad['nome']} {txt_preco}", key=f"man_chk_ad_{p_ad['id']}"):
                adicionais_selecionados_finais.append({"produto_id": p_ad["id"], "nome": p_ad["nome"], "preco": preco_ad})

    st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 12px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #5a3b28; margin-bottom: 4px;'>✍️ Extra Manual</div>", unsafe_allow_html=True)
    cm1, cm2, cm3 = st.columns([2, 1, 1])
    with cm1: nome_extra_man = st.text_input("Nome", placeholder="Ex: Balão", key="man_extra_nome", label_visibility="collapsed")
    with cm2: preco_extra_man = st.number_input("Valor", min_value=0.0, step=5.0, value=0.0, key="man_extra_preco", label_visibility="collapsed")
    with cm3:
        if st.button("➕ Add", use_container_width=True):
            if nome_extra_man.strip():
                st.session_state.man_extras_avulsos.append({"id": str(uuid.uuid4()), "produto_id": None, "nome": nome_extra_man.strip(), "preco": preco_extra_man})
                st.rerun()
            else: st.warning("Nome?")
            
    if st.session_state.man_extras_avulsos:
        for i, extra in enumerate(st.session_state.man_extras_avulsos):
            adicionais_selecionados_finais.append(extra)
            c_l1, c_l2 = st.columns([5, 1])
            with c_l1: st.markdown(f"<div style='margin-top: 5px; font-size:12px; font-weight:600; color: #4a2e1b;'>✅ {extra['nome']} (R$ {formatar_moeda(extra['preco'])})</div>", unsafe_allow_html=True)
            with c_l2:
                if st.button("🗑️", key=f"del_ext_{extra['id']}"):
                    st.session_state.man_extras_avulsos.pop(i)
                    st.rerun()

    polaroid = any("polaroid" in extra["nome"].lower() or "foto" in extra["nome"].lower() for extra in adicionais_selecionados_finais)
    fotos_upload = []
    if polaroid:
        st.markdown("""
        <div class="polaroid-box">
            <h4 style="color: #d1476a; margin-top: 0; margin-bottom: 4px; font-size:13px;">📸 Upload de Fotos Polaroid</h4>
            <p style="font-size: 11px; color: #5a3b28; margin-bottom: 8px;">Salvas no bucket <b>pedido_fotos</b>.</p>
        </div>
        """, unsafe_allow_html=True)
        fotos_upload = st.file_uploader("Anexar fotos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="man_upload_fotos")
    st.markdown('</div>', unsafe_allow_html=True)

    # BLOCO 5: ENDEREÇO E ENTREGA
    st.markdown('<div class="dash-box"><div class="dash-box-title">📍 5. Endereço e Entrega</div>', unsafe_allow_html=True)
    cx1, cx2 = st.columns([1.5, 2.5])
    with cx1:
        cep_in = st.text_input("CEP", max_chars=8, placeholder="Somente números", key="in_cep")
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

    c_r1, c_r2 = st.columns([3, 1])
    with c_r1: rua = st.text_input("Rua/Logradouro *", value=st.session_state.man_rua, key="in_rua")
    with c_r2: num = st.text_input("Nº *", key="in_num")

    c_b1, c_b2 = st.columns(2)
    with c_b1: bairro = st.text_input("Bairro *", value=st.session_state.man_bairro, key="in_bairro")
    with c_b2: cidade = st.text_input("Cidade-UF *", value=st.session_state.man_cidade, key="in_cidade")

    st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 12px 0;'>", unsafe_allow_html=True)
    ce1, ce2 = st.columns(2)
    with ce1: dt_ent = st.date_input("Data Entrega", value=date.today(), format="DD/MM/YYYY", key="man_dt")
    with ce2: per_ent = st.text_input("Horário", placeholder="Ex: 08h-10h", key="man_per")
    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # BLOCO 6: TICKET DE RESUMO DENTRO DA CAIXA VERDE (ABAIXO DA COLUNA 2)
    # =====================================================
    st.markdown('<div class="dash-ticket-verde">', unsafe_allow_html=True)
    st.markdown('<div class="ticket-title">📋 TICKET DE RESUMO & FECHAMENTO</div>', unsafe_allow_html=True)
    
    t_cf1, t_cf2 = st.columns(2)
    with t_cf1: pag = st.selectbox("Pagamento", ["Pix", "Cartão de Crédito"], key="man_pag")
    with t_cf2: status = st.selectbox("Status", ["Recebido", "Pago"], key="man_status")
    
    st.write("")
    t_f1, t_f2 = st.columns(2)
    with t_f1: frete = st.number_input("Frete (R$)", min_value=0.0, step=5.0, value=0.0, key="man_frete")
    with t_f2: desc_perc = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0, key="man_desc")
    
    # CÁLCULOS TOTAIS
    valor_c = float(cesta_sel.get("preco", 0)) if cesta_sel and cesta_sel.get("id") else 0.0
    valor_a = sum(extra.get("preco", 0.0) for extra in adicionais_selecionados_finais)
    subtotal = valor_c + valor_a
    valor_desconto = subtotal * (desc_perc / 100)
    total_liquido = subtotal - valor_desconto + frete

    st.markdown("<hr style='border: none; border-top: 1px dashed #ceead6; margin: 12px 0;'>", unsafe_allow_html=True)
    
    # EXIBIÇÃO NO TICKET VERDE
    nome_c_print = cesta_sel['nome'] if cesta_sel and cesta_sel.get('id') else "Nenhum produto selecionado"
    st.markdown(f'<div class="ticket-line"><span>📦 <b>{nome_c_print}</b></span> <strong>R$ {formatar_moeda(valor_c)}</strong></div>', unsafe_allow_html=True)
    
    if selecoes_admin:
        for cat, itens in selecoes_admin.items():
            for it in itens:
                st.markdown(f'<div class="ticket-line" style="font-size:11px; color:#5a3b28; padding-left:10px;"><span>&bull; {cat}: {it["nome"]}</span></div>', unsafe_allow_html=True)

    if adicionais_selecionados_finais:
        for ad in adicionais_selecionados_finais:
            st.markdown(f'<div class="ticket-line" style="font-size:11.5px;"><span>🎀 {ad["nome"]}</span> <strong>R$ {formatar_moeda(ad["preco"])}</strong></div>', unsafe_allow_html=True)

    if frete > 0:
        st.markdown(f'<div class="ticket-line"><span>🚚 Frete</span> <strong>R$ {formatar_moeda(frete)}</strong></div>', unsafe_allow_html=True)
    if valor_desconto > 0:
        st.markdown(f'<div class="ticket-line" style="color: #c5221f;"><span>🔻 Desconto ({desc_perc}%)</span> <strong>- R$ {formatar_moeda(valor_desconto)}</strong></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ticket-total">
        <span>TOTAL:</span> 
        <span>R$ {formatar_moeda(total_liquido)}</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("✅ GRAVAR PEDIDO NO SISTEMA", type="primary"):
        if not nome_comp: st.error("Informe o nome do comprador."); st.stop()
        if not tel_comp: st.error("Informe o WhatsApp do comprador."); st.stop()
        if not cesta_sel or not cesta_sel.get("id"): st.error("Selecione um Produto Base."); st.stop()
        if not dest_nome: st.error("Informe o Nome do Destinatário."); st.stop()
        if not rua or not num or not bairro: st.error("Complete Rua, Número e Bairro."); st.stop()

        # UPLOAD FOTOS POLAROID
        links_polaroid = []
        if polaroid and fotos_upload:
            with st.spinner("📦 Salvando fotos no bucket 'pedido_fotos'..."):
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
        
        adicionais_str_list = [f"1x {a['nome']} (R$ {formatar_moeda(a.get('preco', 0.0))})" for a in adicionais_selecionados_finais]
        add_text = f"Desconto de {desc_perc}% aplicado." if desc_perc > 0 else ""
        if adicionais_str_list:
            add_text += ("\n\n" if add_text else "") + "ADICIONAIS E EXTRAS:\n" + "\n".join(adicionais_str_list)

        if links_polaroid:
            add_text += "\n\n📸 LINKS FOTOS POLAROID (Acesso p/ Impressão):\n" + "\n".join(links_polaroid)

        cep_str = f" (CEP: {cep_in})" if cep_in.strip() else ""
        end_comp = f"{rua}, {num} - {comp} - {bairro}, {cidade}{cep_str}"
        
        dados_ped = {
            "cliente_nome": nome_comp.strip(),
            "cliente_cpf": re.sub(r'\D', '', cpf_comp),
            "cliente_telefone": re.sub(r'\D', '', tel_comp),
            "destinatario_nome": dest_nome.strip(),
            "destinatario_telefone": dest_tel.strip(),
            "motivo_homenagem": motivo.strip() or "Varejo/Manual",
            "cesta_id": cesta_sel["id"],
            "cesta_nome": cesta_sel["nome"],
            "produtos": prod_text,
            "adicionais": add_text,
            "pagamento": pag,
            "mensagem": mensagem,
            "pedido_especial": "",
            "endereco": end_comp,
            "data_entrega": dt_ent.strftime("%Y-%m-%d"),
            "periodo_entrega": per_ent.strip() or "A combinar",
            "status": status,
            "valor_frete": frete,
            "valor_total": total_liquido,
            "cesta_montada": False
        }
        
        with st.spinner("Registrando pedido..."):
            suc, p_id = salvar_pedido(dados_ped)
            if suc:
                adicionais_para_banco = [{"produto_id": e.get("produto_id"), "nome": e["nome"], "preco": e.get("preco", 0.0)} for e in adicionais_selecionados_finais]
                if adicionais_para_banco: salvar_adicionais_pedido(p_id, adicionais_para_banco)
                
                st.success(f"✅ Pedido criado com sucesso!")
                st.session_state.man_extras_avulsos = []
                st.session_state.man_cesta_sel_id = None
                
                # MENSAGEM WHATSAPP ESTRUTURADA
                linhas_wpp = f"📦 {cesta_sel['nome']} (R$ {formatar_moeda(valor_c)})\n"
                if selecoes_admin:
                    for cat, itens in selecoes_admin.items():
                        for it in itens: linhas_wpp += f"  • {cat}: {it['nome']}\n"
                for a in adicionais_selecionados_finais: linhas_wpp += f"🎀 {a['nome']} (R$ {formatar_moeda(a.get('preco', 0.0))})\n"
                
                texto_wpp = f"""*NOVO PEDIDO - DOCE CESTA BRASÍLIA* 🎁\n\n👤 *De:* {nome_comp}\n💝 *Para:* {dest_nome}\n📅 *Entrega:* {dt_ent.strftime("%d/%m/%Y")} ({per_ent})\n📍 *Local:* {bairro} - {cidade}\n\n*ITENS:*\n{linhas_wpp}\n*VALORES:*\n💰 Subtotal: R$ {formatar_moeda(subtotal)}\n🚚 Frete: R$ {formatar_moeda(frete)}\n🔻 Desconto: - R$ {formatar_moeda(valor_desconto)}\n━━━━━━━━━━━━━━━━━━━━\n*TOTAL:* R$ {formatar_moeda(total_liquido)}\n\n💳 *Pagamento:* {pag}"""
                
                st.info("📱 Copie a mensagem para o WhatsApp:")
                st.code(texto_wpp, language="markdown")
                time.sleep(3)
                st.switch_page("pages/02_Pedidos.py")
            else: 
                st.error("Erro ao registrar no banco de dados.")

    st.markdown('</div>', unsafe_allow_html=True)
