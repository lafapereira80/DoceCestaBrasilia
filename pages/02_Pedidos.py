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
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Pedidos",
    page_icon="📋",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CONTROLE DE IMPRESSÃO
# =====================================================

if "pedidos_impressao" not in st.session_state:
    st.session_state["pedidos_impressao"] = []

if "pdf_gerado" not in st.session_state:
    st.session_state["pdf_gerado"] = None


# =====================================================
# FUNÇÃO CHECKBOX IMPRESSÃO
# =====================================================

def atualizar_selecao_impressao(pedido_id):
    st.session_state["pdf_gerado"] = None
    chave = f"imprimir_{pedido_id}"
    
    if st.session_state.get(chave):
        if pedido_id not in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].append(pedido_id)
    else:
        if pedido_id in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].remove(pedido_id)


# =====================================================
# FORMATADOR DE DATA BRASILEIRO (DD/MM/AAAA)
# =====================================================

def formatar_data(data_str):
    if not data_str:
        return "-"
    try:
        dt = pd.to_datetime(data_str)
        if pd.isna(dt):
            return str(data_str)
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(data_str)


# =====================================================
# CSS COMPACTO E ISOLADO (COM RESPONSIVIDADE MOBILE)
# =====================================================

st.markdown(
"""
<style>
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1200px; }
h1 { font-size: 24px !important; font-weight: 700 !important; color: #5a3b28; margin-bottom: 2px !important; }
h2, h3 { font-size: 16px !important; font-weight: 700 !important; color: #5a3b28; margin-top: 15px !important; margin-bottom: 8px !important; }
.block-container p, .block-container label { font-family: Arial, sans-serif !important; font-size: 13px !important; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 10px 16px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #dfcdbb !important; box-shadow: 0 2px 6px rgba(90, 59, 40, 0.08); }

.preview-impressao { background-color: #fffbf7; border-left: 4px solid #b06000 !important; }
.badge-status { display: inline-block; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 12px !important; text-align: center; }
.badge-pago { background-color: #e6f4ea; color: #137333; }
.badge-recebido { background-color: #fef7e0; color: #b06000; }
.badge-desistencia { background-color: #fce8e6; color: #c5221f; }
.info-label { font-weight: 800; color: #9d7d65; font-size: 10px !important; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.cliente-nome { font-weight: 700; color: #333; font-size: 14px !important; }
.valor-pedido { font-weight: 700; color: #2e7d32; font-size: 14px !important; }

div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] button {
    font-size: 14px !important; padding: 2px !important; border-radius: 8px !important; min-height: 36px !important; display: flex !important; align-items: center !important; justify-content: center !important;
}
div[data-testid="stCheckbox"] { margin-top: 4px; }

@media (max-width: 768px) {
    .block-container { padding-top: 0.5rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    h1 { font-size: 20px !important; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 10px 12px !important;
    }

    div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        flex-direction: row !important;
        display: flex !important;
        gap: 8px !important;
        margin-top: 6px !important;
    }
    
    div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 50% !important;
        min-width: 0 !important;
        flex: 1 1 0% !important;
    }

    .cliente-nome { font-size: 15px !important; margin-bottom: 2px; }
    .info-label { font-size: 11px !important; margin-top: 4px; }
    .valor-pedido { font-size: 16px !important; margin-top: 4px; }
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# TÍTULO DA PÁGINA
# =====================================================
st.title("📋 Gestão de Pedidos")
st.caption("Acompanhamento do fluxo completo de compras.")


# =====================================================
# NOVO: CRIAR PEDIDO MANUAL (WHATSAPP / RECORRENTES)
# =====================================================
@st.fragment
def render_criar_pedido_manual():
    with st.expander("➕ CRIAR NOVO PEDIDO MANUALMENTE", expanded=False):
        st.info("Registre aqui os pedidos feitos por clientes recorrentes via WhatsApp ou telefone. Este registro é interno e não notifica o Telegram.")
        
        # --- 1. BUSCA DE CLIENTES RECORRENTES ---
        st.markdown("#### 👤 Comprador")
        
        try:
            # Busca histórico para autocompletar
            res_cli = supabase.table("pedidos").select("cliente_nome, cliente_cpf, cliente_telefone").execute()
            cli_dict = {}
            for c in (res_cli.data or []):
                cpf_c = c.get("cliente_cpf", "").strip()
                if cpf_c and cpf_c not in cli_dict:
                    cli_dict[cpf_c] = c
            lista_clientes = list(cli_dict.values())
            lista_clientes.sort(key=lambda x: x.get("cliente_nome", ""))
        except:
            lista_clientes = []

        tipo_cliente = st.radio("Origem do Cliente:", ["Novo Cliente", "Cliente Recorrente"], horizontal=True, key="man_tipo_cli")
        
        nome_val, cpf_val, tel_val = "", "", ""
        if tipo_cliente == "Cliente Recorrente":
            if lista_clientes:
                cli_sel = st.selectbox("Selecione o Cliente (Busca por Nome ou CPF)", lista_clientes, format_func=lambda x: f"{x['cliente_nome']} (CPF: {x['cliente_cpf']})", key="man_busca_cli")
                if cli_sel:
                    nome_val = cli_sel["cliente_nome"]
                    cpf_val = cli_sel["cliente_cpf"]
                    tel_val = cli_sel["cliente_telefone"]
            else:
                st.warning("Nenhum cliente recorrente encontrado no histórico.")

        cc1, cc2, cc3 = st.columns(3)
        with cc1: nome_comp = st.text_input("Nome *", value=nome_val, key="man_nome")
        with cc2: cpf_comp = st.text_input("CPF *", value=cpf_val, key="man_cpf")
        with cc3: tel_comp = st.text_input("Telefone *", value=tel_val, key="man_tel")
        
        # --- 2. CESTA E PRODUTOS ---
        st.markdown("#### 🎁 Cesta e Produtos")
        try: 
            cestas = [c for c in listar_cestas() if c.get("ativa", True)]
        except: 
            cestas = []
            
        cesta_sel = st.selectbox("Selecione a Cesta Base *", [{"id": None, "nome": "Selecione..."}] + cestas, format_func=lambda x: x["nome"], key="man_sel_cesta")
        
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
                            esc = st.radio(cat, prods, format_func=lambda p: p["nome"], key=f"man_rad_{cat}")
                            if esc: selecoes_admin[cat] = [esc]
                        else:
                            escs = st.multiselect(cat, prods, format_func=lambda p: p["nome"], max_selections=maximo, key=f"man_mul_{cat}")
                            selecoes_admin[cat] = escs

        # --- 3. ADICIONAIS ---
        st.markdown("#### 🎀 Complementos")
        adicionais_selecionados = []
        try:
            cat_add_id = None
            todas_cats = supabase.table("categorias").select("*").execute().data or []
            for c in todas_cats:
                if c.get("nome", "").strip().lower() == "adicionais":
                    cat_add_id = c["id"]
                    break
            
            if cat_add_id:
                prods_add = listar_produtos_por_categoria_id(cat_add_id)
                cols_ad = st.columns(3)
                for i, p_ad in enumerate(prods_add):
                    with cols_ad[i % 3]:
                        chk = st.checkbox(f"{p_ad['nome']} (R$ {p_ad.get('preco', 0)})", key=f"man_chk_ad_{p_ad['id']}")
                        if chk:
                            adicionais_selecionados.append({
                                "produto_id": p_ad["id"], 
                                "nome": p_ad["nome"], 
                                "preco": float(p_ad.get("preco") or 0)
                            })
        except: pass
        
        # --- 4. HOMENAGEADO E ENTREGA ---
        st.markdown("#### 💝 Homenageado e Entrega")
        cd1, cd2 = st.columns(2)
        with cd1: dest_nome = st.text_input("Nome do Homenageado *", key="man_dest_nome")
        with cd2: dest_tel = st.text_input("Telefone do Homenageado", key="man_dest_tel")
        
        cm1, cm2 = st.columns(2)
        with cm1: motivo = st.text_input("Motivo da Homenagem", key="man_motivo")
        with cm2: mensagem = st.text_area("Mensagem do Cartão", height=68, key="man_msg")
        
        # Integração do CEP (Auto-busca)
        with st.container(border=True):
            st.markdown("**📍 Endereço de Entrega**")
            cx1, cx2 = st.columns([1, 2])
            with cx1:
                cep_in = st.text_input("CEP *", max_chars=8, key="man_cep")
            
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
                
            with cx2: cidade = st.text_input("Cidade-UF *", value=st.session_state.man_cidade, key="man_cid_in")
            rua = st.text_input("Rua/Logradouro *", value=st.session_state.man_rua, key="man_rua_in")
            cn1, cn2 = st.columns(2)
            with cn1: num = st.text_input("Número/Compl. *", key="man_num")
            with cn2: bairro = st.text_input("Bairro *", value=st.session_state.man_bairro, key="man_bairro_in")
            
            ce1, ce2 = st.columns(2)
            with ce1: dt_ent = st.date_input("Data de Entrega", key="man_dt")
            with ce2: per_ent = st.selectbox("Período", ["Manhã", "Tarde", "Noite"], key="man_per")
            pedido_esp = st.text_input("Solicitação Especial (Horário, etc)", key="man_esp")

        # --- 5. FINANCEIRO E FECHAMENTO ---
        st.markdown("#### 💰 Fechamento")
        cf1, cf2, cf3 = st.columns(3)
        with cf1: pag = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Dinheiro", "Transferência"], key="man_pag")
        with cf2: status = st.selectbox("Status Inicial", ["Recebido", "Pago"], key="man_status")
        with cf3: frete = st.number_input("Frete (R$)", min_value=0.0, step=1.0, key="man_frete")
        
        valor_c = float(cesta_sel.get("preco", 0)) if cesta_sel and cesta_sel.get("id") else 0
        valor_a = sum([a["preco"] for a in adicionais_selecionados])
        total = valor_c + valor_a + frete
        
        st.success(f"**Total do Pedido:** R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        if st.button("✅ Salvar Pedido Manual", type="primary", use_container_width=True):
            if not nome_comp: st.error("Informe o nome do comprador."); st.stop()
            if not cpf_comp: st.error("Informe o CPF do comprador."); st.stop()
            if not cesta_sel or not cesta_sel.get("id"): st.error("Selecione uma Cesta."); st.stop()
            if not dest_nome: st.error("Informe o nome do destinatário."); st.stop()
            if not rua or not num: st.error("Informe Rua e Número de entrega."); st.stop()
            
            prod_text = "\n".join([f"{c}: {i['nome']}" for c, itens in selecoes_admin.items() for i in itens])
            add_text = ", ".join([a["nome"] for a in adicionais_selecionados])
            end_comp = f"{rua}, {num} - {bairro}, {cidade} (CEP: {cep_in})"
            
            dados_ped = {
                "cliente_nome": nome_comp.strip(),
                "cliente_cpf": re.sub(r'\D', '', cpf_comp),
                "cliente_telefone": re.sub(r'\D', '', tel_comp),
                "destinatario_nome": dest_nome.strip(),
                "destinatario_telefone": re.sub(r'\D', '', dest_tel),
                "motivo_homenagem": motivo,
                "cesta_id": cesta_sel["id"],
                "cesta_nome": cesta_sel["nome"],
                "produtos": prod_text,
                "adicionais": add_text,
                "pagamento": pag,
                "mensagem": mensagem,
                "pedido_especial": pedido_esp,
                "endereco": end_comp,
                "data_entrega": dt_ent.strftime("%Y-%m-%d") if dt_ent else str(date.today()),
                "periodo_entrega": per_ent,
                "status": status,
                "valor_frete": frete,
                "valor_total": total
            }
            
            suc, p_id = salvar_pedido(dados_ped)
            if suc:
                if adicionais_selecionados:
                    salvar_adicionais_pedido(p_id, adicionais_selecionados)
                st.success("✅ Pedido criado com sucesso! O painel será atualizado...")
                time.sleep(1)
                st.rerun() # Atualiza a página inteira para o pedido aparecer na lista Recebidos/Pagos instantaneamente
            else:
                st.error("Erro ao registrar o pedido no banco de dados.")

render_criar_pedido_manual()
st.divider()


# =====================================================
# CARREGA PEDIDOS DA TELA PRINCIPAL
# =====================================================

try:
    pedidos = listar_pedidos_ativos()
except Exception as erro:
    st.error(f"Erro ao carregar pedidos: {erro}")
    pedidos = []

df = pd.DataFrame(pedidos) if pedidos else pd.DataFrame(columns=["id", "cliente_nome", "status", "created_at"])


# =====================================================
# ORDENAÇÃO E PESQUISA
# =====================================================

if not df.empty and "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at", ascending=False)

st.subheader("🔍 Pesquisar pedido existente")
pesquisa = st.text_input("", placeholder="Digite o nome do cliente...")

if pesquisa.strip() and not df.empty:
    df = df[df["cliente_nome"].fillna("").str.contains(pesquisa, case=False)]


# =====================================================
# STATUS VISUAL
# =====================================================

def status_visual_html(status):
    status_str = str(status).strip().capitalize()
    if status_str == "Pago":
        return '<span class="badge-status badge-pago">🟢 Pago</span>'
    elif status_str == "Recebido":
        return '<span class="badge-status badge-recebido">🟡 Recebido</span>'
    elif status_str == "Desistência" or status_str == "Desistencia":
        return '<span class="badge-status badge-desistencia">🔴 Desistência</span>'
    return f'<span class="badge-status">{status}</span>'


# =====================================================
# FUNÇÃO DE RENDERIZAÇÃO DA LISTA DE PEDIDOS
# =====================================================

def mostrar_lista(titulo, status_filtro, permitir_exclusao=False, permitir_impressao=False):
    st.subheader(titulo)

    if df.empty or "status" not in df.columns:
        st.info(f"Nenhum pedido registrado em '{titulo.replace('📥 ', '').replace('💰 ', '').replace('❌ ', '')}'.")
        return

    pedidos_status = df[df["status"].astype(str).str.strip().str.capitalize() == status_filtro.capitalize()]

    if pedidos_status.empty:
        st.info(f"Nenhum pedido nesta etapa no momento.")
        return

    for _, pedido in pedidos_status.iterrows():
        try:
            pedido_atualizado = buscar_pedido(pedido["id"])
            if pedido_atualizado:
                pedido = pedido_atualizado
        except Exception:
            pass

        with st.container(border=True):
            if permitir_impressao:
                col_check, col_info1, col_info2, col_status, col_valor, col_acoes = st.columns([1.2, 3.2, 2.8, 1.8, 1.8, 1.5])
            else:
                col_info1, col_info2, col_status, col_valor, col_acoes = st.columns([3.8, 3.0, 2.0, 2.0, 1.5])

            if permitir_impressao:
                with col_check:
                    esta_marcado = pedido["id"] in st.session_state["pedidos_impressao"]
                    st.checkbox(
                        "🖨️",
                        value=esta_marcado,
                        key=f"imprimir_{pedido['id']}",
                        on_change=atualizar_selecao_impressao,
                        args=(pedido["id"],),
                        help="Selecionar para impressão"
                    )

            with col_info1:
                nome_cliente = str(pedido.get("cliente_nome", "-")).strip()
                nome_cliente = " ".join(nome_cliente.split())
                st.markdown(f'<div class="cliente-nome">{nome_cliente}</div>', unsafe_allow_html=True)
                st.caption(f"📱 {pedido.get('cliente_telefone', '-')}")

            with col_info2:
                st.write(f"🎁 **{pedido.get('cesta_nome','-')}**")
                data_formatada = formatar_data(pedido.get('data_entrega'))
                st.caption(f"🗓️ Entrega: {data_formatada}")

            with col_status:
                st.markdown(status_visual_html(pedido.get("status", "-")), unsafe_allow_html=True)

            with col_valor:
                valor = float(pedido.get("valor_total", 0) or 0)
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                st.markdown(f'<div class="valor-pedido">{valor_formatado}</div>', unsafe_allow_html=True)

            with col_acoes:
                if permitir_exclusao:
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        if st.button("👁️", key=f"abrir_{pedido['id']}", help="Abrir pedido", use_container_width=True):
                            st.session_state["pedido_aberto"] = pedido["id"]
                            st.switch_page("pages/09_Detalhes_Pedido.py")
                    with sub_col2:
                        if st.button("🗑️", key=f"excluir_{pedido['id']}", help="Excluir pedido", use_container_width=True):
                            sucesso, mensagem = excluir_pedido_completo(pedido["id"])
                            if sucesso:
                                st.success(mensagem)
                                st.rerun()
                            else:
                                st.error(mensagem)
                else:
                    if st.button("👁️", key=f"abrir_{pedido['id']}", help="Abrir pedido", use_container_width=True):
                        st.session_state["pedido_aberto"] = pedido["id"]
                        st.switch_page("pages/09_Detalhes_Pedido.py")


# =====================================================
# FLUXO COMPLETO DE PEDIDOS NA TELA
# =====================================================

mostrar_lista("📥 Pedidos Recebidos", "Recebido")
mostrar_lista("💰 Pedidos Pagos", "Pago", permitir_impressao=True)
mostrar_lista("❌ Desistências", "Desistência", permitir_exclusao=(usuario.get("perfil") == "Administrador"))


# =====================================================
# IMPRESSÃO DOS PEDIDOS SELECIONADOS
# =====================================================

if st.session_state["pedidos_impressao"]:
    st.divider()
    
    col_t_imp1, col_t_imp2 = st.columns([3, 1])
    with col_t_imp1:
        st.subheader("🖨️ Impressão de Pedidos")
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
            if pedido_completo:
                pedidos_selecionados_dados.append(pedido_completo)
            else:
                ids_para_remover.append(pid)
        except Exception:
            ids_para_remover.append(pid)

    for pid in ids_para_remover:
        if pid in st.session_state["pedidos_impressao"]:
            st.session_state["pedidos_impressao"].remove(pid)

    quantidade = len(pedidos_selecionados_dados)
    if quantidade > 0:
        st.success(f"✅ {quantidade} pedido(s) selecionado(s) e pronto(s) para impressão.")

        st.markdown("#### 🛒 Revisão dos Pedidos Selecionados")
        for ped in pedidos_selecionados_dados:
            nome_comprador = ped.get('cliente_nome', '-')
            tel_comprador = ped.get('cliente_telefone', '-')
            nome_homenageado = ped.get('destinatario_nome', '-')
            tel_homenageado = ped.get('destinatario_telefone', '-')
            nome_cesta = ped.get('cesta_nome', '-')
            data_entrega = formatar_data(ped.get('data_entrega'))
            periodo = ped.get('periodo_entrega', '-')
            horario = ped.get('horario_combinado', '')
            horario_str = f" ({horario})" if horario else ""

            st.markdown(
                f"""
                <div data-testid="stVerticalBlockBorderWrapper" class="preview-impressao">
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px;">
                            <div class="info-label">👤 Comprador</div>
                            <div style="font-weight: 600; color: #333;">{nome_comprador}</div>
                            <div style="font-size: 12px; color: #666;">📱 {tel_comprador}</div>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <div class="info-label">💝 Homenageado</div>
                            <div style="font-weight: 600; color: #333;">{nome_homenageado}</div>
                            <div style="font-size: 12px; color: #666;">📱 {tel_homenageado}</div>
                        </div>
                        <div style="flex: 1.5; min-width: 250px;">
                            <div class="info-label">🚚 Cesta e Entrega</div>
                            <div style="font-weight: 600; color: #333;">🎁 {nome_cesta}</div>
                            <div style="font-size: 12px; color: #666;">🗓️ {data_entrega} | 🕒 {periodo}{horario_str}</div>
                        </div>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )

        st.write("") 

        formato_impressao = st.radio(
            "Formato do PDF",
            ["📄 Folha A4 - 12 pedidos por página", "🧾 Individual 7x10 cm"],
            horizontal=True
        )

        if st.button("📄 Gerar PDF Definitivo", use_container_width=True, type="primary"):
            pdf = gerar_pdf_pedidos(pedidos_selecionados_dados, formato_impressao)
            st.session_state["pdf_gerado"] = pdf
            st.success("✅ PDF gerado com sucesso! Clique no botão abaixo para salvar o arquivo.")

        if st.session_state.get("pdf_gerado"):
            st.download_button(
                "⬇️ Baixar PDF",
                st.session_state["pdf_gerado"],
                file_name=f"pedidos_producao_{datetime.now().strftime('%d%m%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption(f"Total de pedidos ativos no painel: {len(df)}")
