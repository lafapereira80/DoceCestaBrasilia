import streamlit as st
import json
import urllib.parse

from services.pedido_service import (
    buscar_pedido,
    atualizar_pedido,
    atualizar_anotacao_pedido
)

from services.pedido_adicional_service import (
    listar_adicionais_pedido
)

from services.foto_service import (
    listar_fotos
)

from services.cesta_service import (
    buscar_cesta,
    listar_cestas
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
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #dfcdbb !important; border-radius: 12px !important; padding: 8px 12px !important; margin-bottom: 4px !important; box-shadow: 0 1px 3px rgba(90, 59, 40, 0.03); }
.card-title { font-size: 14px !important; font-weight: 700 !important; color: #5a3b28 !important; margin-bottom: 6px !important; }
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
# VALIDA PEDIDO ABERTO
# =====================================================

if "pedido_aberto" not in st.session_state:
    st.error("Nenhum pedido selecionado.")
    if st.button("⬅ Voltar"):
        st.switch_page("pages/02_Pedidos.py")
    st.stop()

pedido_id = st.session_state["pedido_aberto"]


# =====================================================
# BUSCA PEDIDO E ADICIONAIS
# =====================================================

try:
    pedido = buscar_pedido(pedido_id)
except Exception as erro:
    st.error(f"Erro ao carregar pedido: {erro}")
    st.stop()

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()

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
# FUNÇÕES AUXILIARES
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


# =====================================================
# GERA WHATSAPP
# =====================================================

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
        st.markdown('<div class="card-title">✏️ Editando Pedido</div>', unsafe_allow_html=True)
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            novo_nome = st.text_input("👤 Nome Comprador", value=pedido.get("cliente_nome") or "")
            novo_telefone = st.text_input("📱 Telefone Comprador", value=pedido.get("cliente_telefone") or "")
            novo_dest_nome = st.text_input("💝 Nome Destinatário", value=pedido.get("destinatario_nome") or "")
            novo_dest_tel = st.text_input("📱 Telefone Destinatário", value=pedido.get("destinatario_telefone") or "")
            novo_motivo = st.text_input("🎉 Motivo da Homenagem", value=pedido.get("motivo_homenagem") or "")
        with col_e2:
            try:
                nomes_cestas = [c.get("nome", "") for c in listar_cestas()]
            except: nomes_cestas = []
            cesta_atual = pedido.get("cesta_nome") or ""
            nova_cesta = st.selectbox("🎁 Cesta", nomes_cestas, index=nomes_cestas.index(cesta_atual) if cesta_atual in nomes_cestas else 0) if nomes_cestas else cesta_atual
            nova_mensagem = st.text_area("💌 Mensagem do Cartão", value=pedido.get("mensagem") or "", height=70)
            novo_especial = st.text_area("✨ Pedido Especial", value=pedido.get("pedido_especial") or "", height=70)
            novo_endereco = st.text_area("📍 Endereço de Entrega", value=pedido.get("endereco") or "", height=70)

        col_salvar, col_cancelar = st.columns(2)
        with col_salvar:
            if st.button("💾 Salvar Alterações", use_container_width=True, type="primary"):
                dados = {"cliente_nome": novo_nome, "cliente_telefone": novo_telefone, "destinatario_nome": novo_dest_nome, "destinatario_telefone": novo_dest_tel, "motivo_homenagem": novo_motivo, "cesta_nome": nova_cesta, "mensagem": nova_mensagem, "pedido_especial": novo_especial, "endereco": novo_endereco}
                atualizar_pedido(pedido["id"], dados)
                st.success("Pedido alterado com sucesso!")
                st.session_state.editar_pedido = False
                st.rerun()
        with col_cancelar:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.editar_pedido = False
                st.rerun()


# =====================================================
# LAYOUT PRINCIPAL (2 COLUNAS LADO A LADO)
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
                for item in produtos.split("\n"): st.write(f"• {item}")
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
        st.text_area("", value=pedido.get("endereco") or "", disabled=True, height=60, key="endereco_entrega")


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
    # MOTOR DE FOTOS (VIA SERVICE) - BLINDADO
    # =====================================================
    with st.container(border=True):
        st.markdown('<div class="card-title">📷 Fotos da Polaroid</div>', unsafe_allow_html=True)
        try:
            fotos = listar_fotos(pedido["id"])
            if fotos:
                colunas = st.columns(2)
                for i, foto in enumerate(fotos):
                    with colunas[i % 2]:
                        # A BLINDAGEM: Tenta pegar a URL de todas as formas possíveis.
                        # Se vier vazia do banco (None), monta o link na hora.
                        link_imagem = foto.get("url") or foto.get("url_publica")
                        
                        if not link_imagem and foto.get("arquivo"):
                            url_base = st.secrets["SUPABASE_URL"].rstrip("/")
                            link_imagem = f"{url_base}/storage/v1/object/public/pedido_fotos/{foto.get('arquivo')}"

                        # Só manda o Streamlit desenhar se o link não for Vazio (evita o erro format)
                        if link_imagem:
                            st.image(link_imagem, caption=foto.get("nome_original", "Foto"), use_container_width=True)
                        else:
                            st.caption("⚠️ Link da foto indisponível.")
            else:
                st.caption("Nenhuma foto enviada ou arquivos inválidos.")
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
