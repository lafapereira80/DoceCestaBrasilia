import streamlit as st
import base64
from pathlib import Path
import importlib

from services.pedido_service import salvar_pedido
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.produto_service import listar_produtos_por_categoria_id
from services.pedido_adicional_service import salvar_adicionais_pedido
from services.telegram_service import enviar_notificacao_telegram
from services.foto_service import salvar_fotos
from config.supabase import supabase


# ==========================================================
# BUSCA INTELIGENTE DE CATEGORIAS
# ==========================================================
def obter_categorias():
    try:
        cat_service = importlib.import_module("services.categoria_service")
        for nome_funcao in dir(cat_service):
            if "listar_categoria" in nome_funcao:
                funcao_encontrada = getattr(cat_service, nome_funcao)
                return funcao_encontrada()
    except:
        pass 
        
    try:
        resposta = supabase.table("categorias").select("*").execute()
        return resposta.data or []
    except Exception as e:
        return []


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# CSS MODERNO E RESPONSIVO
# ==========================================================
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
""",
unsafe_allow_html=True
)


# ==========================================================
# CONTROLE DE ESTADO GLOBAL
# ==========================================================
if "pedido_enviado_com_sucesso" not in st.session_state:
    st.session_state["pedido_enviado_com_sucesso"] = False

if "resumo_pedido_sucesso" not in st.session_state:
    st.session_state["resumo_pedido_sucesso"] = {}

if "cesta_selecionada_id" not in st.session_state:
    st.session_state["cesta_selecionada_id"] = None


# ==========================================================
# LOGO E CABEÇALHO UNIFICADO
# ==========================================================
logo_path = Path("assets/logo.webp")
logo_html = ""
if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    logo_html = f'<img src="data:image/webp;base64,{encoded_logo}" class="header-logo" alt="Logo">'


# ==========================================================
# TELA DE SUCESSO (SUBSTITUI O FORMULÁRIO APÓS O ENVIO)
# ==========================================================
if st.session_state["pedido_enviado_com_sucesso"]:
    dados = st.session_state["resumo_pedido_sucesso"]
    
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
    
    st.markdown(
        f"""
        <div class="sucesso-container">
            <div class="sucesso-titulo">✅ Pedido Realizado com Sucesso!</div>
            <div class="sucesso-texto">
                Muito obrigado, <b>{dados.get('cliente_nome')}</b>! Recebemos o seu pedido com muito carinho. 
                Nossa equipe entrará em contato com você o mais rápido possível para confirmar os detalhes finais e o pagamento.
            </div>
            
            <div class="resumo-box">
                <b>📋 Resumo do Pedido:</b><br><br>
                🎁 <b>Cesta:</b> {dados.get('cesta_nome')}<br>
                🛒 <b>Produtos/Personalização:</b><br>{dados.get('produtos').replace(chr(10), '<br>')}<br><br>
                🎀 <b>Complementos:</b> {dados.get('adicionais_str') if dados.get('adicionais_str') else 'Nenhum'}<br>
                📷 <b>Fotos Polaroid Enviadas:</b> {dados.get('qtd_fotos')} foto(s)<br>
                📅 <b>Entrega:</b> {dados.get('data_entrega')} ({dados.get('periodo_entrega')})<br>
                📍 <b>Endereço:</b> {dados.get('endereco')}<br>
                <hr style="border: 0; border-top: 1px dashed #dfcdbb; margin: 10px 0;">
                💰 <b>Valor Total Estimado:</b> <span style="color: #2e7d32; font-size: 16px; font-weight: 800;">{dados.get('valor_total')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    if st.button("🎁 Fazer Novo Pedido", use_container_width=True, type="primary"):
        st.session_state["pedido_enviado_com_sucesso"] = False
        st.session_state["resumo_pedido_sucesso"] = {}
        st.session_state["cesta_selecionada_id"] = None
        st.rerun()

    st.stop()


# ==========================================================
# FORMULÁRIO DE COMPRA PRINCIPAL
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
# DADOS DO COMPRADOR
# ==========================================================
with st.container(border=True):
    st.markdown('<div class="secao-titulo">👤 Seus Dados (Comprador)</div>', unsafe_allow_html=True)
    st.caption("Preencha com os dados de quem está realizando o pagamento.")

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome completo *", placeholder="Seu nome completo")
    with col2:
        telefone = st.text_input("Seu Telefone *", placeholder="(61) 99999-9999")

    cpf = st.text_input("Seu CPF *", placeholder="000.000.000-00")


# ==========================================================
# SELEÇÃO DA CESTA (BLINDADA CONTRA "PISCA-PISCA")
# ==========================================================
@st.fragment
def renderizar_bloco_cestas():
    try:
        cestas_brutas = listar_cestas()
        cestas_ativas = [c for c in cestas_brutas if c.get("ativa", True)]
        for c in cestas_ativas:
            if "ordem" not in c or c["ordem"] is None:
                c["ordem"] = 999
        cestas = sorted(cestas_ativas, key=lambda x: x["ordem"])
    except:
        cestas = []

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
                if sel:
                    st.session_state["cesta_selecionada_id"] = sel.get("id")

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
            st.warning("Nenhuma cesta cadastrada.")

    return cesta_obj

cesta = renderizar_bloco_cestas()


# ==========================================================
# INFORMAÇÕES VISUAIS DA CESTA
# ==========================================================
if cesta:
    with st.container(border=True):
        col1, col2 = st.columns([1, 1.8])
        with col1:
            if cesta.get("imagem"):
                st.markdown('<div class="imagem-cesta">', unsafe_allow_html=True)
                st.image(cesta["imagem"], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Sem imagem.")
        with col2:
            if cesta.get("descricao"):
                st.info(cesta["descricao"])
            if cesta.get("preco") is not None:
                try:
                    valor = float(cesta["preco"])
                    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f"**🎁 Valor da cesta:** <span style='font-size:16px; color:#2e7d32; font-weight:bold;'>{valor_formatado}</span>", unsafe_allow_html=True)
                except:
                    pass


# ==========================================================
# PERSONALIZAÇÃO DA CESTA (FRAGMENTO ISOLADO)
# ==========================================================
@st.fragment
def renderizar_personalizacao(cesta_atual):
    st.markdown("### 🍓 Personalize sua cesta")
    selecoes_cliente = {}

    if cesta_atual:
        configuracao_cesta = carregar_configuracao_cesta(cesta_atual["id"])
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
                        escolhido = st.radio("Escolha uma opção", produtos, format_func=lambda p: p["nome"], key=f"radio_{cesta_atual['id']}_{categoria}")
                        if escolhido: selecoes_cliente[categoria] = [escolhido]
                    else:
                        escolhidos = st.multiselect(f"Escolha entre {minimo} e {maximo} opções", produtos, format_func=lambda p: p["nome"], max_selections=maximo, key=f"multi_{cesta_atual['id']}_{categoria}")
                        selecoes_cliente[categoria] = escolhidos
        else:
            st.info("Esta cesta ainda não possui produtos configurados.")
    else:
        st.info("Escolha uma cesta acima para visualizar os itens de personalização disponíveis.")
    
    return selecoes_cliente

selecoes_cliente = renderizar_personalizacao(cesta)


# ==========================================================
# COMPLEMENTOS E FOTOS POLAROID (FRAGMENTO ISOLADO)
# ==========================================================
@st.fragment
def renderizar_complementos_e_polaroid():
    st.markdown("### 🎀 Complementos")
    st.caption("Escolha itens adicionais para complementar sua cesta.")
    adicionais_selecionados = []
    polaroid = False

    try:
        categorias_pedido = obter_categorias()
    except:
        categorias_pedido = []

    categoria_adicionais = None
    for categoria_item in categorias_pedido:
        if categoria_item.get("nome", "").strip().lower() == "adicionais":
            categoria_adicionais = categoria_item
            break

    categorias_exibir = [categoria_adicionais] if categoria_adicionais else []

    for categoria_item in categorias_exibir:
        nome_categoria = categoria_item.get("nome", "")
        produtos_categoria = listar_produtos_por_categoria_id(categoria_item["id"])

        if not produtos_categoria: continue

        with st.container(border=True):
            st.markdown(f"**{nome_categoria}**")
            colunas = st.columns(2)

            for indice, produto in enumerate(produtos_categoria):
                coluna = colunas[indice % 2]
                with coluna:
                    preco = produto.get("preco")
                    texto_valor = f"R$ {float(preco):,.2f}".replace(",", "X").replace(".", ",").replace("X",".") if preco is not None else "Consultar valor"
                    marcado = st.checkbox(f"{produto['nome']} | {texto_valor}", key=f"complemento_{produto['id']}")

                    if marcado:
                        adicionais_selecionados.append({"produto_id": produto["id"], "nome": produto["nome"], "preco": produto.get("preco"), "categoria": nome_categoria})
                        if produto["nome"].lower().strip() == "polaroid":
                            polaroid = True

    fotos_up = []
    if polaroid:
        with st.container(border=True):
            st.markdown('<div class="secao-titulo">📷 Fotos da Polaroid (Até 2 fotos)</div>', unsafe_allow_html=True)
            st.caption("Envie até 2 imagens para revelação estilo Polaroid.")
            
            fotos_up = st.file_uploader(
                "Selecione as imagens", 
                type=["jpg", "jpeg", "png", "webp"], 
                accept_multiple_files=True, 
                key="upload_polaroid_cliente"
            )
            
            if fotos_up:
                if len(fotos_up) > 2:
                    st.error("⚠️ Você selecionou mais de 2 fotos. Por favor, mantenha no máximo 2 imagens.")
                else:
                    st.markdown(f"**Fotos anexadas ({len(fotos_up)}/2):**")
                    cols_preview = st.columns(2)
                    for i, arquivo_foto in enumerate(fotos_up):
                        with cols_preview[i % 2]:
                            st.image(arquivo_foto, caption=f"Foto {i+1}", use_container_width=True)

    return adicionais_selecionados, polaroid, fotos_up

adicionais_selecionados, polaroid, fotos = renderizar_complementos_e_polaroid()


# ==========================================================
# HOMENAGEADO E ENTREGA
# ==========================================================
st.markdown("### 💝 Homenageado e Entrega")

with st.container(border=True):
    st.markdown('<div class="secao-titulo">Destinatário</div>', unsafe_allow_html=True)
    col_dest1, col_dest2 = st.columns(2)
    with col_dest1:
        destinatario_nome = st.text_input("Nome do Homenageado *", placeholder="Quem receberá a cesta?")
    with col_dest2:
        destinatario_telefone = st.text_input("Telefone do Homenageado", placeholder="(Opcional)")
        
    motivo_homenagem = st.text_input("Motivo da Homenagem", placeholder="Ex: Aniversário, Dia das Mães, Agradecimento, Surpresa...")

with st.container(border=True):
    st.markdown('<div class="secao-titulo">💌 Mensagem do Cartão</div>', unsafe_allow_html=True)
    mensagem = st.text_area("O que deseja escrever no cartão?", height=80, placeholder="Digite sua mensagem especial...", key="mensagem_cliente")

with st.container(border=True):
    st.markdown('<div class="secao-titulo">📍 Detalhes da Entrega</div>', unsafe_allow_html=True)
    endereco = st.text_area("Endereço de entrega", height=80, placeholder="Informe o endereço completo (Rua, Número, Bairro, Ponto de Referência)...")

    col_ent1, col_ent2 = st.columns(2)
    with col_ent1:
        data_entrega = st.date_input("📅 Data de entrega", format="DD/MM/YYYY")
    with col_ent2:
        periodo_entrega = st.selectbox("🕘 Período", ["Manhã", "Tarde", "Noite"])

    pedido_especial = st.text_area("✨ Alguma solicitação especial?", height=70, placeholder="Exemplo: entregar preferencialmente até as 09:00...")


# ==========================================================
# PAGAMENTO
# ==========================================================
with st.container(border=True):
    st.markdown('<div class="secao-titulo">💳 Forma de Pagamento</div>', unsafe_allow_html=True)
    pagamento = st.radio("Escolha como deseja pagar:", ["Pix", "Cartão de Crédito"], horizontal=True, key="forma_pagamento")


# ==========================================================
# CÁLCULO DOS VALORES
# ==========================================================
valor_cesta = float(cesta.get("preco", 0)) if cesta and cesta.get("preco") is not None else 0
valor_adicionais = 0
tem_adicional_consulta = False

for item in adicionais_selecionados:
    if item["preco"] is None:
        tem_adicional_consulta = True
        continue
    try: valor_adicionais += float(item["preco"])
    except: pass

valor_estimado = valor_cesta + valor_adicionais


# ==========================================================
# RESUMO DO PEDIDO
# ==========================================================
if cesta:
    with st.container(border=True):
        st.markdown('<div class="secao-titulo">💰 Resumo do Pedido</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.caption("🎁 Valor da cesta")
            st.markdown(f"**R$ {valor_cesta:,.2f}**".replace(",", "X").replace(".", ",").replace("X","."))
        with col2:
            st.caption("🎀 Complementos")
            st.markdown(f"**R$ {valor_adicionais:,.2f}**".replace(",", "X").replace(".", ",").replace("X","."))

        st.divider()
        val_fmt = f"R$ {valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
        st.success(f"💝 Valor estimado: **{val_fmt}**")

        if tem_adicional_consulta:
            st.warning("⚠️ Existem itens com valor sob consulta. Nossa equipe confirmará o valor final.")


# ==========================================================
# BOTÃO ENVIO E PROCESSAMENTO
# ==========================================================
st.write("")
enviar = st.button("🎁 ENVIAR PEDIDO", use_container_width=True, type="primary", key="enviar_pedido")

if enviar:
    if not nome.strip(): st.error("Informe o nome do comprador."); st.stop()
    if not cpf.strip(): st.error("Informe o CPF do comprador."); st.stop()
    if not telefone.strip(): st.error("Informe o telefone do comprador."); st.stop()
    if not cesta: st.error("Selecione uma cesta."); st.stop()
    if not destinatario_nome.strip(): st.error("Informe o nome de quem vai receber (Homenageado)."); st.stop()
    if polaroid and len(fotos) > 2: st.error("⚠️ O limite para o Polaroid é de no máximo 2 fotos."); st.stop()

    produtos_escolhidos = [f"{cat_nome}: {item['nome']}" for cat_nome, itens in selecoes_cliente.items() for item in itens]
    complementos_texto = [f"{item['nome']} (Sob consulta)" if item["preco"] is None else item["nome"] for item in adicionais_selecionados]

    dados = {
        "cliente_nome": nome.strip(),
        "cliente_cpf": cpf.strip(),
        "cliente_telefone": telefone.strip(),
        "destinatario_nome": destinatario_nome.strip(),
        "destinatario_telefone": destinatario_telefone.strip(),
        "motivo_homenagem": motivo_homenagem.strip(),
        "cesta_id": cesta["id"],
        "cesta_nome": cesta["nome"],
        "produtos": "\n".join(produtos_escolhidos),
        "adicionais": ", ".join(complementos_texto),
        "pagamento": pagamento,
        "mensagem": mensagem,
        "pedido_especial": pedido_especial,
        "endereco": endereco,
        "data_entrega": data_entrega.strftime("%Y-%m-%d"),
        "periodo_entrega": periodo_entrega,
        "status": "Recebido",
        "valor_frete": 0,
        "valor_total": valor_estimado
    }

    try:
        sucesso, pedido_id = salvar_pedido(dados)
    except Exception as erro:
        st.error(f"Erro ao salvar pedido: {erro}"); st.stop()

    if sucesso:
        if adicionais_selecionados: 
            salvar_adicionais_pedido(pedido_id, adicionais_selecionados)
        
        if polaroid and fotos:
            try:
                salvar_fotos(pedido_id, fotos[:2])
            except Exception as e:
                print(f"Erro ao enviar fotos polaroid: {e}")

        try:
            telefone_limpo = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            texto_aviso = f"""🚨 <b>NOVO PEDIDO RECEBIDO!</b> 🚨

👤 <b>Comprador:</b> {nome}
📱 <b>WhatsApp:</b> <a href="https://wa.me/55{telefone_limpo}">{telefone}</a>
🎁 <b>Cesta:</b> {cesta["nome"]}
💝 <b>Para:</b> {destinatario_nome} ({motivo_homenagem if motivo_homenagem else "Sem motivo"})
💳 <b>Pagamento:</b> {pagamento}
💰 <b>Valor Estimado:</b> R$ {valor_estimado:,.2f}
📷 <b>Contém Fotos Polaroid:</b> {"Sim (" + str(len(fotos)) + " fotos)" if fotos else "Não"}

Abra o painel administrativo para ver os detalhes completos!
"""
            enviar_notificacao_telegram(texto_aviso)
        except:
            pass 

        st.session_state["resumo_pedido_sucesso"] = {
            "cliente_nome": nome.strip(),
            "cesta_nome": cesta["nome"],
            "produtos": "\n".join(produtos_escolhidos) if produtos_escolhidos else "Nenhuma personalização informada",
            "adicionais_str": ", ".join(complementos_texto),
            "qtd_fotos": len(fotos) if polaroid else 0,
            "data_entrega": data_entrega.strftime("%d/%m/%Y"),
            "periodo_entrega": periodo_entrega,
            "endereco": endereco,
            "valor_total": val_fmt
        }
        
        st.session_state["pedido_enviado_com_sucesso"] = True
        st.rerun()

    else:
        st.error(f"Erro ao salvar pedido: {pedido_id}")


# ==========================================================
# RODAPÉ
# ==========================================================
st.divider()
st.markdown('<div style="text-align:center; font-size:12px; color:#888; padding:10px;">Doce Cesta Brasília © 2026</div>', unsafe_allow_html=True)
st.page_link("app.py", label="Voltar para a Vitrine", icon="🛍️")
