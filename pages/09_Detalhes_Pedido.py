import streamlit as st
import json
import urllib.parse
from uuid import uuid4
import re

from services.pedido_service import buscar_pedido
from services.pedido_adicional_service import listar_adicionais_pedido
from config.supabase import supabase
from services.cesta_service import buscar_cesta, listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Ficha do Pedido", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()
usuario = st.session_state.usuario

# =====================================================
# CSS PREMIUM E RESPONSIVIDADE
# =====================================================
st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1250px; }
div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 0px !important; letter-spacing: -0.5px; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

/* =========================================
   CARDS E CONTAINERS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] { 
    background: #ffffff; 
    border: 1px solid #e8ddd3 !important; 
    border-radius: 14px !important; 
    padding: 16px 20px !important; 
    margin-bottom: 8px !important; 
    box-shadow: 0 2px 8px rgba(0,0,0,0.02); 
    transition: all 0.25s ease; 
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { 
    border-color: #d2bfae !important; 
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.06); 
}

/* =========================================
   TIPOGRAFIA INTERNA DOS CARDS
========================================== */
.card-title { font-size: 16px !important; font-weight: 800 !important; color: #5a3b28 !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #f3ece6; padding-bottom: 6px; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.info-value { margin-bottom: 12px; color: #2c1e14; font-weight: 800; font-size: 14px !important; }

/* =========================================
   RESUMO FINANCEIRO (RECIBO)
========================================== */
.resumo-container { background: linear-gradient(145deg, #ffffff 0%, #fdfcfb 100%); border: 1px solid #e8ddd3; border-radius: 12px; padding: 15px; display: flex; flex-direction: column; gap: 8px; }
.resumo-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px !important; color: #444; padding: 4px 0; border-bottom: 1px dashed #e8ddd3; }
.resumo-row:last-child { border-bottom: none; padding-top: 10px; }
.resumo-label { font-weight: 600; color: #775a46; }
.resumo-val { font-weight: 800; color: #2c1e14; }
.resumo-total-val { font-size: 22px !important; font-weight: 800 !important; color: #137333 !important; }

/* =========================================
   BADGES (STATUS, MONTADA E PGTO)
========================================== */
.pgto-badge { background: #f3ece6; color: #5a3b28; padding: 3px 10px; border-radius: 8px; font-weight: 800; border: 1px solid #dfcdbb; font-size: 11px; text-transform: uppercase; }
.badge-montada { background-color: #e6f4ea; color: #137333; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 800; border: 1px solid #ceead6; margin-left: 10px; display: inline-block; text-transform: uppercase; letter-spacing: 0.5px; }

/* =========================================
   BOTÕES E UPLOADER (DROPZONE)
========================================== */
div[data-testid="stButton"] > button { border-radius: 10px !important; min-height: 42px !important; font-weight: 800 !important; font-size: 14px !important; transition: all 0.2s ease; }
div[data-testid="stButton"] > button:hover { transform: scale(1.02); }

div[data-testid="stLinkButton"] > a { width: 100% !important; border-radius: 10px !important; min-height: 42px !important; font-weight: 800 !important; font-size: 14px !important; display: flex !important; align-items: center !important; justify-content: center !important; background-color: #25D366 !important; color: white !important; border: none !important; transition: all 0.2s ease; }
div[data-testid="stLinkButton"] > a:hover { background-color: #128C7E !important; transform: scale(1.02); }

div[data-testid="stFileUploader"] section { background-color: #faf7f3 !important; border: 2px dashed #dfcdbb !important; border-radius: 12px !important; padding: 12px !important; text-align: center !important; transition: all 0.3s ease !important; }
div[data-testid="stFileUploader"] section:hover { border-color: #a87b57 !important; background-color: #f5eee6 !important; }

/* =========================================
   RESPONSIVIDADE MOBILE
========================================== */
@media (max-width: 768px) { 
    .block-container { padding: 1rem 0.5rem !important; } 
    h1 { font-size: 24px !important; } 
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 12px 14px !important; } 
    .info-value { font-size: 13px !important; margin-bottom: 8px; } 
    .resumo-total-val { font-size: 18px !important; } 
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
pedido = buscar_pedido(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()


# =====================================================
# LÓGICA DE BLOQUEIO (MODO ARQUIVO / LOGÍSTICA)
# =====================================================
status_atual_pedido = str(pedido.get("status", "")).strip().capitalize()
perfil_usuario = usuario.get("perfil", "Operador")
e_administrador = (perfil_usuario == "Administrador")

pedido_arquivado = (status_atual_pedido == "Entregue")
bloquear_edicao = (status_atual_pedido == "Enviado") and not e_administrador

if "editar_pedido" not in st.session_state: st.session_state.editar_pedido = False

if pedido_arquivado or bloquear_edicao:
    st.session_state.editar_pedido = False

if pedido_arquivado:
    st.success("📦 **PEDIDO FINALIZADO (ARQUIVO)** - Esta ficha está disponível apenas para leitura do histórico de vendas do cliente.")
elif status_atual_pedido == "Enviado":
    st.info("🛵 **PEDIDO EM ROTA DE ENTREGA** - O status logístico e financeiro estão trancados até que a entrega seja concluída.")

# -----------------------------------------------------
# FILTRO ANTI-DUPLICIDADE E LEITURA JSON
# -----------------------------------------------------
try:
    lista_bruta_adicionais = listar_adicionais_pedido(pedido["id"])
    adicionais_pedido = []
    nomes_vistos = set()
    for ad in lista_bruta_adicionais:
        nome_ad = ad.get("nome_produto")
        if nome_ad and nome_ad not in nomes_vistos:
            adicionais_pedido.append(ad)
            nomes_vistos.add(nome_ad)
except: 
    adicionais_pedido = []

itens_consulta_salvos = pedido.get("itens_consulta") or {}
if isinstance(itens_consulta_salvos, str):
    try: itens_consulta_salvos = json.loads(itens_consulta_salvos)
    except: itens_consulta_salvos = {}

def atualizar_pedido(pid, dados):
    try: supabase.table("pedidos").update(dados).eq("id", pid).execute(); return True
    except: return False

def atualizar_anotacao_pedido(pid, anotacao):
    try: supabase.table("pedidos").update({"anotacoes_internas": anotacao}).eq("id", pid).execute(); return True
    except: return False

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
    if erros: return False, " | ".join(erros)
    return True, ""

def listar_fotos_local(pid):
    try:
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pid).order("created_at").execute()
        fotos = resposta.data or []
        url_base = st.secrets.get("SUPABASE_URL", "").rstrip("/")
        for foto in fotos:
            if not foto.get("url") and foto.get("arquivo"):
                foto["url"] = f"{url_base}/storage/v1/object/public/pedido_fotos/{foto['arquivo']}"
        return fotos, ""
    except Exception as e:
        return [], str(e)

def deletar_foto_local(foto_id, caminho_arquivo):
    try:
        if caminho_arquivo: supabase.storage.from_("pedido_fotos").remove([caminho_arquivo])
        supabase.table("pedido_fotos").delete().eq("id", foto_id).execute()
        return True, ""
    except Exception as e:
        return False, str(e)

def formatar_valor(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
    except: return "R$ 0,00"

def formatar_data(data):
    if not data: return "-"
    try: ano, mes, dia = str(data)[:10].split("-"); return f"{dia}/{mes}/{ano}"
    except: return str(data)

def gerar_whatsapp(pedido, adicionais, valor_final, frete_atual, extras_atual, desconto_atual):
    itens_consulta = pedido.get("itens_consulta") or {}
    if isinstance(itens_consulta, str):
        try: itens_consulta = json.loads(itens_consulta)
        except: itens_consulta = {}

    lista_adicionais = []
    for item in adicionais:
        nome = item.get("nome_produto", "-")
        valor = item.get("valor_unitario")
        if valor is not None: lista_adicionais.append(f"• {nome} - {formatar_valor(valor)}")
        else:
            val_manual = itens_consulta.get(nome, 0)
            if val_manual: lista_adicionais.append(f"• {nome} - {formatar_valor(val_manual)}")
            else: lista_adicionais.append(f"• {nome} (sob consulta)")

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
    if float(extras_atual or 0) > 0: texto_val += f"➕ Extras: {formatar_valor(extras_atual)}\n"
    if float(desconto_atual or 0) > 0: texto_val += f"🏷️ Desconto: - {formatar_valor(desconto_atual)}\n"

    texto = (
        f"🎁 *Doce Cesta Brasília*\n\nOlá {pedido.get('cliente_nome','') if pedido else ''}!\n\n"
        f"{texto_dest}🎀 Cesta: {pedido.get('cesta_nome','-')}\n\n🛒 Produtos:\n{pedido.get('produtos','-')}\n\n"
        f"🎀 Adicionais:\n{chr(10).join(lista_adicionais)}\n\n📍 Entrega:\n"
        f"Data: {formatar_data(pedido.get('data_entrega'))}\nPeríodo: {pedido.get('periodo_entrega','-')}\n"
        f"Horário: {pedido.get('horario_combinado','-')}\n\n💳 Pagamento: {pedido.get('pagamento','-')}\n\n"
        f"💰 *Resumo Financeiro*\n{texto_val}✅ *Valor Final: {formatar_valor(valor_final)}*\n\nObrigado! ❤️"
    )
    
    tel_limpo = re.sub(r'\D', '', str(pedido.get("cliente_telefone", "")))
    if len(tel_limpo) == 10 or len(tel_limpo) == 11: tel_wpp = f"55{tel_limpo}"
    else: tel_wpp = tel_limpo
        
    return f"https://wa.me/{tel_wpp}?text={urllib.parse.quote(texto)}"

def obter_icone_pagamento(metodo):
    m = str(metodo).strip().lower()
    if "pix" in m: 
        return '<div class="pgto-badge" style="background: #e6f4ea; border-color: #137333; color: #137333;" title="Pix">⚡ PIX</div>'
    elif "cart" in m: 
        return '<div class="pgto-badge" style="background: #e8f0fe; border-color: #1a73e8; color: #1a73e8;" title="Cartão de Crédito">💳 CARTÃO</div>'
    elif "dinheiro" in m: 
        return '<div class="pgto-badge" style="background: #fef7e0; border-color: #b06000; color: #b06000;" title="Dinheiro">💵 DINHEIRO</div>'
    elif "transfer" in m: 
        return '<div class="pgto-badge" style="background: #f3ece6; border-color: #5a3b28; color: #5a3b28;" title="Transferência Bancária">🏦 TRANSF.</div>'
    else: 
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
# BLOCO DE EDIÇÃO AVANÇADA
# =====================================================
if st.session_state.editar_pedido:
    st.write("")
    with st.container(border=True):
        st.markdown('<div class="card-title">✏️ Painel de Edição Completo</div>', unsafe_allow_html=True)
        aba_dados, aba_cesta, aba_adicionais = st.tabs(["👤 Dados Cadastrais", "🎁 Cesta e Produtos", "🎀 Adicionais"])

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
            try: cestas = listar_cestas(); nomes_cestas = [c.get("nome", "") for c in cestas]
            except: cestas, nomes_cestas = [], []
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
            st.markdown("<div style='font-size: 14px; font-weight: 800; color: #5a3b28; margin-bottom: 10px;'>🎀 Adicionar Extras Avulsos</div>", unsafe_allow_html=True)
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
        cs1, cs2, cs3 = st.columns([1, 2, 1])
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
# LAYOUT PRINCIPAL (VISUALIZAÇÃO DA FICHA)
# =====================================================
else:
    st.write("")
    col_esquerda, col_direita = st.columns([1.3, 1])

    # -------------------------------------------------
    # COLUNA ESQUERDA: INFOS LOGÍSTICAS E MONTAGEM
    # -------------------------------------------------
    with col_esquerda:
        with st.container(border=True):
            st.markdown('<div class="card-title">👤 Informações de Contato</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: 
                st.markdown('<div class="info-label">Comprador</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-value">{pedido.get("cliente_nome") or "-"} <span style="font-size:12px;color:#666;font-weight:600;">(CPF: {pedido.get("cliente_cpf") or "-"})</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-value">📞 +{pedido.get("cliente_telefone") or "-"}</div>', unsafe_allow_html=True)
            with c2: 
                st.markdown('<div class="info-label">Homenageado (Destinatário)</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-value">{pedido.get("destinatario_nome") or "-"}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-value">📞 {pedido.get("destinatario_telefone") or "-"}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="card-title">🎁 Detalhes da Entrega e Pacote</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="info-label">Cesta Adquirida</div><div class="info-value">{pedido.get("cesta_nome","-")}</div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="info-label">Forma de Pagto</div><div class="info-value">{obter_icone_pagamento(pedido.get("pagamento", "-"))}</div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="info-label">Data Limite</div><div class="info-value">{formatar_data(pedido.get("data_entrega"))}</div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="info-label">Período Ideal</div><div class="info-value">{pedido.get("periodo_entrega","-")}</div>', unsafe_allow_html=True)

        c_p1, c_p2 = st.columns(2)
        valor_adicionais = 0.0
        valor_consulta = 0.0
        itens_consulta = {}

        with c_p1:
            with st.container(border=True):
                st.markdown('<div class="card-title">🛒 Checklist da Cesta</div>', unsafe_allow_html=True)
                produtos = pedido.get("produtos", "")
                if produtos:
                    for item in produtos.split("\n"): st.markdown(f"<div style='font-size:13px; margin-bottom:4px; font-weight:600;'>✅ {item.replace('•','').strip()}</div>", unsafe_allow_html=True)
                else: st.caption("Nenhum item configurado.")

        with c_p2:
            with st.container(border=True):
                st.markdown('<div class="card-title">🎀 Itens Extras Avulsos</div>', unsafe_allow_html=True)
                if adicionais_pedido:
                    for idx_ad, adicional in enumerate(adicionais_pedido):
                        nome = adicional.get("nome_produto", "-")
                        valor = adicional.get("valor_unitario")
                        if valor is not None:
                            valor = float(valor); valor_adicionais += valor
                            st.markdown(f"<div style='font-size:13px; margin-bottom:4px; font-weight:600;'>➕ {nome} - <span style='color:#137333;'>{formatar_valor(valor)}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='font-size:13px; margin-bottom:2px; font-weight:600;'>➕ {nome}</div>", unsafe_allow_html=True)
                            val_salvo = float(itens_consulta_salvos.get(nome, 0) or 0)
                            val_dig = st.number_input("Preço de Fechamento", min_value=0.0, value=val_salvo, step=1.0, key=f"cons_{nome}_{idx_ad}", disabled=(bloquear_edicao or pedido_arquivado), label_visibility="collapsed")
                            itens_consulta[nome] = val_dig
                            if val_dig > 0: valor_consulta += val_dig; valor_adicionais += val_dig
                else: st.caption("Nenhum item extra solicitado.")

        with st.container(border=True):
            st.markdown('<div class="card-title">📍 Localização e Roteirização</div>', unsafe_allow_html=True)
            endereco_pedido = pedido.get("endereco", "")
            st.text_area("", value=endereco_pedido if endereco_pedido else "O cliente não informou o endereço completo.", disabled=True, height=65, label_visibility="collapsed")
            if endereco_pedido:
                endereco_limpo_gps = re.sub(r'\(CEP:.*?\)', '', endereco_pedido).strip()
                endereco_encoded = urllib.parse.quote(endereco_limpo_gps)
                col_map1, col_map2 = st.columns(2)
                with col_map1: st.link_button("🗺️ Ver no Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_encoded}", use_container_width=True)
                with col_map2: st.link_button("🚗 Ver Rota no Waze", url=f"https://waze.com/ul?q={endereco_encoded}&navigate=yes", use_container_width=True)
                
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            with st.container(border=True):
                st.markdown('<div class="card-title">💌 Cartão de Homenagem</div>', unsafe_allow_html=True)
                st.text_area("", value=pedido.get("mensagem") or "Sem cartão.", disabled=True, height=70, label_visibility="collapsed")
        with c_m2:
            with st.container(border=True):
                st.markdown('<div class="card-title">✨ Observações de Entrega</div>', unsafe_allow_html=True)
                st.text_area("", value=pedido.get("pedido_especial") or "Nenhuma solicitação.", disabled=True, height=70, label_visibility="collapsed")


    # -------------------------------------------------
    # COLUNA DIREITA: FINANCEIRO, FOTOS E CONTROLE
    # -------------------------------------------------
    with col_direita:
        valor_cesta = 0.0
        try:
            if pedido.get("cesta_id"):
                cesta = buscar_cesta(pedido["cesta_id"])
                if cesta: valor_cesta = float(cesta.get("preco", 0) or 0)
        except: pass

        with st.container(border=True):
            st.markdown('<div class="card-title">💰 Fechamento Financeiro</div>', unsafe_allow_html=True)
            cf1, cf2, cf3 = st.columns(3)
            travar_financeiro = (bloquear_edicao or pedido_arquivado)
            
            with cf1: valor_frete = st.number_input("🚚 Frete (R$)", min_value=0.0, value=float(pedido.get("valor_frete") or 0), step=1.0, key="frete", disabled=travar_financeiro)
            with cf2: valor_extras = st.number_input("➕ Avulsos (R$)", min_value=0.0, value=float(pedido.get("valor_extras") or 0), step=1.0, key="extras", disabled=travar_financeiro)
            with cf3: desconto = st.number_input("🏷️ Desc. (R$)", min_value=0.0, value=float(pedido.get("desconto") or 0), step=1.0, key="desconto", disabled=travar_financeiro)
            
            st.write("")
            c_status1, c_status2 = st.columns(2)
            with c_status1:
                status_atual = str(pedido.get("status", "Recebido")).strip().capitalize()
                
                # Regras de Status baseadas no Perfil
                if e_administrador and not pedido_arquivado:
                    status_op = ["Recebido", "Pago", "Desistência"]
                    if status_atual not in status_op: status_op.append(status_atual)
                    status = st.selectbox("Status Financeiro", status_op, index=status_op.index(status_atual) if status_atual in status_op else 0, disabled=False)
                else:
                    status_op = [status_atual]
                    status = st.selectbox("Status Financeiro", status_op, index=0, disabled=True)
            
            with c_status2:
                st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
                chk_montada = st.checkbox("🧺 Marcar Cesta como Pronta", value=bool(pedido.get("cesta_montada")), disabled=travar_financeiro)

            horario_combinado = st.text_input("🕒 Horário Fixo (Exato)", value=pedido.get("horario_combinado") or "", placeholder="Ex: 15:30", disabled=travar_financeiro)

            valor_total_calculado = max(0, valor_cesta + valor_adicionais + valor_frete + valor_extras - desconto)

            st.write("")
            st.markdown(
                f"""
                <div class="resumo-container">
                    <div class="resumo-row"><span class="resumo-label">🎁 Valor da Cesta</span><span class="resumo-val">{formatar_valor(valor_cesta)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🎀 Adicionais do Catálogo</span><span class="resumo-val">{formatar_valor(valor_adicionais)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🚚 Taxa de Entrega</span><span class="resumo-val">{formatar_valor(valor_frete)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">➕ Extras Avulsos</span><span class="resumo-val">{formatar_valor(valor_extras)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🏷️ Desconto Especial</span><span class="resumo-val" style="color: #c5221f;">- {formatar_valor(desconto)}</span></div>
                    <div class="resumo-row"><span class="resumo-label" style="font-size:15px; font-weight:800; color:#2c1e14;">💰 VALOR FINAL</span><span class="resumo-total-val">{formatar_valor(valor_total_calculado)}</span></div>
                </div>
                """, unsafe_allow_html=True
            )

        with st.container(border=True):
            st.markdown('<div class="card-title">📝 Anotações e Histórico</div>', unsafe_allow_html=True)
            anotacao = st.text_area("Bloco de anotações internas da equipe", value=pedido.get("anotacoes_internas") or "", height=80, key="campo_anotacao", disabled=pedido_arquivado, label_visibility="collapsed")
            if not pedido_arquivado:
                if st.button("💾 Gravar Anotação Rápida", use_container_width=True):
                    atualizar_anotacao_pedido(pedido["id"], anotacao)
                    st.session_state['msg_geral'] = "✅ Anotação interna salva com sucesso!"
                    st.rerun()

        with st.container(border=True):
            st.markdown('<div class="card-title">📷 Polaroids e Anexos</div>', unsafe_allow_html=True)
            if "msg_foto" in st.session_state:
                if "❌" in st.session_state['msg_foto']: st.error(st.session_state['msg_foto'])
                else: st.success(st.session_state['msg_foto'])
                del st.session_state['msg_foto']
            
            if not pedido_arquivado:
                novas_fotos = st.file_uploader("Enviar arquivos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="up_fotos_multi", label_visibility="collapsed")
                if novas_fotos:
                    if st.button("📤 Salvar Anexos no Pedido", use_container_width=True, type="primary"):
                        with st.spinner("Enviando imagens para a nuvem..."):
                            sucesso, erro_msg = salvar_fotos_local(pedido["id"], novas_fotos)
                        if sucesso: st.session_state['msg_foto'] = "✅ Arquivos salvos!"
                        else: st.session_state['msg_foto'] = f"❌ Erro: {erro_msg}"
                        st.rerun()
                st.divider()
                
            fotos, erro_listar = listar_fotos_local(pedido["id"])
            if erro_listar: st.error(f"❌ Erro ao buscar: {erro_listar}")
            elif fotos:
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
            else: st.caption("Nenhum arquivo anexado a este pedido.")

    # =====================================================
    # BOTÕES PRINCIPAIS E WHATSAPP
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
                dados = {
                    "status": status,
                    "cesta_montada": chk_montada,
                    "valor_frete": valor_frete, 
                    "valor_extras": valor_extras, 
                    "desconto": desconto, 
                    "valor_total": valor_total_calculado, 
                    "horario_combinado": horario_combinado, 
                    "itens_consulta": itens_consulta
                }
                atualizar_pedido(pedido["id"], dados)
                st.session_state['msg_geral'] = "✅ Fechamento financeiro e logística salvos com sucesso!"
                st.rerun()

    with col_bot2:
        link_wpp = gerar_whatsapp(pedido, adicionais_pedido, valor_total_calculado, valor_frete, valor_extras, desconto)
        st.link_button("💬 Enviar Recibo no WhatsApp", url=link_wpp, use_container_width=True)

    with col_bot3:
        if st.button("⬅ Voltar para o Painel", use_container_width=True):
            st.switch_page("pages/03_Clientes.py" if pedido_arquivado else "pages/02_Pedidos.py")

st.write("")
st.caption("📋 Ficha Técnica Oficial - Doce Cesta Brasília")
