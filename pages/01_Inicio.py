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

# Injeta CSS Global
def injetar_css():
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
injetar_css()

# Ajustes Locais Exclusivos do Checkout
st.markdown("""
<style>
.step-container { display: flex; align-items: center; margin-bottom: 18px; border-bottom: 2px solid var(--border-color); padding-bottom: 10px; }
.step-number { background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary-dark) 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px; margin-right: 12px; flex-shrink: 0; }
.receipt-box { background: var(--bg-card); border: 2px dashed var(--border-color); border-radius: 16px; padding: 25px; margin-top: 10px; }
.receipt-line { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 14px; font-weight: 500;}
.receipt-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: 800; color: var(--brand-secondary); margin-top: 15px; padding-top: 15px; border-top: 2px dashed var(--border-color); }
div[data-testid="stCheckbox"] { background: var(--bg-page); border: 1px solid var(--border-color); padding: 12px 16px; border-radius: 14px; margin-bottom: 8px; display: flex; align-items: center; }
</style>
""", unsafe_allow_html=True)

def renderizar_passo(numero, titulo):
    st.markdown(f'<div class="step-container"><div class="step-number">{numero}</div><h3 style="margin:0;">{titulo}</h3></div>', unsafe_allow_html=True)

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

# TELA DE SUCESSO
if st.session_state["pedido_enviado_com_sucesso"]:
    st.balloons()
    dados = st.session_state.get("resumo_pedido_sucesso", {})
    st.markdown(f"""
    <div style="background: #f0f7f4; border: 2px solid #137333; border-radius: 24px; padding: 40px 30px; text-align: center; margin-top: 20px;">
        <div style="font-size: 60px; margin-bottom: 10px;">🎉</div>
        <h2 style="color: #137333; margin-bottom: 12px;">Pedido Confirmado!</h2>
        <p style="font-size: 16px; margin-bottom: 25px;">Que alegria, <b>{dados.get('cliente_nome')}</b>! Seu pedido foi reservado com muito carinho. <br><br>⏳ Nossa equipe entrará em contato via WhatsApp para confirmar a taxa de entrega e o pagamento.</p>
        <div class="receipt-box" style="text-align:left;">
            <div style="font-size: 16px; font-weight: 800; border-bottom: 1px solid #e8ddd3; padding-bottom: 10px; margin-bottom:10px;">📋 Seu Ticket</div>
            <div class="receipt-line"><span>💝 Para:</span> <span>{dados.get('destinatario_nome', '-')}</span></div>
            <div class="receipt-line"><span>🎁 Presente:</span> <span style="text-align: right;">{dados.get('cesta_nome')}</span></div>
            <div class="receipt-total"><span>TOTAL (sem frete)</span> <span>{dados.get('valor_total')}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("🎁 Fazer Novo Pedido", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.stop()

# CABEÇALHO DO FORMULÁRIO
st.markdown(f'<div class="header-banner"><div class="header-text" style="align-items:center;"><h1 class="header-title">{NOME_LOJA_CURTO}</h1><p class="header-subtitle">Finalize sua encomenda em poucos passos 💝</p></div></div>', unsafe_allow_html=True)

# 1. DADOS COMPRADOR
with st.container(border=True):
    renderizar_passo("1", "Quem está presenteando?")
    nome = st.text_input("Seu Nome Completo *", key="input_nome_comprador")
    col_ddi, col_tel, col_cpf = st.columns([1.2, 2.5, 2.5])
    with col_ddi: st.selectbox("DDI *", ["🇧🇷 +55", "🇺🇸 +1", "🇵🇹 +351"], key="input_ddi_comprador")
    with col_tel: st.text_input("Seu WhatsApp *", key="input_tel_comprador")
    with col_cpf: st.text_input("Seu CPF *", max_chars=14, key="input_cpf_comprador")

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
            with col_categoria: st.selectbox("1. Coleção", secoes_disponiveis, index=secoes_disponiveis.index(st.session_state["secao_form"]), key="secao_form", on_change=lambda: st.session_state.update({"cesta_selecionada_id": None}))
            cestas_da_secao = [c for c in cestas_ativas if (c.get("secao_vitrine") or "Cestas").strip().lower() == str(st.session_state["secao_form"]).strip().lower()]
            opcoes_cestas = [{"id": None, "nome": "Selecione o modelo..."}] + cestas_da_secao
            idx = next((i for i, c in enumerate(opcoes_cestas) if c["id"] == st.session_state.get("cesta_selecionada_id")), 0)
            with col_modelo: cesta_selecionada = st.selectbox("2. Modelo", opcoes_cestas, format_func=lambda c: c["nome"], index=idx)
        else:
            opcoes_cestas = [{"id": None, "nome": "Selecione o modelo..."}] + cestas_ativas
            idx = next((i for i, c in enumerate(opcoes_cestas) if c["id"] == st.session_state.get("cesta_selecionada_id")), 0)
            cesta_selecionada = st.selectbox("Escolha o modelo", opcoes_cestas, format_func=lambda c: c["nome"], index=idx)

        if cesta_selecionada and cesta_selecionada.get("id"):
            cesta_obj = cesta_selecionada
            st.session_state["cesta_selecionada_id"] = cesta_obj["id"]
            
            st.markdown("<hr style='border-top: 1px dashed var(--border-color); margin: 20px 0;'>", unsafe_allow_html=True)
            c_img, c_txt = st.columns([1.2, 1.8], gap="large")
            with c_img:
                if cesta_obj.get("imagem"): st.image(cesta_obj["imagem"], use_container_width=True)
                st.markdown(f'<div style="background: var(--bg-page); border-radius: 12px; padding: 15px; text-align: center;"><div style="font-weight: 800; color: var(--brand-primary); text-transform: uppercase;">Valor Base</div><div style="font-size: 26px; color: var(--brand-secondary); font-weight: 800;">R$ {formatar_moeda(cesta_obj.get("preco", 0))}</div></div>', unsafe_allow_html=True)
            with c_txt:
                st.markdown(f'<h2 style="font-family:\'Dancing Script\', cursive; font-size:38px; color:var(--brand-primary); margin:0;">{cesta_obj.get("nome")}</h2>', unsafe_allow_html=True)
                if cesta_obj.get("descricao"): st.info(cesta_obj["descricao"])
            
            configuracao = obter_configuracao_cesta_cacheada(cesta_obj["id"])
            if configuracao:
                st.markdown("#### 🍓 Personalize os Itens")
                for grupo in configuracao:
                    cat = grupo.get("categoria", "Geral")
                    prods = grupo.get("produtos", [])
                    maximo = grupo.get("max_escolhas", 1)
                    if not prods: continue
                    st.markdown(f"**📦 {cat}**")
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
        st.markdown('#### 📷 Envie suas Fotos (Polaroid)')
        fotos_upload = st.file_uploader("Até 2 fotos", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="fotos_polaroid_cliente")
        if fotos_upload and len(fotos_upload) > 2: st.error("⚠️ Limite excedido: Mantenha apenas 2 fotos.")

# 4. HOMENAGEADO
with st.container(border=True):
    renderizar_passo("4", "Para Quem é o Presente?")
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.text_input("Nome de quem vai receber *", key="input_dest_nome")
    with col_d2: st.text_input("WhatsApp do destinatário", key="input_dest_tel")
    st.text_input("Ocasião (Opcional)", key="input_motivo")
    st.text_area("💌 Cartão de Presente", height=100, key="input_mensagem")

# 5. LOCAL E AGENDAMENTO
with st.container(border=True):
    renderizar_passo("5", "Local e Agendamento")
    cep_limpo = re.sub(r'\D', '', st.text_input("CEP da Entrega", max_chars=8, key="input_cep"))
    
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
    with col_num: st.text_input("Nº *", key="input_numero")
    
    st.markdown("<hr style='border-top: 1px dashed var(--border-color); margin: 15px 0;'>", unsafe_allow_html=True)
    col_ent1, col_ent2 = st.columns(2)
    with col_ent1: st.date_input("📅 Data", format="DD/MM/YYYY", key="input_data_entrega")
    with col_ent2: st.selectbox("🕒 Período", ["Manhã", "Tarde", "Noite"], key="input_periodo_entrega")
    st.text_input("✨ Solicitação de Horário Especial", key="input_pedido_especial")

# 6. RESUMO E ENVIO
with st.container(border=True):
    renderizar_passo("6", "Pagamento e Resumo")
    pagamento = st.radio("Forma de Pagamento", ["Pix (Aprovação Imediata)", "Cartão de Crédito"], horizontal=True, key="forma_pagamento_radio")

valor_base = float(cesta_obj.get("preco", 0)) if cesta_obj else 0
valor_adicionais = sum([float(item["preco"]) for item in adicionais_selecionados if item["preco"] is not None])
total_estimado = valor_base + valor_adicionais

if cesta_obj:
    with st.container(border=True):
        st.markdown(f"""
        <div class="receipt-box">
            <h4 style="text-align: center; margin-top:0;">RESUMO DO PEDIDO</h4>
            <div class="receipt-line"><span>🎁 {cesta_obj['nome']}</span> <strong>R$ {formatar_moeda(valor_base)}</strong></div>
            {f'<div class="receipt-line"><span>🎀 Mimos Extras</span> <strong>R$ {formatar_moeda(valor_adicionais)}</strong></div>' if valor_adicionais > 0 else ''}
            <div class="receipt-line"><span>🚚 Taxa de Entrega</span> <strong>A calcular</strong></div>
            <div class="receipt-total"><span>SUBTOTAL:</span> <span>R$ {formatar_moeda(total_estimado)}</span></div>
        </div>
        """, unsafe_allow_html=True)

st.write("")
if st.button("🎁 FINALIZAR MEU PEDIDO AGORA", use_container_width=True, type="primary"):
    nome = st.session_state.get("input_nome_comprador", "")
    cpf_bruto = st.session_state.get("input_cpf_comprador", "")
    tel_bruto = st.session_state.get("input_tel_comprador", "")
    
    if not nome.strip() or not tel_bruto.strip(): st.error("❌ Preencha Nome e WhatsApp."); st.stop()
    if not validar_cpf(cpf_bruto): st.error("❌ CPF inválido."); st.stop()
    if not cesta_obj: st.error("❌ Selecione uma Cesta."); st.stop()
    if not st.session_state.get("input_dest_nome", "").strip(): st.error("❌ Informe quem vai receber."); st.stop()
    if not st.session_state.get("input_rua", "").strip(): st.error("❌ Informe o endereço de entrega."); st.stop()

    fotos_upload = st.session_state.get("fotos_polaroid_cliente", [])
    if polaroid and len(fotos_upload) > 2: st.error("❌ O limite para Polaroid é de 2 fotos."); st.stop()

    ddi = re.sub(r'\D', '', st.session_state.get("input_ddi_comprador", "55"))
    telefone_oficial = f"{ddi}{re.sub(r'\D', '', tel_bruto)}"
    endereco_completo = f"{st.session_state.get('input_rua')}, {st.session_state.get('input_numero')} - {st.session_state.get('input_bairro')}, {st.session_state.get('input_cidade')}"
    
    produtos_txt = [f"{c}: {i['nome']}" for c, itens in selecoes_cliente.items() for i in itens]
    
    dados = {
        "cliente_nome": nome.strip(),
        "cliente_cpf": re.sub(r'\D', '', cpf_bruto),
        "cliente_telefone": telefone_oficial,
        "destinatario_nome": st.session_state.get("input_dest_nome", "").strip(),
        "destinatario_telefone": re.sub(r'\D', '', st.session_state.get("input_dest_tel", "")),
        "motivo_homenagem": st.session_state.get("input_motivo", "").strip(),
        "cesta_id": cesta_obj["id"],
        "cesta_nome": cesta_obj["nome"],
        "produtos": "\n".join(produtos_txt),
        "adicionais": ", ".join([i['nome'] for i in adicionais_selecionados]),
        "pagamento": pagamento,
        "mensagem": st.session_state.get("input_mensagem", "").strip(),
        "pedido_especial": st.session_state.get("input_pedido_especial", "").strip(),
        "endereco": endereco_completo,
        "data_entrega": st.session_state.get("input_data_entrega").strftime("%Y-%m-%d"),
        "periodo_entrega": st.session_state.get("input_periodo_entrega", "Manhã"),
        "status": "Recebido",
        "valor_total": total_estimado
    }

    with st.spinner("Finalizando pedido..."):
        sucesso, pedido_id = salvar_pedido(dados)
        if sucesso:
            if adicionais_selecionados: salvar_adicionais_pedido(pedido_id, adicionais_selecionados)
            if polaroid and fotos_upload: salvar_fotos(pedido_id, fotos_upload[:2])
            
            try:
                enviar_notificacao_telegram(f"🚨 *NOVO PEDIDO (SITE)!*\n📦 *ID:* `#{pedido_id}`\n👤 *Cliente:* {nome}\n🎁 *Cesta:* {cesta_obj['nome']}\n💰 *Estimativa:* R$ {formatar_moeda(total_estimado)}")
            except: pass 

            st.session_state["resumo_pedido_sucesso"] = {
                "cliente_nome": nome.strip(), "destinatario_nome": st.session_state.get("input_dest_nome", "").strip(),
                "cesta_nome": cesta_obj['nome'], "adicionais_str": dados["adicionais"],
                "data_entrega": st.session_state.get("input_data_entrega").strftime("%d/%m/%Y"),
                "periodo_entrega": st.session_state.get("input_periodo_entrega", ""),
                "valor_total": f"R$ {formatar_moeda(total_estimado)}"
            }
            st.session_state["pedido_enviado_com_sucesso"] = True
            st.rerun()
        else:
            st.error("❌ Ocorreu um problema ao registrar o pedido. Tente novamente.")
