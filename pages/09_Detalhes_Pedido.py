import streamlit as st
import json
import urllib.parse
from uuid import uuid4
import re
from datetime import time as dt_time, datetime

from services.pedido_service import buscar_pedido
from services.pedido_adicional_service import listar_adicionais_pedido
from config.supabase import supabase
from services.cesta_service import buscar_cesta, listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CACHING
# =====================================================
st.set_page_config(page_title="Ficha do Pedido", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()
usuario = st.session_state.usuario

@st.cache_data(ttl=60)
def obter_pedido_cacheado(pid):
    return buscar_pedido(pid)

@st.cache_data(ttl=120)
def obter_adicionais_cacheado(pid):
    try: return listar_adicionais_pedido(pid)
    except: return []

@st.cache_data(ttl=300)
def obter_cestas_cacheadas():
    try: return listar_cestas()
    except: return []

@st.cache_data(ttl=300)
def obter_cesta_cacheada(cesta_id):
    try: return buscar_cesta(cesta_id)
    except: return None

@st.cache_data(ttl=60)
def obter_fotos_cacheadas(pid):
    try:
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pid).order("created_at").execute()
        fotos = resposta.data or []
        url_base = st.secrets.get("SUPABASE_URL", "").rstrip("/")
        for foto in fotos:
            if not foto.get("url") and foto.get("arquivo"):
                foto["url"] = f"{url_base}/storage/v1/object/public/pedido_fotos/{foto['arquivo']}"
        return fotos
    except: return []

# =====================================================
# CSS PREMIUM E ESTILO DE ABAS MODERNAS
# =====================================================
st.markdown(
"""
<style>
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1250px; }
div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 0px !important; letter-spacing: -0.5px; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

div[data-testid="stVerticalBlockBorderWrapper"] { 
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 16px !important; 
    padding: 20px 24px !important; margin-bottom: 12px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.03); transition: all 0.25s ease; 
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #d2bfae !important; box-shadow: 0 8px 25px rgba(90, 59, 40, 0.06); }

.card-title { font-size: 16px !important; font-weight: 800 !important; color: #5a3b28 !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #f3ece6; padding-bottom: 6px; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.info-value { margin-bottom: 12px; color: #2c1e14; font-weight: 800; font-size: 14px !important; }

.resumo-container { background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%); border: 1px solid #e8ddd3; border-radius: 14px; padding: 18px; display: flex; flex-direction: column; gap: 8px; }
.resumo-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px !important; color: #444; padding: 4px 0; border-bottom: 1px dashed #e8ddd3; }
.resumo-row:last-child { border-bottom: none; padding-top: 10px; }
.resumo-label { font-weight: 600; color: #775a46; }
.resumo-val { font-weight: 800; color: #2c1e14; }
.resumo-total-val { font-size: 24px !important; font-weight: 800 !important; color: #137333 !important; }

.pgto-badge { background: #f3ece6; color: #5a3b28; padding: 3px 10px; border-radius: 8px; font-weight: 800; border: 1px solid #dfcdbb; font-size: 11px; text-transform: uppercase; }
.badge-montada { background-color: #e6f4ea; color: #137333; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 800; border: 1px solid #ceead6; margin-left: 10px; display: inline-block; text-transform: uppercase; letter-spacing: 0.5px; }

div[data-testid="stButton"] > button { border-radius: 10px !important; min-height: 42px !important; font-weight: 800 !important; font-size: 14px !important; transition: all 0.2s ease; }
div[data-testid="stButton"] > button:hover { transform: scale(1.02); }

div[data-testid="stLinkButton"] > a { width: 100% !important; border-radius: 10px !important; min-height: 42px !important; font-weight: 800 !important; font-size: 14px !important; display: flex !important; align-items: center !important; justify-content: center !important; background-color: #25D366 !important; color: white !important; border: none !important; transition: all 0.2s ease; }
div[data-testid="stLinkButton"] > a:hover { background-color: #128C7E !important; transform: scale(1.02); }

/* Customização de Abas */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0px 0px; font-weight: 800; color: #5a3b28; background-color: #faf7f3; border: 1px solid #e8ddd3; padding: 10px 20px; }
.stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #c5721f !important; border-bottom: 2px solid #c5721f !important; }

@media (max-width: 768px) { 
    .block-container { padding: 1rem 0.5rem !important; } 
    h1 { font-size: 24px !important; } 
}
</style>
""",
unsafe_allow_html=True
)

if "pedido_aberto" not in st.session_state:
    st.error("Nenhum pedido selecionado.")
    if st.button("⬅ Voltar"): st.switch_page("pages/02_Pedidos.py")
    st.stop()

pedido_id = st.session_state["pedido_aberto"]
pedido = obter_pedido_cacheado(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()


# =====================================================
# FUNÇÕES E LÓGICAS DE CONTROLE
# =====================================================
status_atual_pedido = str(pedido.get("status", "")).strip().capitalize()
perfil_usuario = usuario.get("perfil", "Operador")
e_administrador = (perfil_usuario == "Administrador")

pedido_arquivado = (status_atual_pedido == "Entregue")
bloquear_edicao = (status_atual_pedido == "Enviado") and not e_administrador

if "editar_pedido" not in st.session_state: st.session_state.editar_pedido = False
if pedido_arquivado or bloquear_edicao: st.session_state.editar_pedido = False

if pedido_arquivado:
    st.success("📦 **PEDIDO FINALIZADO (ARQUIVO)** - Esta ficha está disponível apenas para leitura do histórico.")
elif status_atual_pedido == "Enviado":
    st.info("🛵 **PEDIDO EM ROTA DE ENTREGA** - O status logístico e financeiro estão trancados até a conclusão.")

lista_bruta_adicionais = obter_adicionais_cacheado(pedido["id"])
adicionais_pedido = []
nomes_vistos = set()
for ad in lista_bruta_adicionais:
    nome_ad = ad.get("nome_produto")
    if nome_ad and nome_ad not in nomes_vistos:
        adicionais_pedido.append(ad)
        nomes_vistos.add(nome_ad)

# Gerenciamento de Extras Dinâmicos
if "lista_extras_dinamicos" not in st.session_state:
    itens_salvos = pedido.get("itens_consulta") or {}
    if isinstance(itens_salvos, str):
        try: itens_salvos = json.loads(itens_salvos)
        except: itens_salvos = {}
    
    lista_temp = []
    for nome, val in itens_salvos.items():
        if "Valor Manual de" not in nome and not nome.startswith("Valor de "):
            lista_temp.append({"nome": nome, "valor": float(val)})
    st.session_state["lista_extras_dinamicos"] = lista_temp

def atualizar_pedido(pid, dados):
    try: 
        supabase.table("pedidos").update(dados).eq("id", pid).execute()
        st.cache_data.clear()
        return True
    except: return False

def atualizar_anotacao_pedido(pid, anotacao):
    return atualizar_pedido(pid, {"anotacoes_internas": anotacao})

def salvar_fotos_local(pid, arquivos):
    if not arquivos: return True, ""
    if not isinstance(arquivos, list): arquivos = [arquivos]
    erros = []
    url_base = st.secrets.get("SUPABASE_URL", "").rstrip("/")
    for arquivo in arquivos:
        try:
            extensao = arquivo.name.split(".")[-1]
            nome_arquivo = f"{pid}/{uuid4()}.{extensao}"
            conteudo = arquivo.getvalue()
            supabase.storage.from_("pedido_fotos").upload(nome_arquivo, conteudo, {"content-type": arquivo.type})
            url_publica = f"{url_base}/storage/v1/object/public/pedido_fotos/{nome_arquivo}"
            supabase.table("pedido_fotos").insert({"pedido_id": pid, "arquivo": nome_arquivo, "nome_original": arquivo.name, "url": url_publica}).execute()
        except Exception as e:
            erros.append(f"Erro {arquivo.name}: {e}")
    st.cache_data.clear()
    if erros: return False, " | ".join(erros)
    return True, ""

def deletar_foto_local(foto_id, caminho_arquivo):
    try:
        if caminho_arquivo: supabase.storage.from_("pedido_fotos").remove([caminho_arquivo])
        supabase.table("pedido_fotos").delete().eq("id", foto_id).execute()
        st.cache_data.clear()
        return True, ""
    except Exception as e: return False, str(e)

def formatar_valor(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
    except: return "R$ 0,00"

def formatar_data(data):
    if not data: return "-"
    try: ano, mes, dia = str(data)[:10].split("-"); return f"{dia}/{mes}/{ano}"
    except: return str(data)

def gerar_whatsapp(pedido, adicionais, valor_final, frete_atual, extras_dinamicos_lista, desconto_atual, itens_consulta_catalogo):
    lista_adicionais = []
    
    for item in adicionais:
        nome = item.get("nome_produto", "-")
        valor = item.get("valor_unitario")
        if valor is not None: 
            lista_adicionais.append(f"• {nome} - {formatar_valor(valor)}")
        else:
            val_manual = itens_consulta_catalogo.get(nome, 0)
            if val_manual > 0:
                lista_adicionais.append(f"• {nome} - {formatar_valor(val_manual)}")
            else:
                lista_adicionais.append(f"• {nome} (sob consulta)")
    
    for extra in extras_dinamicos_lista:
        lista_adicionais.append(f"• {extra['nome']} - {formatar_valor(extra['valor'])}")

    texto_produtos = str(pedido.get('produtos','-'))
    texto_adicionais = '\n'.join(lista_adicionais) if lista_adicionais else "Nenhum"

    dest_nome = (pedido.get("destinatario_nome") or "").strip()
    dest_tel = (pedido.get("destinatario_telefone") or "").strip()
    motivo = (pedido.get("motivo_homenagem") or "").strip()
    texto_dest = ""
    if dest_nome or dest_tel or motivo:
        texto_dest = "💝 *Entrega Especial Para:*\n"
        if dest_nome: texto_dest += f"Nome: {dest_nome}\n"
        if dest_tel: texto_dest += f"Contato: {dest_tel}\n"
        if motivo: texto_dest += f"Motivo: {motivo}\n\n"
        
    texto_val = ""
    if float(frete_atual or 0) > 0: texto_val += f"🚚 Frete: {formatar_valor(frete_atual)}\n"
    if float(desconto_atual or 0) > 0: texto_val += f"🏷️ Desconto: - {formatar_valor(desconto_atual)}\n"

    texto = (
        f"🎁 *Doce Cesta Brasília*\n\n"
        f"Olá {pedido.get('cliente_nome','') if pedido else ''}!\n\n"
        f"{texto_dest}"
        f"🎀 *Cesta:* {pedido.get('cesta_nome','-')}\n\n"
        f"🛒 *Produtos da Cesta:*\n{texto_produtos}\n\n"
        f"🎀 *Adicionais / Extras:*\n{texto_adicionais}\n\n"
        f"📍 *Entrega:*\nData: {formatar_data(pedido.get('data_entrega'))}\n"
        f"Período: {pedido.get('periodo_entrega','-')}\n"
        f"Horário Fixo: {pedido.get('horario_combinado','-')}\n\n"
        f"💳 Pagamento: {pedido.get('pagamento','-')}\n\n"
        f"💰 *Resumo Financeiro*\n"
        f"{texto_val}"
        f"✅ *Valor Final: {formatar_valor(valor_final)}*\n\nObrigado! ❤️"
    )
    
    tel_limpo = re.sub(r'\D', '', str(pedido.get("cliente_telefone", "")))
    if len(tel_limpo) == 10 or len(tel_limpo) == 11: tel_wpp = f"55{tel_limpo}"
    else: tel_wpp = tel_limpo
        
    return f"https://wa.me/{tel_wpp}?text={urllib.parse.quote(texto)}"

def obter_icone_pagamento(metodo):
    m = str(metodo).strip().lower()
    if "pix" in m: return '<div class="pgto-badge" style="background: #e6f4ea; border-color: #137333; color: #137333;">⚡ PIX</div>'
    elif "cart" in m: return '<div class="pgto-badge" style="background: #e8f0fe; border-color: #1a73e8; color: #1a73e8;">💳 CARTÃO</div>'
    elif "dinheiro" in m: return '<div class="pgto-badge" style="background: #fef7e0; border-color: #b06000; color: #b06000;">💵 DINHEIRO</div>'
    elif "transfer" in m: return '<div class="pgto-badge" style="background: #f3ece6; border-color: #5a3b28; color: #5a3b28;">🏦 TRANSF.</div>'
    return f'<span class="pgto-badge">{metodo}</span>'


# =====================================================
# CABEÇALHO 
# =====================================================
col_t1, col_t2 = st.columns([3.5, 1.2])
with col_t1:
    st.title("📋 Ficha do Pedido")
    badge_montada = '<span class="badge-montada">✅ Cesta Montada</span>' if pedido.get("cesta_montada") else ''
    st.markdown(f"**ID #{pedido.get('id')}** | Status da Venda: **{pedido.get('status','-')}** {badge_montada}", unsafe_allow_html=True)
with col_t2:
    st.write("")
    if not pedido_arquivado and not bloquear_edicao:
        if st.button("✏️ Editar Detalhes do Pedido", use_container_width=True):
            st.session_state.editar_pedido = True
            st.rerun()


# =====================================================
# BLOCO DE EDIÇÃO AVANÇADA (MODO EDIÇÃO)
# =====================================================
if st.session_state.editar_pedido:
    st.write("")
    with st.container(border=True):
        st.markdown('<div class="card-title">✏️ Painel de Edição Completo</div>', unsafe_allow_html=True)
        aba_dados, aba_cesta, aba_adicionais = st.tabs(["👤 Dados Cadastrais", "🎁 Cesta e Produtos", "🎀 Adicionais do Catálogo"])

        with aba_dados:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                novo_nome = st.text_input("Comprador - Nome", value=pedido.get("cliente_nome") or "")
                novo_telefone = st.text_input("Comprador - Telefone", value=pedido.get("cliente_telefone") or "")
            with col_d2:
                novo_dest_nome = st.text_input("Homenageado - Nome", value=pedido.get("destinatario_nome") or "")
                novo_dest_tel = st.text_input("Homenageado - Telefone", value=pedido.get("destinatario_telefone") or "")
                novo_motivo = st.text_input("Motivo da Homenagem", value=pedido.get("motivo_homenagem") or "")

        with aba_cesta:
            cestas = obter_cestas_cacheadas()
            nomes_cestas = [c.get("nome", "") for c in cestas]
            cesta_atual = pedido.get("cesta_nome") or ""
            nova_cesta_nome = st.selectbox("🎁 Selecione a Cesta Base", nomes_cestas, index=nomes_cestas.index(cesta_atual) if cesta_atual in nomes_cestas else 0) if nomes_cestas else cesta_atual
            cesta_selecionada = next((c for c in cestas if c.get("nome") == nova_cesta_nome), None)
            novo_produtos = pedido.get("produtos") or ""
            
            if cesta_selecionada:
                config_cesta = carregar_configuracao_cesta(cesta_selecionada["id"])
                if config_cesta:
                    st.write("")
                    st.markdown("#### 🍓 Ajustar Itens da Cesta")
                    selecoes_admin = {}
                    txt_prod_atuais = pedido.get("produtos") or ""
                    for grupo in config_cesta:
                        cat = grupo.get("categoria", "Sem categoria")
                        prods = grupo.get("produtos", [])
                        maximo = grupo.get("max_escolhas", 1)
                        if not prods: continue
                        with st.container(border=True):
                            defaults = [p for p in prods if p["nome"] in txt_prod_atuais]
                            st.markdown(f"<div style='font-size: 14px; font-weight: 800; color: #5a3b28;'>📦 {cat}</div>", unsafe_allow_html=True)
                            if maximo == 1:
                                idx_def = prods.index(defaults[0]) if defaults else 0
                                escolhido = st.radio(f"Escolha 1", prods, format_func=lambda p: p["nome"], index=idx_def, key=f"edit_rad_{cat}", label_visibility="collapsed")
                                if escolhido: selecoes_admin[cat] = [escolhido]
                            else:
                                escolhidos = st.multiselect(f"Escolha até {maximo}", prods, format_func=lambda p: p["nome"], default=defaults, max_selections=maximo, key=f"edit_mult_{cat}")
                                selecoes_admin[cat] = escolhidos
                    novo_produtos = "\n".join([f"{c}: {i['nome']}" for c, itens in selecoes_admin.items() for i in itens])
                else: st.info("Esta cesta não possui produtos configurados.")
            
            st.divider()
            col_m1, col_m2 = st.columns(2)
            with col_m1: nova_mensagem = st.text_area("💌 Texto do Cartão", value=pedido.get("mensagem") or "", height=120)
            with col_m2: novo_endereco = st.text_area("📍 Endereço de Entrega Oficial", value=pedido.get("endereco") or "", height=120)
            novo_especial = st.text_input("✨ Solicitação Especial de Entrega", value=pedido.get("pedido_especial") or "")

        with aba_adicionais:
            st.markdown("<div style='font-size: 14px; font-weight: 800; color: #5a3b28; margin-bottom: 10px;'>🎀 Adicionar Extras Avulsos do Catálogo</div>", unsafe_allow_html=True)
            adicionais_catalogo = []
            try:
                cat_res = supabase.table("categorias").select("id, nome").execute()
                cat_add_id = next((c["id"] for c in (cat_res.data or []) if "adicionais" in str(c.get("nome", "")).lower()), None)
                if cat_add_id: adicionais_catalogo = supabase.table("produtos").select("*").eq("categoria_id", cat_add_id).execute().data or []
            except: pass
            
            nomes_atuais = [a.get("nome_produto") for a in adicionais_pedido]
            adicionais_selecionados = []
            if adicionais_catalogo:
                cols = st.columns(3)
                for i, prod in enumerate(adicionais_catalogo):
                    nome_prod = prod.get("nome", "")
                    preco_prod = prod.get("preco")
                    selec = nome_prod in nomes_atuais
                    txt = f"{nome_prod} - R$ {float(preco_prod):.2f}".replace(".",",") if preco_prod else f"{nome_prod} (Consulta)"
                    with cols[i % 3]:
                        if st.checkbox(txt, value=selec, key=f"chk_ad_{prod.get('id')}"):
                            adicionais_selecionados.append({"produto_id": prod.get("id"), "nome_produto": nome_prod, "valor_unitario": float(preco_prod) if preco_prod else None})
            else: st.caption("O catálogo de adicionais está vazio.")

        st.write("")
        st.divider()
        cs1, cs2 = st.columns(2)
        with cs1:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.editar_pedido = False
                st.rerun()
        with cs2:
            if st.button("💾 Salvar Informações", use_container_width=True, type="primary"):
                dados = {"cliente_nome": novo_nome, "cliente_telefone": novo_telefone, "destinatario_nome": novo_dest_nome, "destinatario_telefone": novo_dest_tel, "motivo_homenagem": novo_motivo, "cesta_nome": nova_cesta_nome, "produtos": novo_produtos, "mensagem": nova_mensagem, "pedido_especial": novo_especial, "endereco": novo_endereco}
                atualizar_pedido(pedido["id"], dados)
                if "erro_admin" in st.session_state: del st.session_state["erro_admin"]
                try:
                    try: supabase.table("pedido_adicionais").delete().eq("pedido_id", pedido["id"]).execute()
                    except Exception as err_del:
                        st.session_state["erro_admin"] = f"❌ Erro ao limpar itens antigos: {err_del}"
                        raise Exception("Falha")
                    if adicionais_selecionados:
                        for ad in adicionais_selecionados: ad["pedido_id"] = pedido["id"]
                        try: supabase.table("pedido_adicionais").insert(adicionais_selecionados).execute()
                        except Exception as err_ins:
                            st.session_state["erro_admin"] = f"❌ Erro ao salvar extras: {err_ins}"
                            raise Exception("Falha")
                except: pass 
                if "erro_admin" not in st.session_state: st.session_state.editar_pedido = False
                st.rerun()
        if "erro_admin" in st.session_state: st.error(st.session_state["erro_admin"])


# =====================================================
# LAYOUT PRINCIPAL (REMODELADO EM ABAS MODERNAS)
# =====================================================
else:
    st.write("")
    
    # -------------------------------------------------
    # ABAS PRINCIPAIS DE NAVEGAÇÃO DA FICHA
    # -------------------------------------------------
    aba_geral, aba_itens, aba_financeiro, aba_anexos = st.tabs([
        "📋 1. Visão Geral & Logística", 
        "🍓 2. Personalização & Extras", 
        "💰 3. Fechamento Financeiro", 
        "📷 4. Anotações & Polaroids"
    ])

    # =================================================
    # ABA 1: VISÃO GERAL & LOGÍSTICA
    # =================================================
    with aba_geral:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            with st.container(border=True):
                st.markdown('<div class="card-title">👤 Informações de Contato</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-label">Comprador</div><div class="info-value">{pedido.get("cliente_nome") or "-"} <span style="font-size:12px;color:#666;">(CPF: {pedido.get("cliente_cpf") or "-"})</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-value">📞 +{pedido.get("cliente_telefone") or "-"}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-label">Homenageado (Destinatário)</div><div class="info-value">{pedido.get("destinatario_nome") or "-"} (📞 {pedido.get("destinatario_telefone") or "Não inf."})</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-label">Motivo</div><div class="info-value">{pedido.get("motivo_homenagem") or "-"}</div>', unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown('<div class="card-title">💌 Cartão de Homenagem</div>', unsafe_allow_html=True)
                st.text_area("", value=pedido.get("mensagem") or "Sem mensagem informada.", disabled=True, height=85, label_visibility="collapsed")

        with col_g2:
            with st.container(border=True):
                st.markdown('<div class="card-title">🎁 Detalhes da Entrega e Pacote</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: 
                    st.markdown(f'<div class="info-label">Cesta Adquirida</div><div class="info-value">{pedido.get("cesta_nome","-")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-label">Data Limite</div><div class="info-value">{formatar_data(pedido.get("data_entrega"))}</div>', unsafe_allow_html=True)
                with c2: 
                    st.markdown(f'<div class="info-label">Forma de Pagto</div><div class="info-value">{obter_icone_pagamento(pedido.get("pagamento", "-"))}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-label">Período Ideal</div><div class="info-value">{pedido.get("periodo_entrega","-")}</div>', unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown('<div class="card-title">✨ Observações Especiais</div>', unsafe_allow_html=True)
                st.text_area("", value=pedido.get("pedido_especial") or "Nenhuma solicitação especial.", disabled=True, height=85, label_visibility="collapsed")

        with st.container(border=True):
            st.markdown('<div class="card-title">📍 Localização e Roteirização (GPS)</div>', unsafe_allow_html=True)
            endereco_pedido = pedido.get("endereco", "")
            st.text_area("", value=endereco_pedido if endereco_pedido else "O cliente não informou o endereço completo.", disabled=True, height=65, label_visibility="collapsed")
            if endereco_pedido:
                endereco_limpo_gps = re.sub(r'\(CEP:.*?\)', '', endereco_pedido).strip()
                endereco_encoded = urllib.parse.quote(endereco_limpo_gps)
                col_map1, col_map2 = st.columns(2)
                with col_map1: st.link_button("🗺️ Abrir no Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_encoded}", use_container_width=True)
                with col_map2: st.link_button("🚗 Abrir Rota no Waze", url=f"https://waze.com/ul?q={endereco_encoded}&navigate=yes", use_container_width=True)


    # =================================================
    # ABA 2: PERSONALIZAÇÃO & EXTRAS
    # =================================================
    with aba_itens:
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            with st.container(border=True):
                st.markdown('<div class="card-title">🛒 Checklist / Composição da Cesta</div>', unsafe_allow_html=True)
                produtos = pedido.get("produtos", "")
                if produtos:
                    for item in produtos.split("\n"): st.markdown(f"<div style='font-size:13px; margin-bottom:6px; font-weight:600;'>✅ {item.replace('•','').strip()}</div>", unsafe_allow_html=True)
                else: st.caption("Nenhum item configurado.")

        with col_i2:
            with st.container(border=True):
                st.markdown('<div class="card-title">🎀 Adicionais do Catálogo</div>', unsafe_allow_html=True)
                itens_consulta = {}
                if adicionais_pedido:
                    for idx_ad, adicional in enumerate(adicionais_pedido):
                        nome = adicional.get("nome_produto", "-")
                        valor = adicional.get("valor_unitario")
                        if valor is not None:
                            st.markdown(f"<div style='font-size:13px; margin-bottom:6px; font-weight:600;'>➕ {nome} - <span style='color:#137333;'>{formatar_valor(valor)}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='font-size:13px; margin-bottom:2px; font-weight:600;'>➕ {nome} <span style='color:#c5721f; font-size:11px;'>(Sob Consulta)</span></div>", unsafe_allow_html=True)
                            val_salvo = float(itens_consulta_salvos.get(nome, 0) or 0)
                            val_dig = st.number_input(f"Definir valor para {nome}", min_value=0.0, value=val_salvo, step=1.0, key=f"cons_{nome}_{idx_ad}", disabled=(bloquear_edicao or pedido_arquivado))
                            itens_consulta[nome] = val_dig
                else: st.caption("Nenhum adicional do catálogo solicitado.")


    # =================================================
    # ABA 3: FECHAMENTO FINANCEIRO
    # =================================================
    with aba_financeiro:
        valor_cesta = 0.0
        cesta = obter_cesta_cacheada(pedido.get("cesta_id"))
        if cesta: valor_cesta = float(cesta.get("preco", 0) or 0)

        # Leitura dos itens de consulta do catálogo caso existam salvos
        itens_consulta = {}
        for ad in adicionais_pedido:
            nome_ad = ad.get("nome_produto")
            if ad.get("valor_unitario") is None and nome_ad:
                val_salvo = float(itens_consulta_salvos.get(nome_ad, 0) or 0)
                itens_consulta[nome_ad] = st.session_state.get(f"cons_{nome_ad}_0", val_salvo)

        col_f1, col_f2 = st.columns([1.2, 1])

        with col_f1:
            with st.container(border=True):
                st.markdown('<div class="card-title">💰 Controles Financeiros e Logísticos</div>', unsafe_allow_html=True)
                travar_financeiro = (bloquear_edicao or pedido_arquivado)
                
                # Horário Fixo
                hora_banco = pedido.get("horario_combinado", "")
                try:
                    if hora_banco and ":" in hora_banco:
                        h, m = hora_banco.split(":")
                        hora_padrao = dt_time(int(h), int(m))
                    else: hora_padrao = dt_time(12, 0)
                except: hora_padrao = dt_time(12, 0)
                
                horario_obj = st.time_input("🕒 Horário Fixo Exato de Entrega", value=hora_padrao, disabled=travar_financeiro)
                horario_str_salvar = horario_obj.strftime("%H:%M")
                
                st.markdown("<hr style='margin:12px 0; border:none; border-top:1px dashed #dfcdbb;'>", unsafe_allow_html=True)
                
                # Valores Básicos
                cf1, cf2 = st.columns(2)
                with cf1: valor_frete = st.number_input("🚚 Frete (R$)", min_value=0.0, value=float(pedido.get("valor_frete") or 0), step=1.0, disabled=travar_financeiro)
                with cf2: desconto = st.number_input("🏷️ Desconto (R$)", min_value=0.0, value=float(pedido.get("desconto") or 0), step=1.0, disabled=travar_financeiro)
                
                st.write("")
                c_status1, c_status2 = st.columns(2)
                with c_status1:
                    status_atual = str(pedido.get("status", "Recebido")).strip().capitalize()
                    if e_administrador and not pedido_arquivado:
                        status_op = ["Recebido", "Pago", "Desistência"]
                        if status_atual not in status_op: status_op.append(status_atual)
                        status = st.selectbox("Status Financeiro", status_op, index=status_op.index(status_atual) if status_atual in status_op else 0, disabled=False)
                    else:
                        status = st.selectbox("Status Financeiro", [status_atual], index=0, disabled=True)
                
                with c_status2:
                    if status not in ["Recebido", "Desistência"]:
                        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
                        chk_montada = st.checkbox("🧺 Cesta Pronta", value=bool(pedido.get("cesta_montada")), disabled=travar_financeiro)
                    else:
                        chk_montada = False

        with col_f2:
            with st.container(border=True):
                st.markdown('<div class="card-title">➕ Extras Avulsos Dinâmicos</div>', unsafe_allow_html=True)
                
                col_add1, col_add2, col_add3 = st.columns([2, 1, 0.4])
                with col_add1: input_nome_extra = st.text_input("Nome", key="nome_extra_dinamico", disabled=travar_financeiro, placeholder="Ex: Urgência")
                with col_add2: input_val_extra = st.number_input("R$", min_value=0.0, step=1.0, key="val_extra_dinamico", disabled=travar_financeiro)
                with col_add3:
                    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
                    if st.button("➕", disabled=travar_financeiro, help="Adicionar"):
                        if input_nome_extra.strip():
                            st.session_state["lista_extras_dinamicos"].append({"nome": input_nome_extra.strip(), "valor": input_val_extra})
                            st.rerun()

                valor_extras_total = 0.0
                idx_remover = None
                if st.session_state["lista_extras_dinamicos"]:
                    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
                    for idx, extra in enumerate(st.session_state["lista_extras_dinamicos"]):
                        valor_extras_total += extra["valor"]
                        
                        c_n, c_v, c_b = st.columns([2, 1, 0.5])
                        with c_n: st.markdown(f"<div style='margin-top: 8px; font-size:12px; font-weight:600;'>{extra['nome']}</div>", unsafe_allow_html=True)
                        with c_v: st.markdown(f"<div style='margin-top: 8px; font-size:12px; font-weight:800; color:#137333;'>{formatar_valor(extra['valor'])}</div>", unsafe_allow_html=True)
                        with c_b:
                            if not travar_financeiro:
                                if st.button("🗑️", key=f"rm_ext_{idx}", help="Remover", use_container_width=True):
                                    idx_remover = idx
                        st.markdown("<hr style='margin: 2px 0 6px 0; border: none; border-bottom: 1px solid #f3ece6;'>", unsafe_allow_html=True)

                if idx_remover is not None:
                    st.session_state["lista_extras_dinamicos"].pop(idx_remover)
                    st.rerun()

            # Cálculo final e Recibo
            valor_adicionais_catalogo = 0.0
            valor_catalogo_consulta = 0.0
            for ad in adicionais_pedido:
                nome_ad = ad.get("nome_produto")
                val_ad = ad.get("valor_unitario")
                if val_ad is not None:
                    valor_adicionais_catalogo += float(val_ad)
                else:
                    val_input_manual = itens_consulta.get(nome_ad, 0.0)
                    valor_catalogo_consulta += float(val_input_manual)

            valor_total_calculado = max(0, valor_cesta + valor_adicionais_catalogo + valor_catalogo_consulta + valor_frete + valor_extras_total - desconto)

            with st.container(border=True):
                st.markdown('<div class="card-title">🧮 Extrato do Recibo</div>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="resumo-container">
                        <div class="resumo-row"><span class="resumo-label">🎁 Valor da Cesta</span><span class="resumo-val">{formatar_valor(valor_cesta)}</span></div>
                        <div class="resumo-row"><span class="resumo-label">🎀 Adicionais (Catálogo)</span><span class="resumo-val">{formatar_valor(valor_adicionais_catalogo + valor_catalogo_consulta)}</span></div>
                        <div class="resumo-row"><span class="resumo-label">🚚 Taxa de Entrega</span><span class="resumo-val">{formatar_valor(valor_frete)}</span></div>
                        <div class="resumo-row"><span class="resumo-label">➕ Extras Dinâmicos</span><span class="resumo-val">{formatar_valor(valor_extras_total)}</span></div>
                        <div class="resumo-row"><span class="resumo-label">🏷️ Desconto</span><span class="resumo-val" style="color: #c5221f;">- {formatar_valor(desconto)}</span></div>
                        <div class="resumo-row"><span class="resumo-label" style="font-size:15px; font-weight:800; color:#2c1e14;">💰 VALOR FINAL</span><span class="resumo-total-val">{formatar_valor(valor_total_calculado)}</span></div>
                    </div>
                    """, unsafe_allow_html=True
                )


    # =================================================
    # ABA 4: ANOTAÇÕES & POLAROIDS
    # =================================================
    with aba_anexos:
        col_an1, col_an2 = st.columns(2)
        
        with col_an1:
            with st.container(border=True):
                st.markdown('<div class="card-title">📝 Anotações Internas da Equipe</div>', unsafe_allow_html=True)
                anotacao = st.text_area("", value=pedido.get("anotacoes_internas") or "", height=140, key="campo_anotacao", disabled=pedido_arquivado, label_visibility="collapsed")
                if not pedido_arquivado:
                    if st.button("💾 Gravar Anotação Interna", use_container_width=True):
                        atualizar_anotacao_pedido(pedido["id"], anotacao)
                        st.session_state['msg_geral'] = "✅ Anotação interna salva com sucesso!"
                        st.rerun()

        with col_an2:
            with st.container(border=True):
                st.markdown('<div class="card-title">📷 Fotos Polaroid & Anexos</div>', unsafe_allow_html=True)
                if "msg_foto" in st.session_state:
                    if "❌" in st.session_state['msg_foto']: st.error(st.session_state['msg_foto'])
                    else: st.success(st.session_state['msg_foto'])
                    del st.session_state['msg_foto']
                
                if not pedido_arquivado:
                    novas_fotos = st.file_uploader("Enviar arquivos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="up_fotos_multi", label_visibility="collapsed")
                    if novas_fotos:
                        if st.button("📤 Enviar Fotos para a Nuvem", use_container_width=True, type="primary"):
                            with st.spinner("Processando imagens..."):
                                sucesso, erro_msg = salvar_fotos_local(pedido["id"], novas_fotos)
                            if sucesso: st.session_state['msg_foto'] = "✅ Arquivos salvos!"
                            else: st.session_state['msg_foto'] = f"❌ Erro: {erro_msg}"
                            st.rerun()
                    st.divider()
                    
                fotos = obter_fotos_cacheadas(pedido["id"])
                if fotos:
                    colunas = st.columns(2)
                    for i, foto in enumerate(fotos):
                        with colunas[i % 2]:
                            link_imagem = foto.get("url")
                            if link_imagem:
                                st.image(link_imagem, caption=foto.get("nome_original", "Foto"), use_container_width=True)
                                if not pedido_arquivado:
                                    if st.button("🗑️ Deletar", key=f"del_foto_{foto['id']}", use_container_width=True):
                                        suc, err_del = deletar_foto_local(foto["id"], foto.get("arquivo"))
                                        if suc: st.session_state['msg_foto'] = "✅ Foto apagada!"
                                        else: st.session_state['msg_foto'] = f"❌ Erro: {err_del}"
                                        st.rerun()
                        else: st.caption("⚠️ Link quebrado.")
                else: st.caption("Nenhum anexo ou Polaroid neste pedido.")

    # =====================================================
    # BOTÕES PRINCIPAIS E WHATSAPP (RODAPÉ FIXO)
    # =====================================================
    if "msg_geral" in st.session_state:
        st.toast(st.session_state['msg_geral'])
        del st.session_state['msg_geral']

    st.write("")
    st.divider()
    col_bot1, col_bot2, col_bot3 = st.columns(3)
    
    if not pedido_arquivado:
        with col_bot1:
            if st.button("💾 Salvar Ficha Completa", use_container_width=True, type="primary", disabled=bloquear_edicao):
                json_extras_salvar = {}
                for extra in st.session_state["lista_extras_dinamicos"]:
                    json_extras_salvar[extra["nome"]] = extra["valor"]
                
                # Coleta também os valores manuais preenchidos na aba de itens
                for k, v in itens_consulta.items():
                    if v > 0: json_extras_salvar[f"Valor de {k}"] = v

                dados = {
                    "status": status,
                    "cesta_montada": chk_montada,
                    "valor_frete": valor_frete, 
                    "valor_extras": valor_extras_total, 
                    "desconto": desconto, 
                    "valor_total": valor_total_calculado, 
                    "horario_combinado": horario_str_salvar, 
                    "itens_consulta": json_extras_salvar
                }
                atualizar_pedido(pedido["id"], dados)
                st.session_state['msg_geral'] = "✅ Fechamento financeiro e logística salvos com sucesso!"
                st.rerun()

    with col_bot2:
        link_wpp = gerar_whatsapp(pedido, adicionais_pedido, valor_total_calculado, valor_frete, st.session_state["lista_extras_dinamicos"], desconto, itens_consulta)
        st.link_button("💬 Enviar Recibo no WhatsApp", url=link_wpp, use_container_width=True)

    with col_bot3:
        if st.button("⬅ Voltar para o Painel", use_container_width=True):
            st.switch_page("pages/03_Clientes.py" if pedido_arquivado else "pages/02_Pedidos.py")

st.write("")
st.caption("📋 Ficha Técnica Oficial - Doce Cesta Brasília")
