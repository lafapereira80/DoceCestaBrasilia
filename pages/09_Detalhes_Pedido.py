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
# CONFIGURAÇÃO DA PÁGINA E CSS
# =====================================================
st.set_page_config(page_title="Detalhes do Pedido", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()
usuario = st.session_state.usuario

st.markdown(
"""
<style>
.block-container { padding-top: 0.8rem !important; padding-bottom: 1.5rem !important; max-width: 1250px; }
div[data-testid="stVerticalBlock"] { gap: 0.35rem !important; }
h1 { font-size: 22px !important; font-weight: 700 !important; color: #5a3b28; margin-bottom: 0px !important; }
.block-container p, .block-container label { font-family: Arial, sans-serif !important; font-size: 12px !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 12px 16px !important; margin-bottom: 6px !important; box-shadow: 0 1px 3px rgba(90, 59, 40, 0.03); }
.card-title { font-size: 15px !important; font-weight: 800 !important; color: #5a3b28 !important; margin-bottom: 8px !important; }
.info-label { font-weight: 700; color: #775a46; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
.info-value { margin-bottom: 4px; color: #222; font-weight: 600; font-size: 13px !important; }
.resumo-container { background: #fff8ef; border: 1px solid #e6d1bb; border-radius: 10px; padding: 10px 12px; display: flex; flex-direction: column; gap: 6px; }
.resumo-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px !important; color: #444; padding: 3px 0; border-bottom: 1px dashed #f0e0d0; }
.resumo-row:last-child { border-bottom: none; padding-top: 6px; }
.resumo-label { font-weight: 600; color: #5a3b28; }
.resumo-val { font-weight: 700; color: #222; }
.resumo-total-val { font-size: 20px !important; font-weight: 800 !important; color: #2e7d32 !important; }
.pgto-badge { background: #f3ece6; color: #5a3b28; padding: 2px 8px; border-radius: 6px; font-weight: 700; border: 1px solid #dfcdbb; }
div[data-testid="stButton"] > button { width: 100% !important; border-radius: 8px !important; min-height: 38px !important; font-weight: 700 !important; }
div[data-testid="stLinkButton"] > a { width: 100% !important; border-radius: 8px !important; min-height: 38px !important; font-weight: 700 !important; display: flex !important; align-items: center !important; justify-content: center !important; background-color: #25D366 !important; color: white !important; border: none !important; }
div[data-testid="stLinkButton"] > a:hover { background-color: #128C7E !important; color: white !important; }
@media (max-width: 768px) { .block-container { padding-top: 0.5rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; } h1 { font-size: 18px !important; } div[data-testid="stVerticalBlockBorderWrapper"] { padding: 8px !important; } .info-value { font-size: 12px !important; } .resumo-total-val { font-size: 17px !important; } .resumo-container { padding: 8px 10px; } }
.badge-montada { background-color: #e6f4ea; color: #137333; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 800; border: 1px solid #137333; margin-left: 10px; display: inline-block; }
</style>
""",
unsafe_allow_html=True
)

if "pedido_aberto" not in st.session_state:
    st.error("Nenhum pedido selecionado.")
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

pedido_arquivado = (status_atual_pedido == "Entregue")
# Se estiver em Rota (Enviado), bloqueia edições operacionais comuns
bloquear_edicao = (status_atual_pedido == "Enviado") and (perfil_usuario != "Administrador")

if "editar_pedido" not in st.session_state: st.session_state.editar_pedido = False

if pedido_arquivado or bloquear_edicao:
    st.session_state.editar_pedido = False

if pedido_arquivado:
    st.success("📦 **PEDIDO FINALIZADO (ARQUIVO)** - Esta ficha está disponível apenas para leitura do histórico de vendas do cliente.")
elif status_atual_pedido == "Enviado":
    st.info("🛵 **PEDIDO EM ROTA DE ENTREGA** - O status logístico está trancado até que a entrega seja concluída.")

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
        return '<div style="background-color: #e6f4ea; border: 1px solid #137333; border-radius: 6px; padding: 2px 10px; display: inline-flex; align-items: center; justify-content: center; height: 26px; color: #137333; font-weight: bold; font-size: 12px;" title="Pix">⚡ PIX</div>'
    elif "cart" in m: 
        return '<div style="background-color: #e8f0fe; border: 1px solid #1a73e8; border-radius: 6px; padding: 2px 10px; display: inline-flex; align-items: center; justify-content: center; height: 26px; color: #1a73e8; font-weight: bold; font-size: 12px;" title="Cartão de Crédito">💳 CARTÃO</div>'
    elif "dinheiro" in m: 
        return '<div style="background-color: #fef7e0; border: 1px solid #b06000; border-radius: 6px; padding: 2px 10px; display: inline-flex; align-items: center; justify-content: center; height: 26px; color: #b06000; font-weight: bold; font-size: 12px;" title="Dinheiro">💵 DINHEIRO</div>'
    elif "transfer" in m: 
        return '<div style="background-color: #f3ece6; border: 1px solid #dfcdbb; border-radius: 6px; padding: 2px 10px; display: inline-flex; align-items: center; justify-content: center; height: 26px; color: #5a3b28; font-weight: bold; font-size: 12px;" title="Transferência Bancária">🏦 TRANSFERÊNCIA</div>'
    else: 
        return f'<span class="pgto-badge">{metodo}</span>'

# =====================================================
# CABEÇALHO 
# =====================================================
col_t1, col_t2 = st.columns([3.5, 1])
with col_t1:
    st.title("📋 Ficha Técnica")
    badge_montada = '<span class="badge-montada">🧺 Cesta Montada</span>' if pedido.get("cesta_montada") else ''
    st.markdown(f"Pedido #{pedido.get('id')} | Status: **{pedido.get('status','-')}** {badge_montada}", unsafe_allow_html=True)
with col_t2:
    if not pedido_arquivado and not bloquear_edicao:
        if st.button("✏️ Alterar Pedido", use_container_width=True):
            st.session_state.editar_pedido = True
            st.rerun()

# =====================================================
# BLOCO DE EDIÇÃO AVANÇADA
# =====================================================
if st.session_state.editar_pedido:
    with st.container(border=True):
        st.markdown('<div class="card-title">✏️ Painel de Edição Avançada</div>', unsafe_allow_html=True)
        aba_dados, aba_cesta, aba_adicionais = st.tabs(["👤 Dados", "🎁 Cesta e Produtos", "🎀 Adicionais"])

        with aba_dados:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                novo_nome = st.text_input("Comprador - Nome", value=pedido.get("cliente_nome") or "")
                novo_telefone = st.text_input("Comprador - Telefone", value=pedido.get("cliente_telefone") or "")
            with col_d2:
                novo_dest_nome = st.text_input("Destinatário - Nome", value=pedido.get("destinatario_nome") or "")
                novo_dest_tel = st.text_input("Destinatário - Telefone", value=pedido.get("destinatario_telefone") or "")
                novo_motivo = st.text_input("Motivo da Homenagem", value=pedido.get("motivo_homenagem") or "")

        with aba_cesta:
            try: cestas = listar_cestas(); nomes_cestas = [c.get("nome", "") for c in cestas]
            except: cestas, nomes_cestas = [], []
            cesta_atual = pedido.get("cesta_nome") or ""
            nova_cesta_nome = st.selectbox("🎁 Cesta Base", nomes_cestas, index=nomes_cestas.index(cesta_atual) if cesta_atual in nomes_cestas else 0) if nomes_cestas else cesta_atual
            cesta_selecionada = next((c for c in cestas if c.get("nome") == nova_cesta_nome), None)
            novo_produtos = pedido.get("produtos") or ""
            
            if cesta_selecionada:
                config_cesta = carregar_configuracao_cesta(cesta_selecionada["id"])
                if config_cesta:
                    st.markdown("### 🍓 Personalização da Cesta")
                    selecoes_admin = {}
                    txt_prod_atuais = pedido.get("produtos") or ""
                    for grupo in config_cesta:
                        cat = grupo.get("categoria", "Sem categoria")
                        prods = grupo.get("produtos", [])
                        maximo = grupo.get("max_escolhas", 1)
                        if not prods: continue
                        with st.container(border=True):
                            defaults = [p for p in prods if p["nome"] in txt_prod_atuais]
                            st.markdown(f"**📦 {cat}**")
                            if maximo == 1:
                                idx_def = prods.index(defaults[0]) if defaults else 0
                                escolhido = st.radio(f"Escolha 1", prods, format_func=lambda p: p["nome"], index=idx_def, key=f"edit_rad_{cat}")
                                if escolhido: selecoes_admin[cat] = [escolhido]
                            else:
                                escolhidos = st.multiselect(f"Escolha até {maximo}", prods, format_func=lambda p: p["nome"], default=defaults, max_selections=maximo, key=f"edit_mult_{cat}")
                                selecoes_admin[cat] = escolhidos
                    novo_produtos = "\n".join([f"{c}: {i['nome']}" for c, itens in selecoes_admin.items() for i in itens])
                else: st.info("Cesta sem produtos configurados.")
            st.divider()
            col_m1, col_m2 = st.columns(2)
            with col_m1: nova_mensagem = st.text_area("💌 Mensagem do Cartão", value=pedido.get("mensagem") or "", height=120)
            with col_m2: novo_endereco = st.text_area("📍 Endereço de Entrega", value=pedido.get("endereco") or "", height=120)
            novo_especial = st.text_input("✨ Solicitação Especial", value=pedido.get("pedido_especial") or "")

        with aba_adicionais:
            st.write("🎀 **Catálogo de Adicionais**")
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
            else: st.caption("Catálogo vazio.")

        st.divider()
        cs1, cs2 = st.columns(2)
        with cs1:
            if st.button("💾 Salvar Todas as Alterações", use_container_width=True, type="primary"):
                dados = {"cliente_nome": novo_nome, "cliente_telefone": novo_telefone, "destinatario_nome": novo_dest_nome, "destinatario_telefone": novo_dest_tel, "motivo_homenagem": novo_motivo, "cesta_nome": nova_cesta_nome, "produtos": novo_produtos, "mensagem": nova_mensagem, "pedido_especial": novo_especial, "endereco": novo_endereco}
                atualizar_pedido(pedido["id"], dados)
                if "erro_admin" in st.session_state: del st.session_state["erro_admin"]
                try:
                    try: supabase.table("pedido_adicionais").delete().eq("pedido_id", pedido["id"]).execute()
                    except Exception as err_del:
                        st.session_state["erro_admin"] = f"❌ Erro ao deletar: {err_del}"
                        raise Exception("Falha")
                    if adicionais_selecionados:
                        for ad in adicionais_selecionados: ad["pedido_id"] = pedido["id"]
                        try: supabase.table("pedido_adicionais").insert(adicionais_selecionados).execute()
                        except Exception as err_ins:
                            st.session_state["erro_admin"] = f"❌ Erro ao inserir: {err_ins}"
                            raise Exception("Falha")
                except: pass 
                if "erro_admin" not in st.session_state: st.session_state.editar_pedido = False
                st.rerun()
        with cs2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.editar_pedido = False
                st.rerun()
        if "erro_admin" in st.session_state: st.error(st.session_state["erro_admin"])


# =====================================================
# LAYOUT PRINCIPAL (VISUALIZAÇÃO DA FICHA)
# =====================================================
else:
    col_esquerda, col_direita = st.columns([1.2, 1])

    with col_esquerda:
        with st.container(border=True):
            st.markdown('<div class="card-title">👤 Cliente (Comprador)</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="info-label">Nome</div><div class="info-value">{pedido.get("cliente_nome") or "-"}</div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="info-label">CPF</div><div class="info-value">{pedido.get("cliente_cpf") or "-"}</div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="info-label">Telefone</div><div class="info-value">+{pedido.get("cliente_telefone") or "-"}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="card-title">💝 Homenageado (Destinatário)</div>', unsafe_allow_html=True)
            h1, h2, h3 = st.columns(3)
            with h1: st.markdown(f'<div class="info-label">Nome</div><div class="info-value">{pedido.get("destinatario_nome") or "-"}</div>', unsafe_allow_html=True)
            with h2: st.markdown(f'<div class="info-label">Telefone</div><div class="info-value">{pedido.get("destinatario_telefone") or "-"}</div>', unsafe_allow_html=True)
            with h3: st.markdown(f'<div class="info-label">Motivo</div><div class="info-value">{pedido.get("motivo_homenagem") or "-"}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="card-title">🎁 Pedido</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="info-label">Cesta</div><div class="info-value">{pedido.get("cesta_nome","-")}</div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="info-label">Pagamento</div><div class="info-value">{obter_icone_pagamento(pedido.get("pagamento", "-"))}</div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="info-label">Entrega</div><div class="info-value">{formatar_data(pedido.get("data_entrega"))}</div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="info-label">Período</div><div class="info-value">{pedido.get("periodo_entrega","-")}</div>', unsafe_allow_html=True)

        c_p1, c_p2 = st.columns(2)
        valor_adicionais = 0.0
        valor_consulta = 0.0
        itens_consulta = {}

        with c_p1:
            with st.container(border=True):
                st.markdown('<div class="card-title">🛒 Produtos da Cesta</div>', unsafe_allow_html=True)
                produtos = pedido.get("produtos", "")
                if produtos:
                    for item in produtos.split("\n"): st.write(f"• {item.replace('•','').strip()}")
                else: st.caption("Nenhum produto informado.")

        with c_p2:
            with st.container(border=True):
                st.markdown('<div class="card-title">🎀 Adicionais</div>', unsafe_allow_html=True)
                if adicionais_pedido:
                    for idx_ad, adicional in enumerate(adicionais_pedido):
                        nome = adicional.get("nome_produto", "-")
                        valor = adicional.get("valor_unitario")
                        if valor is not None:
                            valor = float(valor); valor_adicionais += valor
                            st.write(f"• {nome} - {formatar_valor(valor)}")
                        else:
                            st.write(f"• {nome}")
                            val_salvo = float(itens_consulta_salvos.get(nome, 0) or 0)
                            val_dig = st.number_input("Definir valor", min_value=0.0, value=val_salvo, step=1.0, key=f"cons_{nome}_{idx_ad}", disabled=(bloquear_edicao or pedido_arquivado))
                            itens_consulta[nome] = val_dig
                            if val_dig > 0: valor_consulta += val_dig; valor_adicionais += val_dig
                else: st.caption("Nenhum adicional selecionado.")

        c_m1, c_m2 = st.columns(2)
        with c_m1:
            with st.container(border=True):
                st.markdown('<div class="card-title">💌 Mensagem do Cartão</div>', unsafe_allow_html=True)
                st.text_area("", value=pedido.get("mensagem") or "", disabled=True, height=60, key="msg_vis")
        with c_m2:
            with st.container(border=True):
                st.markdown('<div class="card-title">✨ Pedido Especial</div>', unsafe_allow_html=True)
                st.text_area("", value=pedido.get("pedido_especial") or "", disabled=True, height=60, key="esp_vis")

        with st.container(border=True):
            st.markdown('<div class="card-title">📍 Endereço de Entrega & Rotas</div>', unsafe_allow_html=True)
            endereco_pedido = pedido.get("endereco", "")
            st.text_area("", value=endereco_pedido if endereco_pedido else "Endereço não informado.", disabled=True, height=65, key="end_vis")
            if endereco_pedido:
                endereco_limpo_gps = re.sub(r'\(CEP:.*?\)', '', endereco_pedido).strip()
                endereco_encoded = urllib.parse.quote(endereco_limpo_gps)
                col_map1, col_map2 = st.columns(2)
                with col_map1: st.link_button("🗺️ Abrir no Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_encoded}", use_container_width=True)
                with col_map2: st.link_button("🚗 Abrir no Waze", url=f"https://waze.com/ul?q={endereco_encoded}&navigate=yes", use_container_width=True)

    with col_direita:
        valor_cesta = 0.0
        try:
            if pedido.get("cesta_id"):
                cesta = buscar_cesta(pedido["cesta_id"])
                if cesta: valor_cesta = float(cesta.get("preco", 0) or 0)
        except: pass

        with st.container(border=True):
            st.markdown('<div class="card-title">💰 Fechamento Financeiro</div>', unsafe_allow_html=True)
            cf1, cf2, cf3, cf4 = st.columns(4)
            travar_financeiro = (bloquear_edicao or pedido_arquivado)
            with cf1: valor_frete = st.number_input("🚚 Frete", min_value=0.0, value=float(pedido.get("valor_frete") or 0), step=1.0, key="frete", disabled=travar_financeiro)
            with cf2: valor_extras = st.number_input("➕ Extras", min_value=0.0, value=float(pedido.get("valor_extras") or 0), step=1.0, key="extras", disabled=travar_financeiro)
            with cf3: desconto = st.number_input("🏷️ Desconto", min_value=0.0, value=float(pedido.get("desconto") or 0), step=1.0, key="desconto", disabled=travar_financeiro)
            
            c_status1, c_status2 = st.columns(2)
            with c_status1:
                # O status operacional gerencia APENAS transações financeiras (Recebido, Pago, Desistência).
                # NUNCA permitimos selecionar "Enviado" ou "Entregue" manualmente por aqui para proteger a logística.
                status_op = ["Recebido", "Pago", "Desistência"]
                status_atual = str(pedido.get("status", "Recebido")).strip().capitalize()
                
                # Se o pedido já estiver em Rota ou Entregue, fixamos ele na lista para leitura correta
                if status_atual in ["Enviado", "Entregue"] and status_atual not in status_op:
                    status_op.append(status_atual)
                    
                status = st.selectbox("Status", status_op, index=status_op.index(status_atual) if status_atual in status_op else 0, disabled=True)
            
            with c_status2:
                st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
                chk_montada = st.checkbox("🧺 Cesta Pronta", value=bool(pedido.get("cesta_montada")), disabled=travar_financeiro)

            horario_combinado = st.text_input("🕒 Horário Combinado de Entrega", value=pedido.get("horario_combinado") or "", placeholder="Ex: 15:30", disabled=travar_financeiro)

        valor_total_calculado = max(0, valor_cesta + valor_adicionais + valor_frete + valor_extras - desconto)

        with st.container(border=True):
            st.markdown('<div class="card-title">🧮 Resumo do Pedido</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="resumo-container">
                    <div class="resumo-row"><span class="resumo-label">🎁 Cesta</span><span class="resumo-val">{formatar_valor(valor_cesta)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🎀 Adicionais</span><span class="resumo-val">{formatar_valor(valor_adicionais)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🚚 Frete</span><span class="resumo-val">{formatar_valor(valor_frete)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">➕ Extras</span><span class="resumo-val">{formatar_valor(valor_extras)}</span></div>
                    <div class="resumo-row"><span class="resumo-label">🏷️ Desconto</span><span class="resumo-val" style="color: #c62828;">- {formatar_valor(desconto)}</span></div>
                    <div class="resumo-row"><span class="resumo-label" style="font-size:14px; font-weight:700;">💰 TOTAL</span><span class="resumo-total-val">{formatar_valor(valor_total_calculado)}</span></div>
                </div>
                """, unsafe_allow_html=True
            )

        with st.container(border=True):
            st.markdown('<div class="card-title">📝 Anotações Internas</div>', unsafe_allow_html=True)
            anotacao = st.text_area("Observações do atendimento", value=pedido.get("anotacoes_internas") or "", height=70, key="campo_anotacao", disabled=pedido_arquivado)
            if not pedido_arquivado:
                if st.button("💾 Salvar Anotação", use_container_width=True):
                    atualizar_anotacao_pedido(pedido["id"], anotacao)
                    st.session_state['msg_geral'] = "✅ Anotação salva!"
                    st.rerun()

        with st.container(border=True):
            st.markdown('<div class="card-title">📷 Gestão de Fotos Polaroid</div>', unsafe_allow_html=True)
            if "msg_foto" in st.session_state:
                if "❌" in st.session_state['msg_foto']: st.error(st.session_state['msg_foto'])
                else: st.success(st.session_state['msg_foto'])
                del st.session_state['msg_foto']
            
            if not pedido_arquivado:
                novas_fotos = st.file_uploader("Adicionar fotos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="up_fotos_multi")
                if novas_fotos:
                    if st.button("📤 Salvar Novas Fotos", use_container_width=True):
                        with st.spinner("Processando..."):
                            sucesso, erro_msg = salvar_fotos_local(pedido["id"], novas_fotos)
                        if sucesso: st.session_state['msg_foto'] = "✅ Foto salva!"
                        else: st.session_state['msg_foto'] = f"❌ Erro Supabase: {erro_msg}"
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
                                    if suc: st.session_state['msg_foto'] = "✅ Foto deletada!"
                                    else: st.session_state['msg_foto'] = f"❌ Erro ao deletar: {err_del}"
                                    st.rerun()
                        else: st.caption("⚠️ Link indisponível.")
            else: st.caption("Nenhuma foto anexada.")

    if "msg_geral" in st.session_state:
        st.success(st.session_state['msg_geral'])
        del st.session_state['msg_geral']

    col_bot1, col_bot2, col_bot3 = st.columns(3)
    
    if not pedido_arquivado:
        with col_bot1:
            if st.button("💾 Salvar Atendimento Completo", use_container_width=True, type="primary", disabled=bloquear_edicao):
                dados = {
                    "cesta_montada": chk_montada,
                    "valor_frete": valor_frete, 
                    "valor_extras": valor_extras, 
                    "desconto": desconto, 
                    "valor_total": valor_total_calculado, 
                    "horario_combinado": horario_combinado, 
                    "itens_consulta": itens_consulta
                }
                atualizar_pedido(pedido["id"], dados)
                st.session_state['msg_geral'] = "✅ Atendimento financeiro salvo com sucesso!"
                st.rerun()

    with col_bot2:
        link_wpp = gerar_whatsapp(pedido, adicionais_pedido, valor_total_calculado, valor_frete, valor_extras, desconto)
        st.link_button("💬 Enviar Resumo no WhatsApp", url=link_wpp, use_container_width=True)

    with col_bot3:
        if st.button("⬅ Voltar para Listagem", use_container_width=True):
            st.switch_page("pages/03_Clientes.py" if pedido_arquivado else "pages/02_Pedidos.py")
