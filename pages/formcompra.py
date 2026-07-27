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
# VALIDADOR MATEMÁTICO DE CPF
# ==========================================================
def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11: return False
    if cpf == cpf[0] * 11: return False
    
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    if digito1 != int(cpf[9]): return False
    
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    if digito2 != int(cpf[10]): return False
    
    return True

# ==========================================================
# BUSCA INTELIGENTE (CATEGORIAS E CESTAS)
# ==========================================================
def obter_categorias():
    try:
        cat_service = importlib.import_module("services.categoria_service")
        for nome_funcao in dir(cat_service):
            if "listar_categoria" in nome_funcao:
                return getattr(cat_service, nome_funcao)()
    except: pass 
    try: return supabase.table("categorias").select("*").execute().data or []
    except Exception: return []

def obter_cestas_seguro():
    """Garante que as cestas carreguem mesmo se o acesso for direto pela URL"""
    try:
        cestas = listar_cestas()
        if cestas: return cestas
    except: pass
    try: return supabase.table("cestas").select("*").eq("ativa", True).execute().data or []
    except Exception: return []

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA E CSS
# ==========================================================
st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(
"""
<style>
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { visibility: hidden !important; height: 0px !important; }
footer { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

.block-container {
    max-width: 680px !important;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

div[data-testid="stVerticalBlock"] { gap: 0.6rem !important; }

.header-banner {
    display: flex; align-items: center; justify-content: center;
    gap: 14px; margin-bottom: 12px; width: 100%;
}
.header-logo { width: 65px; height: auto; object-fit: contain; flex-shrink: 0; }
.header-text { display: flex; flex-direction: column; justify-content: center; text-align: left; }
.header-title { font-size: 24px !important; font-weight: 800 !important; color: #5a3b28 !important; margin: 0 !important; line-height: 1.15 !important; }
.header-subtitle { font-size: 13px !important; color: #775a46 !important; margin-top: 2px !important; margin-bottom: 0 !important; }

h2, h3 { font-size: 16px !important; font-weight: 700 !important; color: #5a3b28 !important; margin-top: 8px !important; margin-bottom: 6px !important; }
p, label, span, div { font-family: Arial, sans-serif !important; font-size: 13px !important; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 14px !important;
    padding: 14px 16px !important; margin-bottom: 8px !important; box-shadow: 0 2px 6px rgba(90, 59, 40, 0.03);
}

.secao-titulo { font-size: 15px !important; font-weight: 700 !important; color: #5a3b28 !important; margin-bottom: 8px !important; }

div[data-testid="stFileUploader"] { width: 100% !important; }
div[data-testid="stFileUploader"] section {
    background-color: #faf7f3 !important; border: 2px dashed #dfcdbb !important;
    border-radius: 12px !important; padding: 10px !important; text-align: center !important;
}
div[data-testid="stFileUploader"] section button { background-color: #ffffff !important; border: 1px solid #dfcdbb !important; color: #5a3b28 !important; font-weight: 600 !important; border-radius: 8px !important; }
div[data-testid="stFileUploader"] section button span { display: none !important; }
div[data-testid="stFileUploader"] section button::after { content: "📁 Selecionar Fotos (Máx. 2)" !important; font-size: 13px !important; font-weight: 600 !important; }

.sucesso-container { background: #f0f7f4; border: 2px solid #2e7d32; border-radius: 14px; padding: 24px; text-align: center; margin-top: 20px; }
.sucesso-titulo { font-size: 22px; font-weight: 800; color: #137333; margin-bottom: 8px; }
.sucesso-texto { font-size: 14px; color: #333; line-height: 1.5; margin-bottom: 16px; }
.resumo-box { background: #fff8ef; border: 1px solid #e6d1bb; border-radius: 10px; padding: 14px; text-align: left; margin-bottom: 16px; font-size: 13px; color: #444; }

.stButton button {
    background: #5a3b28 !important; color: white !important; border-radius: 12px !important;
    height: 48px !important; font-size: 16px !important; font-weight: 700 !important;
    border: none !important; box-shadow: 0 4px 10px rgba(90, 59, 40, 0.15) !important; transition: all 0.2s ease !important;
}
.stButton button:hover { background: #42291d !important; color: white !important; }
.imagem-cesta img { border-radius: 12px; object-fit: cover; max-width: 100%; }

@media (max-width: 640px) {
    .block-container { padding-top: 0.5rem !important; }
    .header-banner { gap: 12px; }
    .header-logo { width: 96px !important; }
    .header-title { font-size: 18px !important; }
    .header-subtitle { font-size: 11px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 10px 12px !important; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# CONTROLE DE ESTADO GLOBAL
# ==========================================================
if "pedido_enviado_com_sucesso" not in st.session_state: st.session_state["pedido_enviado_com_sucesso"] = False
if "resumo_pedido_sucesso" not in st.session_state: st.session_state["resumo_pedido_sucesso"] = {}
if "ultimo_cep_buscado" not in st.session_state: st.session_state["ultimo_cep_buscado"] = ""
if "cesta_selecionada_id" not in st.session_state: st.session_state["cesta_selecionada_id"] = None
if "fotos_polaroid_cliente" not in st.session_state: st.session_state["fotos_polaroid_cliente"] = []

# ==========================================================
# LOGO UNIFICADA
# ==========================================================
logo_path = Path("assets/logo.webp")
logo_html = ""
if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    logo_html = f'<img src="data:image/webp;base64,{encoded_logo}" class="header-logo" alt="Logo">'

# ==========================================================
# TELA DE SUCESSO BLINDADA (HTML SEM NENHUM ESPAÇO NO INÍCIO DA LINHA)
# ==========================================================
if st.session_state["pedido_enviado_com_sucesso"]:
    dados = st.session_state["resumo_pedido_sucesso"]
    
    html_banner = f"""
<div class="header-banner">
{logo_html}
<div class="header-text">
<h1 class="header-title">Doce Cesta Brasília</h1>
<p class="header-subtitle">Cestas personalizadas para momentos especiais 💝</p>
</div>
</div>
"""
    st.markdown(html_banner, unsafe_allow_html=True)
    
    html_sucesso = f"""
<div class="sucesso-container">
<div class="sucesso-titulo">✅ Pedido Realizado com Sucesso!</div>
<div class="sucesso-texto">
Muito obrigado, <b>{dados.get('cliente_nome')}</b>! Recebemos o seu pedido com muito carinho. 
Nossa equipe entrará em contato com você o mais rápido possível para confirmar os detalhes finais e o pagamento.
</div>
<div class="resumo-box">
<b>📋 Resumo do Pedido:</b><br><br>
💝 <b>Para (Homenageado):</b> {dados.get('destinatario_nome', '-')}<br>
🎁 <b>Cesta:</b> {dados.get('cesta_nome')}<br>
🛒 <b>Produtos/Personalização:</b><br>{dados.get('produtos').replace(chr(10), '<br>')}<br><br>
🎀 <b>Complementos:</b> {dados.get('adicionais_str') if dados.get('adicionais_str') else 'Nenhum'}<br>
🚚 <b>Frete:</b> A calcular<br>
📷 <b>Fotos Polaroid Enviadas:</b> {dados.get('qtd_fotos')} foto(s)<br>
📅 <b>Data da Entrega:</b> {dados.get('data_entrega')}<br>
🕘 <b>Turno da Entrega:</b> {dados.get('periodo_entrega')}<br>
📍 <b>Endereço:</b> {dados.get('endereco')}<br>
<div style="font-size: 12px; color: #b06000; background: #fef7e0; padding: 8px; border-radius: 6px; margin-top: 14px; margin-bottom: 10px; border-left: 4px solid #b06000;">
⚠️ <b>Aviso Importante:</b> Nossa equipe entrará em contato para informar o valor do frete, os produtos sob consulta (caso existam) e para verificar o horário exato da sua entrega.
</div>
<hr style="border: 0; border-top: 1px dashed #dfcdbb; margin: 10px 0;">
💰 <b>Valor Total Estimado (sem frete):</b> <span style="color: #2e7d32; font-size: 16px; font-weight: 800;">{dados.get('valor_total')}</span>
</div>
</div>
"""
    st.markdown(html_sucesso, unsafe_allow_html=True)

    st.write("")
    if st.button("🎁 Fazer Novo Pedido", use_container_width=True, type="primary"):
        st.session_state["pedido_enviado_com_sucesso"] = False
        st.session_state["resumo_pedido_sucesso"] = {}
        st.session_state["cesta_selecionada_id"] = None
        st.session_state["fotos_polaroid_cliente"] = []
        for key in ["input_cep", "input_rua", "input_numero", "input_bairro", "input_cidade"]:
            if key in st.session_state: del st.session_state[key]
        st.session_state["ultimo_cep_buscado"] = ""
        st.rerun()
    st.stop()


# ==========================================================
# CABEÇALHO DO FORMULÁRIO DE COMPRA
# ==========================================================
st.markdown(
    f"""
<div class="header-banner">
{logo_html}
<div class="header-text">
<h1 class="header-title">Doce Cesta Brasília</h1>
<p class="header-subtitle">Cestas personalizadas para momentos especiais 💝</p>
</div>
</div>
    """,
    unsafe_allow_html=True
)
st.write("")

# ==========================================================
# 1. DADOS DO COMPRADOR
# ==========================================================
with st.container(border=True):
    st.markdown('<div class="secao-titulo">👤 Seus Dados (Comprador)</div>', unsafe_allow_html=True)
    st.caption("Preencha com os dados de quem está realizando o pagamento.")
    nome = st.text_input("Nome completo *", placeholder="Seu nome completo", key="input_nome_comprador")
    col_ddi, col_tel, col_cpf = st.columns([1.2, 2, 2])
    with col_ddi:
        opcoes_ddi = [
            "🇧🇷 +55", "🇺🇸 +1", "🇵🇹 +351", "🇦🇷 +54", "🇬🇧 +44", 
            "🇪🇸 +34", "🇮🇹 +39", "🇫🇷 +33", "🇩🇪 +49", "🇨🇭 +41", 
            "🇦🇺 +61", "🇯🇵 +81", "🇨🇱 +56", "🇨🇴 +57", "🇺🇾 +598", 
            "🇵🇾 +595", "🇲🇽 +52", "🇨🇦 +1"
        ]
        st.selectbox("País (DDI) *", opcoes_ddi, index=0, key="input_ddi_comprador")
    with col_tel:
        st.text_input("Telefone (WhatsApp) *", placeholder="(61) 99999-9999", key="input_tel_comprador")
    with col_cpf:
        st.text_input("Seu CPF *", placeholder="Apenas números", max_chars=14, key="input_cpf_comprador")

# ==========================================================
# 2. SELEÇÃO DA CESTA
# ==========================================================
cestas_ativas = obter_cestas_seguro()
for c in cestas_ativas:
    if "ordem" not in c or c["ordem"] is None:
        c["ordem"] = 999
cestas = sorted(cestas_ativas, key=lambda x: x["ordem"])

cesta_obj = None
if cestas:
    opcoes_cestas = [{"id": None, "nome": "Selecione uma cesta..."}] + cestas
    
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
        
        def atualizar_cesta_selecionada():
            sel = st.session_state.get("selectbox_cesta_escolhida")
            if sel: st.session_state["cesta_selecionada_id"] = sel.get("id")

        cesta_selecionada = st.selectbox(
            "Selecione a cesta", 
            opcoes_cestas, 
            format_func=lambda c: c["nome"], 
            index=cesta_inicial_index,
            key="selectbox_cesta_escolhida",
            on_change=atualizar_cesta_selecionada
        )

        if cesta_selecionada and cesta_selecionada.get("id"):
            cesta_obj = cesta_selecionada
            st.session_state["cesta_selecionada_id"] = cesta_selecionada.get("id")
else:
    with st.container(border=True):
        st.warning("Nenhuma cesta cadastrada e ativa no momento.")

# ==========================================================
# INFORMAÇÕES VISUAIS DA CESTA
# ==========================================================
if cesta_obj:
    with st.container(border=True):
        col1, col2 = st.columns([1, 1.8])
        with col1:
            if cesta_obj.get("imagem"):
                st.markdown('<div class="imagem-cesta">', unsafe_allow_html=True)
                st.image(cesta_obj["imagem"], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            if cesta_obj.get("descricao"): st.info(cesta_obj["descricao"])
            if cesta_obj.get("preco") is not None:
                valor_cesta_formatado = f"R$ {float(cesta_obj['preco']):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                st.markdown(f"**🎁 Valor da cesta:** <span style='font-size:16px; color:#2e7d32; font-weight:bold;'>{valor_cesta_formatado}</span>", unsafe_allow_html=True)

# ==========================================================
# 3. PERSONALIZAÇÃO DA CESTA (COM PROTEÇÃO CONTRA TIMEOUT)
# ==========================================================
st.markdown("### 🍓 Personalize sua cesta")
selecoes_cliente = {}

if cesta_obj:
    configuracao_cesta = None
    try:
        configuracao_cesta = carregar_configuracao_cesta(cesta_obj["id"])
    except Exception:
        st.warning("⚠️ Ocorreu uma instabilidade na rede ao buscar as personalizações. Caso não apareçam opções abaixo, atualize a página.")
        
    if configuracao_cesta:
        for grupo in configuracao_cesta:
            categoria = grupo.get("categoria", "Sem categoria")
            produtos = grupo.get("produtos", [])
            minimo = grupo.get("min_escolhas", 0)
            maximo = grupo.get("max_escolhas", 1)

            if not produtos: continue
            with st.container(border=True):
                st.markdown(f"**📦 {categoria}**")
                if maximo == 1:
                    escolhido = st.radio("Escolha uma opção", produtos, format_func=lambda p: p["nome"], key=f"radio_{cesta_obj['id']}_{categoria}")
                    if escolhido: selecoes_cliente[categoria] = [escolhido]
                else:
                    escolhidos = st.multiselect(f"Escolha entre {minimo} e {maximo} opções", produtos, format_func=lambda p: p["nome"], max_selections=maximo, key=f"multi_{cesta_obj['id']}_{categoria}")
                    selecoes_cliente[categoria] = escolhidos
    else:
        st.info("Esta cesta ainda não possui produtos configurados para escolha.")
else:
    st.info("Escolha uma cesta acima para visualizar os itens de personalização disponíveis.")

# ==========================================================
# 4. COMPLEMENTOS E FOTOS POLAROID (COM PROTEÇÃO CONTRA TIMEOUT)
# ==========================================================
st.markdown("### 🎀 Complementos")
st.caption("Escolha itens adicionais para complementar sua cesta.")
adicionais_selecionados = []
polaroid = False

categorias_pedido = obter_categorias()
categoria_adicionais = next((c for c in categorias_pedido if c.get("nome", "").strip().lower() == "adicionais"), None)
categorias_exibir = [categoria_adicionais] if categoria_adicionais else []

for categoria_item in categorias_exibir:
    nome_categoria = categoria_item.get("nome", "")
    
    produtos_categoria = []
    try:
        produtos_categoria = listar_produtos_por_categoria_id(categoria_item["id"])
    except Exception:
        pass
        
    if not produtos_categoria: continue

    with st.container(border=True):
        st.markdown(f"**{nome_categoria}**")
        colunas = st.columns(2)
        for indice, produto in enumerate(produtos_categoria):
            with colunas[indice % 2]:
                preco = produto.get("preco")
                texto_valor = f"R$ {float(preco):,.2f}".replace(",", "X").replace(".", ",").replace("X",".") if preco is not None else "Sob consulta"
                
                # Checkbox normal fora de fragmento garante reatividade imediata no total
                if st.checkbox(f"{produto['nome']} | {texto_valor}", key=f"complemento_{produto['id']}"):
                    adicionais_selecionados.append({
                        "produto_id": produto["id"], 
                        "nome": produto["nome"], 
                        "preco": float(preco) if preco is not None else None, 
                        "categoria": nome_categoria
                    })
                    if produto["nome"].lower().strip() == "polaroid": polaroid = True

if polaroid:
    with st.container(border=True):
        st.markdown('<div class="secao-titulo">📷 Fotos da Polaroid (Até 2 fotos)</div>', unsafe_allow_html=True)
        st.caption("Envie até 2 imagens para revelação estilo Polaroid.")
        
        def processar_novo_upload():
            novos = st.session_state.get("uploader_polaroid_input", [])
            for arq in novos:
                if arq not in st.session_state["fotos_polaroid_cliente"] and len(st.session_state["fotos_polaroid_cliente"]) < 2:
                    st.session_state["fotos_polaroid_cliente"].append(arq)

        st.file_uploader(
            "Selecione as imagens", 
            type=["jpg", "jpeg", "png", "webp", "heic"], 
            accept_multiple_files=True, 
            key="uploader_polaroid_input",
            on_change=processar_novo_upload
        )

        if st.session_state["fotos_polaroid_cliente"]:
            st.markdown(f"**Fotos anexadas ({len(st.session_state['fotos_polaroid_cliente'])}/2):**")
            cols_preview = st.columns(2)
            remover_indice = None
            
            for i, arquivo_foto in enumerate(st.session_state["fotos_polaroid_cliente"]):
                with cols_preview[i % 2]:
                    try:
                        img_bytes = arquivo_foto.getvalue()
                        img_pil = Image.open(BytesIO(img_bytes))
                        st.image(img_pil, caption=f"Foto {i+1}", use_container_width=True)
                    except Exception:
                        st.image(arquivo_foto, caption=f"Foto {i+1}", use_container_width=True)
                    if st.button("🗑️ Remover Foto", key=f"btn_remover_idx_{i}", use_container_width=True):
                        remover_indice = i

            if remover_indice is not None:
                st.session_state["fotos_polaroid_cliente"].pop(remover_indice)
                st.rerun()
else:
    st.session_state["fotos_polaroid_cliente"] = []

fotos = st.session_state["fotos_polaroid_cliente"]

# ==========================================================
# 5. HOMENAGEADO E ENTREGA (VIACEP INTEGRADO)
# ==========================================================
st.markdown("### 💝 Homenageado e Entrega")

with st.container(border=True):
    st.markdown('<div class="secao-titulo">Destinatário</div>', unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.text_input("Nome do Homenageado *", placeholder="Quem receberá a cesta?", key="input_dest_nome")
    with col_d2: st.text_input("Telefone do Homenageado", placeholder="(Opcional)", key="input_dest_tel")
    st.text_input("Motivo da Homenagem", placeholder="Ex: Aniversário, Dia das Mães...", key="input_motivo")

with st.container(border=True):
    st.markdown('<div class="secao-titulo">💌 Mensagem do Cartão</div>', unsafe_allow_html=True)
    st.text_area("O que deseja escrever no cartão?", height=80, placeholder="Digite sua mensagem especial...", key="input_mensagem")

with st.container(border=True):
    st.markdown('<div class="secao-titulo">📍 Detalhes da Entrega</div>', unsafe_allow_html=True)
    
    col_cep, col_cid = st.columns([1, 1.5])
    with col_cep:
        cep_input = st.text_input("CEP (Opcional)", max_chars=8, placeholder="Somente números", key="input_cep")
    
    cep_limpo = re.sub(r'\D', '', cep_input)
    if len(cep_limpo) == 8 and st.session_state["ultimo_cep_buscado"] != cep_limpo:
        try:
            res = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
            if res.status_code == 200:
                dados_cep = res.json()
                if "erro" not in dados_cep:
                    st.session_state["input_rua"] = dados_cep.get("logradouro", "")
                    st.session_state["input_bairro"] = dados_cep.get("bairro", "")
                    st.session_state["input_cidade"] = f"{dados_cep.get('localidade', '')} - {dados_cep.get('uf', '')}"
        except: pass
        st.session_state["ultimo_cep_buscado"] = cep_limpo
        st.rerun() 
        
    with col_cid: st.text_input("Cidade - UF *", placeholder="Ex: Brasília - DF", key="input_cidade")
    st.text_input("Rua / Logradouro *", placeholder="Ex: SQS 101 Bloco A", key="input_rua")

    col_num, col_bairro = st.columns([1, 1])
    with col_num: st.text_input("Número / Complemento *", placeholder="Ex: Apto 202", key="input_numero")
    with col_bairro: st.text_input("Bairro *", placeholder="Ex: Asa Sul", key="input_bairro")

    st.divider()
    col_ent1, col_ent2 = st.columns(2)
    with col_ent1: st.date_input("📅 Data de entrega", format="DD/MM/YYYY", key="input_data_entrega")
    with col_ent2: st.selectbox("🕘 Período", ["Manhã", "Tarde", "Noite"], key="input_periodo_entrega")

    st.text_area("✨ Alguma solicitação especial?", height=70, placeholder="Exemplo: entregar preferencialmente até as 09:00...", key="input_pedido_especial")

# ==========================================================
# 6. PAGAMENTO E CÁLCULO DINÂMICO DE VALORES
# ==========================================================
with st.container(border=True):
    st.markdown('<div class="secao-titulo">💳 Forma de Pagamento</div>', unsafe_allow_html=True)
    pagamento = st.radio("Escolha como deseja pagar:", ["Pix", "Cartão de Crédito"], horizontal=True, key="forma_pagamento_radio")

# Cálculo total dinâmico
valor_base_cesta = float(cesta_obj.get("preco", 0)) if cesta_obj and cesta_obj.get("preco") is not None else 0
valor_adicionais_calculado = 0
tem_adicional_consulta = False

for item in adicionais_selecionados:
    if item["preco"] is None: 
        tem_adicional_consulta = True
    else:
        try: valor_adicionais_calculado += float(item["preco"])
        except: pass

valor_total_estimado = valor_base_cesta + valor_adicionais_calculado

if cesta_obj:
    with st.container(border=True):
        st.markdown('<div class="secao-titulo">💰 Resumo do Pedido</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: 
            st.caption("🎁 Valor da cesta")
            st.markdown(f"**R$ {valor_base_cesta:,.2f}**".replace(",", "X").replace(".", ",").replace("X","."))
        with col2: 
            st.caption("🎀 Complementos")
            st.markdown(f"**R$ {valor_adicionais_calculado:,.2f}**".replace(",", "X").replace(".", ",").replace("X","."))
        with col3:
            st.caption("🚚 Frete")
            st.markdown("**A calcular**")
        
        st.divider()
        val_total_fmt = f"R$ {valor_total_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
        st.success(f"💝 Valor estimado (sem frete): **{val_total_fmt}**")
        
        # Alerta reativo (Aparece instantaneamente se marcar um item sem preço configurado)
        if tem_adicional_consulta: 
            st.warning("⚠️ **Aviso:** Existem itens com valor *Sob consulta* no seu pedido. Nossa equipe informará o valor final pelo WhatsApp.")

# ==========================================================
# ENVIO DO PEDIDO
# ==========================================================
st.write("")
enviar = st.button("🎁 ENVIAR PEDIDO", use_container_width=True, type="primary")

if enviar:
    nome = st.session_state.get("input_nome_comprador", "")
    
    # Validação do CPF
    cpf_bruto = st.session_state.get("input_cpf_comprador", "")
    if not validar_cpf(cpf_bruto):
        st.error("⚠️ O CPF informado é inválido. Por favor, verifique os números digitados.")
        st.stop()
    cpf_limpo = re.sub(r'\D', '', cpf_bruto)
        
    ddi_bruto = st.session_state.get("input_ddi_comprador", "🇧🇷 +55")
    ddi_comprador = re.sub(r'\D', '', ddi_bruto)
    tel_comprador = re.sub(r'\D', '', st.session_state.get("input_tel_comprador", "")) 
    telefone_completo = f"{ddi_comprador}{tel_comprador}"
    
    dest_nome = st.session_state.get("input_dest_nome", "")
    dest_tel = re.sub(r'\D', '', st.session_state.get("input_dest_tel", "")) 
    motivo_homenagem = st.session_state.get("input_motivo", "")
    mensagem = st.session_state.get("input_mensagem", "")
    
    cep = st.session_state.get("input_cep", "")
    rua = st.session_state.get("input_rua", "")
    num = st.session_state.get("input_numero", "")
    bairro = st.session_state.get("input_bairro", "")
    cidade = st.session_state.get("input_cidade", "")
    
    cep_str = f" (CEP: {cep})" if cep.strip() else ""
    endereco_completo = f"{rua}, {num} - {bairro}, {cidade}{cep_str}"

    dt_ent = st.session_state.get("input_data_entrega")
    data_entrega_str = dt_ent.strftime("%Y-%m-%d") if dt_ent else str(date.today())
    data_entrega_br = dt_ent.strftime("%d/%m/%Y") if dt_ent else ""
    periodo_entrega = st.session_state.get("input_periodo_entrega", "")
    pedido_especial = st.session_state.get("input_pedido_especial", "")

    if not nome.strip(): st.error("Informe o nome do comprador."); st.stop()
    if not tel_comprador.strip(): st.error("Informe o telefone do comprador."); st.stop()
    if not cesta_obj: st.error("Selecione uma cesta."); st.stop()
    if not dest_nome.strip(): st.error("Informe o nome de quem vai receber (Homenageado)."); st.stop()
    if not rua.strip() or not num.strip(): st.error("Informe a Rua e o Número da entrega."); st.stop()
    if polaroid and fotos and len(fotos) > 2: st.error("⚠️ O limite para o Polaroid é de no máximo 2 fotos."); st.stop()

    produtos_escolhidos = [f"{cat_nome}: {item['nome']}" for cat_nome, itens in selecoes_cliente.items() for item in itens]
    complementos_texto = [f"{item['nome']} (Sob consulta)" if item["preco"] is None else f"{item['nome']} (R$ {item['preco']:,.2f})".replace(".", ",") for item in adicionais_selecionados]

    dados = {
        "cliente_nome": nome.strip(),
        "cliente_cpf": cpf_limpo,
        "cliente_telefone": telefone_completo,
        "destinatario_nome": dest_nome.strip(),
        "destinatario_telefone": dest_tel.strip(),
        "motivo_homenagem": motivo_homenagem.strip(),
        "cesta_id": cesta_obj["id"],
        "cesta_nome": cesta_obj["nome"],
        "produtos": "\n".join(produtos_escolhidos),
        "adicionais": ", ".join(complementos_texto),
        "pagamento": pagamento,
        "mensagem": mensagem,
        "pedido_especial": pedido_especial,
        "endereco": endereco_completo,
        "data_entrega": data_entrega_str,
        "periodo_entrega": periodo_entrega,
        "status": "Recebido",
        "valor_frete": 0,
        "valor_total": valor_total_estimado
    }

    try: sucesso, pedido_id = salvar_pedido(dados)
    except Exception as erro: st.error(f"Erro ao salvar pedido: {erro}"); st.stop()

    if sucesso:
        if adicionais_selecionados: salvar_adicionais_pedido(pedido_id, adicionais_selecionados)
        if polaroid and fotos:
            try: salvar_fotos(pedido_id, fotos[:2])
            except Exception as e: print(f"Erro ao enviar fotos polaroid: {e}")

        try:
            texto_aviso = f"""🚨 <b>NOVO PEDIDO RECEBIDO!</b> 🚨\n\n👤 <b>Comprador:</b> {nome}\n📱 <b>WhatsApp:</b> <a href="https://wa.me/{telefone_completo}">+{ddi_comprador} {tel_comprador}</a>\n🎁 <b>Cesta:</b> {cesta_obj["nome"]}\n💝 <b>Para:</b> {dest_nome}\n📍 <b>Local:</b> {bairro}\n💰 <b>Valor Estimado:</b> R$ {valor_total_estimado:,.2f}"""
            enviar_notificacao_telegram(texto_aviso)
        except: pass 

        st.session_state["resumo_pedido_sucesso"] = {
            "cliente_nome": nome.strip(),
            "destinatario_nome": dest_nome.strip(),
            "cesta_nome": cesta_obj["nome"],
            "produtos": "\n".join(produtos_escolhidos) if produtos_escolhidos else "Nenhuma personalização informada",
            "adicionais_str": ", ".join(complementos_texto),
            "qtd_fotos": len(fotos) if polaroid and fotos else 0,
            "data_entrega": data_entrega_br,
            "periodo_entrega": periodo_entrega,
            "endereco": endereco_completo,
            "valor_total": val_total_fmt
        }
        
        st.session_state["pedido_enviado_com_sucesso"] = True
        st.rerun()
    else:
        st.error(f"Erro ao salvar pedido: {pedido_id}")

st.divider()
st.markdown('<div style="text-align:center; font-size:12px; color:#888; padding:10px;">Doce Cesta Brasília © 2026</div>', unsafe_allow_html=True)
st.page_link("app.py", label="Voltar para a Vitrine", icon="🛍️")
