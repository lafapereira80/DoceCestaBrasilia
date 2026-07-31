import streamlit as st
import base64
import re
from pathlib import Path
import uuid
from datetime import date
import requests

from services.pedido_service import salvar_pedido
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.produto_service import listar_produtos_por_categoria_id
from services.pedido_adicional_service import salvar_adicionais_pedido
from services.telegram_service import enviar_notificacao_telegram
from services.foto_service import salvar_fotos
from config.supabase import supabase
from utils.formatacao import NOME_LOJA, NOME_LOJA_CURTO, formatar_moeda

st.set_page_config(page_title=f"Finalizar | {NOME_LOJA_CURTO}", page_icon="🎁", layout="centered", initial_sidebar_state="collapsed")

# ==========================================================
# CSS BOUTIQUE (WIZARD DE CHECKOUT)
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Montserrat:wght@400;500;600;700;800&display=swap');

/* Esconde barras do Streamlit */
section[data-testid="stSidebar"], [data-testid="collapsedControl"], header, footer, .stAppDeployMenu { display: none !important; }

/* Fundo da Página e Fontes */
.stApp { background-color: #FCF9F2; }
html, body, [class*="css"], p, span, div, label { font-family: 'Montserrat', sans-serif; color: #2C1E14; }
.block-container { max-width: 850px !important; padding-top: 1.5rem !important; padding-bottom: 4rem !important; }

/* Cabeçalho do Checkout */
.checkout-header { text-align: center; margin-bottom: 2.5rem; }
.checkout-title { font-family: 'Dancing Script', cursive; font-size: 48px; color: #C5721F; margin: 0; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.03); }
.checkout-sub { font-size: 15px; color: #8B5A2B; margin-top: 8px; font-weight: 500; }

/* Passos do Formulário */
.step-header { display: flex; align-items: center; gap: 15px; margin-bottom: 1.5rem; padding-bottom: 10px; border-bottom: 1px solid #F0E6DC; }
.step-number { background: linear-gradient(135deg, #C5721F 0%, #9e520b 100%); color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 16px; font-weight: 800; box-shadow: 0 4px 10px rgba(197, 114, 31, 0.3); flex-shrink: 0;}
.step-title { margin: 0 !important; font-size: 22px !important; font-weight: 800 !important; color: #2C1E14 !important; letter-spacing: -0.5px;}

/* Estilização dos Containers Nativos do Streamlit */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important; border: 1px solid #F0E6DC !important; border-radius: 16px !important;
    padding: 30px 25px !important; margin-bottom: 20px !important; box-shadow: 0 8px 25px rgba(139, 90, 43, 0.03) !important;
}

/* Inputs e Formulários mais elegantes */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
    border-radius: 10px !important; border: 1px solid #E0D4C8 !important; background-color: #FAf7f3 !important; color: #2C1E14 !important; padding: 12px 16px !important; font-size: 14px !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stSelectbox>div>div>div:focus {
    border-color: #C5721F !important; box-shadow: 0 0 0 2px rgba(197, 114, 31, 0.2) !important; background-color: #FFFFFF !important;
}
div[data-testid="stCheckbox"] { background: #FAf7f3; border: 1px solid #F0E6DC; padding: 12px 16px; border-radius: 12px; margin-bottom: 8px; display: flex; align-items: center; transition: all 0.2s; }
div[data-testid="stCheckbox"]:hover { border-color: #d2bfae; transform: translateX(2px); }

/* Recibo / Ticket Style */
.receipt-box {
    background: #FFFFFF; position: relative; border: 1px solid #F0E6DC; border-radius: 12px; padding: 25px; margin-top: 15px;
    box-shadow: 0 10px 30px rgba(139, 90, 43, 0.05);
}
.receipt-box::before {
    content: ''; position: absolute; top: -8px; left: 0; right: 0; height: 8px;
    background-size: 16px 16px; background-image: radial-gradient(circle at 8px 0, transparent 8px, #FFFFFF 9px);
}
.receipt-title { font-family: 'Dancing Script', cursive; font-size: 32px; color: #C5721F; text-align: center; border-bottom: 2px dashed #F0E6DC; padding-bottom: 15px; margin-bottom: 20px; margin-top:0;}
.receipt-line { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 14px; font-weight: 500; color: #555;}
.receipt-total { display: flex; justify-content: space-between; font-size: 20px; font-weight: 800; color: #2C1E14; margin-top: 20px; padding-top: 20px; border-top: 2px dashed #F0E6DC; }

/* Botões */
div[data-testid="stButton"] button {
    background-color: #2C1E14 !important; color: #FFFFFF !important; border-radius: 30px !important; 
    border: none !important; height: 60px !important; font-size: 16px !important; font-weight: 700 !important; 
    letter-spacing: 1px !important; text-transform: uppercase !important; transition: all 0.3s ease !important;
    box-shadow: 0 5px 15px rgba(44, 30, 20, 0.2) !important; margin-top: 10px;
}
div[data-testid="stButton"] button:hover { background-color: #C5721F !important; box-shadow: 0 10px 25px rgba(197, 114, 31, 0.3) !important; transform: translateY(-3px) !important; }

/* Tela de Sucesso */
.sucesso-container { background: #FFFFFF; border: 2px solid #E0D4C8; border-radius: 24px; padding: 50px 30px; text-align: center; margin-top: 20px; box-shadow: 0 20px 50px rgba(139, 90, 43, 0.1); }
.sucesso-icone { font-size: 70px; margin-bottom: 15px; }
.sucesso-titulo { font-family: 'Dancing Script', cursive; font-size: 48px; color: #137333; margin: 0 0 15px 0; line-height: 1; }
.sucesso-texto { font-size: 16px; color: #555; line-height: 1.7; margin-bottom: 30px; }

@media (max-width: 640px) {
    .block-container { padding: 1rem 0.8rem !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 25px 15px !important; }
    .checkout-title { font-size: 40px; }
}
</style>
""", unsafe_allow_html=True)

def renderizar_passo(numero, titulo):
    st.markdown(f'<div class="step-header"><div class="step-number">{numero}</div><h2 class="step-title">{titulo}</h2></div>', unsafe_allow_html=True)

# ==========================================================
# CACHING E FUNÇÕES BASE
# ==========================================================
@st.cache_data(ttl=600, show_spinner=False)
def obter_categorias_cacheadas():
    try: return supabase.table("categorias").select("*").execute().data or []
    except: return []

@st.cache_data(ttl=60, show_spinner=False)
def obter_secoes_e_cestas_ativas():
    try:
        res_secoes = supabase.table("vitrine_secoes").select("nome", "ativa").eq("ativa", True).order("ordem").execute()
        secoes_ativas = [s["nome"] for s in (res_secoes.data or [])]
        cestas = [c for c in listar_cestas() if c.get("ativa", True)]
        return secoes_ativas if secoes_ativas else ["Cestas"], sorted(cestas, key=lambda x: x.get("ordem", 999))
    except: return ["Cestas"], []

@st.cache_data(ttl=300, show_spinner=False)
def obter_configuracao_cesta_cacheada(cesta_id):
    try: return carregar_configuracao_cesta(cesta_id)
    except: return []

@st.cache_data(ttl=300, show_spinner=False)
def obter_produtos_por_categoria_cacheados(categoria_id):
    try: return listar_produtos_por_categoria_id(categoria_id)
    except: return []

@st.cache_data(ttl=86400, show_spinner=False)
def buscar_cep_cacheado(cep_limpo):
    try:
        res = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
        if res.status_code == 200 and "erro" not in res.json(): return res.json()
    except: pass
    return None

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11: return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    if (soma * 10 % 11) % 10 != int(cpf[9]): return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    if (soma * 10 % 11) % 10 != int(cpf[10]): return False
    return True

# CONTROLE DE ESTADO
for key in ["pedido_enviado_com_sucesso", "ultimo_cep_buscado", "cesta_selecionada_id", "fotos_polaroid_cliente"]:
    if key not in st.session_state: st.session_state[key] = False if key == "pedido_enviado_com_sucesso" else [] if key == "fotos_polaroid_cliente" else "" if key == "ultimo_cep_buscado" else None

# ==========================================================
# TELA DE SUCESSO BOUTIQUE
# ==========================================================
if st.session_state["pedido_enviado_com_sucesso"]:
    st.balloons()
    dados = st.session_state.get("resumo_pedido_sucesso", {})
    st.markdown(f'<div class="checkout-header"><h1 class="checkout-title">{NOME_LOJA_CURTO}</h1></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sucesso-container">
        <div class="sucesso-icone">🎉</div>
        <h2 class="sucesso-titulo">Pedido Confirmado!</h2>
        <p class="sucesso-texto">Que alegria, <b>{dados.get('cliente_nome')}</b>! O seu presente foi reservado com muito carinho pela nossa equipe.<br><br>⏳ <b>Próximo Passo:</b> Aguarde alguns instantes. Nossa equipe enviará uma mensagem no seu WhatsApp para confirmar a taxa de entrega e o link de pagamento.</p>
        
        <div class="receipt-box" style="text-align:left; background: #FCF9F2;">
            <h3 class="receipt-title" style="font-size:26px;">Ticket do Presente</h3>
            <div class="receipt-line"><span>💝 Para:</span> <b>{dados.get('destinatario_nome', '-')}</b></div>
            <div class="receipt-line"><span>🎁 Presente:</span> <b>{dados.get('cesta_nome')}</b></div>
            <div class="receipt-line"><span>🎀 Extras:</span> <b>{dados.get('adicionais_str') if dados.get('adicionais_str') else 'Nenhum'}</b></div>
            <div class="receipt-line"><span>📅 Data:</span> <b>{dados.get('data_entrega')} ({dados.get('periodo_entrega')})</b></div>
            <div class="receipt-total"><span style="color:#C5721F;">TOTAL (S/ FRETE)</span> <span>{dados.get('valor_total')}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("🎁 Fazer Novo Pedido", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.stop()

# ==========================================================
# FORMULÁRIO DE CHECKOUT WIZARD
# ==========================================================
st.markdown(f"""
<div class="checkout-header">
    <h1 class="checkout-title">{NOME_LOJA_CURTO}</h1>
    <div class="checkout-sub">Finalize sua encomenda em poucos passos 💝</div>
</div>
""", unsafe_allow_html=True)

# 1. DADOS COMPRADOR
with st.container(border=True):
    renderizar_passo("1", "Quem está presenteando?")
    st.caption("Precisamos dos seus dados para confirmar o pagamento e te enviar atualizações.")
    nome = st.text_input("Seu Nome Completo *", key="input_nome_comprador")
    col_ddi, col_tel, col_cpf = st.columns([1.2, 2.5, 2.5])
    with col_ddi: st.selectbox("DDI *", ["🇧🇷 +55", "🇺🇸 +1", "🇵🇹 +351"], key="input_ddi_comprador")
    with col_tel: st.text_input("Seu WhatsApp *", placeholder="(11) 99999-9999", key="input_tel_comprador")
    with col_cpf: st.text_input("Seu CPF *", max_chars=14, placeholder="Apenas números", key="input_cpf_comprador")

# 2. ESCOLHA PRESENTE
secoes_disponiveis, cestas_ativas = obter_secoes_e_cestas_ativas()
cesta_obj = None
selecoes_cliente = {}

if cestas_ativas:
    if st.session_state.get("cesta_selecionada_home"):
        for c in cestas_ativas:
            if c["id"] == st.session_state["cesta_selecionada_home"]:
                st.session_state["secao_form"] = c.get("secao_vitrine", "Cestas")
                st.session_state["cesta_selecionada_id"] = c["id"]
        st.session_state["cesta_selecionada_home"] = None

    if "secao_form" not in st.session_state or st.session_state["secao_form"] not in secoes_disponiveis:
        st.session_state["secao_form"] = secoes_disponiveis[0]

    with st.container(border=True):
        renderizar_passo("2", "A Escolha do Presente")
        if len(secoes_disponiveis) > 1:
            col_categoria, col_modelo = st.columns(2)
            with col_categoria: st.selectbox("1. Qual coleção deseja explorar?", secoes_disponiveis, index=secoes_disponiveis.index(st.session_state["secao_form"]), key="secao_form", on_change=lambda: st.session_state.update({"cesta_selecionada_id": None}))
            cestas_da_secao = [c for c in cestas_ativas if (c.get("secao_vitrine") or "Cestas").strip().lower() == str(st.session_state["secao_form"]).strip().lower()]
            opcoes_cestas = [{"id": None, "nome": "Selecione o modelo perfeito..."}] + cestas_da_secao
            idx = next((i for i, c in enumerate(opcoes_cestas) if c["id"] == st.session_state.get("cesta_selecionada_id")), 0)
            with col_modelo: cesta_selecionada = st.selectbox("2. Escolha o modelo", opcoes_cestas, format_func=lambda c: c["nome"], index=idx)
        else:
            opcoes_cestas = [{"id": None, "nome": "Selecione o modelo perfeito..."}] + cestas_ativas
            idx = next((i for i, c in enumerate(opcoes_cestas) if c["id"] == st.session_state.get("cesta_selecionada_id")), 0)
            cesta_selecionada = st.selectbox("Escolha o modelo", opcoes_cestas, format_func=lambda c: c["nome"], index=idx)

        if cesta_selecionada and cesta_selecionada.get("id"):
            cesta_obj = cesta_selecionada
            st.session_state["cesta_selecionada_id"] = cesta_obj["id"]
            
            st.markdown("<hr style='border-top: 1px dashed #F0E6DC; margin: 25px 0;'>", unsafe_allow_html=True)
            c_img, c_txt = st.columns([1.2, 1.8], gap="large", vertical_alignment="center")
            with c_img:
                if cesta_obj.get("imagem"): st.markdown(f'<img src="{cesta_obj["imagem"]}" style="width:100%; border-radius:12px; border:1px solid #F0E6DC; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
                st.markdown(f'<div style="text-align:center; margin-top:15px;"><span style="color:#C5721F; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Valor Base</span><br><span style="font-size: 28px; color: #2C1E14; font-weight: 800;">R$ {formatar_moeda(cesta_obj.get("preco", 0))}</span></div>', unsafe_allow_html=True)
            with c_txt:
                st.markdown(f'<h3 style="font-family:\'Dancing Script\', cursive; font-size:42px; color:#C5721F; margin:0 0 10px 0; line-height:1.1;">{cesta_obj.get("nome")}</h3>', unsafe_allow_html=True)
                if cesta_obj.get("descricao"): st.markdown(f'<div style="font-size:14px; color:#555; line-height:1.6; background:#FCF9F2; padding:15px; border-radius:10px; border-left:3px solid #C5721F;">{cesta_obj["descricao"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            
            configuracao = obter_configuracao_cesta_cacheada(cesta_obj["id"])
            if configuracao:
                st.markdown("<div style='margin-top:25px; margin-bottom:15px; font-size:18px; font-weight:800; color:#2C1E14;'>🍓 Personalize os Itens</div>", unsafe_allow_html=True)
                for grupo in configuracao:
                    cat = grupo.get("categoria", "Geral")
                    prods = grupo.get("produtos", [])
                    maximo = grupo.get("max_escolhas", 1)
                    if not prods: continue
                    st.markdown(f"<div style='font-size:14px; font-weight:700; color:#C5721F; margin-bottom:5px; margin-top:10px;'>📦 {cat}</div>", unsafe_allow_html=True)
                    if maximo == 1:
                        esc = st.radio("Escolha 1", prods, format_func=lambda p: p["nome"], key=f"rad_{cesta_obj['id']}_{cat}", label_visibility="collapsed")
                        if esc: selecoes_cliente[cat] = [esc]
                    else:
                        escs = st.multiselect(f"Máximo {maximo}", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"mul_{cesta_obj['id']}_{cat}")
                        selecoes_cliente[cat] = escs

# 3. EXTRAS E POLAROID
adicionais_selecionados = []
polaroid = False
categorias = obter_categorias_cacheadas()
cat_adicionais = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)

if cat_adicionais:
    produtos_adicionais = obter_produtos_por_categoria_cacheados(cat_adicionais["id"])
    if produtos_adicionais:
        with st.container(border=True):
            renderizar_passo("3", "Adicionar Mimos Extras")
            st.caption("Deixe o presente ainda mais surpreendente com nossos itens exclusivos.")
            cols = st.columns(2)
            for i, prod in enumerate(produtos_adicionais):
                preco_add = prod.get("preco")
                txt_val = f"+ R$ {formatar_moeda(preco_add)}" if preco_add is not None else "Sob Consulta"
                with cols[i % 2]:
                    if st.checkbox(f"✨ {prod['nome']} **{txt_val}**", key=f"add_{prod['id']}"):
                        adicionais_selecionados.append({"produto_id": prod["id"], "nome": prod["nome"], "preco": float(preco_add) if preco_add is not None else None, "categoria": "Adicionais"})
                        if "polaroid" in prod["nome"].lower() or "foto" in prod["nome"].lower(): polaroid = True

if polaroid:
    with st.container(border=True):
        st.markdown('<div style="font-size:18px; font-weight:800; color:#C5721F; margin-bottom:5px;">📷 Envie suas Fotos (Polaroid)</div>', unsafe_allow_html=True)
        st.caption("Você selecionou as fotos Polaroid. Envie até 2 imagens para revelarmos.")
        fotos_upload = st.file_uploader("Até 2 fotos", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="fotos_polaroid_cliente")
        if fotos_upload and len(fotos_upload) > 2: st.error("⚠️ Limite excedido: Mantenha apenas 2 fotos anexadas.")

# 4. HOMENAGEADO E CARTÃO
with st.container(border=True):
    renderizar_passo("4", "Para Quem é o Presente?")
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.text_input("Nome de quem vai receber *", placeholder="Ex: Ana Clara", key="input_dest_nome")
    with col_d2: st.text_input("WhatsApp do destinatário", placeholder="(Opcional)", key="input_dest_tel")
    st.text_input("Qual a Ocasião? (Opcional)", placeholder="Ex: Aniversário, Dia das Mães, Pedido de Desculpas...", key="input_motivo")
    st.text_area("💌 Cartão de Presente", height=100, placeholder="Escreva aqui a mensagem especial que iremos imprimir no cartão...", key="input_mensagem")

# 5. LOCAL E AGENDAMENTO
with st.container(border=True):
    renderizar_passo("5", "Local e Agendamento")
    cep_limpo = re.sub(r'\D', '', st.text_input("CEP da Entrega", max_chars=8, placeholder="Somente números", key="input_cep"))
    
    if len(cep_limpo) == 8 and st.session_state["ultimo_cep_buscado"] != cep_limpo:
        dados_cep = buscar_cep_cacheado(cep_limpo)
        if dados_cep:
            st.session_state["input_rua"] = dados_cep.get("logradouro", "")
            st.session_state["input_bairro"] = dados_cep.get("bairro", "")
            st.session_state["input_cidade"] = f"{dados_cep.get('localidade', '')} - {dados_cep.get('uf', '')}"
        st.session_state["ultimo_cep_buscado"] = cep_limpo

    col_cid, col_bairro = st.columns([1.5, 1])
    with col_cid: st.text_input("Cidade - UF *", key="input_cidade")
    with col_bairro: st.text_input("Bairro *", key="input_bairro")
    
    col_rua, col_num = st.columns([2.5, 1])
    with col_rua: st.text_input("Logradouro *", key="input_rua")
    with col_num: st.text_input("Nº / Apto *", key="input_numero")
    
    st.markdown("<hr style='border-top: 1px dashed #F0E6DC; margin: 15px 0;'>", unsafe_allow_html=True)
    col_ent1, col_ent2 = st.columns(2)
    with col_ent1: st.date_input("📅 Data da Entrega", format="DD/MM/YYYY", key="input_data_entrega")
    with col_ent2: st.selectbox("🕒 Período Desejado", ["Manhã", "Tarde", "Noite"], key="input_periodo_entrega")
    st.text_input("✨ Solicitação de Horário Especial (Opcional)", placeholder="Ex: Entregar exatamente às 07h00? (Sujeito a taxa)", key="input_pedido_especial")

# 6. RESUMO E FECHAMENTO
with st.container(border=True):
    renderizar_passo("6", "Resumo e Fechamento")
    pagamento = st.radio("Como você prefere pagar?", ["Pix (Aprovação Imediata)", "Cartão de Crédito"], horizontal=True, key="forma_pagamento_radio")

valor_base = float(cesta_obj.get("preco", 0)) if cesta_obj else 0
valor_adicionais = sum([float(item["preco"]) for item in adicionais_selecionados if item["preco"] is not None])
tem_consulta = any(item["preco"] is None for item in adicionais_selecionados)
total_estimado = valor_base + valor_adicionais

if cesta_obj:
    with st.container(border=False):
        st.markdown(f"""
        <div class="receipt-box">
            <h3 class="receipt-title">Resumo do Pedido</h3>
            <div class="receipt-line"><span>🎁 <b>{cesta_obj['nome']}</b></span> <span>R$ {formatar_moeda(valor_base)}</span></div>
            {f'<div class="receipt-line"><span>🎀 Mimos Extras</span> <span>R$ {formatar_moeda(valor_adicionais)}</span></div>' if valor_adicionais > 0 else ''}
            <div class="receipt-line"><span>🚚 Taxa de Entrega</span> <span style="color:#C5721F; font-size:12px;">A CALCULAR NO WHATSAPP</span></div>
            <div class="receipt-total"><span style="color:#C5721F;">SUBTOTAL:</span> <span>R$ {formatar_moeda(total_estimado)}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if tem_consulta: st.warning("⚠️ **Nota:** Você incluiu itens '*Sob Consulta*'. O valor exato será confirmado por nossa equipe.")

# ==========================================================
# PROCESSAMENTO FINAL (SALVAMENTO CASCATA SEGURO)
# ==========================================================
st.write("")
enviar = st.button("🎁 FINALIZAR MEU PEDIDO AGORA", use_container_width=True, type="primary")

if enviar:
    nome = st.session_state.get("input_nome_comprador", "")
    cpf_bruto = st.session_state.get("input_cpf_comprador", "")
    tel_bruto = st.session_state.get("input_tel_comprador", "")
    ddi = re.sub(r'\D', '', st.session_state.get("input_ddi_comprador", "55"))
    
    if not nome.strip(): st.error("❌ Por favor, informe seu Nome."); st.stop()
    if not tel_bruto.strip(): st.error("❌ Por favor, informe seu WhatsApp."); st.stop()
    if not validar_cpf(cpf_bruto): st.error("❌ CPF inválido. Verifique os números."); st.stop()
    if not cesta_obj: st.error("❌ Selecione uma opção de Cesta."); st.stop()
    
    dest_nome = st.session_state.get("input_dest_nome", "")
    if not dest_nome.strip(): st.error("❌ Informe o nome de quem vai receber o presente."); st.stop()
    
    rua = st.session_state.get("input_rua", "")
    num = st.session_state.get("input_numero", "")
    if not rua.strip() or not num.strip(): st.error("❌ Informe a Rua e o Número de entrega."); st.stop()
    
    fotos_upload = st.session_state.get("fotos_polaroid_cliente", [])
    if polaroid and len(fotos_upload) > 2: st.error("❌ O limite para Polaroid é de 2 fotos."); st.stop()

    cpf_limpo = re.sub(r'\D', '', cpf_bruto)
    telefone_oficial = f"{ddi}{re.sub(r'\D', '', tel_bruto)}"
    cep = st.session_state.get("input_cep", "")
    bairro = st.session_state.get("input_bairro", "")
    cidade = st.session_state.get("input_cidade", "")
    endereco_completo = f"{rua}, {num} - {bairro}, {cidade}" + (f" (CEP: {cep})" if cep else "")
    
    dt_ent = st.session_state.get("input_data_entrega")
    produtos_txt = [f"{c}: {i['nome']}" for c, itens in selecoes_cliente.items() for i in itens]
    adicionais_lista = [f"{i['nome']}" for i in adicionais_selecionados]
    texto_adicionais_bd = ", ".join(adicionais_lista) if adicionais_lista else "Nenhum"
    
    dados = {
        "cliente_nome": nome.strip(),
        "cliente_cpf": cpf_limpo,
        "cliente_telefone": telefone_oficial,
        "destinatario_nome": dest_nome.strip(),
        "destinatario_telefone": re.sub(r'\D', '', st.session_state.get("input_dest_tel", "")),
        "motivo_homenagem": st.session_state.get("input_motivo", "").strip(),
        "cesta_id": cesta_obj["id"],
        "cesta_nome": cesta_obj["nome"],
        "produtos": "\n".join(produtos_txt),
        "adicionais": texto_adicionais_bd, 
        "pagamento": pagamento,
        "mensagem": st.session_state.get("input_mensagem", "").strip(),
        "pedido_especial": st.session_state.get("input_pedido_especial", "").strip(),
        "endereco": endereco_completo,
        "data_entrega": dt_ent.strftime("%Y-%m-%d") if dt_ent else str(date.today()),
        "periodo_entrega": st.session_state.get("input_periodo_entrega", "Manhã"),
        "status": "Recebido",
        "valor_frete": 0,
        "valor_total": total_estimado
    }

    with st.spinner("Reservando seu presente e finalizando pedido..."):
        try: sucesso, pedido_id = salvar_pedido(dados)
        except Exception as e: st.error("❌ Erro de conexão ao salvar pedido. Tente novamente."); st.stop()
        
        if sucesso:
            if adicionais_selecionados: salvar_adicionais_pedido(pedido_id, adicionais_selecionados)
            if polaroid and fotos_upload:
                with st.spinner("📦 Processando fotos Polaroid no servidor..."):
                    salvar_fotos(pedido_id, fotos_upload[:2])
            
            try:
                texto_aviso = (
                    f"🚨 *NOVO PEDIDO RECEBIDO (SITE)!* 🚨\n\n"
                    f"📦 *ID:* `#{str(pedido_id).split('-')[0].upper()}`\n"
                    f"👤 *Cliente:* {nome}\n"
                    f"📱 *Contato:* [{telefone_oficial}](https://wa.me/{telefone_oficial})\n"
                    f"🎁 *Cesta:* {cesta_obj['nome']}\n"
                    f"📍 *Bairro:* {bairro}\n"
                    f"💰 *Estimativa:* R$ {formatar_moeda(total_estimado)}\n\n"
                    f"⚡ *Acesse o painel para processar!*"
                )
                enviar_notificacao_telegram(texto_aviso)
            except: pass 

            st.session_state["resumo_pedido_sucesso"] = {
                "cliente_nome": nome.strip(),
                "destinatario_nome": dest_nome.strip(),
                "cesta_nome": f"{cesta_obj['nome']}",
                "adicionais_str": ", ".join(adicionais_lista),
                "data_entrega": dt_ent.strftime("%d/%m/%Y") if dt_ent else "",
                "periodo_entrega": st.session_state.get("input_periodo_entrega", ""),
                "endereco": f"{rua}, {num} - {bairro}",
                "valor_total": f"R$ {formatar_moeda(total_estimado)}"
            }
            st.session_state["pedido_enviado_com_sucesso"] = True
            st.rerun()
        else:
            st.error("❌ Ocorreu um problema ao registrar o pedido. Tente novamente em instantes.")

st.divider()
st.markdown(f'<div style="text-align:center; font-size:12px; color:#888; font-weight: 500;">{NOME_LOJA_CURTO} © {date.today().year}<br>Transação 100% Segura 🔒</div>', unsafe_allow_html=True)
st.page_link("app.py", label="⬅️ Voltar para a Loja", icon="🛍️")
