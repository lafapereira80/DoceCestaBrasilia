import streamlit as st
import urllib.parse
import re
from datetime import datetime
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from services.telegram_service import enviar_notificacao_telegram

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E BLINDAGEM DE SESSÃO
# =====================================================
st.set_page_config(page_title="Gestão de Entregas", page_icon="🛵", layout="wide")
configurar_pagina()
menu_lateral()

usuario = st.session_state.get("usuario")
if not usuario:
    st.warning("⚠️ Você precisa fazer login para acessar esta página.")
    st.stop()
perfil_usuario = usuario.get("perfil", "Operador")
login_atual = usuario.get("login", "Sistema")

# =====================================================
# ESTILOS GERAIS E LAYOUT MODERNO PREMIUM
# =====================================================
st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1250px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 2px !important; letter-spacing: -0.5px; text-align: center; }
h3, h4 { color: #5a3b28 !important; font-weight: 800 !important; margin-top: 15px !important; margin-bottom: 10px !important; }
p, label { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 13px !important; }

/* =========================================
   CARDS DE PEDIDO (ENTREGAS)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] { 
    background: #ffffff; 
    border: 1px solid #e8ddd3 !important; 
    border-radius: 14px !important; 
    padding: 14px 16px !important; 
    margin-bottom: 10px !important; 
    box-shadow: 0 2px 8px rgba(0,0,0,0.02); 
    transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #d2bfae !important;
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08);
}

/* =========================================
   TIPOGRAFIA INTERNA DOS CARDS
========================================== */
.pedido-id-badge { background: #f3ece6; color: #5a3b28; padding: 4px 10px; border-radius: 20px; font-weight: 800; font-size: 11px; display: inline-block; letter-spacing: 0.5px; text-transform: uppercase; }
.comprador-txt { font-size: 12px; color: #666; margin-top: 6px; font-weight: 600; }
.destinatario-txt { font-size: 15px; font-weight: 800; color: #2c1e14; margin-top: 2px; }
.endereco-box { font-size: 13px; color: #444; margin-top: 10px; background: #faf7f3; padding: 10px 12px; border-radius: 10px; border-left: 4px solid #b06000; line-height: 1.4; font-weight: 500; }
.hora-badge { font-size: 11px; font-weight: 800; color: #b06000; background: #fef7e0; padding: 4px 8px; border-radius: 8px; display: inline-block; margin-top: 8px; border: 1px solid #fce8b2; }

/* =========================================
   BOTÕES DE AÇÃO E SELECTS
========================================== */
div[data-testid="stButton"] > button { border-radius: 10px !important; font-weight: 800 !important; font-size: 13px !important; min-height: 38px !important; transition: all 0.2s ease; }
div[data-testid="stButton"] > button:hover { transform: scale(1.02); }
div[data-baseweb="select"] { margin-top: 0px !important; }

/* =========================================
   FICHA DE ENTREGA E BOTÕES GPS (VISÃO MOTOBOY)
========================================== */
.ficha-entrega { font-size: 14px; color: #444; }
.ficha-entrega strong { color: #5a3b28; font-weight: 800; }
.ficha-secao { margin-top: 12px; padding-top: 12px; border-top: 1px dashed #dfcdbb; }
div[data-testid="stLinkButton"] > a { font-weight: 800 !important; font-size: 14px !important; border-radius: 10px !important; padding: 10px !important; display: flex; justify-content: center; transition: all 0.2s; }
div[data-testid="stLinkButton"] > a:hover { transform: scale(1.03); }
.btn-waze > a { background-color: #33ccff !important; color: #004d66 !important; border: none !important; }
.btn-maps > a { background-color: #fce8e6 !important; color: #c5221f !important; border: none !important; }

/* =========================================
   CARTÃO DE ENTREGUE E CABEÇALHO DO ADMIN
========================================== */
.entregue-box { opacity: 0.85; background-color: #f0f7f4 !important; border: 1px solid #c8e6c9 !important; border-left: 6px solid #137333 !important; }
.admin-card-header { text-align: center; background: linear-gradient(135deg, #fef7e0 0%, #fffbf7 100%); color: #b06000; font-weight: 800; padding: 12px; border-radius: 12px; margin-bottom: 15px; font-size: 16px; border: 1px solid #fce8b2; box-shadow: 0 2px 4px rgba(176,96,0,0.05); }

/* =========================================
   RESPONSIVIDADE MOBILE E BOTÕES LADO A LADO
========================================== */
@media (max-width: 768px) {
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    h1 { font-size: 24px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 12px !important; }
    
    /* Força os botões da direita (ações rápidas do motoboy) a ficarem na horizontal */
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-top: 10px !important;
        justify-content: space-between;
    }
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {
        flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important;
    }
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) button {
        width: 100% !important; padding: 6px 0px !important;
    }
}
</style>
""",
unsafe_allow_html=True)

if "modo_entrega_ativa" not in st.session_state: st.session_state.modo_entrega_ativa = False

# =====================================================
# FUNÇÕES DE BANCO E LÓGICA COMPARTILHADA
# =====================================================
def formatar_data(data_str):
    if not data_str: return "-"
    try:
        dt = datetime.strptime(str(data_str)[:10], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return str(data_str)

def buscar_entregas_dia(driver_login=None):
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    query_env = supabase.table("pedidos").select("*").eq("status", "Enviado")
    if perfil_usuario == "Entregador" or driver_login:
        alvo = login_atual if perfil_usuario == "Entregador" else driver_login
        query_env = query_env.eq("entregador_login", alvo)
        
    res_env = query_env.execute()
    enviados = res_env.data or []
    enviados.sort(key=lambda x: (x.get('ordem_entrega') if x.get('ordem_entrega') is not None else 999, x.get('created_at')))
    
    query_ent = supabase.table("pedidos").select("*").eq("status", "Entregue")
    if perfil_usuario == "Entregador" or driver_login:
        alvo = login_atual if perfil_usuario == "Entregador" else driver_login
        query_ent = query_ent.eq("entregador_login", alvo)
        
    res_ent = query_ent.execute()
    entregues = res_ent.data or []
    entregues_hoje = [p for p in entregues if p.get('hora_entrega_realizada') and data_hoje in p.get('hora_entrega_realizada')]
    entregues_hoje.sort(key=lambda x: x.get('hora_entrega_realizada', ''), reverse=True)
    
    return enviados, entregues_hoje

def salvar_ordem(pedidos_ordenados):
    for i, p in enumerate(pedidos_ordenados):
        if p.get("ordem_entrega") != i:
            try: supabase.table("pedidos").update({"ordem_entrega": i}).eq("id", p["id"]).execute()
            except: pass 

def atualizar_entregador(pedido_id, widget_key):
    novo_entregador = st.session_state[widget_key]
    val = None if novo_entregador == "Não atribuído" else novo_entregador
    try: 
        supabase.table("pedidos").update({"entregador_login": val}).eq("id", pedido_id).execute()
        st.toast("✅ Entregador atribuído com sucesso!")
    except Exception as e: 
        st.error(f"Erro ao atribuir: {e}")

def marcar_como_entregue(pedido, login_autor):
    try:
        agora = datetime.now()
        hora_formatada = agora.strftime("%d/%m/%Y %H:%M")
        apenas_hora = agora.strftime("%H:%M")
        
        supabase.table("pedidos").update({"status": "Entregue", "ordem_entrega": 999, "hora_entrega_realizada": hora_formatada}).eq("id", pedido["id"]).execute()
        
        texto_telegram = f"""✅ *ENTREGA REALIZADA!* ✅\n\n🛵 *Responsável:* {login_autor}\n📦 *Cesta:* {pedido.get('cesta_nome', '-')}\n💝 *Destinatário:* {pedido.get('destinatario_nome', '-')}\n📍 *Local:* {str(pedido.get('endereco', '')).split(',')[-1].split('(')[0].strip()}\n⏰ *Horário:* {apenas_hora}"""
        enviar_notificacao_telegram(texto_telegram)
    except Exception as e:
        st.error(f"Erro ao finalizar entrega: {e}")

def voltar_para_enviado(pedido_id):
    try:
        supabase.table("pedidos").update({"status": "Enviado", "ordem_entrega": 0, "hora_entrega_realizada": None}).eq("id", pedido_id).execute()
        st.toast("↩️ Cesta retornada para a rota com sucesso!")
    except Exception as e:
        st.error(f"Erro ao reverter status: {e}")


pedidos_ativos_geral, pedidos_concluidos_geral = buscar_entregas_dia()


# =====================================================
# VISÃO 1: ADMINISTRADOR E OPERADOR (PAINEL DE CONTROLE)
# =====================================================
if perfil_usuario in ["Administrador", "Operador"]:
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.title("🗺️ Painel de Despacho e Rotas")
    with col_t2:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar Tempo Real", use_container_width=True):
            st.rerun()

    aba_geral, aba_visao_motoboy = st.tabs(["🗺️ Despacho e Rotas", "🚴 Simulador do Entregador"])

    # -------------------------------------------------
    # ABA 1: PAINEL GERAL DE DESPACHO E ROTAS
    # -------------------------------------------------
    with aba_geral:
        lista_entregadores = []
        try:
            res_ent = supabase.table("usuarios").select("login").eq("perfil", "Entregador").execute()
            lista_entregadores = [e["login"] for e in (res_ent.data or [])]
        except: pass
        opcoes_ent = ["Não atribuído"] + lista_entregadores

        nao_atribuidos = [p for p in pedidos_ativos_geral if not p.get("entregador_login")]
        
        st.markdown("<h3>📦 Cestas na Base (Aguardando Atribuição)</h3>", unsafe_allow_html=True)
        
        if not nao_atribuidos:
            st.info("✨ Fantástico! Todas as cestas enviadas já foram atribuídas a um entregador.")
        else:
            cols_despacho = st.columns(2)
            for i, ped in enumerate(nao_atribuidos):
                with cols_despacho[i % 2]:
                    with st.container(border=True):
                        endereco_completo = ped.get('endereco', 'Endereço não informado')
                        data_entrega = formatar_data(ped.get('data_entrega'))
                        turno = ped.get('periodo_entrega', 'N/I')
                        hora_combinada = ped.get('horario_combinado', '')
                        hora_str = f" • Às {hora_combinada}" if hora_combinada else ""
                        
                        tel_dest = ped.get('destinatario_telefone')
                        tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                        
                        col_detalhes, col_acao = st.columns([1.6, 1])
                        
                        with col_detalhes:
                            st.markdown(
                                f"""
                                <div>
                                    <span class="pedido-id-badge">ID #{ped.get('id')}</span>
                                    <div class="comprador-txt">👤 Comprador: <strong>{ped.get('cliente_nome')}</strong> ({ped.get('cliente_telefone')})</div>
                                    <div class="destinatario-txt">🎁 {ped.get('cesta_nome')} p/ <em>{ped.get('destinatario_nome')}</em>{tel_dest_str}</div>
                                    <div class="endereco-box">📍 {endereco_completo}</div>
                                    <div class="hora-badge">📅 {data_entrega} | 🕒 {turno}{hora_str}</div>
                                </div>
                                """, unsafe_allow_html=True
                            )
                        
                        with col_acao:
                            st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 4px; text-transform: uppercase;'>Despachar para:</div>", unsafe_allow_html=True)
                            chave_widget = f"despacho_{ped['id']}"
                            st.selectbox("Entregador", opcoes_ent, index=0, key=chave_widget, label_visibility="collapsed", on_change=atualizar_entregador, args=(ped["id"], chave_widget))
                            
                            st.write("")
                            if st.button("✅ Marcar como Entregue", key=f"entregue_desp_{ped['id']}", use_container_width=True):
                                marcar_como_entregue(ped, login_atual)
                                st.rerun()

        # Verifica rigorosamente se algum entregador possui rotas ativas ou concluídas hoje
        data_hoje = datetime.now().strftime("%d-%m-%Y")
        rotas_ativas_existem = False
        if lista_entregadores:
            for driver in lista_entregadores:
                p_ativos = [p for p in pedidos_ativos_geral if p.get("entregador_login") == driver]
                p_concl = [p for p in pedidos_concluidos_geral if p.get("entregador_login") == driver]
                arquivada = st.session_state.get(f"limpar_rota_{driver}_{data_hoje}", False)
                if p_ativos or (p_concl and not arquivada):
                    rotas_ativas_existem = True
                    break

        if rotas_ativas_existem:
            st.divider()
            st.markdown("<h3>🛵 Rotas Ativas (Em Andamento)</h3>", unsafe_allow_html=True)
            cols_rotas = st.columns(2)
            
            for idx_driver, driver in enumerate(lista_entregadores):
                ped_driver_ativos = [p for p in pedidos_ativos_geral if p.get("entregador_login") == driver]
                ped_driver_concluidos = [p for p in pedidos_concluidos_geral if p.get("entregador_login") == driver]
                
                rota_arquivada = st.session_state.get(f"limpar_rota_{driver}_{data_hoje}", False)
                if rota_arquivada:
                    ped_driver_concluidos = []

                if not ped_driver_ativos and not ped_driver_concluidos:
                    continue 
                    
                with cols_rotas[idx_driver % 2]:
                    with st.container(border=True):
                        st.markdown(f"<div class='admin-card-header'>🚴 Rota Atual de: {driver}</div>", unsafe_allow_html=True)

                        salvar_ordem(ped_driver_ativos)
                        
                        if ped_driver_ativos:
                            st.markdown("<span style='font-size:12px; font-weight:800; color:#5a3b28; text-transform: uppercase;'>Itens na Rota:</span>", unsafe_allow_html=True)
                            for i, ped in enumerate(ped_driver_ativos):
                                with st.container(border=True):
                                    endereco_completo = ped.get('endereco', 'Endereço não informado')
                                    data_entrega = formatar_data(ped.get('data_entrega'))
                                    turno = ped.get('periodo_entrega', 'N/I')
                                    hora_combinada = ped.get('horario_combinado', '')
                                    hora_str = f" • Às {hora_combinada}" if hora_combinada else ""
                                    
                                    tel_dest = ped.get('destinatario_telefone')
                                    tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                                    
                                    col_inf_ativa, col_acoes_ativa = st.columns([1.6, 1])
                                    
                                    with col_inf_ativa:
                                        st.markdown(
                                            f"""
                                            <div>
                                                <div class="comprador-txt" style="margin-top: 0px;">👤 Comprador: <strong>{ped.get('cliente_nome')}</strong></div>
                                                <div class="destinatario-txt">#{i+1} - 🎁 {ped.get('cesta_nome')} p/ <em>{ped.get('destinatario_nome')}</em>{tel_dest_str}</div>
                                                <div class="endereco-box">📍 {endereco_completo}</div>
                                                <div class="hora-badge">📅 {data_entrega} | 🕒 {turno}{hora_str}</div>
                                            </div>
                                            """, unsafe_allow_html=True
                                        )
                                    
                                    with col_acoes_ativa:
                                        st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 4px; text-transform: uppercase;'>Realocar para:</div>", unsafe_allow_html=True)
                                        chave_realocar = f"realocar_{ped['id']}"
                                        indice_atual = opcoes_ent.index(driver) if driver in opcoes_ent else 0
                                        st.selectbox("Realocar", opcoes_ent, index=indice_atual, key=chave_realocar, label_visibility="collapsed", on_change=atualizar_entregador, args=(ped["id"], chave_realocar))
                                        
                                        st.write("")
                                        if st.button("✅ Marcar como Entregue", key=f"entregue_ativa_{ped['id']}", use_container_width=True, type="primary"):
                                            marcar_como_entregue(ped, login_atual)
                                            st.rerun()

                                    st.write("")
                                    col_u, col_d = st.columns(2)
                                    with col_u:
                                        if i > 0:
                                            if st.button("⬆️ Subir na Rota", key=f"up_admin_{ped['id']}", use_container_width=True):
                                                ped_driver_ativos[i], ped_driver_ativos[i-1] = ped_driver_ativos[i-1], ped_driver_ativos[i]
                                                salvar_ordem(ped_driver_ativos)
                                                st.rerun()
                                    with col_d:
                                        if i < len(ped_driver_ativos) - 1:
                                            if st.button("⬇️ Descer na Rota", key=f"down_admin_{ped['id']}", use_container_width=True):
                                                ped_driver_ativos[i], ped_driver_ativos[i+1] = ped_driver_ativos[i+1], ped_driver_ativos[i]
                                                salvar_ordem(ped_driver_ativos)
                                                st.rerun()

                        if ped_driver_concluidos:
                            st.markdown("<span style='font-size:12px; font-weight:800; color:#137333; margin-top:15px; display:block; text-transform: uppercase;'>✅ Finalizados Hoje:</span>", unsafe_allow_html=True)
                            for ped in ped_driver_concluidos:
                                hora_ext = ped.get('hora_entrega_realizada', '')[-5:]
                                bairro_con = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip()
                                st.markdown(f"""
                                <div data-testid="stVerticalBlockBorderWrapper" class="entregue-box" style="padding: 10px !important;">
                                    <div style="font-size:13px; font-weight:800; color:#137333;">✅ Entregue às {hora_ext} - 📍 {bairro_con} ({ped.get('cesta_nome')})</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if perfil_usuario == "Administrador":
                                    if st.button("↩️ Retornar para a Rota", key=f"voltar_rota_{ped['id']}", use_container_width=True):
                                        voltar_para_enviado(ped['id'])
                                        st.rerun()

                        if len(ped_driver_ativos) == 0 and len(ped_driver_concluidos) > 0:
                            st.write("")
                            if st.button(f"🧹 Concluir Entregas e Limpar Painel", key=f"btn_ok_{driver}", use_container_width=True):
                                st.session_state[f"limpar_rota_{driver}_{data_hoje}"] = True
                                st.rerun()

    # -------------------------------------------------
    # ABA 2: VISÃO POR ENTREGADOR (SIMULADOR)
    # -------------------------------------------------
    with aba_visao_motoboy:
        st.markdown("### 🚴 Simulador do Aplicativo do Entregador")
        st.caption("Selecione um motoboy abaixo para visualizar a tela exata que ele enxerga no celular durante a rota.")
        
        lista_entregadores_todos = []
        try:
            res_ent = supabase.table("usuarios").select("login").eq("perfil", "Entregador").execute()
            lista_entregadores_todos = [e["login"] for e in (res_ent.data or [])]
        except: pass

        if not lista_entregadores_todos:
            st.warning("⚠️ Nenhum entregador cadastrado no sistema.")
        else:
            motoboy_selecionado = st.selectbox("Selecione o Entregador para simular:", lista_entregadores_todos, key="select_vis_motoboy")
            st.divider()

            p_ativos_mb, p_concluidos_mb = buscar_entregas_dia(driver_login=motoboy_selecionado)

            if not p_ativos_mb and not p_concluidos_mb:
                st.info(f"📭 A rota de **{motoboy_selecionado}** está vazia no momento.")
            else:
                st.markdown(f"#### 📱 Tela do Entregador: {motoboy_selecionado}")
                
                if p_ativos_mb:
                    salvar_ordem(p_ativos_mb)
                    for i, ped in enumerate(p_ativos_mb):
                        with st.container(border=True):
                            bairro = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip() or "Endereço incompleto"
                            horario = ped.get('horario_combinado', '') or ped.get('periodo_entrega', 'Livre')
                            data_e = formatar_data(ped.get('data_entrega'))
                            tel_dest = ped.get('destinatario_telefone')
                            tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                            
                            col_info_mb, col_btn_mb = st.columns([1.6, 1])
                            
                            with col_info_mb:
                                st.markdown(f"""
                                    <div>
                                        <span class="pedido-id-badge">📍 PARADA #{i+1}</span>
                                        <div class="comprador-txt" style="margin-top: 8px;">👤 Comprador: {ped.get('cliente_nome')} ({ped.get('cliente_telefone')})</div>
                                        <div class="destinatario-txt">🎁 {ped.get('cesta_nome')} p/ <strong>{ped.get('destinatario_nome')}</strong>{tel_dest_str}</div>
                                        <div class="endereco-box">📍 {ped.get('endereco')}</div>
                                        <div class="hora-badge">📅 {data_e} | 🕒 {horario}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                st.write("")
                                endereco_gps = urllib.parse.quote(re.sub(r'\(CEP:.*?\)', '', ped.get('endereco', '')).strip())
                                c_m, c_w = st.columns(2)
                                with c_m:
                                    st.markdown('<div class="btn-maps">', unsafe_allow_html=True)
                                    st.link_button("🗺️ Abrir no Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_gps}", use_container_width=True, key=f"map_sim_{ped['id']}")
                                    st.markdown('</div>', unsafe_allow_html=True)
                                with c_w:
                                    st.markdown('<div class="btn-waze">', unsafe_allow_html=True)
                                    st.link_button("🚗 Abrir no Waze", url=f"https://waze.com/ul?q={endereco_gps}&navigate=yes", use_container_width=True, key=f"wz_sim_{ped['id']}")
                                    st.markdown('</div>', unsafe_allow_html=True)

                            with col_btn_mb:
                                st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 4px; text-transform: uppercase;'>Ação Rápida:</div>", unsafe_allow_html=True)
                                if st.button("✅ Finalizar Entrega", key=f"entregue_sim_{ped['id']}", use_container_width=True, type="primary"):
                                    marcar_como_entregue(ped, motoboy_selecionado)
                                    st.rerun()
                                
                                st.write("")
                                st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 4px; text-transform: uppercase;'>Ajustar Rota:</div>", unsafe_allow_html=True)
                                col_u_s, col_d_s = st.columns(2)
                                with col_u_s:
                                    if i > 0:
                                        if st.button("⬆️ Subir", key=f"up_sim_{ped['id']}", use_container_width=True):
                                            p_ativos_mb[i], p_ativos_mb[i-1] = p_ativos_mb[i-1], p_ativos_mb[i]
                                            salvar_ordem(p_ativos_mb)
                                            st.rerun()
                                with col_d_s:
                                    if i < len(p_ativos_mb) - 1:
                                        if st.button("⬇️ Descer", key=f"down_sim_{ped['id']}", use_container_width=True):
                                            p_ativos_mb[i], p_ativos_mb[i+1] = p_ativos_mb[i+1], p_ativos_mb[i]
                                            salvar_ordem(p_ativos_mb)
                                            st.rerun()

                if p_concluidos_mb:
                    st.write("")
                    st.markdown("<span style='font-size:12px; font-weight:800; color:#137333; margin-top:10px; display:block; text-transform: uppercase;'>✅ Histórico de Hoje:</span>", unsafe_allow_html=True)
                    for ped in p_concluidos_mb:
                        hora_extraida = ped.get('hora_entrega_realizada', '')[-5:] 
                        bairro_concluido = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip()
                        tel_dest = ped.get('destinatario_telefone')
                        tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                        st.markdown(f"""
                        <div data-testid="stVerticalBlockBorderWrapper" class="entregue-box">
                            <div style="font-size:13px; font-weight:800; color:#137333;">✅ Entregue às {hora_extraida} - 📍 {bairro_concluido}</div>
                            <div class="nome-destaque" style="margin-top:4px;">🎁 {ped.get('cesta_nome')} para <strong>{ped.get('destinatario_nome')}</strong>{tel_dest_str}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if perfil_usuario == "Administrador":
                            if st.button("↩️ Retornar p/ Rota", key=f"voltar_sim_{ped['id']}", use_container_width=True):
                                voltar_para_enviado(ped['id'])
                                st.rerun()


# =====================================================
# VISÃO 2: ENTREGADOR REAL (APLICATIVO DO MOTOBOY)
# =====================================================
else:
    st.title(f"🛵 Minha Rota de Entregas")

    pedidos_ativos_driver, pedidos_concluidos_driver = buscar_entregas_dia()

    if not pedidos_ativos_driver and not pedidos_concluidos_driver:
        st.success("🎉 Rota limpa! Nenhuma entrega pendente para você no momento.")
        st.session_state.modo_entrega_ativa = False
        st.stop()

    if not st.session_state.modo_entrega_ativa:
        if pedidos_ativos_driver:
            st.info("👇 As cestas abaixo estão sob sua responsabilidade. Finalize por aqui ou inicie o Modo Navegação.")
            salvar_ordem(pedidos_ativos_driver)
            
            for i, ped in enumerate(pedidos_ativos_driver):
                with st.container(border=True):
                    endereco_completo = ped.get('endereco', 'Endereço não informado')
                    data_entrega = formatar_data(ped.get('data_entrega'))
                    turno = ped.get('periodo_entrega', 'N/I')
                    hora_combinada = ped.get('horario_combinado', '')
                    hora_str = f" • Às {hora_combinada}" if hora_combinada else ""
                    
                    tel_dest = ped.get('destinatario_telefone')
                    tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                    
                    col_inf_drv, col_btn_drv = st.columns([1.6, 1])
                    
                    with col_inf_drv:
                        st.markdown(
                            f"""
                            <div>
                                <span class="pedido-id-badge">📍 PARADA #{i+1}</span>
                                <div class="comprador-txt" style="margin-top: 8px;">👤 Comprador: {ped.get('cliente_nome')} ({ped.get('cliente_telefone')})</div>
                                <div class="destinatario-txt">🎁 <strong>{ped.get('cesta_nome')}</strong> p/ <em>{ped.get('destinatario_nome')}</em>{tel_dest_str}</div>
                                <div class="endereco-box">📍 {endereco_completo}</div>
                                <div class="hora-badge">📅 {data_entrega} | 🕒 {turno}{hora_str}</div>
                            </div>
                            """, unsafe_allow_html=True
                        )
                        
                        st.write("")
                        endereco_gps = urllib.parse.quote(re.sub(r'\(CEP:.*?\)', '', ped.get('endereco', '')).strip())
                        c_m_d, c_w_d = st.columns(2)
                        with c_m_d:
                            st.markdown('<div class="btn-maps">', unsafe_allow_html=True)
                            st.link_button("🗺️ Abrir no Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_gps}", use_container_width=True, key=f"map_drv_{ped['id']}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with c_w_d:
                            st.markdown('<div class="btn-waze">', unsafe_allow_html=True)
                            st.link_button("🚗 Abrir no Waze", url=f"https://waze.com/ul?q={endereco_gps}&navigate=yes", use_container_width=True, key=f"wz_drv_{ped['id']}")
                            st.markdown('</div>', unsafe_allow_html=True)

                    with col_btn_drv:
                        st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 4px; text-transform: uppercase;'>Ação Rápida:</div>", unsafe_allow_html=True)
                        if st.button("✅ Finalizar Entrega", key=f"entregue_fila_{ped['id']}", use_container_width=True, type="primary"):
                            marcar_como_entregue(ped, login_atual)
                            st.rerun()

                        st.write("")
                        st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 4px; text-transform: uppercase;'>Mudar Ordem:</div>", unsafe_allow_html=True)
                        col_up, col_down = st.columns(2)
                        with col_up:
                            if i > 0:
                                if st.button("⬆️ Subir", key=f"up_{ped['id']}", use_container_width=True):
                                    pedidos_ativos_driver[i], pedidos_ativos_driver[i-1] = pedidos_ativos_driver[i-1], pedidos_ativos_driver[i]
                                    salvar_ordem(pedidos_ativos_driver)
                                    st.rerun()
                        with col_down:
                            if i < len(pedidos_ativos_driver) - 1:
                                if st.button("⬇️ Descer", key=f"down_{ped['id']}", use_container_width=True):
                                    pedidos_ativos_driver[i], pedidos_ativos_driver[i+1] = pedidos_ativos_driver[i+1], pedidos_ativos_driver[i]
                                    salvar_ordem(pedidos_ativos_driver)
                                    st.rerun()

            st.write("")
            if st.button("🚀 INICIAR MODO NAVEGAÇÃO FOCO", type="primary", use_container_width=True):
                st.session_state.modo_entrega_ativa = True
                st.rerun()
        else:
            st.success("🎉 Nenhuma entrega pendente na fila ativa.")

    else:
        if pedidos_ativos_driver:
            pedido_atual = pedidos_ativos_driver[0] 
            st.warning("⚠️ **Modo Foco Ativo:** Siga as instruções até o destino. Conclua a parada atual para prosseguir na rota.")
            
            with st.container(border=True):
                st.markdown(f'<div style="font-size:20px; font-weight:800; color:#5a3b28; text-align:center; margin-bottom: 4px; text-transform: uppercase;">🎯 Parada Atual</div>', unsafe_allow_html=True)
                st.divider()
                tel_dest_atual = pedido_atual.get('destinatario_telefone')
                tel_dest_atual_str = f" (📞 {tel_dest_atual})" if tel_dest_atual else " (Sem telefone)"
                
                col_foco_info, col_foco_botoes = st.columns([1.6, 1])
                
                with col_foco_info:
                    st.markdown(f"""
                        <div class="ficha-entrega">
                            <div><strong>👤 Comprador:</strong> {pedido_atual.get('cliente_nome')} (📞 {pedido_atual.get('cliente_telefone')})</div>
                            <div class="ficha-secao"><strong>🎁 Pacote:</strong> {pedido_atual.get('cesta_nome')}</div>
                            <div class="ficha-secao"><strong>💝 Quem Recebe:</strong><br>{pedido_atual.get('destinatario_nome')}{tel_dest_atual_str}</div>
                            <div class="ficha-secao"><strong>📍 Endereço de Entrega:</strong><br><span style="font-size: 16px; font-weight: 800; color: #137333;">{pedido_atual.get('endereco')}</span></div>
                            <div class="ficha-secao"><strong>📅 Data e Horário:</strong><br>{formatar_data(pedido_atual.get('data_entrega'))} | 🕒 {pedido_atual.get('horario_combinado') or pedido_atual.get('periodo_entrega', 'Livre')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")
                    endereco_gps = urllib.parse.quote(re.sub(r'\(CEP:.*?\)', '', pedido_atual.get('endereco', '')).strip())
                    c_maps, c_waze = st.columns(2)
                    with c_maps:
                        st.markdown('<div class="btn-maps">', unsafe_allow_html=True)
                        st.link_button("🗺️ Abrir Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_gps}", use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    with c_waze:
                        st.markdown('<div class="btn-waze">', unsafe_allow_html=True)
                        st.link_button("🚗 Abrir Waze", url=f"https://waze.com/ul?q={endereco_gps}&navigate=yes", use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                with col_foco_botoes:
                    st.markdown("<div style='font-size: 11px; font-weight: 800; color: #137333; margin-bottom: 6px; text-transform: uppercase;'>Concluir Atendimento:</div>", unsafe_allow_html=True)
                    if st.button("✅ MARCAR COMO ENTREGUE", type="primary", use_container_width=True):
                        with st.spinner("Confirmando entrega na central..."):
                            marcar_como_entregue(pedido_atual, login_atual)
                        st.rerun() 
                        
                    st.write("")
                    st.markdown("<div style='font-size: 11px; font-weight: 800; color: #775a46; margin-bottom: 6px; text-transform: uppercase;'>Gerenciar Rota:</div>", unsafe_allow_html=True)
                    if st.button("⏸️ Pausar e Ver Fila Completa", use_container_width=True):
                        st.session_state.modo_entrega_ativa = False
                        st.rerun()
        else:
            st.session_state.modo_entrega_ativa = False
            st.rerun()

    if pedidos_concluidos_driver and not st.session_state.modo_entrega_ativa:
        st.write("")
        st.markdown("<span style='font-size:14px; font-weight:800; color:#137333; margin-top:10px; display:block; text-transform: uppercase;'>✅ Histórico de Hoje:</span>", unsafe_allow_html=True)
        
        for ped in pedidos_concluidos_driver:
            hora_extraida = ped.get('hora_entrega_realizada', '')[-5:] 
            bairro_concluido = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip()
            tel_dest = ped.get('destinatario_telefone')
            tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
            st.markdown(f"""
            <div data-testid="stVerticalBlockBorderWrapper" class="entregue-box">
                <div style="font-size:13px; font-weight:800; color:#137333;">✅ Entregue às {hora_extraida} - 📍 {bairro_concluido}</div>
                <div class="nome-destaque" style="margin-top:4px;">🎁 {ped.get('cesta_nome')} para <strong>{ped.get('destinatario_nome')}</strong>{tel_dest_str}</div>
            </div>
            """, unsafe_allow_html=True)
