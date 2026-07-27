import streamlit as st
import urllib.parse
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Gestão de Entregas", page_icon="🛵", layout="wide")
configurar_pagina()
menu_lateral()

usuario = st.session_state.usuario

# =====================================================
# ESTILOS MOBILE-FIRST (APLICATIVO)
# =====================================================
st.markdown(
"""
<style>
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 800px; }
h1 { font-size: 22px !important; font-weight: 800 !important; color: #5a3b28; margin-bottom: 5px !important; text-align: center;}
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 12px 14px !important; margin-bottom: 8px !important; box-shadow: 0 2px 4px rgba(90, 59, 40, 0.04); }
.card-compact { display: flex; justify-content: space-between; align-items: center; }
.card-info { flex: 1; }
.bairro-destaque { font-size: 15px; font-weight: 800; color: #333; margin-bottom: 2px;}
.nome-destaque { font-size: 13px; font-weight: 600; color: #666; }
.hora-destaque { font-size: 12px; font-weight: 700; color: #b06000; background: #fef7e0; padding: 2px 6px; border-radius: 6px; display: inline-block; margin-top:4px;}
.btn-updown button { font-size: 18px !important; padding: 0 !important; height: 36px !important; width: 36px !important; border-radius: 50% !important; border: 1px solid #dfcdbb !important; background: #faf7f3 !important; }
.btn-updown button:hover { background: #e8ddd3 !important; }

.ficha-entrega { font-size: 14px; color: #444; }
.ficha-entrega strong { color: #5a3b28; }
.ficha-secao { margin-top: 12px; padding-top: 12px; border-top: 1px dashed #dfcdbb; }

div[data-testid="stLinkButton"] > a { font-weight: 700 !important; font-size: 14px !important; border-radius: 10px !important; padding: 8px !important;}
.btn-waze > a { background-color: #33ccff !important; color: #004d66 !important; }
.btn-maps > a { background-color: #fce8e6 !important; color: #c5221f !important; }

@media (max-width: 768px) {
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    h1 { font-size: 20px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 10px !important; }
}
</style>
""", unsafe_allow_html=True)

# Controle de Estado da Rota
if "modo_entrega_ativa" not in st.session_state:
    st.session_state.modo_entrega_ativa = False

# =====================================================
# BANCO DE DADOS - BUSCAR E ATUALIZAR
# =====================================================
def buscar_entregas():
    query = supabase.table("pedidos").select("*").eq("status", "Enviado")
    if usuario["perfil"] == "Entregador":
        query = query.eq("entregador_login", usuario["login"])
    
    res = query.execute()
    pedidos = res.data or []
    # Ordena pelos que tem ordem_entrega (nulos jogados pro final) e depois data
    pedidos.sort(key=lambda x: (x.get('ordem_entrega') if x.get('ordem_entrega') is not None else 999, x.get('created_at')))
    return pedidos

def salvar_ordem(pedidos_ordenados):
    for i, p in enumerate(pedidos_ordenados):
        if p.get("ordem_entrega") != i:
            supabase.table("pedidos").update({"ordem_entrega": i}).eq("id", p["id"]).execute()

def marcar_como_entregue(pedido_id):
    supabase.table("pedidos").update({"status": "Entregue", "ordem_entrega": 999}).eq("id", pedido_id).execute()

# Carrega os pedidos dinamicamente
pedidos = buscar_entregas()

st.title(f"🛵 Rota de Entregas ({len(pedidos)})")

# Se não tem entregas
if not pedidos:
    st.success("🎉 Nenhuma entrega pendente! A rota está limpa.")
    st.session_state.modo_entrega_ativa = False
    st.stop()

# Garante que todos tem uma ordem salva no banco
salvar_ordem(pedidos)


# =====================================================
# MODO 1: ORGANIZAÇÃO (FILA DE ENTREGA)
# =====================================================
if not st.session_state.modo_entrega_ativa:
    st.info("👇 Ajuste a ordem clicando nas setas e inicie a rota quando estiver pronto.")
    
    for i, ped in enumerate(pedidos):
        with st.container(border=True):
            col_info, col_up, col_down = st.columns([5, 1, 1])
            
            with col_info:
                bairro = str(ped.get('endereco', '')).split(',')[-1].split('(')[0].strip() or "Endereço incompleto"
                horario = ped.get('horario_combinado', '') or ped.get('periodo_entrega', 'Horário Livre')
                
                st.markdown(f"""
                    <div class="card-info">
                        <div class="bairro-destaque">📍 {i+1}º - {bairro}</div>
                        <div class="nome-destaque">Para: {ped.get('destinatario_nome', 'N/A')}</div>
                        <div class="hora-destaque">🕒 {horario}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_up:
                if i > 0:
                    st.markdown('<div class="btn-updown">', unsafe_allow_html=True)
                    if st.button("⬆️", key=f"up_{ped['id']}", use_container_width=True):
                        # Troca de lugar com o de cima
                        pedidos[i], pedidos[i-1] = pedidos[i-1], pedidos[i]
                        salvar_ordem(pedidos)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            with col_down:
                if i < len(pedidos) - 1:
                    st.markdown('<div class="btn-updown">', unsafe_allow_html=True)
                    if st.button("⬇️", key=f"down_{ped['id']}", use_container_width=True):
                        # Troca de lugar com o de baixo
                        pedidos[i], pedidos[i+1] = pedidos[i+1], pedidos[i]
                        salvar_ordem(pedidos)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    if st.button("🚀 INICIAR ROTA DE ENTREGA", type="primary", use_container_width=True):
        st.session_state.modo_entrega_ativa = True
        st.rerun()

# =====================================================
# MODO 2: GPS E CONFIRMAÇÃO (ENTREGA ATIVA)
# =====================================================
else:
    pedido_atual = pedidos[0] # Puxa sempre o que está no topo da fila
    
    st.warning("⚠️ **Atenção:** Você está com a rota iniciada. Entregue este pedido antes de ir para o próximo.")
    
    with st.container(border=True):
        st.markdown(f'<div class="bairro-destaque" style="font-size:20px; text-align:center;">Próxima Parada</div>', unsafe_allow_html=True)
        st.divider()
        
        st.markdown(f"""
            <div class="ficha-entrega">
                <div><strong>Comprador:</strong> {pedido_atual.get('cliente_nome')} (📞 +{pedido_atual.get('cliente_telefone')})</div>
                <div class="ficha-secao">
                    <strong>Homenageado (Quem Recebe):</strong><br>
                    {pedido_atual.get('destinatario_nome')}<br>
                    📞 {pedido_atual.get('destinatario_telefone') or 'Sem telefone'}
                </div>
                <div class="ficha-secao">
                    <strong>Pacote:</strong> 🎁 {pedido_atual.get('cesta_nome')}
                </div>
                <div class="ficha-secao">
                    <strong>Endereço Completo:</strong><br>
                    📍 {pedido_atual.get('endereco')}
                </div>
                <div class="ficha-secao">
                    <strong>Horário Combinado:</strong><br>
                    🕒 {pedido_atual.get('horario_combinado') or pedido_atual.get('periodo_entrega', 'Livre')}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        # Botões de GPS
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
        marcar_como_entregue(pedido_atual["id"])
        st.rerun() # Atualiza a tela, o próximo pedido subirá automaticamente
        
    st.write("")
    if st.button("⏸️ Pausar e Voltar à Fila", use_container_width=True):
        st.session_state.modo_entrega_ativa = False
        st.rerun()
