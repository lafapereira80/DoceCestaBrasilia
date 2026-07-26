import streamlit as st
import json
import urllib.parse
from uuid import uuid4

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
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button,
div[data-testid="stColumn"] > div > div > div > div[data-testid="stLinkButton"] > a { font-size: 12px !important; padding: 2px 6px !important; border-radius: 8px !important; min-height: 34px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
@media (max-width: 768px) { .block-container { padding-top: 0.5rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; } h1 { font-size: 18px !important; } div[data-testid="stVerticalBlockBorderWrapper"] { padding: 8px !important; } .info-value { font-size: 12px !important; } .resumo-total-val { font-size: 17px !important; } .resumo-container { padding: 8px 10px; } }
</style>
""",
unsafe_allow_html=True
)

# =====================================================
# VALIDA PEDIDO ABERTO E BUSCA DADOS
# =====================================================
if "pedido_aberto" not in st.session_state:
    st.error("Nenhum pedido selecionado.")
    st.stop()

pedido_id = st.session_state["pedido_aberto"]
pedido = buscar_pedido(pedido_id)

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()

try: adicionais_pedido = listar_adicionais_pedido(pedido["id"])
except: adicionais_pedido = []

if "editar_pedido" not in st.session_state:
    st.session_state.editar_pedido = False

itens_consulta_salvos = pedido.get("itens_consulta") or {}
if isinstance(itens_consulta_salvos, str):
    try: itens_consulta_salvos = json.loads(itens_consulta_salvos)
    except: itens_consulta_salvos = {}


# =====================================================
# FUNÇÕES DE BANCO (LIMPAS E DIRETAS)
# =====================================================
def atualizar_pedido(pid, dados):
    try: supabase.table("pedidos").update(dados).eq("id", pid).execute(); return True
    except: return False

def atualizar_anotacao_pedido(pid, anotacao):
    try: supabase.table("pedidos").update({"anotacoes_internas": anotacao}).eq("id", pid).execute(); return True
    except: return False


# =====================================================
# FOTOS - INTEGRAÇÃO PURA COM A TABELA 'pedido_fotos'
# =====================================================
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
            
            # 1. Faz o upload pro Bucket (Storage)
            supabase.storage.from_("pedido_fotos").upload(nome_arquivo, conteudo, {"content-type": arquivo.type})
            
            # 2. Cria a URL pública baseada no padrão do Supabase
            url_publica = f"{url_base}/storage/v1/object/public/pedido_fotos/{nome_arquivo}"
            
            # 3. Salva no banco de dados respeitando exatamente as colunas
            supabase.table("pedido_fotos").insert({
                "pedido_id": pid,
                "arquivo": nome_arquivo,
                "nome_original": arquivo.name,
                "url": url_publica
            }).execute()
            
        except Exception as e:
            erros.append(f"Erro ao processar {arquivo.name}: {e}")
            
    if erros: return False, " | ".join(erros)
    return True, ""

def listar_fotos_local(pid):
    try:
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pid).order("created_at").execute()
        fotos = resposta.data or []
        
        # SISTEMA DE RESGATE PARA FOTOS ANTIGAS
        url_base = st.secrets.get("SUPABASE_URL", "").rstrip("/")
        for foto in fotos:
            if not foto.get("url") and foto.get("arquivo"):
                foto["url"] = f"{url_base}/storage/v1/object/public/pedido_fotos/{foto['arquivo']}"
                
        return fotos, ""
    except Exception as e:
        return [], str(e)

def deletar_foto_local(foto_id, caminho_arquivo):
    try:
        # 1. Deleta fisicamente do Bucket
        if caminho_arquivo:
            supabase.storage.from_("pedido_fotos").remove([caminho_arquivo])
        # 2. Deleta o registro do banco
        supabase.table("pedido_fotos").delete().eq("id", foto_id).execute()
        return True, ""
    except Exception as e:
        return False, str(e)


# =====================================================
# FUNÇÕES AUXILIARES E WHATSAPP
# =====================================================
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
    telefone = str(pedido.get("cliente_telefone", "")).replace("(","").replace(")","").replace("-","").replace(" ","")
    return f"https://wa.me/55{telefone}?text={urllib.parse.quote(texto)}"


# =====================================================
# CABEÇALHO & EDIÇÃO DO PEDIDO
# =====================================================
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("📋 Detalhes do Pedido")
    st.caption(f"Pedido #{pedido.get('id')} | Status: **{pedido.get('status','-')}**")
with col_t2:
    if st.button("✏️ Alterar Pedido", use_container_width=True):
        st.session_state.editar_pedido = not st.session_state.editar_pedido

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
                            adicionais_selecionados.append({"nome_produto": nome_prod, "valor_unitario": float(preco_prod) if preco_prod else None})
            else: st.caption("Catálogo vazio.")

        st.divider()
        cs1, cs2 = st.columns(2)
        with cs1:
            if st.button("💾 Salvar Todas as Alterações", use_container_width=True, type="primary"):
                dados = {"cliente_nome": novo_nome, "cliente_telefone": novo_telefone, "destinatario_nome": novo_dest_nome, 
                         "destinatario_telefone": novo_dest_tel, "motivo_homenagem": novo_motivo, "cesta_nome": nova_cesta_nome, 
                         "produtos": novo_produtos, "mensagem": nova_mensagem, "pedido_especial": novo_especial, "endereco": novo_endereco}
                atualizar_pedido(pedido["id"], dados)

                try:
                    supabase.table("pedido_adicionais").delete().eq("pedido_id", pedido["id"]).execute()
                    for ad in adicionais_selecionados: ad["pedido_id"] = pedido["id"]
                    if adicionais_selecionados: 
                        supabase.table("pedido_adicionais").insert(adicionais_selecionados).execute()
                except: pass
                st.session_state.editar_pedido = False
                st.rerun()
        with cs2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.editar_pedido = False
                st.rerun()


# =====================================================
# LAYOUT PRINCIPAL (VISUALIZAÇÃO)
# =====================================================
col_esquerda, col_direita = st.columns([1.2, 1])

with col_esquerda:
    with st.container(border=True):
        st.markdown('<div class="card-title">👤 Cliente (Comprador)</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="info-label">Nome</div><div class="info-value">{pedido.get("cliente_nome") or "-"}</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="info-label">CPF</div><div class="info-value">{pedido.get("cliente_cpf") or "-"}</div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="info-label">Telefone</div><div class="info-value">{pedido.get("cliente_telefone") or "-"}</div>', unsafe_allow_html=True)

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
        with c2: st.markdown(f'<div class="info-label">Pagamento</div><div class="info-value"><span class="pgto-badge">{pedido.get("pagamento","-")}</span></div>', unsafe_allow_html=True)
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
                for adicional in adicionais_pedido:
                    nome = adicional.get("nome_produto", "-")
                    valor = adicional.get("valor_unitario")
                    if valor is not None:
                        valor = float(valor); valor_adicionais += valor
                        st.write(f"• {nome} - {formatar_valor(valor)}")
                    else:
                        st.write(f"• {nome}")
                        val_salvo = float(itens_consulta_salvos.get(nome, 0) or 0)
                        val_dig = st.number_input("Definir valor", min_value=0.0, value=val_salvo, step=1.0, key=f"cons_{nome}")
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
        st.markdown('<div class="card-title">📍 Endereço de Entrega</div>', unsafe_allow_html=True)
        st.text_area("", value=pedido.get("endereco") or "", disabled=True, height=60, key="end_vis")

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
        with cf1: valor_frete = st.number_input("🚚 Frete", min_value=0.0, value=float(pedido.get("valor_frete") or 0), step=1.0, key="frete")
        with cf2: valor_extras = st.number_input("➕ Extras", min_value=0.0, value=float(pedido.get("valor_extras") or 0), step=1.0, key="extras")
        with cf3: desconto = st.number_input("🏷️ Desconto", min_value=0.0, value=float(pedido.get("desconto") or 0), step=1.0, key="desconto")
        with cf4:
            status_op = ["Recebido", "Pago", "Desistência", "Entregue"]
            status_atual = pedido.get("status", "Recebido")
            status = st.selectbox("Status", status_op, index=status_op.index(status_atual) if status_atual in status_op else 0)

        horario_combinado = st.text_input("🕒 Horário Combinado de Entrega", value=pedido.get("horario_combinado") or "", placeholder="Ex: 15:30")

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
        anotacao = st.text_area("Observações do atendimento", value=pedido.get("anotacoes_internas") or "", height=70, key="campo_anotacao")
        if st.button("💾 Salvar Anotação", use_container_width=True):
            atualizar_anotacao_pedido(pedido["id"], anotacao)
            st.session_state['msg_geral'] = "✅ Anotação salva!"
            st.rerun()

    # =====================================================
    # MOTOR DE FOTOS BLINDADO COM FEEDBACK VISUAL
    # =====================================================
    with st.container(border=True):
        st.markdown('<div class="card-title">📷 Gestão de Fotos Polaroid</div>', unsafe_allow_html=True)
        
        if "msg_foto" in st.session_state:
            if "❌" in st.session_state['msg_foto']: st.error(st.session_state['msg_foto'])
            else: st.success(st.session_state['msg_foto'])
            del st.session_state['msg_foto']
        
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
        
        if erro_listar:
            st.error(f"❌ Erro ao buscar: {erro_listar}")
        elif fotos:
            colunas = st.columns(2)
            for i, foto in enumerate(fotos):
                with colunas[i % 2]:
                    link_imagem = foto.get("url")
                    if link_imagem:
                        st.image(link_imagem, caption=foto.get("nome_original", "Foto"), use_container_width=True)
                        if st.button("🗑️ Deletar", key=f"del_foto_{foto['id']}", use_container_width=True):
                            suc, err_del = deletar_foto_local(foto["id"], foto.get("arquivo"))
                            if suc: st.session_state['msg_foto'] = "✅ Foto deletada!"
                            else: st.session_state['msg_foto'] = f"❌ Erro ao deletar: {err_del}"
                            st.rerun()
                    else: st.caption("⚠️ Link da foto indisponível.")
        else:
            st.caption("Nenhuma foto anexada ao pedido.")


if "msg_geral" in st.session_state:
    st.success(st.session_state['msg_geral'])
    del st.session_state['msg_geral']

col_bot1, col_bot2 = st.columns(2)
with col_bot1:
    if st.button("💾 Salvar Atendimento Completo", use_container_width=True, type="primary"):
        dados = {"status": status, "valor_frete": valor_frete, "valor_extras": valor_extras, "desconto": desconto, "valor_total": valor_total_calculado, "horario_combinado": horario_combinado, "itens_consulta": itens_consulta}
        atualizar_pedido(pedido["id"], dados)
        st.session_state['msg_geral'] = "✅ Atendimento financeiro salvo com sucesso!"
        st.rerun()
with col_bot2:
    if st.button("⬅ Voltar para Pedidos", use_container_width=True):
        st.switch_page("pages/02_Pedidos.py")
