import streamlit as st
import base64
import re
from pathlib import Path
import importlib
from io import BytesIO
from PIL import Image
from datetime import date
import requests
import time
import uuid

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
    page_title="Finalizar Pedido | Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# CACHING DINÂMICO UNIFICADO (BLINDADO E OTIMIZADO)
# ==========================================================
@st.cache_data(ttl=600, show_spinner=False)
def obter_categorias_cacheadas():
    try:
        return supabase.table("categorias").select("*").execute().data or []
    except:
        return []

@st.cache_data(ttl=5, show_spinner=False)
def obter_secoes_e_cestas_ativas():
    try:
        res_secoes = supabase.table("vitrine_secoes").select("nome", "ativa").eq("ativa", True).order("ordem").execute()
        secoes_ativas = [s["nome"] for s in (res_secoes.data or [])]
        
        if not secoes_ativas:
            secoes_ativas = ["Cestas de Café"]
            
        cestas_todas = listar_cestas()
        cestas_ativas = [c for c in cestas_todas if c.get("ativa", True)]
        cestas_ativas = sorted(cestas_ativas, key=lambda x: x.get("ordem", 999))
        
        return secoes_ativas, cestas_ativas
    except Exception as e:
        print(f"Erro ao carregar catálogo: {e}")
        try:
            cestas = [c for c in listar_cestas() if c.get("ativa", True)]
            return ["Cestas de Café"], sorted(cestas, key=lambda x: x.get("ordem", 999))
        except:
            return ["Cestas de Café"], []

@st.cache_data(ttl=300, show_spinner=False)
def obter_configuracao_cesta_cacheada(cesta_id):
    try:
        return carregar_configuracao_cesta(cesta_id)
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def obter_produtos_por_categoria_cacheados(categoria_id):
    try:
        return listar_produtos_por_categoria_id(categoria_id)
    except:
        return []

@st.cache_data(show_spinner=False)
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
# CSS PREMIUM E UX DESIGN EXCLUSIVO
# ==========================================================
st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');

/* Ocultar elementos padrão do Streamlit */
section[data-testid="stSidebar"], [data-testid="collapsedControl"], header, footer, .stAppDeployMenu { display: none !important; }

/* Corpo Principal */
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }
.block-container { max-width: 850px !important; padding-top: 1.5rem !important; padding-bottom: 4rem !important; }

/* Banner / Cabeçalho Luxuoso */
.header-banner {
    display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 2rem;
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 22px 28px;
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
}
.header-logo { width: 90px; height: auto; object-fit: contain; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.05)); }
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px !important; font-weight: 700 !important; color: #c5721f !important; margin: 0 !important; line-height: 1.1 !important; }
.header-subtitle { font-size: 13.5px !important; color: #775a46 !important; font-weight: 600 !important; margin-top: 6px !important; letter-spacing: 0.5px; }

/* Stepper - Passos Guiados */
.step-container { display: flex; align-items: center; margin-bottom: 18px; border-bottom: 2px solid #f5eee6; padding-bottom: 10px; }
.step-number { background: linear-gradient(135deg, #c5721f 0%, #a65d14 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 15px; margin-right: 12px; box-shadow: 0 4px 10px rgba(197, 114, 31, 0.3); flex-shrink: 0; }
.step-title { font-size: 20px; font-weight: 800; color: #5a3b28; letter-spacing: -0.3px; margin: 0;}

/* Cards do Formulário */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important; border: 1px solid #e8ddd3 !important; border-radius: 22px !important;
    padding: 26px 30px !important; margin-bottom: 16px !important; box-shadow: 0 6px 20px rgba(90, 59, 40, 0.03);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #d2bfae !important; box-shadow: 0 10px 30px rgba(90, 59, 40, 0.06); }

/* Nome da Cesta em Destaque */
.destaque-cesta-nome-local {
    font-family: 'Dancing Script', cursive !important; font-size: 38px !important; font-weight: 700 !important;
    color: #c5721f !important; line-height: 1.1 !important; margin-bottom: 2px; text-shadow: 1px 1px 0px rgba(255,255,255,0.5);
}

/* Campos de Entrada Modernos */
input, textarea, select {
    border-radius: 12px !important; border: 1px solid #dfcdbb !important; background-color: #faf7f3 !important;
    font-family: 'Montserrat', sans-serif !important; font-size: 14px !important; color: #4a2e1b !important; padding: 12px !important;
}
input:focus, textarea:focus, select:focus {
    border-color: #c5721f !important; background-color: #ffffff !important; box-shadow: 0 0 0 3px rgba(197, 114, 31, 0.1) !important;
}

/* Checkboxes (Pílulas) */
div[data-testid="stCheckbox"] {
    background: #faf7f3; border: 1px solid #e8ddd3; padding: 12px 16px; border-radius: 14px;
    margin-bottom: 8px; transition: all 0.2s ease; display: flex; align-items: center;
}
div[data-testid="stCheckbox"]:hover { background: #fdfcfb; border-color: #c5721f; transform: translateY(-1px); }

/* Caixa de Resumo / Ticket */
.receipt-box {
    background: #ffffff;
    background-image: radial-gradient(#faf7f3 20%, transparent 20%), radial-gradient(#faf7f3 20%, transparent 20%);
    background-position: 0 0, 10px 10px;
    background-size: 20px 20px;
    border: 1px solid #e8ddd3; border-radius: 16px; padding: 25px; text-align: left;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05);
    position: relative; margin-top: 10px;
}
.receipt-box::before {
    content: ''; position: absolute; top: -10px; left: 0; right: 0; height: 10px;
    background: radial-gradient(circle, transparent, transparent 50%, #ffffff 50%, #ffffff 100%) 0 0 / 20px 20px repeat-x;
}
.receipt-line { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 14px; color: #5a3b28; }
.receipt-line strong { font-weight: 700; color: #2c1e14; }
.receipt-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: 800; color: #137333; margin-top: 15px; padding-top: 15px; border-top: 2px dashed #dfcdbb; }

/* Botão de Pagamento */
.stButton button {
    background: linear-gradient(135deg, #137333 0%, #0d4e22) !important; color: white !important;
    border-radius: 16px !important; height: 60px !important; font-size: 17px !important;
    font-weight: 800 !important; border: none !important; box-shadow: 0 8px 25px rgba(19, 115, 51, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px;
}
.stButton button:hover {
    transform: translateY(-3px) !important; box-shadow: 0 12px 30px rgba(19, 115, 51, 0.45) !important;
    background: linear-gradient(135deg, #0f5c28 0%, #093818) !important;
}

/* Imagens */
.stImage img { border-radius: 16px !important; box-shadow: 0 6px 15px rgba(0,0,0,0.08); border: 1px solid #e8ddd3; object-fit: cover;}

/* Tela de Sucesso */
.sucesso-container {
    background: linear-gradient(145deg, #f0f7f4 0%, #e6f4ed 100%); border: 2px solid #137333;
    border-radius: 24px; padding: 40px 30px; text-align: center; margin-top: 20px;
    box-shadow: 0 15px 40px rgba(19, 115, 51, 0.15); position: relative; overflow: hidden;
}
.sucesso-icone { font-size: 60px; margin-bottom: 10px; animation: bounce 2s infinite; }
@keyframes bounce { 0%, 20%, 50%, 80%, 100% {transform: translateY(0);} 40% {transform: translateY(-15px);} 60% {transform: translateY(-7px);} }
.sucesso-titulo { font-size: 32px; font-weight: 800; color: #137333; margin-bottom: 12px; font-family: 'Montserrat', sans-serif; letter-spacing: -0.5px;}
.sucesso-texto { font-size: 16px; color: #4a2e1b; line-height: 1.6; margin-bottom: 25px; font-weight: 500; }

/* Responsividade Mobile */
@media (max-width: 640px) {
    .block-container { padding: 0.8rem 0.5rem !important; }
    .header-banner { flex-direction: column; text-align: center; padding: 25px 16px; gap: 12px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 20px 16px !important; }
    .header-logo { width: 85px; }
    .header-title { font-size: 36px !important; }
    .step-title { font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# FUNÇÃO UI - RENDERIZAR CABEÇALHO DO PASSO
# ==========================================================
def renderizar_passo(numero, titulo):
    st.markdown(f"""
    <div class="step-container">
        <div class="step-number">{numero}</div>
        <h3 class="step-title">{titulo}</h3>
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# CONTROLE DE ESTADO E INICIALIZAÇÃO
# ==========================================================
if "pedido_enviado_com_sucesso" not in st.session_state: st.session_state["pedido_enviado_com_sucesso"] = False
if "ultimo_cep_buscado" not in st.session_state: st.session_state["ultimo_cep_buscado"] = ""
if "cesta_selecionada_id" not in st.session_state: st.session_state["cesta_selecionada_id"] = None
if "fotos_polaroid_cliente" not in st.session_state: st.session_state["fotos_polaroid_cliente"] = []

# ==========================================================
# TELA DE SUCESSO (DISPARA BALÕES 🎉)
# ==========================================================
if st.session_state["pedido_enviado_com_sucesso"]:
    st.balloons()
    
    dados = st.session_state.get("resumo_pedido_sucesso", {})
    st.markdown(f'<div class="header-banner">{carregar_logo_base64()}<div class="header-text"><h1 class="header-title">Doce Cesta Brasília</h1></div></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="sucesso-container">
        <div class="sucesso-icone">🎉</div>
        <div class="sucesso-titulo">Pedido Confirmado!</div>
        <div class="sucesso-texto">
            Que alegria, <b>{dados.get('cliente_nome')}</b>! Seu pedido foi reservado com muito carinho pela nossa equipe. <br><br>
            ⏳ <b>Próximo Passo:</b> Nossa equipe entrará em contato via WhatsApp em instantes para confirmar a taxa de entrega e enviar o link/chave de pagamento.
        </div>
        
        <div class="receipt-box" style="margin-top: 0; background-image: none; background: #ffffff;">
            <div style="font-size: 16px; font-weight: 800; color: #5a3b28; margin-bottom: 15px; border-bottom: 1px solid #e8ddd3; padding-bottom: 10px;">📋 Seu Ticket de Encomenda</div>
            <div class="receipt-line"><span>💝 <b>Para:</b></span> <span>{dados.get('destinatario_nome', '-')}</span></div>
            <div class="receipt-line"><span>🎁 <b>Presente:</b></span> <span style="text-align: right;">{dados.get('cesta_nome')}</span></div>
            <div class="receipt-line"><span>🎀 <b>Extras:</b></span> <span style="text-align: right;">{dados.get('adicionais_str') if dados.get('adicionais_str') else 'Nenhum'}</span></div>
            <div class="receipt-line"><span>📅 <b>Data:</b></span> <span>{dados.get('data_entrega')} ({dados.get('periodo_entrega')})</span></div>
            <div class="receipt-total"><span>TOTAL (sem frete)</span> <span>{dados.get('valor_total')}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("🎁 Fazer Novo Pedido", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("input_") or key in ["pedido_enviado_com_sucesso", "cesta_selecionada_id", "fotos_polaroid_cliente", "ultimo_cep_buscado", "secao_form", "cesta_selecionada_home"]:
                del st.session_state[key]
        st.rerun()
    st.stop()


# ==========================================================
# CABEÇALHO DO FORMULÁRIO DE COMPRA
# ==========================================================
st.markdown(f'<div class="header-banner">{carregar_logo_base64()}<div class="header-text"><h1 class="header-title">Doce Cesta Brasília</h1><p class="header-subtitle">Finalize sua encomenda em poucos passos 💝</p></div></div>', unsafe_allow_html=True)


# ==========================================================
# PASSO 1: DADOS DO COMPRADOR
# ==========================================================
with st.container(border=True):
    renderizar_passo("1", "Quem está presenteando?")
    st.caption("Precisamos dos seus dados para confirmar o pagamento e te enviar atualizações do pedido.")
    
    nome = st.text_input("Seu Nome Completo *", placeholder="Ex: Maria Clara Souza", key="input_nome_comprador")
    
    col_ddi, col_tel, col_cpf = st.columns([1.2, 2.5, 2.5])
    with col_ddi:
        st.selectbox("DDI *", ["🇧🇷 +55", "🇺🇸 +1", "🇵🇹 +351", "🇪🇸 +34", "🇮🇹 +39", "🇫🇷 +33"], key="input_ddi_comprador")
    with col_tel:
        st.text_input("Seu WhatsApp *", placeholder="(61) 99999-9999", key="input_tel_comprador")
    with col_cpf:
        st.text_input("Seu CPF *", placeholder="Apenas números", max_chars=14, key="input_cpf_comprador", help="Necessário para segurança e emissão de recibo.")


# ==========================================================
# PASSO 2: SELEÇÃO DO PRESENTE
# ==========================================================
with st.spinner():
    secoes_disponiveis, cestas_ativas = obter_secoes_e_cestas_ativas()

cesta_obj = None
selecoes_cliente = {}

if cestas_ativas and secoes_disponiveis:
    
    cesta_veio_da_home = st.session_state.get("cesta_selecionada_home")
    if cesta_veio_da_home:
        for c in cestas_ativas:
            if c["id"] == cesta_veio_da_home:
                st.session_state["secao_form"] = c.get("secao_vitrine") or "Cestas de Café"
                st.session_state["cesta_selecionada_id"] = cesta_veio_da_home
                break
        st.session_state["cesta_selecionada_home"] = None

    if "secao_form" not in st.session_state or st.session_state["secao_form"] not in secoes_disponiveis:
        st.session_state["secao_form"] = secoes_disponiveis[0]

    with st.container(border=True):
        renderizar_passo("2", "A Escolha do Presente")
        
        def ao_mudar_secao():
            st.session_state["cesta_selecionada_id"] = None

        if len(secoes_disponiveis) > 1:
            col_categoria, col_modelo = st.columns(2)
            
            with col_categoria:
                st.selectbox(
                    "💌 1. O que você deseja enviar?", 
                    secoes_disponiveis,
                    index=secoes_disponiveis.index(st.session_state["secao_form"]) if st.session_state["secao_form"] in secoes_disponiveis else 0,
                    key="secao_form",
                    on_change=ao_mudar_secao
                )

            cestas_da_secao = [
                c for c in cestas_ativas 
                if (c.get("secao_vitrine") or "Cestas de Café").strip().lower() == str(st.session_state["secao_form"]).strip().lower()
            ]
            opcoes_cestas = [{"id": None, "nome": "Clique para selecionar o modelo..."}] + cestas_da_secao
            
            cesta_idx = 0
            if st.session_state.get("cesta_selecionada_id"):
                for i, c in enumerate(opcoes_cestas):
                    if c["id"] == st.session_state["cesta_selecionada_id"]:
                        cesta_idx = i; break

            with col_modelo:
                cesta_selecionada = st.selectbox(
                    "💝 2. Escolha o modelo", 
                    opcoes_cestas, 
                    format_func=lambda c: c["nome"], 
                    index=cesta_idx
                )
        else:
            st.session_state["secao_form"] = secoes_disponiveis[0]
            
            cestas_da_secao = [
                c for c in cestas_ativas 
                if (c.get("secao_vitrine") or "Cestas de Café").strip().lower() == str(st.session_state["secao_form"]).strip().lower()
            ]
            opcoes_cestas = [{"id": None, "nome": "Clique para selecionar o modelo..."}] + cestas_da_secao
            
            cesta_idx = 0
            if st.session_state.get("cesta_selecionada_id"):
                for i, c in enumerate(opcoes_cestas):
                    if c["id"] == st.session_state["cesta_selecionada_id"]:
                        cesta_idx = i; break

            cesta_selecionada = st.selectbox(
                "💝 Escolha o modelo do presente", 
                opcoes_cestas, 
                format_func=lambda c: c["nome"], 
                index=cesta_idx
            )

        # ==================================================
        # NOVO LAYOUT DO PRODUTO (IMAGEM + PREÇO À ESQUERDA)
        # ==================================================
        if cesta_selecionada and cesta_selecionada.get("id"):
            cesta_obj = cesta_selecionada
            st.session_state["cesta_selecionada_id"] = cesta_selecionada.get("id")

            st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 20px 0;'>", unsafe_allow_html=True)
            
            col_img, col_txt = st.columns([1.2, 1.8], gap="large")
            
            with col_img:
                if cesta_obj.get("imagem"):
                    st.image(cesta_obj["imagem"], use_container_width=True)
                
                valor_base_num = float(cesta_obj.get("preco", 0))
                valor_base_txt = f"R$ {valor_base_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                # PREÇO EMBAIXO DA IMAGEM PARA BALANCEAR O LAYOUT
                st.markdown(f"""
                <div style="margin-top: 15px; background: linear-gradient(145deg, #ffffff 0%, #fdfbf8 100%); border: 2px solid #e8ddd3; border-radius: 16px; padding: 15px 10px; text-align: center; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05);">
                    <div style="font-size: 11px; font-weight: 800; color: #a65d14; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px;">Valor do Presente</div>
                    <div style="font-size: 28px; color: #137333; font-weight: 800; line-height: 1;">{valor_base_txt}</div>
                </div>
                """, unsafe_allow_html=True)
                    
            with col_txt:
                sec_txt = cesta_obj.get("secao_vitrine") or "Cestas de Café"
                st.markdown(f'<div class="destaque-cesta-nome-local" style="margin-top: -5px;">{cesta_obj.get("nome", "")}</div>', unsafe_allow_html=True)
                st.markdown(f"<div style='color: #8c7362; font-size:13px; font-weight: 600; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;'>Coleção: {sec_txt}</div>", unsafe_allow_html=True)
                
                # DESCRIÇÃO LIMPA E ALINHADA NA DIREITA
                if cesta_obj.get("descricao"):
                    st.markdown(f"""
                    <div style="background: #ffffff; padding: 20px; border-radius: 16px; font-size: 14.5px; color: #4a2e1b; line-height: 1.6; border: 1px solid #f5eee6; box-shadow: inset 0 2px 8px rgba(0,0,0,0.01);">
                        <div style="color: #c5721f; font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 16px;">✨</span> O que compõe esta cesta?
                        </div>
                        <div style="text-align: justify; text-justify: inter-word; color: #6b5343;">
                            {cesta_obj.get('descricao')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # PERSONALIZAÇÃO DA CESTA (SABORES/BEBIDAS)
            configuracao = obter_configuracao_cesta_cacheada(cesta_obj["id"])
            if configuracao and any(grp.get("produtos") for grp in configuracao):
                st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 20px 0;'>", unsafe_allow_html=True)
                st.markdown('<div style="font-size: 16px; font-weight: 800; color: #5a3b28; margin-bottom: 15px;">🍓 Personalize os Itens da Cesta</div>', unsafe_allow_html=True)
                
                for grupo in configuracao:
                    cat = grupo.get("categoria", "Categoria")
                    prods = grupo.get("produtos", [])
                    maximo = grupo.get("max_escolhas", 1)

                    if not prods: continue
                    
                    st.markdown(f"<div style='font-size: 14px; font-weight: 700; color: #775a46; margin-bottom: 6px; margin-top: 10px;'>📦 {cat}</div>", unsafe_allow_html=True)
                    if maximo == 1:
                        escolhido = st.radio(f"Escolha 1 opção", prods, format_func=lambda p: p["nome"], key=f"rad_{cesta_obj['id']}_{cat}", label_visibility="collapsed")
                        if escolhido: selecoes_cliente[cat] = [escolhido]
                    else:
                        escolhidos = st.multiselect(f"Escolha até {maximo} opções", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"mul_{cesta_obj['id']}_{cat}")
                        selecoes_cliente[cat] = escolhidos
else:
    st.error("O catálogo está vazio no momento.")


# ==========================================================
# PASSO 3: COMPLEMENTOS E FOTOS (SE HOUVER)
# ==========================================================
adicionais_selecionados = []
polaroid = False

categorias = obter_categorias_cacheadas()
cat_adicionais = next((c for c in categorias if c.get("nome", "").strip().lower() == "adicionais"), None)

if cat_adicionais:
    produtos_adicionais = obter_produtos_por_categoria_cacheados(cat_adicionais["id"])
    if produtos_adicionais:
        with st.container(border=True):
            renderizar_passo("3", "Adicionar Mimos Extras")
            st.caption("Deixe o presente ainda mais surpreendente com itens exclusivos.")
            
            colunas = st.columns(2)
            for indice, prod in enumerate(produtos_adicionais):
                preco_add = prod.get("preco")
                txt_val_add = f"+ R$ {float(preco_add):,.2f}".replace(",", "X").replace(".", ",").replace("X",".") if preco_add is not None else "Sob Consulta"
                
                with colunas[indice % 2]:
                    if st.checkbox(f"✨ {prod['nome']} **{txt_val_add}**", key=f"add_{prod['id']}"):
                        adicionais_selecionados.append({
                            "produto_id": prod["id"], "nome": prod["nome"], 
                            "preco": float(preco_add) if preco_add is not None else None, "categoria": "Adicionais"
                        })
                        if prod["nome"].lower().strip() == "polaroid" or "foto" in prod["nome"].lower().strip(): polaroid = True

if polaroid:
    with st.container(border=True):
        st.markdown('<div style="font-size: 18px; font-weight: 800; color: #d1476a; margin-bottom: 5px;">📷 Envie suas Fotos (Polaroid)</div>', unsafe_allow_html=True)
        st.caption("Você selecionou as fotos Polaroid. Envie até 2 imagens para revelarmos.")
        fotos_upload = st.file_uploader("Toque para anexar do seu celular/PC", type=["jpg", "jpeg", "png", "webp", "heic"], accept_multiple_files=True, key="fotos_polaroid_cliente", label_visibility="collapsed")
        
        if fotos_upload:
            if len(fotos_upload) > 2:
                st.error("⚠️ Limite excedido: Por favor, mantenha apenas 2 fotos anexadas.")
            else:
                st.success(f"✅ {len(fotos_upload)} foto(s) anexada(s) prontas para impressão!")


# ==========================================================
# PASSO 4: O HOMENAGEADO E A MENSAGEM
# ==========================================================
with st.container(border=True):
    renderizar_passo("4", "Para Quem é o Presente?")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.text_input("Nome de quem vai receber *", placeholder="Ex: Ana Clara", key="input_dest_nome")
    with col_d2: st.text_input("WhatsApp do destinatário", placeholder="(Opcional)", key="input_dest_tel", help="Caso o entregador precise ligar na hora.")
    
    st.text_input("Qual a Ocasião? (Opcional)", placeholder="Ex: Aniversário, Dia das Mães, Pedido de Desculpas...", key="input_motivo")
    st.text_area("💌 Cartão de Presente", height=100, placeholder="Escreva aqui a mensagem especial que iremos imprimir e colocar junto ao presente...", key="input_mensagem")


# ==========================================================
# PASSO 5: LOCAL E DATA DE ENTREGA
# ==========================================================
with st.container(border=True):
    renderizar_passo("5", "Local e Agendamento")
    
    cep_input = st.text_input("CEP da Entrega", max_chars=8, placeholder="Somente números (Preenche automático)", key="input_cep")
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

    col_cid, col_bairro = st.columns([1.5, 1])
    with col_cid: st.text_input("Cidade - UF *", placeholder="Ex: Brasília - DF", key="input_cidade")
    with col_bairro: st.text_input("Bairro *", placeholder="Ex: Asa Sul", key="input_bairro")
    
    col_rua, col_num = st.columns([2.5, 1])
    with col_rua: st.text_input("Rua / Logradouro *", placeholder="Ex: SQS 101 Bloco A", key="input_rua")
    with col_num: st.text_input("Nº / Apto *", placeholder="Ex: Apto 202", key="input_numero")
    
    st.markdown("<hr style='border: none; border-top: 1px dashed #dfcdbb; margin: 15px 0;'>", unsafe_allow_html=True)
    
    col_ent1, col_ent2 = st.columns(2)
    with col_ent1: st.date_input("📅 Data da Entrega", format="DD/MM/YYYY", key="input_data_entrega")
    with col_ent2: st.selectbox("🕒 Período Desejado", ["Manhã", "Tarde", "Noite"], key="input_periodo_entrega")
    
    st.text_input("✨ Solicitação de Horário Especial (Opcional)", placeholder="Ex: Pode entregar exatamente às 07h00? (Sujeito a taxa)", key="input_pedido_especial")


# ==========================================================
# PASSO 6: RESUMO E FECHAMENTO
# ==========================================================
with st.container(border=True):
    renderizar_passo("6", "Pagamento e Resumo")
    
    pagamento = st.radio("Como você prefere pagar?", ["Pix (Aprovação Imediata)", "Cartão de Crédito"], horizontal=True, key="forma_pagamento_radio")

valor_base = float(cesta_obj.get("preco", 0)) if cesta_obj and cesta_obj.get("preco") is not None else 0
valor_adicionais = sum([float(item["preco"]) for item in adicionais_selecionados if item["preco"] is not None])
tem_consulta = any(item["preco"] is None for item in adicionais_selecionados)
total_estimado = valor_base + valor_adicionais

valor_base_fmt = f"R$ {valor_base:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
valor_adc_fmt = f"R$ {valor_adicionais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
total_fmt = f"R$ {total_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

if cesta_obj:
    with st.container(border=True):
        st.markdown(f"""
        <div class="receipt-box">
            <div style="font-size: 16px; font-weight: 800; color: #5a3b28; margin-bottom: 15px; text-align: center;">RESUMO DO PEDIDO</div>
            
            <div class="receipt-line"><span>🎁 <b>{cesta_obj['nome']}</b></span> <strong>{valor_base_fmt}</strong></div>
            <div class="receipt-line"><span>🎀 Mimos Extras</span> <strong>{valor_adc_fmt}</strong></div>
            <div class="receipt-line"><span>🚚 Taxa de Entrega</span> <strong>A calcular pelo WhatsApp</strong></div>
            
            <div class="receipt-total">
                <span>SUBTOTAL:</span> 
                <span>{total_fmt}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if tem_consulta:
            st.warning("⚠️ **Nota:** Você incluiu itens '*Sob Consulta*'. O valor exato será confirmado por nossa equipe.")

# ==========================================================
# PROCESSAMENTO FINAL (BOTÃO DE ENVIO)
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
    
    cpf_limpo = re.sub(r'\D', '', cpf_bruto)
    telefone_oficial = f"{ddi}{re.sub(r'\D', '', tel_bruto)}"

    if not cesta_obj: st.error("❌ Selecione uma opção de Cesta."); st.stop()
    
    dest_nome = st.session_state.get("input_dest_nome", "")
    if not dest_nome.strip(): st.error("❌ Informe o nome de quem vai receber o presente."); st.stop()
    
    rua = st.session_state.get("input_rua", "")
    num = st.session_state.get("input_numero", "")
    if not rua.strip() or not num.strip(): st.error("❌ Informe a Rua e o Número de entrega."); st.stop()
    
    fotos_upload = st.session_state.get("fotos_polaroid_cliente", [])
    if polaroid and len(fotos_upload) > 2: st.error("❌ O limite para Polaroid é de 2 fotos."); st.stop()

    # ==========================================================
    # UPLOAD DAS POLAROIDS NO SUPABASE BUCKET "pedido_fotos"
    # ==========================================================
    links_polaroid = []
    if polaroid and fotos_upload:
        with st.spinner("📦 Salvando suas fotos com segurança..."):
            for foto in fotos_upload[:2]:
                ext = foto.name.split('.')[-1]
                file_name = f"polaroid_{uuid.uuid4().hex}.{ext}"
                try:
                    supabase.storage.from_("pedido_fotos").upload(file_name, foto.read(), {"content-type": foto.type})
                    url = supabase.storage.from_("pedido_fotos").get_public_url(file_name)
                    links_polaroid.append(url)
                except Exception as e:
                    pass

    cep = st.session_state.get("input_cep", "")
    bairro = st.session_state.get("input_bairro", "")
    cidade = st.session_state.get("input_cidade", "")
    endereco_completo = f"{rua}, {num} - {bairro}, {cidade}" + (f" (CEP: {cep})" if cep else "")
    
    dt_ent = st.session_state.get("input_data_entrega")
    produtos_txt = [f"{c}: {i['nome']}" for c, itens in selecoes_cliente.items() for i in itens]
    adicionais_lista = [f"{i['nome']}" for i in adicionais_selecionados]
    
    texto_adicionais_bd = ", ".join(adicionais_lista) if adicionais_lista else "Nenhum"
    
    # Anexando os Links Públicos no pedido para facilitar acesso no painel!
    if links_polaroid:
        texto_adicionais_bd += "\n\n📸 LINKS FOTOS POLAROID:\n" + "\n".join(links_polaroid)
    
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
            
            try:
                texto_aviso = (
                    f"🚨 *NOVO PEDIDO RECEBIDO (SITE)!* 🚨\n\n"
                    f"📦 *ID:* `#{pedido_id}`\n"
                    f"👤 *Cliente:* {nome}\n"
                    f"📱 *Contato:* [{telefone_oficial}](https://wa.me/{telefone_oficial})\n"
                    f"🎁 *Cesta:* {cesta_obj['nome']}\n"
                    f"📍 *Bairro:* {bairro}\n"
                    f"💰 *Estimativa:* R$ {total_estimado:,.2f}\n\n"
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
                "valor_total": total_fmt
            }
            st.session_state["pedido_enviado_com_sucesso"] = True
            st.rerun()
        else:
            st.error("❌ Ocorreu um problema ao registrar o pedido. Tente novamente em instantes.")

st.divider()
st.markdown('<div style="text-align:center; font-size:12px; color:#888; font-weight: 500;">Doce Cesta Brasília © 2026<br>Transação 100% Segura 🔒</div>', unsafe_allow_html=True)
st.page_link("app.py", label="⬅️ Voltar para a Loja", icon="🛍️")
