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

# =====================================================
# ESTILOS GERAIS E MOBILE-FIRST
# =====================================================
st.markdown(
"""
<style>
.block-container { padding-top: 1rem !important; padding-bottom: 2.5rem !important; max-width: 1200px; }
h1 { font-size: 24px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 5px !important; text-align: center;}
h3 { font-size: 18px !important; font-weight: 800 !important; color: #2e7d32; margin-top: 10px !important; margin-bottom: 10px !important; }

/* Cartões de Pedido */
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 12px 14px !important; margin-bottom: 8px !important; box-shadow: 0 2px 4px rgba(90, 59, 40, 0.04); }
.card-info { flex: 1; }
.bairro-destaque { font-size: 15px; font-weight: 800; color: #333; margin-bottom: 2px;}
.nome-destaque { font-size: 13px; font-weight: 600; color: #666; }
.hora-destaque { font-size: 12px; font-weight: 700; color: #b06000; background: #fef7e0; padding: 3px 8px; border-radius: 6px; display: inline-block; margin-top: 6px; border: 1px solid #f0e0d0; }

/* Botões de Ordenação Simulações de Drag & Drop */
.btn-updown button { font-size: 18px !important; padding: 0 !important; height: 36px !important; width: 36px !important; border-radius: 50% !important; border: 1px solid #dfcdbb !important; background: #faf7f3 !important; }
.btn-updown button:hover { background: #e8ddd3 !important; }

/* Ficha e Botões GPS (Visão Entregador) */
.ficha-entrega { font-size: 14px; color: #444; }
.ficha-entrega strong { color: #5a3b28; }
.ficha-secao { margin-top: 12px; padding-top: 12px; border-top: 1px dashed #dfcdbb; }
div[data-testid="stLinkButton"] > a { font-weight: 700 !important; font-size: 14px !important; border-radius: 10px !important; padding: 8px !important;}
.btn-waze > a { background-color: #33ccff !important; color: #004d66 !important; }
.btn-maps > a { background-color: #fce8e6 !important; color: #c5221f !important; }

/* Cartão de Entregue */
.entregue-box { opacity: 0.7; background-color: #f0f7f4 !important; border: 1px dashed #c8e6c9 !important; }
.admin-card-header { text-align: center; background-color: #fef7e0; color: #b06000; font-weight: 800; padding: 10px; border-radius: 8px; margin-bottom: 12px; font-size: 16px; border: 1px solid #dfcdbb; }

div[data-baseweb="select"] { margin-top: 0px; }

@media (max-width: 768px) {
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    h1 { font-size: 20px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 10px !important; }
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
    """Busca pedidos Enviados (Ativos) e Entregues hoje (Concluídos)"""
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    # 1. Ativos (Enviados)
    query_env = supabase.table("pedidos").select("*").eq("status", "Enviado")
    if perfil_usuario == "Entregador" or driver_login:
        alvo = usuario.get("login") if perfil_usuario == "Entregador" else driver_login
        query_env = query_env.eq("entregador_login", alvo)
        
    res_env = query_env.execute()
    enviados = res_env.data or []
    enviados.sort(key=lambda x: (x.get('ordem_entrega') if x.get('ordem_entrega') is not None else 999, x.get('created_at')))
    
    # 2. Concluídos (Entregues hoje)
    query_ent = supabase.table("pedidos").select("*").eq("status", "Entregue")
    if perfil_usuario == "Entregador" or driver_login:
        alvo = usuario.get("login") if perfil_usuario == "Entregador" else driver_login
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
        st.toast("✅ Entregador atualizado com sucesso!")
    except Exception as e: 
        st.error(f"Erro ao atribuir: {e}")

def marcar_como_entregue(pedido, login_motorista):
    try:
        agora = datetime.now()
        hora_formatada = agora.strftime("%d/%m/%Y %H:%M")
        apenas_hora = agora.strftime("%H:%M")
        
        supabase.table("pedidos").update({"status": "Entregue", "ordem_entrega": 999, "hora_entrega_realizada": hora_formatada}).eq("id", pedido["id"]).execute()
        
        texto_telegram = f"""✅ *ENTREGA REALIZADA!* ✅\n\n🛵 *Entregador:* {login_motorista}\n📦 *Cesta:* {pedido.get('cesta_nome', '-')}\n💝 *Destinatário:* {pedido.get('destinatario_nome', '-')}\n📍 *Local:* {str(pedido.get('endereco', '')).split(',')[-1].split('(')[0].strip()}\n⏰ *Horário da Entrega:* {apenas_hora}"""
        enviar_notificacao_telegram(texto_telegram)
    except Exception as e:
        st.error(f"Erro ao finalizar entrega: {e}")


# Carregamento Global para Admin
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

    aba_geral, aba_visao_motoboy = st.tabs(["🗺️ Despacho e Rotas", "🚴 Visão por Entregador"])

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
        
        st.markdown("<h3 style='color: #b06000; margin-top: 15px;'>📦 Cestas na Rota (Aguardando Atribuição)</h3>", unsafe_allow_html=True)
        
        if not nao_atribuidos:
            st.caption("✨ Todas as cestas enviadas já foram atribuídas a um entregador.")
        else:
            cols_despacho = st.columns(3)
            for i, ped in enumerate(nao_atribuidos):
                with cols_despacho[i % 3]:
                    with st.container(border=True):
                        endereco_completo = ped.get('endereco', 'Endereço não informado')
                        data_entrega = formatar_data(ped.get('data_entrega'))
                        turno = ped.get('periodo_entrega', 'N/I')
                        hora_combinada = ped.get('horario_combinado', '')
                        hora_str = f" • Às {hora_combinada}" if hora_combinada else ""
                        
                        tel_dest = ped.get('destinatario_telefone')
                        tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                        
                        st.markdown(
                            f"""
                            <div style="margin-bottom: 8px;">
                                <span style="font-size: 11px; font-weight: 800; color: #9d7d65; text-transform: uppercase;">Pedido #{ped.get('id')}</span>
                                <div style="font-size: 12px; color: #444; margin-top: 2px;">👤 <strong>Comprador:</strong> {ped.get('cliente_nome')} (📞 {ped.get('cliente_telefone')})</div>
                                <div class="nome-destaque" style="margin-top: 4px;">🎁 <strong>{ped.get('cesta_nome')}</strong> para <em>{ped.get('destinatario_nome')}</em>{tel_dest_str}</div>
                                <div style="font-size: 12px; color: #333; font-weight: 700; margin-top: 6px; background: #faf7f3; padding: 6px; border-radius: 6px; border-left: 3px solid #dfcdbb;">📍 {endereco_completo}</div>
                                <div class="hora-destaque">📅 {data_entrega} | 🕒 {turno}{hora_str}</div>
                            </div>
                            """, unsafe_allow_html=True
                        )
                        
                        st.write("")
                        chave_widget = f"despacho_{ped['id']}"
                        st.selectbox("Definir Entregador:", opcoes_ent, index=0, key=chave_widget, on_change=atualizar_entregador, args=(ped["id"], chave_widget))

        tem_ativos_vinculados = any(p.get("entregador_login") for p in pedidos_ativos_geral)
        tem_concluidos_vinculados = any(p.get("entregador_login") for p in pedidos_concluidos_geral)

        if tem_ativos_vinculados or tem_concluidos_vinculados:
            st.divider()
            st.markdown("### 🛵 Rotas Ativas (Itens por Entregador)")
            if not lista_entregadores:
                st.info("Nenhum usuário com perfil 'Entregador' cadastrado no sistema.")
            else:
                cols_rotas = st.columns(2)
                data_hoje = datetime.now().strftime("%d-%m-%Y")
                
                for idx_driver, driver in enumerate(lista_entregadores):
                    ped_driver_ativos = [p for p in pedidos_ativos_geral if p.get("entregador_login") == driver]
                    ped_driver_concluidos = [p for p in pedidos_concluidos_geral if p.get("entregador_login") == driver]
                    
                    if not ped_driver_ativos and not ped_driver_concluidos:
                        continue 
                        
                    with cols_rotas[idx_driver % 2]:
                        with st.container(border=True):
                            st.markdown(f"<div class='admin-card-header'>🚴 Entregador: {driver}</div>", unsafe_allow_html=True)
                            
                            rota_arquivada = st.session_state.get(f"limpar_rota_{driver}_{data_hoje}", False)
                            if rota_arquivada:
                                ped_driver_concluidos = []

                            salvar_ordem(ped_driver_ativos)
                            
                            if ped_driver_ativos:
                                st.markdown("<span style='font-size:13px; font-weight:700; color:#5a3b28;'>Itens na Rota deste Entregador:</span>", unsafe_allow_html=True)
                                for i, ped in enumerate(ped_driver_ativos):
                                    with st.container(border=True):
                                        endereco_completo = ped.get('endereco', 'Endereço não informado')
                                        data_entrega = formatar_data(ped.get('data_entrega'))
                                        turno = ped.get('periodo_entrega', 'N/I')
                                        hora_combinada = ped.get('horario_combinado', '')
                                        hora_str = f" • Às {hora_combinada}" if hora_combinada else ""
                                        
                                        tel_dest = ped.get('destinatario_telefone')
                                        tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                                        
                                        st.markdown(
                                            f"""
                                            <div style="margin-bottom: 6px;">
                                                <div style="font-size:12px; color:#444;">👤 <strong>Comprador:</strong> {ped.get('cliente_nome')} (📞 {ped.get('cliente_telefone')})</div>
                                                <div style="font-size:13px; font-weight:800; color:#5a3b28; margin-top: 2px;">#{i+1} - 🎁 {ped.get('cesta_nome')} ({ped.get('destinatario_nome')}{tel_dest_str})</div>
                                                <div style="font-size:12px; color:#333; margin-top: 4px; background: #faf7f3; padding: 4px 8px; border-radius: 4px;">📍 {endereco_completo}</div>
                                                <div style="font-size: 11px; color: #b06000; font-weight: 700; margin-top: 4px;">📅 {data_entrega} | 🕒 {turno}{hora_str}</div>
                                            </div>
                                            """, unsafe_allow_html=True
                                        )
                                        
                                        chave_realocar = f"realocar_{ped['id']}"
                                        indice_atual = opcoes_ent.index(driver) if driver in opcoes_ent else 0
                                        st.selectbox("Realocar para:", opcoes_ent, index=indice_atual, key=chave_realocar, on_change=atualizar_entregador, args=(ped["id"], chave_realocar))
                                        
                                        st.write("")
                                        col_u, col_d = st.columns(2)
                                        with col_u:
                                            if i > 0:
                                                st.markdown('<div class="btn-updown">', unsafe_allow_html=True)
                                                if st.button("⬆️ Subir", key=f"up_admin_{ped['id']}", use_container_width=True):
                                                    ped_driver_ativos[i], ped_driver_ativos[i-1] = ped_driver_ativos[i-1], ped_driver_ativos[i]
                                                    salvar_ordem(ped_driver_ativos)
                                                    st.rerun()
                                                st.markdown('</div>', unsafe_allow_html=True)
                                        with col_d:
                                            if i < len(ped_driver_ativos) - 1:
                                                st.markdown('<div class="btn-updown">', unsafe_allow_html=True)
                                                if st.button("⬇️ Descer", key=f"down_admin_{ped['id']}", use_container_width=True):
                                                    ped_driver_ativos[i], ped_driver_ativos[i+1] = ped_driver_ativos[i+1], ped_driver_ativos[i]
                                                    salvar_ordem(ped_driver_ativos)
                                                    st.rerun()
                                                st.markdown('</div>', unsafe_allow_html=True)

                            if ped_driver_concluidos:
                                st.markdown("<span style='font-size:13px; font-weight:700; color:#137333; margin-top:10px; display:block;'>✅ Finalizados Hoje:</span>", unsafe_allow_html=True)
                                for ped in ped_driver_concluidos:
                                    hora_ext = ped.get('hora_entrega_realizada', '')[-5:]
                                    bairro_con = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip()
                                    st.markdown(f"""
                                    <div data-testid="stVerticalBlockBorderWrapper" class="entregue-box" style="padding: 8px !important;">
                                        <div style="font-size:12px; font-weight:700; color:#137333;">✅ Às {hora_ext} - 📍 {bairro_con} ({ped.get('cesta_nome')})</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                            if len(ped_driver_ativos) == 0 and len(ped_driver_concluidos) > 0:
                                st.write("")
                                if st.button(f"🧹 Concluir Entregas e Limpar Rota", key=f"btn_ok_{driver}", use_container_width=True):
                                    st.session_state[f"limpar_rota_{driver}_{data_hoje}"] = True
                                    st.rerun()

    # -------------------------------------------------
    # ABA 2: VISÃO POR ENTREGADOR (SIMULADOR DO APLICATIVO)
    # -------------------------------------------------
    with aba_visao_motoboy:
        st.markdown("### 🚴 Simulador de Tela do Entregador")
        st.caption("Selecione um entregador abaixo para visualizar exatamente o que ele enxerga no aplicativo de rotas dele.")
        
        lista_entregadores_todos = []
        try:
            res_ent = supabase.table("usuarios").select("login").eq("perfil", "Entregador").execute()
            lista_entregadores_todos = [e["login"] for e in (res_ent.data or [])]
        except: pass

        if not lista_entregadores_todos:
            st.warning("⚠️ Nenhum entregador cadastrado no sistema.")
        else:
            motoboy_selecionado = st.selectbox("Selecione o Entregador:", lista_entregadores_todos, key="select_vis_motoboy")
            st.divider()

            p_ativos_mb, p_concluidos_mb = buscar_entregas_dia(driver_login=motoboy_selecionado)

            if not p_ativos_mb and not p_concluidos_mb:
                st.info(f"📭 O entregador **{motoboy_selecionado}** não possui nenhuma entrega atribuída no momento.")
            else:
                st.markdown(f"#### Rota Atual de: 🚴 {motoboy_selecionado}")
                
                if p_ativos_mb:
                    salvar_ordem(p_ativos_mb)
                    for i, ped in enumerate(p_ativos_mb):
                        with st.container(border=True):
                            bairro = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip() or "Endereço incompleto"
                            horario = ped.get('horario_combinado', '') or ped.get('periodo_entrega', 'Livre')
                            data_e = formatar_data(ped.get('data_entrega'))
                            tel_dest = ped.get('destinatario_telefone')
                            tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                            
                            st.markdown(f"""
                                <div class="card-info">
                                    <div class="bairro-destaque">📍 Parada #{i+1} - {bairro}</div>
                                    <div style="font-size:12px; color:#444; margin-top: 2px;">👤 <strong>Comprador:</strong> {ped.get('cliente_nome')} (📞 {ped.get('cliente_telefone')})</div>
                                    <div class="nome-destaque" style="margin-top: 2px;">🎁 {ped.get('cesta_nome')} para <strong>{ped.get('destinatario_nome')}</strong>{tel_dest_str}</div>
                                    <div class="hora-destaque">📅 {data_e} | 🕒 {horario}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            endereco_gps = urllib.parse.quote(re.sub(r'\(CEP:.*?\)', '', ped.get('endereco', '')).strip())
                            c_m, c_w = st.columns(2)
                            with c_m:
                                st.markdown('<div class="btn-maps">', unsafe_allow_html=True)
                                st.link_button("🗺️ Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_gps}", use_container_width=True, key=f"map_sim_{ped['id']}")
                                st.markdown('</div>', unsafe_allow_html=True)
                            with c_w:
                                st.markdown('<div class="btn-waze">', unsafe_allow_html=True)
                                st.link_button("🚗 Waze", url=f"https://waze.com/ul?q={endereco_gps}&navigate=yes", use_container_width=True, key=f"wz_sim_{ped['id']}")
                                st.markdown('</div>', unsafe_allow_html=True)

                if p_concluidos_mb:
                    st.write("")
                    st.markdown("##### ✅ Entregas já realizadas hoje por ele:")
                    for ped in p_concluidos_mb:
                        hora_extraida = ped.get('hora_entrega_realizada', '')[-5:] 
                        bairro_concluido = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip()
                        tel_dest = ped.get('destinatario_telefone')
                        tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                        st.markdown(f"""
                        <div data-testid="stVerticalBlockBorderWrapper" class="entregue-box">
                            <div class="bairro-destaque" style="color: #137333;">✅ Entregue às {hora_extraida}</div>
                            <div class="nome-destaque">📍 {bairro_concluido}</div>
                            <div style="font-size:12px; color:#444;">👤 Comprador: {ped.get('cliente_nome')} (📞 {ped.get('cliente_telefone')})</div>
                            <div class="nome-destaque">🎁 {ped.get('cesta_nome')} para <strong>{ped.get('destinatario_nome')}</strong>{tel_dest_str}</div>
                        </div>
                        """, unsafe_allow_html=True)


# =====================================================
# VISÃO 2: ENTREGADOR (APLICATIVO GPS DO MOTOBOY)
# =====================================================
else:
    st.title(f"🛵 Rota de Entregas")

    pedidos_ativos_driver, pedidos_concluidos_driver = buscar_entregas_dia()

    if not pedidos_ativos_driver and not pedidos_concluidos_driver:
        st.success("🎉 Nenhuma entrega pendente. A rota está limpa!")
        st.session_state.modo_entrega_ativa = False
        st.stop()

    if not st.session_state.modo_entrega_ativa:
        if pedidos_ativos_driver:
            st.info("👇 Ajuste sua rota clicando nas setas e Inicie quando estiver pronto.")
            salvar_ordem(pedidos_ativos_driver)
            
            for i, ped in enumerate(pedidos_ativos_driver):
                with st.container(border=True):
                    col_info, col_up, col_down = st.columns([5, 1, 1])
                    with col_info:
                        bairro = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip() or "Endereço incompleto"
                        horario = ped.get('horario_combinado', '') or ped.get('periodo_entrega', 'Livre')
                        data_e = formatar_data(ped.get('data_entrega'))
                        tel_dest = ped.get('destinatario_telefone')
                        tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
                        st.markdown(f"""
                            <div class="card-info">
                                <div class="bairro-destaque">📍 {i+1}º - {bairro}</div>
                                <div style="font-size:12px; color:#444;">👤 <strong>Comprador:</strong> {ped.get('cliente_nome')} (📞 {ped.get('cliente_telefone')})</div>
                                <div class="nome-destaque">🎁 {ped.get('cesta_nome')} para <strong>{ped.get('destinatario_nome')}</strong>{tel_dest_str}</div>
                                <div class="hora-destaque">📅 {data_e} | 🕒 {horario}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    with col_up:
                        if i > 0:
                            st.markdown('<div class="btn-updown">', unsafe_allow_html=True)
                            if st.button("⬆️", key=f"up_{ped['id']}", use_container_width=True):
                                pedidos_ativos_driver[i], pedidos_ativos_driver[i-1] = pedidos_ativos_driver[i-1], pedidos_ativos_driver[i]
                                salvar_ordem(pedidos_ativos_driver)
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

                    with col_down:
                        if i < len(pedidos_ativos_driver) - 1:
                            st.markdown('<div class="btn-updown">', unsafe_allow_html=True)
                            if st.button("⬇️", key=f"down_{ped['id']}", use_container_width=True):
                                pedidos_ativos_driver[i], pedidos_ativos_driver[i+1] = pedidos_ativos_driver[i+1], pedidos_ativos_driver[i]
                                salvar_ordem(pedidos_ativos_driver)
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            if st.button("🚀 INICIAR ROTA DE ENTREGA", type="primary", use_container_width=True):
                st.session_state.modo_entrega_ativa = True
                st.rerun()
        else:
            st.success("🎉 Fila ativa vazia! Todas as entregas programadas foram finalizadas.")

    else:
        if pedidos_ativos_driver:
            pedido_atual = pedidos_ativos_driver[0] 
            st.warning("⚠️ **Atenção:** Entregue este pedido antes de ir para o próximo.")
            
            with st.container(border=True):
                st.markdown(f'<div class="bairro-destaque" style="font-size:20px; text-align:center;">Próxima Parada</div>', unsafe_allow_html=True)
                st.divider()
                tel_dest_atual = pedido_atual.get('destinatario_telefone')
                tel_dest_atual_str = f" (📞 {tel_dest_atual})" if tel_dest_atual else " (Sem telefone)"
                st.markdown(f"""
                    <div class="ficha-entrega">
                        <div><strong>Comprador:</strong> {pedido_atual.get('cliente_nome')} (📞 {pedido_atual.get('cliente_telefone')})</div>
                        <div class="ficha-secao"><strong>Pacote:</strong> 🎁 {pedido_atual.get('cesta_nome')}</div>
                        <div class="ficha-secao"><strong>Homenageado (Quem Recebe):</strong><br>{pedido_atual.get('destinatario_nome')}{tel_dest_atual_str}</div>
                        <div class="ficha-secao"><strong>Endereço Completo:</strong><br>📍 {pedido_atual.get('endereco')}</div>
                        <div class="ficha-secao"><strong>Data e Horário:</strong><br>📅 {formatar_data(pedido_atual.get('data_entrega'))} | 🕒 {pedido_atual.get('horario_combinado') or pedido_atual.get('periodo_entrega', 'Livre')}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                endereco_gps = urllib.parse.quote(re.sub(r'\(CEP:.*?\)', '', pedido_atual.get('endereco', '')).strip())
                c_maps, c_waze = st.columns(2)
                with c_maps:
                    st.markdown('<div class="btn-maps">', unsafe_allow_html=True)
                    st.link_button("🗺️ Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={endereco_gps}", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with c_waze:
                    st.markdown('<div class="btn-waze">', unsafe_allow_html=True)
                    st.link_button("🚗 Waze", url=f"https://waze.com/ul?q={endereco_gps}&navigate=yes", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            if st.button("✅ MARCAR COMO ENTREGUE", type="primary", use_container_width=True):
                with st.spinner("Confirmando entrega e avisando a central..."):
                    marcar_como_entregue(pedido_atual, usuario.get('login', 'Motoboy'))
                st.rerun() 
                
            st.write("")
            if st.button("⏸️ Pausar e Voltar à Fila", use_container_width=True):
                st.session_state.modo_entrega_ativa = False
                st.rerun()
        else:
            st.session_state.modo_entrega_ativa = False
            st.rerun()

    if pedidos_concluidos_driver and not st.session_state.modo_entrega_ativa:
        st.write("")
        st.markdown("### ✅ Minhas Entregas Hoje")
        
        for ped in pedidos_concluidos_driver:
            hora_extraida = ped.get('hora_entrega_realizada', '')[-5:] 
            bairro_concluido = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip()
            tel_dest = ped.get('destinatario_telefone')
            tel_dest_str = f" (📞 {tel_dest})" if tel_dest else ""
            st.markdown(f"""
            <div data-testid="stVerticalBlockBorderWrapper" class="entregue-box">
                <div class="bairro-destaque" style="color: #137333;">✅ Entregue às {hora_extraida}</div>
                <div class="nome-destaque">📍 {bairro_concluido}</div>
                <div style="font-size:12px; color:#444;">👤 Comprador: {ped.get('cliente_nome')} (📞 {ped.get('cliente_telefone')})</div>
                <div class="nome-destaque">🎁 {ped.get('cesta_nome')} para <strong>{ped.get('destinatario_nome')}</strong>{tel_dest_str}</div>
            </div>
            """, unsafe_allow_html=True)
