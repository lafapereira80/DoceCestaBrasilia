import streamlit as st
import json
import urllib.parse
import pandas as pd
from uuid import uuid4

# Importando apenas o que temos certeza que existe no cache antigo para evitar erros!
from services.pedido_service import (
    buscar_pedido
)

from services.pedido_adicional_service import (
    listar_adicionais_pedido
)

from config.supabase import supabase

from services.cesta_service import (
    buscar_cesta,
    listar_cestas
)

from services.configuracao_cesta_service import (
    carregar_configuracao_cesta
)

from utils.menu import (
    configurar_pagina,
    menu_lateral
)

from utils.permissao import (
    administrador_operador
)


# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Detalhes do Pedido",
    page_icon="📋",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CSS ULTRA COMPACTO, ISOLADO E RESPONSIVO
# =====================================================

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
    if st.button("⬅ Voltar"):
        st.switch_page("pages/02_Pedidos.py")
    st.stop()

pedido_id = st.session_state["pedido_aberto"]

try:
    pedido = buscar_pedido(pedido_id)
except Exception as erro:
    st.error(f"Erro ao carregar pedido: {erro}"); st.stop()

if not pedido:
    st.error("Pedido não encontrado."); st.stop()

try:
    adicionais_pedido = listar_adicionais_pedido(pedido["id"])
except:
    adicionais_pedido = []

if "editar_pedido" not in st.session_state:
    st.session_state.editar_pedido = False

itens_consulta_salvos = pedido.get("itens_consulta")
if not itens_consulta_salvos: itens_consulta_salvos = {}
elif isinstance(itens_consulta_salvos, str):
    try: itens_consulta_salvos = json.loads(itens_consulta_salvos)
    except: itens_consulta_salvos = {}
if not isinstance(itens_consulta_salvos, dict): itens_consulta_salvos = {}


# =====================================================
# FUNÇÕES DE BANCO DE DADOS (INCORPORADAS PARA EVITAR ERRO DE CACHE)
# =====================================================

def atualizar_pedido(pid, dados):
    """Atualiza as informações de um pedido diretamente no banco"""
    try:
        supabase.table("pedidos").update(dados).eq("id", pid).execute()
        return True
    except Exception as erro:
        print(f"Erro ao atualizar pedido: {erro}")
        return False

def atualizar_anotacao_pedido(pid, anotacao):
    """Atualiza a anotação do pedido diretamente no banco"""
    try:
        supabase.table("pedidos").update({"anotacoes_internas": anotacao}).eq("id", pid).execute()
        return True
    except Exception as erro:
        print(f"Erro ao atualizar anotação: {erro}")
        return False


# =====================================================
# FUNÇÕES DE FOTO LOCAIS
# =====================================================

def salvar_fotos_local(pid, arquivos):
    if not arquivos: return
    if not isinstance(arquivos, list): arquivos = [arquivos]
    for arquivo in arquivos:
        try:
            extensao = arquivo.name.split(".")[-1]
            nome_arquivo = f"{pid}/{uuid4()}.{extensao}"
            conteudo = arquivo.getvalue()
            supabase.storage.from_("pedido_fotos").upload(
                nome_arquivo, conteudo, {"content-type": arquivo.type}
            )
            supabase.table("pedido_fotos").insert({
                "pedido_id": pid, "arquivo": nome_arquivo, "nome_original": arquivo.name
            }).execute()
        except Exception as e:
            print(f"Erro ao salvar foto: {e}")

def listar_fotos_local(pid):
    try:
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pid).order("created_at").execute()
        fotos = resposta.data or []
        fotos_validas = []
        url_base = st.secrets["SUPABASE_URL"].rstrip("/")
        for foto in fotos:
            caminho = foto.get("arquivo")
            if caminho:
                foto["url"] = f"{url_base}/storage/v1/object/public/pedido_fotos/{caminho}"
                fotos_validas.append(foto)
        return fotos_validas
    except Exception as e:
        print(f"Erro ao listar fotos: {e}")
        return []

def deletar_foto_local(foto_id, caminho_arquivo):
    try:
        supabase.storage.from_("pedido_fotos").remove([caminho_arquivo])
        supabase.table("pedido_fotos").delete().eq("id", foto_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return False


# =====================================================
# FUNÇÕES AUXILIARES E WHATSAPP
# =====================================================

def formatar_valor(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
    except: return "R$ 0,00"

def limpar_telefone(numero):
    return str(numero).replace("(","").replace(")","").replace("-","").replace(" ","")

def formatar_data(data):
    if not data: return "-"
    try:
        ano, mes, dia = str(data)[:10].split("-")
        return f"{dia}/{mes}/{ano}"
    except: return str(data)

def gerar_whatsapp(pedido, adicionais, valor_final, frete_atual, extras_atual, desconto_atual):
    itens_consulta = pedido.get("itens_consulta")
    if not itens_consulta: itens_consulta = {}
    elif isinstance(itens_consulta, str):
        try: itens_consulta = json.loads(itens_consulta)
        except: itens_consulta = {}
    if not isinstance(itens_consulta, dict): itens_consulta = {}

    lista_adicionais = []
    for item in adicionais:
        nome = item.get("nome_produto", "-")
        valor = item.get("valor_unitario")
        if valor is not None: lista_adicionais.append(f"• {nome} - {formatar_valor(valor)}")
        else:
            valor_manual = itens_consulta.get(nome, 0)
            if valor_manual: lista_adicionais.append(f"• {nome} - {formatar_valor(valor_manual)}")
            else: lista_adicionais.append(f"• {nome} (sob consulta)")

    dest_nome = (pedido.get("destinatario_nome") or "").strip()
    dest_tel = (pedido.get("destinatario_telefone") or "").strip()
    motivo = (pedido.get("motivo_homenagem") or "").strip()
    
    texto_destinatario = ""
    if dest_nome or dest_tel or motivo:
        texto_destinatario = "💝 *Entrega Especial Para:*\n"
        if dest_nome: texto_destinatario += f"Nome: {dest_nome}\n"
        if dest_tel: texto_destinatario += f"Contato: {dest_tel}\n"
        if motivo: texto_destinatario += f"Motivo: {motivo}\n"
        texto_destinatario += "\n"
        
    texto_valores = ""
    if float(frete_atual or 0) > 0: texto_valores += f"🚚 Frete: {formatar_valor(frete_atual)}\n"
    if float(extras_atual or 0) > 0: texto_valores += f"➕ Extras/Acréscimos: {formatar_valor(extras_atual)}\n"
    if float(desconto_atual or 0) > 0: texto_valores += f"🏷️ Desconto: - {formatar_valor(desconto_atual)}\n"

    texto = (
        f"🎁 *Doce Cesta Brasília*\n\n"
        f"Olá {pedido.get('cliente_nome','') if pedido else ''}!\n\n"
        f"{texto_destinatario}"
        f"🎀 Cesta: {pedido.get('cesta_nome','-') if pedido else '-'}\n\n"
        f"🛒 Produtos:\n{pedido.get('produtos','-') if pedido else '-'}\n\n"
        f"🎀 Adicionais:\n{chr(10).join(lista_adicionais)}\n\n"
        f"📍 Entrega:\n"
        f"Data: {formatar_data(pedido.get('data_entrega')) if pedido else '-'}\n"
        f"Período: {pedido.get('periodo_entrega','-') if pedido else '-'}\n"
        f"Horário: {pedido.get('horario_combinado','-') if pedido else '-'}\n\n"
        f"💳 Pagamento: {pedido.get('pagamento','-') if pedido else '-'}\n\n"
        f"💰 *Resumo Financeiro*\n{texto_valores}"
        f"✅ *Valor Final: {formatar_valor(valor_final)}*\n\nObrigado! ❤️"
    )
    telefone = limpar_telefone(pedido.get("cliente_telefone", ""))
    return f"https://wa.me/55{telefone}?text={urllib.parse.quote(texto)}"


# =====================================================
# CABEÇALHO & EDIÇÃO DO PEDIDO (MODO SUPER ADMIN)
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
        aba_dados, aba_cesta, aba_adicionais = st.tabs(["👤 Dados", "🎁 Cesta e Produtos", "🎀 Adicionais e Extras"])

        # ------------------- ABA 1: DADOS -------------------
        with aba_dados:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.write("**Comprador**")
                novo_nome = st.text_input("Nome", value=pedido.get("cliente_nome") or "")
                novo_telefone = st.text_input("Telefone", value=pedido.get("cliente_telefone") or "")
            with col_d2:
                st.write("**Destinatário (Homenageado)**")
                novo_dest_nome = st.text_input("Nome Destinatário", value=pedido.get("destinatario_nome") or "")
                novo_dest_tel = st.text_input("Telefone Destinatário", value=pedido.get("destinatario_telefone") or "")
                novo_motivo = st.text_input("Motivo", value=pedido.get("motivo_homenagem") or "")

        # ------------------- ABA 2: CESTA, PRODUTOS E MSG -------------------
        with aba_cesta:
            try:
                cestas = listar_cestas()
                nomes_cestas = [c.get("nome", "") for c in cestas]
            except: 
                cestas = []
                nomes_cestas = []
            
            cesta_atual = pedido.get("cesta_nome") or ""
            nova_cesta_nome = st.selectbox("🎁 Cesta Base", nomes_cestas, index=nomes_cestas.index(cesta_atual) if cesta_atual in nomes_cestas else 0) if nomes_cestas else cesta_atual
            cesta_selecionada = next((c for c in cestas if c.get("nome") == nova_cesta_nome), None)
            
            novo_produtos = pedido.get("produtos") or ""
            
            if cesta_selecionada:
                configuracao_cesta = carregar_configuracao_cesta(cesta_selecionada["id"])
                
                if configuracao_cesta:
                    st.markdown("### 🍓 Personalização da Cesta")
                    st.caption("O sistema marcou as opções originais do cliente. Altere o que for necessário.")
                    
                    selecoes_admin = {}
                    texto_produtos_atuais = pedido.get("produtos") or ""

                    for grupo in configuracao_cesta:
                        categoria = grupo.get("categoria", "Sem categoria")
                        produtos = grupo.get("produtos", [])
                        minimo = grupo.get("min_escolhas", 0)
                        maximo = grupo.get("max_escolhas", 1)

                        if not produtos: continue

                        with st.container(border=True):
                            defaults_encontrados = []
                            for p in produtos:
                                if p["nome"] in texto_produtos_atuais:
                                    defaults_encontrados.append(p)
                            
                            st.markdown(f"**📦 {categoria}**")
                            
                            if maximo == 1:
                                idx_default = 0
                                if defaults_encontrados:
                                    try: idx_default = produtos.index(defaults_encontrados[0])
                                    except: pass
                                    
                                escolhido = st.radio(f"Escolha 1 ({categoria})", produtos, format_func=lambda p: p["nome"], index=idx_default, key=f"edit_rad_{categoria}")
                                if escolhido: selecoes_admin[categoria] = [escolhido]
                            else:
                                escolhidos = st.multiselect(f"Escolha entre {minimo} e {maximo}", produtos, format_func=lambda p: p["nome"], default=defaults_encontrados, max_selections=maximo, key=f"edit_mult_{categoria}")
                                selecoes_admin[categoria] = escolhidos

                    produtos_escolhidos_texto = [f"{cat_nome}: {item['nome']}" for cat_nome, itens in selecoes_admin.items() for item in itens]
                    novo_produtos = "\n".join(produtos_escolhidos_texto)
                else:
                    st.info("Essa cesta não possui configurações ativas de produtos.")

            st.divider()
            st.markdown('<div class="card-title">📍 Destino, Mensagem e Observações</div>', unsafe_allow_html=True)
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                nova_mensagem = st.text_area("💌 Mensagem do Cartão", value=pedido.get("mensagem") or "", height=120)
            with col_m2:
                novo_endereco = st.text_area("📍 Endereço de Entrega", value=pedido.get("endereco") or "", height=120)
                
            novo_especial = st.text_input("✨ Solicitação / Pedido Especial", value=pedido.get("pedido_especial") or "")

        # ------------------- ABA 3: ADICIONAIS E ENTREGA -------------------
        with aba_adicionais:
            st.write("🎀 **Catálogo de Adicionais**")
            
            adicionais_catalogo = []
            try:
                cat_res = supabase.table("categorias").select("id, nome").execute()
                cats = cat_res.data or []
                cat_adicionais_id = next((c["id"] for c in cats if "adicionais" in str(c.get("nome", "")).lower()), None)
                if cat_adicionais_id:
                    prod_res = supabase.table("produtos").select("*").eq("categoria_id", cat_adicionais_id).execute()
                    adicionais_catalogo = prod_res.data or []
            except: pass
            
            nomes_adicionais_atuais = [a.get("nome_produto") for a in adicionais_pedido]
            adicionais_selecionados = []

            if adicionais_catalogo:
                cols = st.columns(3)
                for i, prod in enumerate(adicionais_catalogo):
                    nome_prod = prod.get("nome", "")
                    preco_prod = prod.get("preco")
                    selecionado = nome_prod in nomes_adicionais_atuais
                    texto_cb = f"{nome_prod} - R$ {float(preco_prod):.2f}".replace(".",",") if preco_prod else f"{nome_prod} (Consulta)"
                    
                    with cols[i % 3]:
                        if st.checkbox(texto_cb, value=selecionado, key=f"chk_ad_{prod.get('id')}"):
                            adicionais_selecionados.append({"nome_produto": nome_prod, "valor_unitario": float(preco_prod) if preco_prod else None})
            else:
                st.caption("Nenhum adicional no catálogo.")
            
            st.divider()
            st.write("➕ **Adicionais Avulsos**")
            
            nomes_no_catalogo = [p.get("nome") for p in adicionais_catalogo]
            adicionais_avulsos = [a for a in adicionais_pedido if a.get("nome_produto") not in nomes_no_catalogo]
            
            df_ad = pd.DataFrame(adicionais_avulsos) if adicionais_avulsos else pd.DataFrame(columns=["nome_produto", "valor_unitario"])
            if not df_ad.empty and "nome_produto" in df_ad.columns: df_ad = df_ad[["nome_produto", "valor_unitario"]]
            else: df_ad = pd.DataFrame(columns=["nome_produto", "valor_unitario"])
            
            df_editado = st.data_editor(
                df_ad,
                column_config={"nome_produto": st.column_config.TextColumn("Nome Específico", required=True), "valor_unitario": st.column_config.NumberColumn("Valor (R$)", min_value=0.0, format="%.2f")},
                num_rows="dynamic", use_container_width=True, key="editor_adicionais_avulsos"
            )

        # ------------------- BOTÕES DE SALVAMENTO -------------------
        st.divider()
        col_salvar, col_cancelar = st.columns(2)
        with col_salvar:
            if st.button("💾 Salvar Todas as Alterações", use_container_width=True, type="primary"):
                dados = {
                    "cliente_nome": novo_nome, 
                    "cliente_telefone": novo_telefone, 
                    "destinatario_nome": novo_dest_nome, 
                    "destinatario_telefone": novo_dest_tel, 
                    "motivo_homenagem": novo_motivo, 
                    "cesta_nome": nova_cesta_nome, 
                    "produtos": novo_produtos,
                    "mensagem": nova_mensagem, 
                    "pedido_especial": novo_especial, 
                    "endereco": novo_endereco
                }
                atualizar_pedido(pedido["id"], dados)

                try:
                    supabase.table("pedido_adicionais").delete().eq("pedido_id", pedido["id"]).execute()
                    lista_salvar = list(adicionais_selecionados)
                    for index, row in df_editado.iterrows():
                        nome_ad = str(row["nome_produto"]).strip()
                        if nome_ad and nome_ad != "nan":
                            val = row["valor_unitario"]
                            lista_salvar.append({"nome_produto": nome_ad, "valor_unitario": float(val) if pd.notna(val) else None})
                    
                    for ad in lista_salvar: ad["pedido_id"] = pedido["id"]
                    if lista_salvar: supabase.table("pedido_adicionais").insert(lista_salvar).execute()
                except: pass

                st.success("Pedido alterado com sucesso!")
                st.session_state.editar_pedido = False
                st.rerun()

        with col_cancelar:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.editar_pedido = False
                st.rerun()


# =====================================================
# LAYOUT PRINCIPAL (VISUALIZAÇÃO DOS DADOS SALVOS)
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
                        valor = float(valor)
                        valor_adicionais += valor
                        st.write(f"• {nome} - {formatar_valor(valor)}")
                    else:
                        st.write(f"• {nome}")
                        valor_salvo = float(itens_consulta_salvos.get(nome, 0) or 0)
                        valor_digitado = st.number_input("Definir valor", min_value=0.0, value=valor_salvo, step=1.0, key=f"consulta_{nome}")
                        itens_consulta[nome] = valor_digitado
                        if valor_digitado > 0:
                            valor_consulta += valor_digitado
                            valor_adicionais += valor_digitado
            else: st.caption("Nenhum adicional selecionado.")

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        with st.container(border=True):
            st.markdown('<div class="card-title">💌 Mensagem da Cesta</div>', unsafe_allow_html=True)
            st.text_area("", value=pedido.get("mensagem") or "", disabled=True, height=60, key="mensagem_cliente")

    with c_m2:
        with st.container(border=True):
            st.markdown('<div class="card-title">✨ Pedido Especial</div>', unsafe_allow_html=True)
            st.text_area("", value=pedido.get("pedido_especial") or "", disabled=True, height=60, key="pedido_especial")

    with st.container(border=True):
        st.markdown('<div class="card-title">📍 Endereço de Entrega</div>', unsafe_allow_html=True)
        st.text_area("", value=pedido.get("endereco") or "", disabled=True, height=60, key="endereco_entrega_vis")


with col_direita:
    valor_cesta = 0.0
    try:
        if pedido.get("cesta_id"):
            cesta = buscar_cesta(pedido["cesta_id"])
            if cesta: valor_cesta = float(cesta.get("preco", 0) or 0)
    except: valor_cesta = 0.0

    with st.container(border=True):
        st.markdown('<div class="card-title">💰 Fechamento Financeiro</div>', unsafe_allow_html=True)
        cf1, cf2, cf3, cf4 = st.columns(4)
        with cf1: valor_frete = st.number_input("🚚 Frete", min_value=0.0, value=float(pedido.get("valor_frete") or 0), step=1.0, key="frete")
        with cf2: valor_extras = st.number_input("➕ Extras", min_value=0.0, value=float(pedido.get("valor_extras") or 0), step=1.0, key="extras")
        with cf3: desconto = st.number_input("🏷️ Desconto", min_value=0.0, value=float(pedido.get("desconto") or 0), step=1.0, key="desconto")
        with cf4:
            status_opcoes = ["Recebido", "Pago", "Desistência", "Entregue"]
            status_atual = pedido.get("status", "Recebido")
            if status_atual not in status_opcoes: status_atual = "Recebido"
            status = st.selectbox("Status", status_opcoes, index=status_opcoes.index(status_atual))

        horario_combinado = st.text_input("🕒 Horário Combinado de Entrega", value=pedido.get("horario_combinado") or "", placeholder="Ex: 15:30")

    valor_total_calculado = max(0, valor_cesta + valor_adicionais + valor_frete + valor_extras - desconto)

    with st.container(border=True):
        st.markdown('<div class="card-title">🧮 Resumo do Pedido</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="resumo-container">
                <div class="resumo-row"><span class="resumo-label">🎁 Cesta</span><span class="resumo-val">{formatar_valor(valor_cesta)}</span></div>
                <div class="resumo-row"><span class="resumo-label">🎀 Adicionais</span><span class="resumo-val">{formatar_valor(valor_adicionais)}</span></div>
                <div class="resumo-row"><span class="resumo-label">⚠️ Sob consulta</span><span class="resumo-val">{formatar_valor(valor_consulta)}</span></div>
                <div class="resumo-row"><span class="resumo-label">🚚 Frete</span><span class="resumo-val">{formatar_valor(valor_frete)}</span></div>
                <div class="resumo-row"><span class="resumo-label">➕ Extras</span><span class="resumo-val">{formatar_valor(valor_extras)}</span></div>
                <div class="resumo-row"><span class="resumo-label">🏷️ Desconto</span><span class="resumo-val" style="color: #c62828;">- {formatar_valor(desconto)}</span></div>
                <div class="resumo-row"><span class="resumo-label">💳 Pagamento</span><span class="pgto-badge">{pedido.get('pagamento','-')}</span></div>
                <div class="resumo-row"><span class="resumo-label" style="font-size:14px; font-weight:700;">💰 TOTAL</span><span class="resumo-total-val">{formatar_valor(valor_total_calculado)}</span></div>
            </div>
            """, unsafe_allow_html=True
        )

    with st.container(border=True):
        st.markdown('<div class="card-title">📲 Atendimento WhatsApp</div>', unsafe_allow_html=True)
        if valor_total_calculado > 0:
            link_whatsapp = gerar_whatsapp(pedido, adicionais_pedido, valor_total_calculado, valor_frete, valor_extras, desconto)
            st.link_button("📲 Enviar resumo pelo WhatsApp", link_whatsapp, use_container_width=True)
        else: st.info("Defina os valores para liberar o WhatsApp.")

    with st.container(border=True):
        st.markdown('<div class="card-title">📝 Anotações Internas</div>', unsafe_allow_html=True)
        anotacao = st.text_area("Observações do atendimento", value=pedido.get("anotacoes_internas") or "", height=70, key="campo_anotacao")
        if st.button("💾 Salvar Anotação", use_container_width=True):
            atualizar_anotacao_pedido(pedido["id"], anotacao)
            st.success("✅ Anotação salva!")
            st.rerun()

    # =====================================================
    # MOTOR DE FOTOS LOCAL: GESTÃO DE MÚLTIPLAS FOTOS & DELEÇÃO
    # =====================================================
    with st.container(border=True):
        st.markdown('<div class="card-title">📷 Gestão de Fotos Polaroid</div>', unsafe_allow_html=True)
        
        novas_fotos = st.file_uploader(
            "Adicionar uma ou mais fotos", 
            type=["jpg", "jpeg", "png", "webp"], 
            accept_multiple_files=True, 
            key="up_fotos_multi"
        )
        
        if novas_fotos:
            if st.button("📤 Salvar Novas Fotos", use_container_width=True):
                with st.spinner("Enviando fotos..."):
                    salvar_fotos_local(pedido["id"], novas_fotos)
                st.success("✅ Fotos enviadas com sucesso!")
                st.rerun()

        st.divider()

        try:
            fotos = listar_fotos_local(pedido["id"])
            if fotos:
                colunas = st.columns(2)
                for i, foto in enumerate(fotos):
                    with colunas[i % 2]:
                        link_imagem = foto.get("url")
                        caminho_arquivo = foto.get("arquivo")

                        if link_imagem:
                            st.image(link_imagem, caption=foto.get("nome_original", "Foto"), use_container_width=True)
                            if st.button("🗑️ Deletar Foto", key=f"del_foto_{foto.get('id')}", use_container_width=True):
                                if caminho_arquivo:
                                    sucesso = deletar_foto_local(foto["id"], caminho_arquivo)
                                    if sucesso:
                                        st.rerun()
                                    else:
                                        st.error("Erro ao deletar arquivo.")
                        else:
                            st.caption("⚠️ Link da foto indisponível.")
            else:
                st.caption("Nenhuma foto enviada.")
        except Exception as erro:
            st.error(f"Erro ao carregar fotos na tela: {erro}")


col_bot1, col_bot2 = st.columns(2)
with col_bot1:
    if st.button("💾 Salvar Atendimento Completo", use_container_width=True, type="primary"):
        dados = {"status": status, "valor_frete": valor_frete, "valor_extras": valor_extras, "desconto": desconto, "valor_total": valor_total_calculado, "horario_combinado": horario_combinado, "itens_consulta": itens_consulta}
        atualizar_pedido(pedido["id"], dados)
        st.success("✅ Atendimento salvo com sucesso!")
        st.rerun()
with col_bot2:
    if st.button("⬅ Voltar para Pedidos", use_container_width=True):
        st.switch_page("pages/02_Pedidos.py")
