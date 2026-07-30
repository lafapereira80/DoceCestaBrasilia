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
# CONFIGURAÇÃO DA PÁGINA E CSS
# =====================================================
st.set_page_config(page_title="Novo Pedido Manual", page_icon="🛍️", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1000px; }

/* CABEÇALHO PREMIUM */
.header-banner { 
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 30px 20px; 
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04); 
    margin-bottom: 2rem; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 6px; 
}
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; text-align: center;}
.header-subtitle { font-size: 14px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 0px !important; text-align: center;}

/* CONTAINERS */
div[data-testid="stVerticalBlockBorderWrapper"] { 
    background: #ffffff !important; border: 1px solid #e8ddd3 !important; border-radius: 16px !important; 
    padding: 24px 28px !important; margin-bottom: 15px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03) !important; 
}
h4 { font-size: 18px !important; font-weight: 800 !important; color: #c5721f !important; margin-bottom: 15px !important; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px;}

/* Checkboxes dos Adicionais */
div[data-testid="stCheckbox"] { background: #faf7f3; border: 1px solid #e8ddd3; padding: 10px 15px; border-radius: 12px; margin-bottom: 8px; transition: all 0.2s ease;}
div[data-testid="stCheckbox"]:hover { background: #fdfcfb; border-color: #c5721f; transform: translateY(-1px); }

/* Resumo Financeiro */
.resumo-financeiro { background: #fdfbf8; border: 2px solid #137333; border-radius: 16px; padding: 25px; text-align: center; margin-top: 15px; box-shadow: 0 4px 15px rgba(19, 115, 51, 0.05);}
.resumo-label { font-size: 13px; font-weight: 800; color: #137333; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
.resumo-valor { font-size: 42px; font-weight: 800; color: #137333; line-height: 1.1;}
.resumo-detalhes { font-size: 14px; color: #5a3b28; margin-top: 10px; font-weight: 600;}

.polaroid-box { background: #fffcf8; border: 2px dashed #ffb6c1; border-radius: 12px; padding: 20px; margin-top: 15px;}

/* Botão Salvar */
div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important; border-radius: 14px !important; font-weight: 800 !important; border: none !important; box-shadow: 0 6px 20px rgba(19, 115, 51, 0.2) !important; font-size: 18px !important; padding: 25px !important; width: 100% !important;}
div[data-testid="stButton"] button[kind="primary"]:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(19, 115, 51, 0.3) !important;}
</style>
""", unsafe_allow_html=True)

# CABEÇALHO COM BOTÃO DE VOLTAR
c_head, c_btn = st.columns([4, 1], vertical_alignment="center")
with c_head:
    st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">Cadastrar Pedido (Varejo)</h1>
        <p class="header-subtitle">Fluxo limpo e rápido para vendas da Loja Física e WhatsApp 🛍️</p>
    </div>
    """, unsafe_allow_html=True)
with c_btn:
    if st.button("⬅️ Voltar ao Mural", use_container_width=True):
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
        res = supabase.table("produtos").select("*").execute()
        # Busca produtos com "Adicionais" ou "Adicional" na categoria
        ativos = [p for p in (res.data or []) if p.get("ativo", True) and ("adicional" in p.get("categoria", "").strip().lower() or "adicionais" in p.get("categoria", "").strip().lower())]
        return sorted(ativos, key=lambda x: x.get("nome", ""))
    except: return []

secoes_disponiveis, cestas_ativas = obter_secoes_e_cestas()
adicionais_catalogo = obter_adicionais_catalogo()

# =====================================================
# GERENCIAMENTO DE ESTADO (SESSÃO)
# =====================================================
for key in ["man_nome", "man_cpf", "man_tel", "man_rua", "man_num", "man_comp", "man_bairro", "man_cidade", "man_cep", "ultimo_cep_man"]:
    if key not in st.session_state: st.session_state[key] = ""
if "modo_busca_cli" not in st.session_state: st.session_state.modo_busca_cli = False
if "man_extras_avulsos" not in st.session_state: st.session_state.man_extras_avulsos = [] 


# =====================================================
# 1. DADOS DO COMPRADOR
# =====================================================
with st.container(border=True):
    st.markdown("#### 👤 1. Dados do Comprador")
    
    cc1, cc_btn, cc2, cc3 = st.columns([3, 1, 2, 2])
    with cc1: nome_comp = st.text_input("Nome Completo *", value=st.session_state.man_nome, key="in_nome")
    with cc_btn:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Buscar Antigo", use_container_width=True):
            st.session_state.modo_busca_cli = not st.session_state.modo_busca_cli
            st.rerun()
    with cc2: cpf_comp = st.text_input("CPF", value=st.session_state.man_cpf, key="in_cpf")
    with cc3: tel_comp = st.text_input("Telefone / WhatsApp *", value=st.session_state.man_tel, key="in_tel")

    if st.session_state.modo_busca_cli:
        st.markdown("<div style='background: #faf7f3; padding: 15px; border-radius: 12px; margin-top: 10px; border: 1px solid #e8ddd3;'>", unsafe_allow_html=True)
        termo_busca = st.text_input("🔍 Digite Nome ou CPF do cliente:", key="man_termo_busca")
        try:
            res_cli = supabase.table("pedidos").select("cliente_nome, cliente_cpf, cliente_telefone").not_.ilike("cliente_nome", "%[B2B]%").execute()
            cli_dict = {c.get("cliente_telefone", "").strip(): c for c in (res_cli.data or []) if c.get("cliente_telefone", "").strip()}
            lista_clientes = sorted(list(cli_dict.values()), key=lambda x: x.get("cliente_nome", ""))
        except: lista_clientes = []
        
        if termo_busca: lista_clientes = [c for c in lista_clientes if termo_busca.lower() in str(c.get("cliente_nome", "")).lower() or termo_busca in str(c.get("cliente_cpf", ""))]
        opcoes_cli = [{"cliente_nome": "--- Selecione o cliente ---", "cliente_cpf": "", "cliente_telefone": ""}] + lista_clientes
        cli_sel = st.selectbox("Resultados:", opcoes_cli, format_func=lambda x: f"{x['cliente_nome']} (Tel: {x['cliente_telefone']})", key="man_busca_dropdown")
        
        if cli_sel and cli_sel["cliente_nome"] != "--- Selecione o cliente ---":
            st.session_state.man_nome = cli_sel["cliente_nome"]
            st.session_state.man_cpf = cli_sel["cliente_cpf"]
            st.session_state.man_tel = cli_sel["cliente_telefone"]
            st.session_state.modo_busca_cli = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# =====================================================
# 2. PRODUTO PRINCIPAL E SUAS OPÇÕES (COMO NO 02_PEDIDOS)
# =====================================================
selecoes_admin = {}

with st.container(border=True):
    st.markdown("#### 🎁 2. Seleção de Catálogo e Produto")
    
    if "man_secao_form" not in st.session_state or st.session_state["man_secao_form"] not in secoes_disponiveis:
        st.session_state["man_secao_form"] = secoes_disponiveis[0]

    def reset_cesta(): st.session_state["man_cesta_sel_id"] = None

    if len(secoes_disponiveis) > 1:
        c_sec, c_prod = st.columns(2)
        with c_sec: secao_escolhida = st.selectbox("1. Qual o Catálogo / Seção?", secoes_disponiveis, index=secoes_disponiveis.index(st.session_state["man_secao_form"]), key="man_secao_form", on_change=reset_cesta)
    else:
        secao_escolhida = secoes_disponiveis[0]
        st.session_state["man_secao_form"] = secao_escolhida

    cestas_da_secao = [c for c in cestas_ativas if (c.get("secao_vitrine") or "Cestas de Café").strip().lower() == secao_escolhida.strip().lower()]
    opcoes_cestas = [{"id": None, "nome": "Selecione o Produto Principal...", "preco": 0}] + cestas_da_secao
    
    idx_cesta = 0
    if st.session_state.get("man_cesta_sel_id"):
        for i, c in enumerate(opcoes_cestas):
            if c["id"] == st.session_state["man_cesta_sel_id"]: idx_cesta = i; break

    if len(secoes_disponiveis) > 1:
        with c_prod: cesta_sel = st.selectbox("2. Escolha o Produto Base", opcoes_cestas, format_func=lambda c: f"{c['nome']} (R$ {tratar_preco(c.get('preco')):.2f})" if c.get("id") else c["nome"], index=idx_cesta)
    else:
        cesta_sel = st.selectbox("Escolha o Produto Base", opcoes_cestas, format_func=lambda c: f"{c['nome']} (R$ {tratar_preco(c.get('preco')):.2f})" if c.get("id") else c["nome"], index=idx_cesta)

    # ITENS SELECIONÁVEIS DA CESTA
    if cesta_sel and cesta_sel.get("id"):
        st.session_state["man_cesta_sel_id"] = cesta_sel["id"]
        cfg = carregar_configuracao_cesta(cesta_sel["id"])
        if cfg and any(grp.get("produtos") for grp in cfg):
            st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 15px 0;'>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 15px; font-weight: 800; color: #137333; margin-bottom: 10px;'>🍓 Personalização da Cesta (Obrigatório)</div>", unsafe_allow_html=True)
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


# =====================================================
# 3. EXTRAS GLOBAIS E MANUAIS (CHECKBOXES)
# =====================================================
adicionais_selecionados_finais = []

with st.container(border=True):
    st.markdown("#### 🎀 3. Adicionais e Extras Globais")
    
    # LISTA EM CHECKBOXES
    if adicionais_catalogo:
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #5a3b28; margin-bottom: 10px;'>✨ Itens Oficiais do Catálogo</div>", unsafe_allow_html=True)
        cols_ad = st.columns(3)
        for i, p_ad in enumerate(adicionais_catalogo):
            preco_ad = tratar_preco(p_ad.get("preco"))
            txt_preco = f"(+ R$ {preco_ad:.2f})" if preco_ad > 0 else "(Sob Consulta)"
            with cols_ad[i % 3]:
                if st.checkbox(f"{p_ad['nome']} {txt_preco}", key=f"man_chk_ad_{p_ad['id']}"):
                    adicionais_selecionados_finais.append({"produto_id": p_ad["id"], "nome": p_ad["nome"], "preco": preco_ad})

    st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 15px 0;'>", unsafe_allow_html=True)
    
    # EXTRA MANUAL AVULSO
    st.markdown("<div style='font-size: 14px; font-weight: 700; color: #5a3b28; margin-bottom: 5px;'>✍️ Inserir Extra Manual (Não cadastrado)</div>", unsafe_allow_html=True)
    cm1, cm2, cm3 = st.columns([3, 1, 1.5])
    with cm1: nome_extra_man = st.text_input("Nome do Extra Avulso", placeholder="Ex: Urso de Pelúcia Grande", key="man_extra_nome", label_visibility="collapsed")
    with cm2: preco_extra_man = st.number_input("Valor (R$)", min_value=0.0, step=5.0, key="man_extra_preco", label_visibility="collapsed")
    with cm3:
        if st.button("➕ Inserir Manual", use_container_width=True):
            if nome_extra_man.strip():
                st.session_state.man_extras_avulsos.append({
                    "id": str(uuid.uuid4()), "produto_id": None, "nome": nome_extra_man.strip(), "preco": preco_extra_man
                })
                st.rerun()
            else: st.warning("Digite o nome do extra.")
            
    # MOSTRA OS EXTRAS MANUAIS ADICIONADOS
    if st.session_state.man_extras_avulsos:
        for i, extra in enumerate(st.session_state.man_extras_avulsos):
            adicionais_selecionados_finais.append(extra) # Junta na lista final matemática
            c_l1, c_l2 = st.columns([5, 1])
            with c_l1: st.markdown(f"<div style='margin-top: 8px; font-weight:600; color: #4a2e1b;'>✅ {extra['nome']} (R$ {formatar_moeda(extra['preco'])})</div>", unsafe_allow_html=True)
            with c_l2:
                if st.button("🗑️", key=f"del_ext_{extra['id']}", help="Remover"):
                    st.session_state.man_extras_avulsos.pop(i)
                    st.rerun()

    # POLAROID UPLOAD
    polaroid = any("polaroid" in extra["nome"].lower() or "foto" in extra["nome"].lower() for extra in adicionais_selecionados_finais)
    fotos_upload = []
    if polaroid:
        st.markdown("""
        <div class="polaroid-box">
            <h4 style="color: #d1476a; margin-top: 0; margin-bottom: 5px;">📸 Upload de Fotos Polaroid</h4>
            <p style="font-size: 13px; color: #5a3b28; margin-bottom: 15px;">O sistema detectou que você inseriu fotos no pedido! Faça o upload das imagens enviadas pelo cliente. Elas serão salvas no Supabase (bucket <b>pedido_fotos</b>) e os links irão direto para a ficha de produção.</p>
        </div>
        """, unsafe_allow_html=True)
        fotos_upload = st.file_uploader("Anexar fotos (PNG, JPG, JPEG)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="man_upload_fotos")


# =====================================================
# 4. DESTINATÁRIO E MENSAGEM
# =====================================================
with st.container(border=True):
    st.markdown("#### 💌 4. Destinatário e Cartão")
    cd1, cd2 = st.columns(2)
    with cd1: dest_nome = st.text_input("Nome do Homenageado *", key="man_dest_nome")
    with cd2: dest_tel = st.text_input("Telefone do Homenageado (Opcional)", key="man_dest_tel")
    motivo = st.text_input("Qual a Ocasião? (Ex: Aniversário de Casamento)", key="man_motivo")
    mensagem = st.text_area("Mensagem do Cartão", height=80, key="man_msg", placeholder="Texto que irá impresso no cartão.")


# =====================================================
# 5. ENDEREÇO E LOGÍSTICA
# =====================================================
with st.container(border=True):
    st.markdown("#### 📍 5. Endereço de Entrega")
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


# =====================================================
# 6. FECHAMENTO E RESUMO FINANCEIRO
# =====================================================
with st.container(border=True):
    st.markdown("#### 💰 6. Pagamento e Resumo Final")
    
    cf1, cf2 = st.columns(2)
    with cf1: pag = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito"], key="man_pag")
    with cf2: status = st.selectbox("Status Inicial", ["Recebido", "Pago"], key="man_status", help="Nasce como Recebido para confirmar o pagamento depois no Mural.")
    
    c_f1, c_f2 = st.columns(2)
    with c_f1: frete = st.number_input("Frete / Taxa de Entrega (R$)", min_value=0.0, step=5.0, value=0.0, key="man_frete")
    with c_f2: desc_perc = st.number_input("Desconto Concedido (%)", min_value=0.0, max_value=100.0, step=1.0, value=0.0, key="man_desc")
    
    # CÁLCULOS MATEMÁTICOS À PROVA DE FALHAS
    valor_c = float(cesta_sel.get("preco", 0)) if cesta_sel and cesta_sel.get("id") else 0.0
    valor_a = sum(extra.get("preco", 0.0) for extra in adicionais_selecionados_finais)
    
    subtotal = valor_c + valor_a
    valor_desconto = subtotal * (desc_perc / 100)
    total_liquido = subtotal - valor_desconto + frete

    # PAINEL DE RESUMO GIGANTE
    st.markdown(f"""
    <div class="resumo-financeiro">
        <div class="resumo-label">VALOR TOTAL A COBRAR DO CLIENTE</div>
        <div class="resumo-valor">R$ {formatar_moeda(total_liquido)}</div>
        <div class="resumo-detalhes">
            Subtotal Produtos: R$ {formatar_moeda(subtotal)} &nbsp;|&nbsp; 
            Desconto: - R$ {formatar_moeda(valor_desconto)} &nbsp;|&nbsp; 
            Frete: R$ {formatar_moeda(frete)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("✅ GRAVAR PEDIDO NO SISTEMA", type="primary", use_container_width=True):
        if not nome_comp: st.error("Informe o nome do comprador no Passo 1."); st.stop()
        if not tel_comp: st.error("Informe o WhatsApp do comprador no Passo 1."); st.stop()
        if not cesta_sel or not cesta_sel.get("id"): st.error("Selecione um Produto Base no Passo 2."); st.stop()
        if not dest_nome: st.error("Informe o Nome do Destinatário no Passo 4."); st.stop()
        if not rua or not num or not bairro: st.error("Complete Rua, Número e Bairro no Passo 5."); st.stop()

        # UPLOAD FOTOS POLAROID PARA SUPABASE
        links_polaroid = []
        if polaroid and fotos_upload:
            with st.spinner("📦 Salvando fotos no banco de dados (Supabase)..."):
                for foto in fotos_upload:
                    ext = foto.name.split('.')[-1]
                    file_name = f"polaroid_{uuid.uuid4().hex}.{ext}"
                    try:
                        supabase.storage.from_("pedido_fotos").upload(file_name, foto.read(), {"content-type": foto.type})
                        url = supabase.storage.from_("pedido_fotos").get_public_url(file_name)
                        links_polaroid.append(url)
                    except Exception as e:
                        pass

        # MONTAGEM DA STRING DA FICHA DE PRODUÇÃO
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
                # Salva a tabela relacional de adicionais para relatórios
                adicionais_para_banco = [{"produto_id": e.get("produto_id"), "nome": e["nome"], "preco": e.get("preco", 0.0)} for e in adicionais_selecionados_finais]
                if adicionais_para_banco: salvar_adicionais_pedido(p_id, adicionais_para_banco)
                
                st.success(f"✅ Pedido criado com sucesso para {nome_comp}!")
                st.session_state.man_extras_avulsos = []
                for k in ["pf_cep", "pf_rua", "pf_num", "pf_comp", "pf_bairro", "pf_cidade", "pf_ult_cep"]: st.session_state[k] = ""
                time.sleep(1.5)
                st.switch_page("pages/02_Pedidos.py")
            else: 
                st.error("Erro ao registrar no banco de dados.")
