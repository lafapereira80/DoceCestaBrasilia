import streamlit as st
import pandas as pd
from datetime import datetime, date
import re
import requests
import time

from config.supabase import supabase

from services.pedido_service import (
    listar_pedidos_ativos,
    excluir_pedido_completo,
    buscar_pedido,
    salvar_pedido
)
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.produto_service import listar_produtos_por_categoria_id
from services.pedido_adicional_service import salvar_adicionais_pedido

from utils.menu import (
    configurar_pagina,
    menu_lateral
)
from utils.permissao import (
    administrador_operador
)
from utils.impressao_pedido import (
    gerar_pdf_pedidos
)

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS PREMIUM
# =====================================================
st.set_page_config(page_title="Gestão de Pedidos", page_icon="📋", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()
usuario = st.session_state.usuario

if "pedidos_impressao" not in st.session_state: st.session_state["pedidos_impressao"] = []
if "pdf_gerado" not in st.session_state: st.session_state["pdf_gerado"] = None

def atualizar_selecao_impressao(pedido_id):
    st.session_state["pdf_gerado"] = None
    chave = f"imprimir_{pedido_id}"
    if st.session_state.get(chave):
        if pedido_id not in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].append(pedido_id)
    else:
        if pedido_id in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].remove(pedido_id)

def formatar_data(data_str):
    if not data_str: return "-"
    try:
        dt = pd.to_datetime(data_str)
        if pd.isna(dt): return str(data_str)
        return dt.strftime("%d/%m/%Y")
    except: return str(data_str)

# =====================================================
# CACHING DINÂMICO PARA SEÇÕES E CESTAS (BLINDADO)
# =====================================================
@st.cache_data(ttl=5, show_spinner=False)
def obter_secoes_e_cestas_ativas():
    try:
        # Busca exclusivamente as seções ativas na tabela vitrine_secoes ordenadas
        secoes_bd = supabase.table("vitrine_secoes").select("nome", "ativa", "ordem").execute().data or []
        secoes_ativas = sorted([s for s in secoes_bd if s.get("ativa", True)], key=lambda x: x.get("ordem", 99))
        nomes_secoes_ativas = [s["nome"] for s in secoes_ativas]

        # Busca todas as cestas ativas
        cestas_todas = listar_cestas()
        cestas_ativas = [c for c in cestas_todas if c.get("ativa", True)]
        
        # Garante fallback se alguma seção ativa não tiver nome
        if not nomes_secoes_ativas:
            nomes_secoes_ativas = ["Cestas de Café"]

        return nomes_secoes_ativas, sorted(cestas_ativas, key=lambda x: x.get("ordem", 999))
    except:
        return ["Cestas de Café"], []

# =====================================================
# FUNÇÃO LOCAL PARA MUDAR STATUS NO BANCO
# =====================================================
def alterar_para_enviado(pedido_id):
    try:
        supabase.table("pedidos").update({"status": "Enviado"}).eq("id", pedido_id).execute()
        st.toast("🛵 Pedido enviado para a Rota de Entregas!")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao enviar para a rota: {e}")

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 2px !important; letter-spacing: -0.5px; }
h2, h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-top: 15px !important; margin-bottom: 10px !important; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

/* =========================================
   ACORDEÃO (EXPANDER) "NOVO PEDIDO"
========================================== */
div[data-testid="stExpander"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 16px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05) !important; overflow: hidden; margin-bottom: 20px; }
div[data-testid="stExpander"] summary { background: #faf7f3; padding: 15px 20px !important; font-size: 16px !important; font-weight: 800 !important; color: #5a3b28 !important; transition: all 0.3s ease; }
div[data-testid="stExpander"] summary:hover { background: #f3ece6; }
div[data-testid="stExpanderDetails"] { padding: 20px !important; }

/* =========================================
   CARDS DE PEDIDOS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 14px !important; padding: 12px 16px !important; margin-bottom: 10px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.02); transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1); }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #d2bfae !important; box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08); transform: translateY(-2px); }

/* TEXTOS INTERNOS DO CARD */
.cliente-nome { font-weight: 800; color: #2c1e14; font-size: 15px !important; margin-bottom: 2px; }
.valor-pedido { font-weight: 800; color: #2e7d32; font-size: 16px !important; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 10px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.preview-impressao { background-color: #faf7f3 !important; border-left: 4px solid #b06000 !important; border-radius: 8px !important; padding: 15px !important; }

/* =========================================
   BADGES DE STATUS E INFORMAÇÕES
========================================== */
.badge-status { display: inline-block; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; text-align: center; }
.badge-pago { background-color: #e6f4ea; color: #137333; border: 1px solid #ceead6; }
.badge-recebido { background-color: #fef7e0; color: #b06000; border: 1px solid #fce8b2; }
.badge-enviado { background-color: #e8f0fe; color: #1a73e8; border: 1px solid #d2e3fc; }
.badge-desistencia { background-color: #fce8e6; color: #c5221f; border: 1px solid #fad2cf; }
.badge-montada { background-color: #e6f4ea; color: #137333; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 800; border: 1px solid #ceead6; margin-left: 6px; vertical-align: middle; }

/* =========================================
   BOTÕES DENTRO DO CARD (AÇÕES) E CHECKBOX
========================================== */
div[data-testid="stColumn"] div[data-testid="stButton"] button { font-size: 15px !important; padding: 4px 6px !important; border-radius: 10px !important; min-height: 38px !important; border: 1px solid #e8ddd3 !important; background: #faf7f3 !important; transition: all 0.2s ease; display: flex; justify-content: center; align-items: center; }
div[data-testid="stColumn"] div[data-testid="stButton"] button:hover { background: #e8ddd3 !important; transform: scale(1.05); }
div[data-testid="stCheckbox"] { margin-top: 6px; }

/* =========================================
   RESPONSIVIDADE MOBILE E BOTÕES (LADO A LADO)
========================================== */
@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
    .cliente-nome { font-size: 16px !important; }
    
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-top: 10px !important;
        justify-content: space-between;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {
        flex: 1 1 0% !important; 
        min-width: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) button {
        width: 100% !important;
        padding: 6px 0px !important;
    }
}
</style>
""", unsafe_allow_html=True)


st.title("📋 Gestão de Pedidos")
st.caption("Central de acompanhamento de vendas, pagamentos e fila de produção.")

# =====================================================
# CRIAR NOVO PEDIDO MANUAL (EXPANDER PREMIUM)
# =====================================================
@st.fragment
def render_criar_pedido_manual():
    with st.expander("✨ Cadastrar Novo Pedido Manual", expanded=False):
        st.info("💡 Registre aqui pedidos feitos por WhatsApp ou Telefone. Este registro é apenas para controle interno e não dispara notificações automáticas no Telegram.")
        if "man_nome" not in st.session_state: st.session_state.man_nome = ""
        if "man_cpf" not in st.session_state: st.session_state.man_cpf = ""
        if "man_tel" not in st.session_state: st.session_state.man_tel = ""
        if "modo_busca_cli" not in st.session_state: st.session_state.modo_busca_cli = False

        st.markdown("#### 👤 Dados do Comprador")
        cc1, cc_btn, cc2, cc3 = st.columns([3, 1, 2, 2])
        with cc1: nome_comp = st.text_input("Nome *", key="man_nome")
        with cc_btn:
            st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
            if st.button("🔍 Buscar", use_container_width=True, help="Pesquisar cliente já cadastrado no sistema"):
                st.session_state.modo_busca_cli = not st.session_state.modo_busca_cli
                st.rerun(scope="fragment")
        with cc2: cpf_comp = st.text_input("CPF *", key="man_cpf")
        with cc3: tel_comp = st.text_input("Telefone / WhatsApp *", key="man_tel")

        if st.session_state.modo_busca_cli:
            with st.container(border=True):
                st.markdown("<div style='font-size: 14px; font-weight: 800; color: #5a3b28; margin-bottom: 8px;'>🔍 Pesquisar na Base de Clientes</div>", unsafe_allow_html=True)
                termo_busca = st.text_input("Digite o Nome ou CPF para filtrar a lista:", key="man_termo_busca")
                try:
                    res_cli = supabase.table("pedidos").select("cliente_nome, cliente_cpf, cliente_telefone").execute()
                    cli_dict = {}
                    for c in (res_cli.data or []):
                        cpf_c = c.get("cliente_cpf", "").strip()
                        if cpf_c and cpf_c not in cli_dict: cli_dict[cpf_c] = c
                    lista_clientes = list(cli_dict.values())
                    lista_clientes.sort(key=lambda x: x.get("cliente_nome", ""))
                except: lista_clientes = []
                if termo_busca: lista_clientes = [c for c in lista_clientes if termo_busca.lower() in str(c.get("cliente_nome", "")).lower() or termo_busca in str(c.get("cliente_cpf", ""))]
                opcoes_cli = [{"cliente_nome": "--- Clique aqui para selecionar o cliente ---", "cliente_cpf": "", "cliente_telefone": ""}] + lista_clientes
                cli_sel = st.selectbox("Resultados Encontrados:", opcoes_cli, format_func=lambda x: f"{x['cliente_nome']} (CPF: {x['cliente_cpf']})" if x['cliente_cpf'] else x['cliente_nome'], key="man_busca_dropdown")
                if cli_sel and cli_sel["cliente_nome"] != "--- Clique aqui para selecionar o cliente ---":
                    st.session_state.man_nome = cli_sel["cliente_nome"]
                    st.session_state.man_cpf = cli_sel["cliente_cpf"]
                    st.session_state.man_tel = cli_sel["cliente_telefone"]
                    st.session_state.modo_busca_cli = False
                    st.rerun(scope="fragment")
        
        st.markdown("#### 🎁 Seleção da Cesta e Montagem")
        secoes_ativas, todas_cestas = obter_secoes_e_cestas_ativas()
        
        # 1. Caixa de Seleção do Tipo de Seção
        col_sec, col_mod = st.columns(2)
        with col_sec:
            secao_escolhida = st.selectbox("💌 1. Escolha a Seção", secoes_ativas, key="man_sel_secao")
            
        # Filtra as cestas correspondentes à seção escolhida (ignorando maiúsculas/minúsculas para maior segurança)
        cestas_da_secao = [
            c for c in todas_cestas 
            if str(c.get("secao_vitrine", "")).strip().lower() == str(secao_escolhida).strip().lower()
        ]
        
        # 2. Caixa com os Modelos Cadastrados na Seção
        with col_mod:
            cesta_sel = st.selectbox(
                "💝 2. Escolha o Modelo", 
                [{"id": None, "nome": "Selecione o modelo..."}] + cestas_da_secao, 
                format_func=lambda x: x["nome"], 
                key="man_sel_cesta_modelo"
            )

        selecoes_admin = {}
        if cesta_sel and cesta_sel.get("id"):
            cfg = carregar_configuracao_cesta(cesta_sel["id"])
            if cfg:
                for grp in cfg:
                    cat = grp.get("categoria", "Geral")
                    prods = grp.get("produtos", [])
                    maximo = grp.get("max_escolhas", 1)
                    if not prods: continue
                    with st.container(border=True):
                        if maximo == 1:
                            esc = st.radio(f"Opções de {cat}", prods, format_func=lambda p: p["nome"], key=f"man_rad_{cat}")
                            if esc: selecoes_admin[cat] = [esc]
                        else:
                            escs = st.multiselect(f"Opções de {cat}", prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"man_mul_{cat}")
                            selecoes_admin[cat] = escs

        st.markdown("#### 🎀 Adicionais e Extras")
        adicionais_selecionados = []
        try:
            cat_add_id = None
            todas_cats = supabase.table("categorias").select("*").execute().data or []
            for c in todas_cats:
                if c.get("nome", "").strip().lower() == "adicionais": cat_add_id = c["id"]; break
            if cat_add_id:
                prods_add = listar_produtos_por_categoria_id(cat_add_id)
                cols_ad = st.columns(3)
                for i, p_ad in enumerate(prods_add):
                    with cols_ad[i % 3]:
                        chk = st.checkbox(f"{p_ad['nome']} (R$ {p_ad.get('preco', 0)})", key=f"man_chk_ad_{p_ad['id']}")
                        if chk: adicionais_selecionados.append({"produto_id": p_ad["id"], "nome": p_ad["nome"], "preco": float(p_ad.get("preco") or 0)})
        except: pass
        
        st.markdown("#### 💝 Informações de Entrega e Homenageado")
        cd1, cd2 = st.columns(2)
        with cd1: dest_nome = st.text_input("Nome de quem vai receber (Homenageado) *", key="man_dest_nome")
        with cd2: dest_tel = st.text_input("Telefone do Homenageado", key="man_dest_tel")
        
        cm1, cm2 = st.columns(2)
        with cm1: motivo = st.text_input("Motivo (Ex: Aniversário, Aniversário de Casamento)", key="man_motivo")
        with cm2: mensagem = st.text_area("Mensagem do Cartão", height=68, key="man_msg")
        
        with st.container(border=True):
            st.markdown("<div style='font-size: 13px; font-weight: 800; color: #5a3b28; margin-bottom: 8px;'>📍 Endereço de Entrega</div>", unsafe_allow_html=True)
            cx1, cx2 = st.columns([1, 2])
            with cx1: cep_in = st.text_input("CEP (Opcional - Preenche Automático)", max_chars=8, key="man_cep")
            if "man_rua" not in st.session_state: st.session_state.man_rua = ""
            if "man_bairro" not in st.session_state: st.session_state.man_bairro = ""
            if "man_cidade" not in st.session_state: st.session_state.man_cidade = ""
            if "ultimo_cep_man" not in st.session_state: st.session_state.ultimo_cep_man = ""
            cep_limpo = re.sub(r'\D', '', cep_in)
            if len(cep_limpo) == 8 and st.session_state.ultimo_cep_man != cep_limpo:
                try:
                    r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
                    if r.status_code == 200:
                        d = r.json()
                        if "erro" not in d:
                            st.session_state.man_rua = d.get("logradouro", "")
                            st.session_state.man_bairro = d.get("bairro", "")
                            st.session_state.man_cidade = f"{d.get('localidade', '')} - {d.get('uf', '')}"
                except: pass
                st.session_state.ultimo_cep_man = cep_limpo
                st.rerun(scope="fragment")
                
            with cx2: cidade = st.text_input("Cidade-UF", value=st.session_state.man_cidade, key="man_cid_in")
            rua = st.text_input("Rua/Logradouro *", value=st.session_state.man_rua, key="man_rua_in")
            
            cn1, cn2 = st.columns(2)
            with cn1: num = st.text_input("Número/Compl. *", key="man_num")
            with cn2: bairro = st.text_input("Bairro *", value=st.session_state.man_bairro, key="man_bairro_in")
            
            ce1, ce2 = st.columns(2)
            with ce1: dt_ent = st.date_input("Data da Entrega", key="man_dt")
            with ce2: per_ent = st.selectbox("Período Desejado", ["Manhã", "Tarde", "Noite"], key="man_per")
            pedido_esp = st.text_input("Solicitações Especiais (Ex: Entregar exatamente às 08h)", key="man_esp")

        st.markdown("#### 💰 Configuração de Fechamento")
        cf1, cf2, cf3 = st.columns(3)
        with cf1: pag = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Dinheiro", "Transferência"], key="man_pag")
        with cf2: status = st.selectbox("Status Inicial do Pedido", ["Recebido", "Pago"], key="man_status")
        with cf3: frete = st.number_input("Valor do Frete (R$)", min_value=0.0, step=1.0, key="man_frete")
        
        valor_c = float(cesta_sel.get("preco", 0)) if cesta_sel and cesta_sel.get("id") else 0
        valor_a = sum([a["preco"] for a in adicionais_selecionados])
        total = valor_c + valor_a + frete
        
        st.write("")
        st.success(f"**Total Final do Pedido:** R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.write("")
        if st.button("✅ Confirmar e Salvar Pedido", type="primary", use_container_width=True):
            if not nome_comp: st.error("Informe o nome do comprador."); st.stop()
            if not cpf_comp: st.error("Informe o CPF do comprador."); st.stop()
            if not cesta_sel or not cesta_sel.get("id"): st.error("Selecione um modelo de Cesta."); st.stop()
            if not dest_nome: st.error("Informe o nome do destinatário."); st.stop()
            if not rua or not num: st.error("Informe Rua e Número de entrega."); st.stop()
            
            prod_text = "\n".join([f"{c}: {i['nome']}" for c, itens in selecoes_admin.items() for i in itens])
            add_text = ", ".join([a["nome"] for a in adicionais_selecionados])
            cep_str = f" (CEP: {cep_in})" if cep_in.strip() else ""
            end_comp = f"{rua}, {num} - {bairro}, {cidade}{cep_str}"
            
            dados_ped = {
                "cliente_nome": nome_comp.strip(), "cliente_cpf": re.sub(r'\D', '', cpf_comp), "cliente_telefone": re.sub(r'\D', '', tel_comp),
                "destinatario_nome": dest_nome.strip(), "destinatario_telefone": re.sub(r'\D', '', dest_tel), "motivo_homenagem": motivo,
                "cesta_id": cesta_sel["id"], "cesta_nome": cesta_sel["nome"], "produtos": prod_text, "adicionais": add_text,
                "pagamento": pag, "mensagem": mensagem, "pedido_especial": pedido_esp, "endereco": end_comp,
                "data_entrega": dt_ent.strftime("%Y-%m-%d") if dt_ent else str(date.today()), "periodo_entrega": per_ent,
                "status": status, "valor_frete": frete, "valor_total": total, "cesta_montada": False
            }
            suc, p_id = salvar_pedido(dados_ped)
            if suc:
                if adicionais_selecionados: salvar_adicionais_pedido(p_id, adicionais_selecionados)
                st.success("✅ Pedido criado com sucesso! Atualizando...")
                for key in ["man_nome", "man_cpf", "man_tel", "man_rua", "man_bairro", "man_cidade", "man_cep", "ultimo_cep_man", "man_termo_busca"]:
                    if key in st.session_state: del st.session_state[key]
                st.session_state.modo_busca_cli = False
                time.sleep(1)
                st.rerun() 
            else: st.error("Erro ao registrar.")

render_criar_pedido_manual()
st.write("")


# =====================================================
# LISTAGEM COM EXPURGO DE FINALIZADOS
# =====================================================
try: pedidos = listar_pedidos_ativos()
except Exception as erro:
    st.error(f"Erro ao carregar pedidos: {erro}")
    pedidos = []

df = pd.DataFrame(pedidos) if pedidos else pd.DataFrame(columns=["id", "cliente_nome", "status", "created_at", "cesta_montada"])

if not df.empty and "status" in df.columns:
    df["status_limpo"] = df["status"].astype(str).str.strip().str.capitalize()
    df = df[df["status_limpo"] != "Entregue"]
    
if not df.empty and "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at", ascending=False)

def status_visual_html(status):
    status_str = str(status).strip().capitalize()
    if status_str == "Pago": return '<span class="badge-status badge-pago">🟢 Pago</span>'
    elif status_str == "Recebido": return '<span class="badge-status badge-recebido">🟡 Recebido</span>'
    elif status_str == "Enviado": return '<span class="badge-status badge-enviado">🛵 Enviado (Rota)</span>'
    elif status_str == "Desistência" or status_str == "Desistencia": return '<span class="badge-status badge-desistencia">🔴 Desistência</span>'
    return f'<span class="badge-status">{status}</span>'

def mostrar_lista(titulo, status_filtro_lista, eh_pago=False, permitir_exclusao=False):
    if df.empty or "status_limpo" not in df.columns:
        st.info(f"Nenhum pedido registrado em '{titulo}'.")
        return

    status_formatados = [s.capitalize() for s in status_filtro_lista]
    pedidos_status = df[df["status_limpo"].isin(status_formatados)]
    
    if pedidos_status.empty:
        st.info(f"Nenhum pedido nesta etapa no momento.")
        return
        
    pesquisa_local = st.text_input(f"🔍 Buscar cliente em {titulo}:", placeholder="Digite o nome...", key=f"pesquisa_{status_filtro_lista[0]}")
    if pesquisa_local.strip():
        pedidos_status = pedidos_status[pedidos_status["cliente_nome"].fillna("").str.contains(pesquisa_local, case=False)]
        if pedidos_status.empty:
            st.info("Nenhum pedido encontrado com esse nome nesta aba.")
            return

    for _, pedido in pedidos_status.iterrows():
        try:
            pedido_atualizado = buscar_pedido(pedido["id"])
            if pedido_atualizado: pedido = pedido_atualizado
        except: pass

        with st.container(border=True):
            if eh_pago: 
                col_check, col_info1, col_info2, col_status, col_valor, col_acoes = st.columns([0.8, 3.8, 2.5, 1.8, 1.8, 1.8])
                with col_check:
                    esta_marcado = pedido["id"] in st.session_state["pedidos_impressao"]
                    st.checkbox("🖨️", value=esta_marcado, key=f"imprimir_{pedido['id']}", on_change=atualizar_selecao_impressao, args=(pedido["id"],), help="Selecionar para impressão")
            else: 
                col_info1, col_info2, col_status, col_valor, col_acoes = st.columns([4.0, 3.2, 2.0, 2.0, 1.5])

            with col_info1:
                nome_cliente = " ".join(str(pedido.get("cliente_nome", "-")).strip().split())
                st.markdown(f'<div class="cliente-nome">{nome_cliente}</div>', unsafe_allow_html=True)
                
                txt_pagamento = str(pedido.get('pagamento', 'N/I'))
                icone_pag = "💳" if "Cartão" in txt_pagamento or "Cartao" in txt_pagamento else "⚡" if "Pix" in txt_pagamento else "💵"
                st.caption(f"📱 +{pedido.get('cliente_telefone', '-')} | {icone_pag} {txt_pagamento}")

            with col_info2:
                tag_montada = ""
                if eh_pago and pedido.get("cesta_montada"):
                    tag_montada = '<span class="badge-montada">🧺 MONTADA</span>'
                
                st.markdown(f"🎁 **{pedido.get('cesta_nome','-')}** {tag_montada}", unsafe_allow_html=True)
                st.caption(f"🗓️ Entrega: {formatar_data(pedido.get('data_entrega'))}")

            with col_status:
                st.markdown(status_visual_html(pedido.get("status", "-")), unsafe_allow_html=True)

            with col_valor:
                valor = float(pedido.get("valor_total", 0) or 0)
                st.markdown(f'<div class="valor-pedido">R$ {valor:,.2f}</div>'.replace(",", "X").replace(".", ",").replace("X","."), unsafe_allow_html=True)

            with col_acoes:
                status_atual = str(pedido.get("status", "")).strip().capitalize()
                
                if eh_pago:
                    sub_p1, sub_p2 = st.columns(2)
                    with sub_p1:
                        if st.button("👁️", key=f"abrir_{pedido['id']}", help="Abrir Ficha Técnica", use_container_width=True):
                            st.session_state["pedido_aberto"] = pedido["id"]
                            st.switch_page("pages/09_Detalhes_Pedido.py")
                    
                    with sub_p2:
                        if status_atual == "Enviado":
                            st.markdown('<div style="text-align:center; padding-top: 5px; font-size: 18px;" title="Já está na Rota de Entregas">🚚</div>', unsafe_allow_html=True)
                        else:
                            if st.button("🛵", key=f"enviar_{pedido['id']}", help="Mandar para Rotas de Entrega", use_container_width=True):
                                alterar_para_enviado(pedido["id"])
                
                elif permitir_exclusao:
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        if st.button("👁️", key=f"abrir_{pedido['id']}", help="Abrir pedido", use_container_width=True):
                            st.session_state["pedido_aberto"] = pedido["id"]
                            st.switch_page("pages/09_Detalhes_Pedido.py")
                    with sub_col2:
                        if st.button("🗑️", key=f"excluir_{pedido['id']}", help="Excluir pedido permanentemente", use_container_width=True):
                            sucesso, mensagem = excluir_pedido_completo(pedido["id"])
                            if sucesso: st.toast("✅ " + mensagem); st.rerun()
                            else: st.error(mensagem)
                else:
                    if st.button("👁️ Abrir", key=f"abrir_{pedido['id']}", help="Abrir para Conferência", use_container_width=True):
                        st.session_state["pedido_aberto"] = pedido["id"]
                        st.switch_page("pages/09_Detalhes_Pedido.py")

# =====================================================
# ABAS DO PAINEL (LIMPAS E DIRETAS)
# =====================================================
if not df.empty and "status_limpo" in df.columns:
    df_status = df["status_limpo"]
    qtd_rec = len(df_status[df_status == "Recebido"])
    qtd_pag = len(df_status[df_status.isin(["Pago", "Enviado"])])
    qtd_des = len(df_status[df_status.isin(["Desistência", "Desistencia"])])
else: qtd_rec = qtd_pag = qtd_des = 0

aba_recebidos, aba_pagos, aba_desistencias = st.tabs([
    f"📥 Recebidos ({qtd_rec})", 
    f"💰 Pagos / Produção ({qtd_pag})", 
    f"❌ Desistências ({qtd_des})"
])

with aba_recebidos: mostrar_lista("Aguardando Pagamento", ["Recebido"], eh_pago=False)
with aba_pagos: mostrar_lista("Fila de Produção", ["Pago", "Enviado"], eh_pago=True)
with aba_desistencias: mostrar_lista("Desistências", ["Desistência", "Desistencia"], eh_pago=False, permitir_exclusao=(usuario.get("perfil") == "Administrador"))

# =====================================================
# IMPRESSÃO
# =====================================================
if st.session_state["pedidos_impressao"]:
    st.divider()
    col_t_imp1, col_t_imp2 = st.columns([3, 1])
    with col_t_imp1: st.markdown("### 🖨️ Fila de Impressão (Fichas de Produção)")
    with col_t_imp2:
        if st.button("🧹 Limpar Fila", use_container_width=True):
            st.session_state["pedidos_impressao"] = []
            st.session_state["pdf_gerado"] = None
            st.rerun()

    pedidos_selecionados_dados = []
    ids_para_remover = []
    for pid in st.session_state["pedidos_impressao"]:
        try:
            pedido_completo = buscar_pedido(pid)
            if pedido_completo: pedidos_selecionados_dados.append(pedido_completo)
            else: ids_para_remover.append(pid)
        except: ids_para_remover.append(pid)

    for pid in ids_para_remover:
        if pid in st.session_state["pedidos_impressao"]: st.session_state["pedidos_impressao"].remove(pid)

    quantidade = len(pedidos_selecionados_dados)
    if quantidade > 0:
        st.success(f"✅ {quantidade} pedido(s) selecionado(s) e pronto(s) para impressão.")
        st.write("")
        st.markdown("<div style='font-size: 15px; font-weight: 800; color: #5a3b28; margin-bottom: 8px;'>🛒 Revisão dos Pedidos Selecionados</div>", unsafe_allow_html=True)
        for ped in pedidos_selecionados_dados:
            horario = ped.get('horario_combinado', '')
            horario_str = f" ({horario})" if horario else ""
            st.markdown(
                f"""
                <div class="preview-impressao" style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px;">
                            <div class="info-label">👤 Comprador</div>
                            <div style="font-weight: 800; color: #333; font-size: 14px;">{ped.get('cliente_nome', '-')}</div>
                            <div style="font-size: 12px; color: #666;">📱 {ped.get('cliente_telefone', '-')}</div>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <div class="info-label">💝 Homenageado</div>
                            <div style="font-weight: 800; color: #333; font-size: 14px;">{ped.get('destinatario_nome', '-')}</div>
                            <div style="font-size: 12px; color: #666;">📱 {ped.get('destinatario_telefone', '-')}</div>
                        </div>
                        <div style="flex: 1.5; min-width: 250px;">
                            <div class="info-label">🚚 Cesta e Entrega</div>
                            <div style="font-weight: 800; color: #333; font-size: 14px;">🎁 {ped.get('cesta_nome', '-')}</div>
                            <div style="font-size: 12px; color: #666;">🗓️ {formatar_data(ped.get('data_entrega'))} | 🕒 {ped.get('periodo_entrega', '-')}{horario_str}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

        st.write("") 
        formato_impressao = st.radio("Formato de Exportação do PDF", ["📄 Folha A4 - 12 pedidos por página", "🧾 Individual 7x10 cm"], horizontal=True)
        
        st.write("")
        if st.button("📄 Gerar PDF Definitivo", use_container_width=True, type="primary"):
            pdf = gerar_pdf_pedidos(pedidos_selecionados_dados, formato_impressao)
            st.session_state["pdf_gerado"] = pdf
            st.success("✅ PDF gerado com sucesso! Clique no botão abaixo para salvar o arquivo.")
            
        if st.session_state.get("pdf_gerado"):
            st.download_button("⬇️ Baixar PDF", st.session_state["pdf_gerado"], file_name=f"pedidos_producao_{datetime.now().strftime('%d%m%H%M')}.pdf", mime="application/pdf", use_container_width=True)

st.write("")
st.divider()
st.caption("📦 Gerenciamento de Pedidos - Doce Cesta Brasília")
