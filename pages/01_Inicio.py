import streamlit as st
import base64
import re
from pathlib import Path
import importlib
from io import BytesIO
from PIL import Image
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

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Formulário de Pedido | Doce Cesta",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# CACHING DE ALTA PERFORMANCE (Evita a tela piscar/travar)
# ==========================================================
@st.cache_data(ttl=300)
def obter_categorias_cacheadas():
    try:
        return supabase.table("categorias").select("*").execute().data or []
    except:
        return []

@st.cache_data(ttl=60)
def obter_cestas_cacheadas():
    try:
        cestas = supabase.table("cestas").select("*").eq("ativa", True).execute().data or []
        return sorted(cestas, key=lambda x: x.get("ordem", 999))
    except:
        return []

@st.cache_data(ttl=60)
def obter_configuracao_cesta_cacheada(cesta_id):
    try:
        return carregar_configuracao_cesta(cesta_id)
    except:
        return []

@st.cache_data(ttl=300)
def obter_produtos_por_categoria_cacheados(categoria_id):
    try:
        return listar_produtos_por_categoria_id(categoria_id)
    except:
        return []

@st.cache_data
def carregar_logo_base64():
    logo_path = Path("assets/logo.webp")
    if logo_path.exists():
        with open(logo_path, "rb") as img_file:
            encoded_logo = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/webp;base64,{encoded_logo}" class="header-logo" alt="Logo">'
    return "🎁"

# ==========================================================
# VALIDADOR DE CPF
# ==========================================================
def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11: return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    if (soma * 10 % 11) % 10 != int(cpf[9]): return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    if (soma * 10 % 11) % 10 != int(cpf[10]): return False
    return True

# ==========================================================
# CSS PREMIUM E RESPONSIVO
# ==========================================================
st.markdown(
"""
<style>
/* Remoção de menus laterais */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { visibility: hidden !important; height: 0px !important; }
footer { visibility: hidden !important; }

/* Espaçamento principal fluido */
.block-container { max-width: 720px !important; padding-top: 1rem !important; padding-bottom: 3rem !important; }
div[data-testid="stVerticalBlock"] { gap: 0.8rem !important; }

/* Fontes e Textos */
h2, h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-bottom: 10px !important; }
p, label, span { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 14px !important; }

/* Banner / Cabeçalho */
.header-banner { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 1.5rem; background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 20px; border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.04); }
.header-logo { width: 80px; height: auto; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.05)); }
.header-text { display: flex; flex-direction: column; justify-content: center; }
.header-title { font-size: 26px !important; font-weight: 800 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; }
.header-subtitle { font-size: 13px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 4px !important; }

/* Containers (Cards de Formulário) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 16px !important;
    padding: 20px 24px !important; margin-bottom: 12px !important; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.03); transition: all 0.2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:focus-within { border-color: #cbab92 !important; box-shadow: 0 6px 18px rgba(197, 114, 31, 0.08); }

.secao-titulo { font-size: 18px !important; font-weight: 800 !important; color: #5a3b28 !important; border-bottom: 1px solid #f3ece6; padding-bottom: 6px; margin-bottom: 12px !important; }

/* Checkboxes como Pílulas (Botões clicáveis) */
div[data-testid="stCheckbox"] { background: #faf7f3; border: 1px solid #e8ddd3; padding: 10px 14px; border-radius: 12px; margin-bottom: 6px; transition: all 0.2s ease; }
div[data-testid="stCheckbox"]:hover { background: #fdfcfb; border-color: #d2bfae; transform: translateX(2px); }

/* =========================================
   UPLOADER DROPZONE (CORRIGIDO PARA POLAROID)
========================================== */
div[data-testid="stFileUploader"] { width: 100% !important; }
div[data-testid="stFileUploader"] section { 
    background-color: #faf7f3 !important; border: 2px dashed #dfcdbb !important; 
    border-radius: 14px !important; padding: 16px !important; text-align: center !important; 
    transition: all 0.3s ease !important; 
}
div[data-testid="stFileUploader"] section:hover { border-color: #a87b57 !important; background-color: #fdfcfb !important; }

div[data-testid="stFileUploader"] section button { 
    background-color: #ffffff !important; border: 1px solid #dfcdbb !important; 
    color: #5a3b28 !important; font-weight: 800 !important; border-radius: 10px !important; 
    padding: 6px 16px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important; 
    transition: all 0.2s ease !important; 
}
div[data-testid="stFileUploader"] section button:hover { transform: scale(1.02); }

/* Esconde o texto nativo "Browse Files" do Streamlit e adiciona o nosso customizado */
div[data-testid="stFileUploader"] section button span { display: none !important; }
div[data-testid="stFileUploader"] section button::after { 
    content: "📷 Anexar Fotos" !important; 
    font-size: 14px !important; 
    font-weight: 800 !important; 
    display: block; 
}

/* =========================================
   RESUMO E BOTÃO DE ENVIO
========================================== */
.resumo-box { background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%); border: 1px solid #dfcdbb; border-radius: 14px; padding: 18px; text-align: left; }
.stButton button { background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important; color: white !important; border-radius: 14px !important; height: 54px !important; font-size: 16px !important; font-weight: 800 !important; border: none !important; box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3) !important; transition: all 0.3s ease !important; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px; }
.stButton button:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 20px rgba(46, 125, 50, 0.4) !important; }

/* Tela de Sucesso */
.sucesso-container { background: #f0f7f4; border: 2px solid #2e7d32; border-radius: 16px; padding: 30px; text-align: center; margin-top: 20px; box-shadow: 0 10px 30px rgba(46,125,50,0.1); }
.sucesso-titulo { font-size: 26px; font-weight: 800; color: #137333; margin-bottom: 10px; }
.sucesso-texto { font-size: 15px; color: #333; line-height: 1.6; margin-bottom: 20px; font-weight: 500; }

/* Estilização para imagens */
.stImage img { border-radius: 12px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

@media (max-width: 640px) {
    .block-container { padding: 1rem 0.6rem !important; }
    .header-banner { flex-direction: column; text-align: center; padding: 20px 16px; gap: 12px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 16px 14px !important; }
    .header-logo { width: 100px; }
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# CONTROLE DE ESTADO
# ==========================================================
if "pedido_enviado_com_sucesso" not in st.session_state: st.session_state["pedido_enviado_com_sucesso"] = False
if "ultimo_cep_buscado" not in st.session_state: st.session_state["ultimo_cep_buscado"] = ""
if "cesta_selecionada_id" not in st.session_state: st.session_state["cesta_selecionada_id"] = None
if "fotos_polaroid_cliente" not in st.session_state: st.session_state["fotos_polaroid_cliente"] = []


# ==========================================================
# TELA DE SUCESSO
# ==========================================================
if st.session_state["pedido_enviado_com_sucesso"]:
    dados = st.session_state.get("resumo_pedido_sucesso", {})
    
    st.markdown(f'<div class="header-banner">{carregar_logo_base64()}<div class="header-text"><h1 class="header-title">Doce Cesta Brasília</h1><p class="header-subtitle">Pedido Registrado! 💝</p></div></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="sucesso-container">
        <div class="sucesso-titulo">✅ Seu pedido foi recebido!</div>
        <div class="sucesso-texto">
            Muito obrigado, <b>{dados.get('cliente_nome')}</b>! Recebemos o seu pedido com muito carinho. <br>
            Nossa equipe vai analisar e entrar em contato com você pelo WhatsApp em instantes para enviar o link de pagamento e confirmar o valor do frete.
        </div>
        <div class="resumo-box">
            <span style="font-size: 16px; font-weight: 800; color: #5a3b28;">📋 Resumo do Pedido:</span><br><br>
            💝 <b>Para:</b> {dados.get('destinatario_nome', '-')}<br>
            🎁 <b>Cesta:</b> {dados.get('cesta_nome')}<br>
            🎀 <b>Complementos:</b> {dados.get('adicionais_str') if dados.get('adicionais_str') else 'Nenhum'}<br>
            📅 <b>Data:</b> {dados.get('data_entrega')} ({dados.get('periodo_entrega')})<br>
            📍 <b>Endereço:</b> {dados.get('endereco')}<br>
            <hr style="border: 0; border-top: 1px dashed #dfcdbb; margin: 12px 0;">
            💰 <b>Total Estimado (sem frete):</b> <span style="color: #2e7d32; font-size: 18px; font-weight: 800;">{dados.get('valor_total')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("🎁 Fazer Novo Pedido", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("input_") or key in ["pedido_enviado_com_sucesso", "cesta_selecionada_id", "fotos_polaroid_cliente", "ultimo_cep_buscado"]:
                del st.session_state[key]
        st.rerun()
    st.stop()


# ==========================================================
# CABEÇALHO DO FORMULÁRIO DE COMPRA
# ==========================================================
st.markdown(f'<div class="header-banner">{carregar_logo_base64()}<div class="header-text"><h1 class="header-title">Doce Cesta Brasília</h1><p class="header-subtitle">Monte sua cesta perfeita 💝</p></div></div>', unsafe_allow_html=True)


# ==========================================================
# 1. DADOS DO COMPRADOR
# ==========================================================
with st.container(border=True):
    st.markdown('<div class="secao-titulo">👤 Seus Dados (Comprador)</div>', unsafe_allow_html=True)
    st.caption("Preencha com os dados de quem está realizando o pagamento.")
    nome = st.text_input("Nome completo *", placeholder="Ex: João da Silva", key="input_nome_comprador")
    
    col_ddi, col_tel, col_cpf = st.columns([1.2, 2.5, 2.5])
    with col_ddi:
        st.selectbox("País (DDI) *", ["🇧🇷 +55", "🇺🇸 +1", "🇵🇹 +351", "🇪🇸 +34", "🇮🇹 +39", "🇫🇷 +33"], key="input_ddi_comprador")
    with col_tel:
        st.text_input("WhatsApp *", placeholder="(61) 99999-9999", key="input_tel_comprador")
    with col_cpf:
        st.text_input("Seu CPF *", placeholder="Apenas números", max_chars=14, key="input_cpf_comprador")


# ==========================================================
# 2. SELEÇÃO DA CESTA E PERSONALIZAÇÃO
# ==========================================================
cestas = obter_cestas_cacheadas()
cesta_obj = None
selecoes_cliente = {}

if cestas:
    opcoes_cestas = [{"id": None, "nome": "Selecione o modelo da cesta..."}] + cestas
    
    # Sincroniza escolha que veio da página inicial
    if st.session_state.get("cesta_selecionada_home"):
        st.session_state["cesta_selecionada_id"] = st.session_state["cesta_selecionada_home"]
        st.session_state["cesta_selecionada_home"] = None

    cesta_inicial_index = 0
    current_id = st.session_state.get("cesta_selecionada_id")
    if current_id:
        for idx, item in enumerate(opcoes_cestas):
            if item.get("id") == current_id:
                cesta_inicial_index = idx
                break

    with st.container(border=True):
        st.markdown('<div class="secao-titulo">🎁 Escolha sua Cesta</div>', unsafe_allow_html=True)
        
        cesta_selecionada = st.selectbox(
            "Modelo Desejado", 
            opcoes_cestas, 
            format_func=lambda c: c["nome"], 
            index=cesta_inicial_index,
            label_visibility="collapsed"
        )

        if cesta_selecionada and cesta_selecionada.get("id"):
            cesta_obj = cesta_selecionada
            st.session_state["cesta_selecionada_id"] = cesta_selecionada.get("id")
            
            # Mostra imagem e preço dinâmico sem precisar de st.rerun
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                if cesta_obj.get("imagem"):
                    st.image(cesta_obj["imagem"], use_container_width=True)
            with col_txt:
                if cesta_obj.get("descricao"): st.caption(cesta_obj["descricao"])
                valor = float(cesta_obj.get("preco", 0))
                st.markdown(f"**Valor da cesta:** <span style='font-size:18px; color:#137333; font-weight:800;'>R$ {valor:,.2f}</span>".replace(",", "X").replace(".", ",").replace("X","."), unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px dashed #dfcdbb;'>", unsafe_allow_html=True)
            st.markdown('<div style="font-size: 15px; font-weight: 800; color: #5a3b28; margin-bottom: 10px;">🍓 Personalize os Itens</div>', unsafe_allow_html=True)
            
            configuracao = obter_configuracao_cesta_cacheada(cesta_obj["id"])
            if configuracao:
                for grupo in configuracao:
                    cat = grupo.get("categoria", "Categoria")
                    prods = grupo.get("produtos", [])
                    maximo = grupo.get("max_escolhas", 1)
                    minimo = grupo.get("min_escolhas", 0)

                    if not prods: continue
                    
                    st.markdown(f"<div style='font-size: 13px; font-weight: 700; color: #775a46; margin-bottom: 4px; margin-top: 10px;'>📦 {cat}</div>", unsafe_allow_html=True)
                    if maximo == 1:
                        escolhido = st.radio(f"Escolha 1", prods, format_func=lambda p: p["nome"], key=f"rad_{cesta_obj['id']}_{cat}", label_visibility="collapsed")
                        if escolhido: selecoes_cliente[cat] = [escolhido]
                    else:
                        escolhidos = st.multiselect(f"Escolha até {maximo}", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"mul_{cesta_obj['id']}_{cat}")
                        selecoes_cliente[cat] = escolhidos
            else:
                st.info("Esta cesta possui itens padronizados e não requer personalização.")
else:
    st.error("O catálogo está vazio no momento.")


# ==========================================================
# 3. COMPLEMENTOS E FOTOS
# ==========================================================
adicionais_selecionados = []
polaroid = False

categorias = obter_categorias_cacheadas()
cat_adicionais = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)

if cat_adicionais:
    produtos_adicionais = obter_produtos_por_categoria_cacheados(cat_adicionais["id"])
    if produtos_adicionais:
        with st.container(border=True):
            st.markdown('<div class="secao-titulo">🎀 Adicionar Complementos</div>', unsafe_allow_html=True)
            st.caption("Deixe o presente ainda mais inesquecível com itens extras.")
            
            colunas = st.columns(2)
            for indice, prod in enumerate(produtos_adicionais):
                preco = prod.get("preco")
                txt_val = f"R$ {float(preco):,.2f}".replace(",", "X").replace(".", ",").replace("X",".") if preco else "Consulta"
                
                with colunas[indice % 2]:
                    if st.checkbox(f"{prod['nome']} | {txt_val}", key=f"add_{prod['id']}"):
                        adicionais_selecionados.append({
                            "produto_id": prod["id"], "nome": prod["nome"], 
                            "preco": float(preco) if preco else None, "categoria": "Adicionais"
                        })
                        if prod["nome"].lower().strip() == "polaroid": polaroid = True

if polaroid:
    with st.container(border=True):
        st.markdown('<div class="secao-titulo">📷 Envie suas Fotos (Polaroid)</div>', unsafe_allow_html=True)
        st.caption("Você selecionou o item Polaroid. Envie até 2 fotos para revelação.")
        
        # Uploader sem causar st.rerun manual. O Streamlit gerencia os arquivos na sessão automaticamente.
        fotos_upload = st.file_uploader("Upload", type=["jpg", "jpeg", "png", "webp", "heic"], accept_multiple_files=True, key="fotos_polaroid_cliente", label_visibility="collapsed")
        
        if fotos_upload:
            if len(fotos_upload) > 2:
                st.error("⚠️ Você enviou mais de 2 fotos. Por favor, remova algumas na lixeirinha acima.")
            else:
                st.success(f"✅ {len(fotos_upload)} foto(s) anexada(s) com sucesso!")


# ==========================================================
# 4. VIACEP E DADOS DE ENTREGA INTELIGENTES
# ==========================================================
with st.container(border=True):
    st.markdown('<div class="secao-titulo">📍 Endereço de Entrega</div>', unsafe_allow_html=True)
    
    # O PULO DO GATO DO VIACEP SEM TRAVAR A TELA:
    # Verificamos o CEP ANTES de desenhar os Text Inputs da rua e bairro!
    cep_input = st.text_input("CEP (Opcional - Preenche Automático)", max_chars=8, placeholder="Somente números", key="input_cep")
    cep_limpo = re.sub(r'\D', '', cep_input)
    
    if len(cep_limpo) == 8 and st.session_state["ultimo_cep_buscado"] != cep_limpo:
        try:
            res = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
            if res.status_code == 200 and "erro" not in res.json():
                dados_cep = res.json()
                st.session_state["input_rua"] = dados_cep.get("logradouro", "")
                st.session_state["input_bairro"] = dados_cep.get("bairro", "")
                st.session_state["input_cidade"] = f"{dados_cep.get('localidade', '')} - {dados_cep.get('uf', '')}"
        except: pass
        st.session_state["ultimo_cep_buscado"] = cep_limpo
        # Removido o st.rerun()! O Streamlit aplica as chaves acima instantaneamente nos inputs abaixo.

    col_cid, col_bairro = st.columns([1.5, 1])
    with col_cid: st.text_input("Cidade - UF *", placeholder="Ex: Brasília - DF", key="input_cidade")
    with col_bairro: st.text_input("Bairro *", placeholder="Ex: Asa Sul", key="input_bairro")
    
    st.text_input("Rua / Logradouro *", placeholder="Ex: SQS 101 Bloco A", key="input_rua")
    st.text_input("Número / Complemento *", placeholder="Ex: Apto 202, Lote 5", key="input_numero")
    
    st.divider()
    st.markdown('<div style="font-size: 15px; font-weight: 800; color: #5a3b28; margin-bottom: 8px;">💝 O Destinatário</div>', unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.text_input("Nome do Homenageado *", placeholder="Quem receberá a cesta?", key="input_dest_nome")
    with col_d2: st.text_input("WhatsApp do Homenageado", placeholder="(Opcional)", key="input_dest_tel")
    
    st.text_area("💌 Mensagem do Cartão", height=90, placeholder="Escreva uma mensagem especial para ir impressa no cartão...", key="input_mensagem")
    st.text_input("Motivo da Homenagem", placeholder="Ex: Aniversário, Aniversário de Namoro...", key="input_motivo")
    
    st.divider()
    st.markdown('<div style="font-size: 15px; font-weight: 800; color: #5a3b28; margin-bottom: 8px;">📅 Agendamento</div>', unsafe_allow_html=True)
    col_ent1, col_ent2 = st.columns(2)
    with col_ent1: st.date_input("Data de entrega", format="DD/MM/YYYY", key="input_data_entrega")
    with col_ent2: st.selectbox("Período Ideal", ["Manhã", "Tarde", "Noite"], key="input_periodo_entrega")
    st.text_input("✨ Solicitação Especial (Opcional)", placeholder="Ex: Entregar exatamente às 09h00...", key="input_pedido_especial")


# ==========================================================
# 5. RESUMO, PAGAMENTO E ENVIO
# ==========================================================
with st.container(border=True):
    st.markdown('<div class="secao-titulo">💳 Fechamento</div>', unsafe_allow_html=True)
    pagamento = st.radio("Como deseja pagar?", ["Pix", "Cartão de Crédito"], horizontal=True, key="forma_pagamento_radio")

valor_base = float(cesta_obj.get("preco", 0)) if cesta_obj and cesta_obj.get("preco") is not None else 0
valor_adicionais = 0
tem_consulta = False

for item in adicionais_selecionados:
    if item["preco"] is None: tem_consulta = True
    else: valor_adicionais += float(item["preco"])

total_estimado = valor_base + valor_adicionais

if cesta_obj:
    with st.container(border=True):
        st.markdown('<div class="secao-titulo">💰 Resumo do Pedido</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="resumo-box">
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>🎁 Cesta Escolhida</span> <strong>R$ {valor_base:,.2f}</strong></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>🎀 Adicionais</span> <strong>R$ {valor_adicionais:,.2f}</strong></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>🚚 Taxa de Entrega</span> <strong>A calcular</strong></div>
            <hr style="border:0; border-top:1px dashed #dfcdbb; margin:10px 0;">
            <div style="display:flex; justify-content:space-between; font-size:16px;"><span><strong>TOTAL ESTIMADO</strong></span> <strong style="color:#137333;">R$ {total_estimado:,.2f}</strong></div>
        </div>
        """.replace(",", "X").replace(".", ",").replace("X","."), unsafe_allow_html=True)
        
        if tem_consulta:
            st.warning("⚠️ **Aviso:** Existem itens *Sob Consulta* no seu pacote. O valor final será atualizado pela nossa equipe.")

# ==========================================================
# PROCESSAMENTO DO BOTÃO DE ENVIO
# ==========================================================
st.write("")
enviar = st.button("🎁 CONFIRMAR E ENVIAR PEDIDO", use_container_width=True, type="primary")

if enviar:
    
    # 1. Coleta de Dados Pessoais
    nome = st.session_state.get("input_nome_comprador", "")
    cpf_bruto = st.session_state.get("input_cpf_comprador", "")
    tel_bruto = st.session_state.get("input_tel_comprador", "")
    ddi = re.sub(r'\D', '', st.session_state.get("input_ddi_comprador", "55"))
    
    if not nome.strip(): st.error("❌ Preencha o nome do comprador."); st.stop()
    if not tel_bruto.strip(): st.error("❌ Preencha o telefone do comprador."); st.stop()
    if not validar_cpf(cpf_bruto): st.error("❌ CPF inválido. Verifique os números digitados."); st.stop()
    
    cpf_limpo = re.sub(r'\D', '', cpf_bruto)
    tel_limpo = re.sub(r'\D', '', tel_bruto)
    telefone_oficial = f"{ddi}{tel_limpo}"

    # 2. Coleta da Cesta e Endereço
    if not cesta_obj: st.error("❌ Selecione o modelo da cesta."); st.stop()
    
    dest_nome = st.session_state.get("input_dest_nome", "")
    if not dest_nome.strip(): st.error("❌ Informe o nome de quem receberá a cesta."); st.stop()
    
    rua = st.session_state.get("input_rua", "")
    num = st.session_state.get("input_numero", "")
    if not rua.strip() or not num.strip(): st.error("❌ Informe a Rua e o Número de entrega."); st.stop()
    
    fotos_upload = st.session_state.get("fotos_polaroid_cliente", [])
    if polaroid and len(fotos_upload) > 2: st.error("❌ O limite para Polaroid é de 2 fotos."); st.stop()

    # 3. Formatação Final
    cep = st.session_state.get("input_cep", "")
    bairro = st.session_state.get("input_bairro", "")
    cidade = st.session_state.get("input_cidade", "")
    endereco_completo = f"{rua}, {num} - {bairro}, {cidade}" + (f" (CEP: {cep})" if cep else "")
    
    dt_ent = st.session_state.get("input_data_entrega")
    
    produtos_txt = [f"{c}: {i['nome']}" for c, itens in selecoes_cliente.items() for i in itens]
    adicionais_txt = [f"{i['nome']} (Consulta)" if i["preco"] is None else f"{i['nome']} (R$ {i['preco']:,.2f})".replace(".",",") for i in adicionais_selecionados]
    
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
        "adicionais": ", ".join(adicionais_txt),
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

    # 4. Salvar Banco de Dados
    with st.spinner("Registrando seu pedido seguro..."):
        try: sucesso, pedido_id = salvar_pedido(dados)
        except Exception as e: st.error(f"❌ Erro de conexão: {e}"); st.stop()
        
        if sucesso:
            if adicionais_selecionados: salvar_adicionais_pedido(pedido_id, adicionais_selecionados)
            if polaroid and fotos_upload:
                try: salvar_fotos(pedido_id, fotos_upload[:2])
                except Exception as e: print(f"Aviso foto: {e}")
                
            try:
                texto_aviso = f"🚨 <b>NOVO PEDIDO (SITE)!</b> 🚨\n\n👤 <b>Cliente:</b> {nome}\n📱 <b>Tel:</b> <a href='https://wa.me/{telefone_oficial}'>+{ddi} {tel_limpo}</a>\n🎁 <b>Cesta:</b> {cesta_obj['nome']}\n💝 <b>Para:</b> {dest_nome}\n📍 <b>Local:</b> {bairro}\n💰 <b>Estimativa:</b> R$ {total_estimado:,.2f}"
                enviar_notificacao_telegram(texto_aviso)
            except: pass 

            # Configura Tela de Sucesso
            st.session_state["resumo_pedido_sucesso"] = {
                "cliente_nome": nome.strip(),
                "destinatario_nome": dest_nome.strip(),
                "cesta_nome": cesta_obj["nome"],
                "adicionais_str": ", ".join(adicionais_txt),
                "data_entrega": dt_ent.strftime("%d/%m/%Y") if dt_ent else "",
                "periodo_entrega": st.session_state.get("input_periodo_entrega", ""),
                "endereco": endereco_completo,
                "valor_total": f"R$ {total_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
            }
            st.session_state["pedido_enviado_com_sucesso"] = True
            st.rerun()
        else:
            st.error("❌ Não foi possível registrar o pedido agora. Tente novamente.")

st.divider()
st.markdown('<div style="text-align:center; font-size:12px; color:#888; font-weight: 500;">Doce Cesta Brasília © 2026<br>Ambiente Seguro</div>', unsafe_allow_html=True)
st.page_link("app.py", label="Voltar para a Vitrine", icon="🛍️")
