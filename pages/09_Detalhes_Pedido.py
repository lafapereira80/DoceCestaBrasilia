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
# CSS ULTRA COMPACTO E ISOLADO
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1250px;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

h1 {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 0px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 12px !important;
}

/* ==========================================
   CARDS COMPACTOS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #dfcdbb !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    margin-bottom: 4px !important;
    box-shadow: 0 1px 3px rgba(90, 59, 40, 0.03);
}

.card-title {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #5a3b28 !important;
    margin-bottom: 6px !important;
}

/* ==========================================
   TEXTOS INTERNOS
========================================== */
.info-label {
    font-weight: 700;
    color: #775a46;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.info-value {
    margin-bottom: 4px;
    color: #222;
    font-weight: 600;
    font-size: 13px !important;
}

/* ==========================================
   CARD RESUMO
========================================== */
.resumo-card {
    background: #fff8ef;
    border: 1px solid #e6d1bb;
    border-radius: 10px;
    padding: 10px 12px;
}

.resumo-card table {
    width: 100%;
}

.resumo-card td {
    padding: 3px 0;
    font-size: 12px !important;
}

/* ==========================================
   BOTÕES E INPUTS
========================================== */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 12px !important;
    padding: 2px 6px !important;
    border-radius: 8px !important;
    min-height: 32px !important;
}
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
# BUSCA PEDIDO
# =====================================================

try:
    pedido = buscar_pedido(pedido_id)
except Exception as erro:
    st.error(f"Erro ao carregar pedido: {erro}")
    st.stop()

if not pedido:
    st.error("Pedido não encontrado.")
    st.stop()


# =====================================================
# BUSCA ADICIONAIS
# =====================================================

try:
    adicionais_pedido = listar_adicionais_pedido(pedido["id"])
except:
    adicionais_pedido = []


# =====================================================
# CONTROLE DE EDIÇÃO
# =====================================================

if "editar_pedido" not in st.session_state:
    st.session_state.editar_pedido = False


# =====================================================
# VALORES SOB CONSULTA
# =====================================================

itens_consulta_salvos = pedido.get("itens_consulta", {})

if isinstance(itens_consulta_salvos, str):
    try:
        itens_consulta_salvos = json.loads(itens_consulta_salvos)
    except:
        itens_consulta_salvos = {}

if not isinstance(itens_consulta_salvos, dict):
    itens_consulta_salvos = {}


# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def formatar_valor(valor):
    try:
        return (
            f"R$ {float(valor):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X",".")
        )
    except:
        return "R$ 0,00"


def limpar_telefone(numero):
    return (
        str(numero)
        .replace("(","")
        .replace(")","")
        .replace("-","")
        .replace(" ","")
    )


def formatar_data(data):
    if not data:
        return "-"
    try:
        ano, mes, dia = str(data)[:10].split("-")
        return f"{dia}/{mes}/{ano}"
    except:
        return str(data)


# =====================================================
# GERA WHATSAPP
# =====================================================

def gerar_whatsapp(pedido, adicionais, valor_final):
    itens_consulta = pedido.get("itens_consulta", {})

    if isinstance(itens_consulta, str):
        try:
            itens_consulta = json.loads(itens_consulta)
        except:
            itens_consulta = {}

    lista_adicionais = []

    for item in adicionais:
        nome = item.get("nome_produto", "-")
        valor = item.get("valor_unitario")

        if valor is not None:
            lista_adicionais.append(f"• {nome} - {formatar_valor(valor)}")
        else:
            valor_manual = itens_consulta.get(nome, 0)
            if valor_manual:
                lista_adicionais.append(f"• {nome} - {formatar_valor(valor_manual)}")
            else:
                lista_adicionais.append(f"• {nome} (sob consulta)")

    texto = (
        f"🎁 *Doce Cesta Brasília*\n\n"
        f"Olá {pedido.get('cliente_nome','') if pedido else ''}!\n\n"
        f"🎀 Cesta: {pedido.get('cesta_nome','-') if pedido else '-'}\n\n"
        f"🛒 Produtos:\n"
        f"{pedido.get('produtos','-') if pedido else '-'}\n\n"
        f"🎀 Adicionais:\n"
        f"{chr(10).join(lista_adicionais)}\n\n"
        f"📍 Entrega:\n"
        f"Data: {formatar_data(pedido.get('data_entrega')) if pedido else '-'}\n"
        f"Período: {pedido.get('periodo_entrega','-') if pedido else '-'}\n"
        f"Horário: {pedido.get('horario_combinado','-') if pedido else '-'}\n\n"
        f"💳 Pagamento: {pedido.get('pagamento','-') if pedido else '-'}\n"
        f"💰 Valor Final: {formatar_valor(valor_final)}\n\n"
        f"Obrigado! ❤️"
    )

    telefone = limpar_telefone(pedido.get("cliente_telefone", ""))

    return f"https://wa.me/55{telefone}?text={urllib.parse.quote(texto)}"


# =====================================================
# CABEÇALHO & AÇÕES
# =====================================================

col_t1, col_t2 = st.columns([3, 1])

with col_t1:
    st.title("📋 Detalhes do Pedido")
    st.caption(f"Pedido #{pedido.get('id')} | Status: **{pedido.get('status','-')}**")

with col_t2:
    if st.button("✏️ Alterar Pedido", use_container_width=True):
        st.session_state.editar_pedido = not st.session_state.editar_pedido


# =====================================================
# CARD - EDIÇÃO DO PEDIDO
# =====================================================

if st.session_state.editar_pedido:
    with st.container(border=True):
        st.markdown('<div class="card-title">✏️ Editando Pedido</div>', unsafe_allow_html=True)

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            novo_nome = st.text_input("👤 Nome", value=pedido.get("cliente_nome", ""))
            novo_telefone = st.text_input("📱 Telefone", value=pedido.get("cliente_telefone", ""))

            try:
                cestas = listar_cestas()
                nomes_cestas = [c.get("nome", "") for c in cestas]
            except:
                nomes_cestas = []

            cesta_atual = pedido.get("cesta_nome", "")

            if nomes_cestas:
                indice_cesta = nomes_cestas.index(cesta_atual) if cesta_atual in nomes_cestas else 0
                nova_cesta = st.selectbox("🎁 Cesta", nomes_cestas, index=indice_cesta)
            else:
                nova_cesta = cesta_atual

        with col_e2:
            nova_mensagem = st.text_area("💌 Mensagem", value=pedido.get("mensagem", ""), height=60)
            novo_especial = st.text_area("✨ Pedido Especial", value=pedido.get("pedido_especial", ""), height=60)
            novo_endereco = st.text_area("📍 Endereço", value=pedido.get("endereco", ""), height=60)

        col_salvar, col_cancelar = st.columns(2)

        with col_salvar:
            if st.button("💾 Salvar Alterações", use_container_width=True, type="primary"):
                dados = {
                    "cliente_nome": novo_nome,
                    "cliente_telefone": novo_telefone,
                    "cesta_nome": nova_cesta,
                    "mensagem": nova_mensagem,
                    "pedido_especial": novo_especial,
                    "endereco": novo_endereco
                }
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

# =====================================================
# COLUNA DA ESQUERDA (DADOS DO PEDIDO & ITENS)
# =====================================================

with col_esquerda:
    # Card Cliente
    with st.container(border=True):
        st.markdown('<div class="card-title">👤 Cliente</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="info-label">Nome</div><div class="info-value">{pedido.get("cliente_nome","-")}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="info-label">CPF</div><div class="info-value">{pedido.get("cliente_cpf","-")}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="info-label">Telefone</div><div class="info-value">{pedido.get("cliente_telefone","-")}</div>', unsafe_allow_html=True)

    # Card Informações do Pedido
    with st.container(border=True):
        st.markdown('<div class="card-title">🎁 Pedido</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="info-label">Cesta</div><div class="info-value">{pedido.get("cesta_nome","-")}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="info-label">Pagamento</div><div class="info-value">{pedido.get("pagamento","-")}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="info-label">Entrega</div><div class="info-value">{formatar_data(pedido.get("data_entrega"))}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="info-label">Período</div><div class="info-value">{pedido.get("periodo_entrega","-")}</div>', unsafe_allow_html=True)

    # Produtos da Cesta & Adicionais
    c_p1, c_p2 = st.columns(2)
    valor_adicionais = 0.0
    valor_consulta = 0.0
    itens_consulta = {}

    with c_p1:
        with st.container(border=True):
            st.markdown('<div class="card-title">🛒 Produtos da Cesta</div>', unsafe_allow_html=True)
            produtos = pedido.get("produtos", "")
            if produtos:
                for item in produtos.split("\n"):
                    st.write(f"• {item}")
            else:
                st.caption("Nenhum produto informado.")

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
            else:
                st.caption("Nenhum adicional selecionado.")

    # Mensagem & Pedido Especial
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        with st.container(border=True):
            st.markdown('<div class="card-title">💌 Mensagem da Cesta</div>', unsafe_allow_html=True)
            st.text_area("", value=pedido.get("mensagem", ""), disabled=True, height=60, key="mensagem_cliente")

    with c_m2:
        with st.container(border=True):
            st.markdown('<div class="card-title">✨ Pedido Especial</div>', unsafe_allow_html=True)
            st.text_area("", value=pedido.get("pedido_especial", ""), disabled=True, height=60, key="pedido_especial")

    # Endereço
    with st.container(border=True):
        st.markdown('<div class="card-title">📍 Endereço de Entrega</div>', unsafe_allow_html=True)
        st.text_area("", value=pedido.get("endereco", ""), disabled=True, height=60, key="endereco_entrega")


# =====================================================
# COLUNA DA DIREITA (FINANCEIRO, ANOTAÇÕES & FOTOS)
# =====================================================

with col_direita:
    # Busca Preço da Cesta
    valor_cesta = 0.0
    try:
        if pedido.get("cesta_id"):
            cesta = buscar_cesta(pedido["cesta_id"])
            if cesta:
                valor_cesta = float(cesta.get("preco", 0) or 0)
    except:
        valor_cesta = 0.0

    # Fechamento Financeiro
    with st.container(border=True):
        st.markdown('<div class="card-title">💰 Fechamento Financeiro</div>', unsafe_allow_html=True)

        cf1, cf2, cf3 = st.columns(3)
        with cf1:
            valor_frete = st.number_input("🚚 Frete", min_value=0.0, value=float(pedido.get("valor_frete", 0) or 0), step=1.0, key="frete")
        with cf2:
            desconto = st.number_input("🏷️ Desconto", min_value=0.0, value=float(pedido.get("desconto", 0) or 0), step=1.0, key="desconto")
        with cf3:
            status_opcoes = ["Recebido", "Pago", "Desistência", "Entregue"]
            status_atual = pedido.get("status", "Recebido")
            if status_atual not in status_opcoes:
                status_atual = "Recebido"
            status = st.selectbox("Status", status_opcoes, index=status_opcoes.index(status_atual))

        horario_combinado = st.text_input("🕒 Horário Combinado de Entrega", value=pedido.get("horario_combinado", ""), placeholder="Ex: 15:30")

    # Resumo Final do Valor
    valor_total_calculado = valor_cesta + valor_adicionais + valor_frete - desconto
    if valor_total_calculado < 0:
        valor_total_calculado = 0

    with st.container(border=True):
        st.markdown('<div class="card-title">🧮 Resumo do Pedido</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="resumo-card">
            <table>
            <tr><td>🎁 Cesta</td><td align="right"><b>{formatar_valor(valor_cesta)}</b></td></tr>
            <tr><td>🎀 Adicionais</td><td align="right"><b>{formatar_valor(valor_adicionais)}</b></td></tr>
            <tr><td>⚠️ Sob consulta</td><td align="right"><b>{formatar_valor(valor_consulta)}</b></td></tr>
            <tr><td>🚚 Frete</td><td align="right"><b>{formatar_valor(valor_frete)}</b></td></tr>
            <tr><td>🏷️ Desconto</td><td align="right"><b>{formatar_valor(desconto)}</b></td></tr>
            <tr><td><b>💰 TOTAL</b></td><td align="right"><h3 style="margin:0; color:#2e7d32;">{formatar_valor(valor_total_calculado)}</h3></td></tr>
            </table>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption(f"💳 Forma de Pagamento: **{pedido.get('pagamento','-')}**")

    # WhatsApp Link
    with st.container(border=True):
        st.markdown('<div class="card-title">📲 Atendimento WhatsApp</div>', unsafe_allow_html=True)
        if valor_total_calculado > 0:
            link_whatsapp = gerar_whatsapp(pedido, adicionais_pedido, valor_total_calculado)
            st.link_button("📲 Enviar resumo pelo WhatsApp", link_whatsapp, use_container_width=True)
        else:
            st.info("Defina os valores para liberar o WhatsApp.")

    # Anotações Internas
    with st.container(border=True):
        st.markdown('<div class="card-title">📝 Anotações Internas</div>', unsafe_allow_html=True)
        anotacao = st.text_area("Observações do atendimento", value=pedido.get("anotacoes_internas", "") or "", height=70, key="campo_anotacao")
        if st.button("💾 Salvar Anotação", use_container_width=True):
            atualizar_anotacao_pedido(pedido["id"], anotacao)
            st.success("✅ Anotação salva!")
            st.rerun()

    # Fotos Polaroid
    with st.container(border=True):
        st.markdown('<div class="card-title">📷 Fotos da Polaroid</div>', unsafe_allow_html=True)
        try:
            fotos = listar_fotos(pedido["id"])
            if fotos:
                colunas = st.columns(4)
                for i, foto in enumerate(fotos):
                    with colunas[i % 4]:
                        st.image(foto.get("url"), caption=foto.get("nome_original", "Foto"), use_container_width=True)
            else:
                st.caption("Nenhuma foto enviada.")
        except Exception as erro:
            st.error(f"Erro ao carregar fotos: {erro}")


# =====================================================
# BOTÕES FINAIS
# =====================================================

col_bot1, col_bot2 = st.columns(2)

with col_bot1:
    if st.button("💾 Salvar Atendimento Completo", use_container_width=True, type="primary"):
        dados = {
            "status": status,
            "valor_frete": valor_frete,
            "desconto": desconto,
            "valor_total": valor_total_calculado,
            "horario_combinado": horario_combinado,
            "itens_consulta": itens_consulta
        }
        atualizar_pedido(pedido["id"], dados)
        st.success("✅ Atendimento salvo com sucesso!")
        st.rerun()

with col_bot2:
    if st.button("⬅ Voltar para Pedidos", use_container_width=True):
        st.switch_page("pages/02_Pedidos.py")
