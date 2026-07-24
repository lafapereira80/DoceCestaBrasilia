import streamlit as st

from config.supabase import supabase  # Importação direta para driblar o cache

from services.cesta_service import (
    buscar_cesta,
    atualizar_cesta,
    upload_imagem_cesta,
    remover_imagem_cesta,
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
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Editar Cesta",
    page_icon="✏️",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()


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
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1050px;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}

h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-top: 6px !important;
    margin-bottom: 6px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINER CARD DO FORMULÁRIO
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* =========================================
   CUSTOMIZAÇÃO DO UPLOADER MODERNO (DROPZONE)
========================================== */
div[data-testid="stFileUploader"] {
    width: 100% !important;
}

div[data-testid="stFileUploader"] section {
    background-color: #faf7f3 !important;
    border: 2px dashed #dfcdbb !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stFileUploader"] section:hover {
    border-color: #a87b57 !important;
    background-color: #f5eee6 !important;
}

div[data-testid="stFileUploader"] section button {
    background-color: #ffffff !important;
    border: 1px solid #dfcdbb !important;
    color: #5a3b28 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 4px 12px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stFileUploader"] section button span {
    display: none !important;
}

div[data-testid="stFileUploader"] section button::after {
    content: "📁 Selecionar Foto" !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

/* Botões da Página */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 13px !important;
    border-radius: 8px !important;
    min-height: 36px !important;
}

.stImage img {
    border-radius: 8px;
    object-fit: cover;
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# VERIFICA CESTA
# =====================================================

if "cesta_editar" not in st.session_state:
    st.warning("Nenhuma cesta selecionada.")
    if st.button("⬅ Voltar"):
        st.switch_page("pages/04_Cestas.py")
    st.stop()

cesta_id = st.session_state["cesta_editar"]


# =====================================================
# BUSCA CESTA
# =====================================================

try:
    cesta = buscar_cesta(cesta_id)
    if not cesta:
        st.error("Cesta não encontrada.")
        st.stop()
except Exception as erro:
    st.error(f"Erro ao carregar cesta: {erro}")
    st.stop()


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

st.title("✏️ Editar Cesta")
st.caption("Atualize os dados, a posição e a imagem da cesta.")
st.divider()


# =====================================================
# FORMULÁRIO DE EDIÇÃO (SIDE-BY-SIDE COMPACTO)
# =====================================================

with st.container(border=True):
    col_dados, col_imagem = st.columns([1.3, 1])

    # Coluna 1: Informações da Cesta
    with col_dados:
        st.subheader("📝 Dados Principais")
        nome = st.text_input("Nome da Cesta", value=cesta.get("nome", ""), placeholder="Ex: Cesta Café Especial")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            preco = st.number_input("Preço (R$)", min_value=0.0, value=float(cesta.get("preco", 0)), step=1.0, format="%.2f")
        with col_p2:
            ordem_banco = cesta.get("ordem")
            ordem_atual = int(ordem_banco) if ordem_banco is not None and int(ordem_banco) >= 1 else 1
            nova_ordem = st.number_input("Ordem / Posição", min_value=1, value=ordem_atual, step=1)

        descricao = st.text_area("Descrição", value=cesta.get("descricao", "") or "", height=95, placeholder="Descreva os itens principais...")
        ativa = st.checkbox("Cesta ativa", value=cesta.get("ativa", True))

    # Coluna 2: Gestão de Imagem
    with col_imagem:
        st.subheader("📷 Imagem da Cesta")
        imagem_atual = cesta.get("imagem", "")

        col_img1, col_img2 = st.columns(2)

        # Bloco da Imagem Atual + Botão de Excluir
        with col_img1:
            if imagem_atual:
                st.caption("Imagem Atual")
                st.image(imagem_atual, width=130)
                
                if st.button("🗑️ Remover Foto", key="rm_foto_editar", use_container_width=True):
                    try:
                        remover_imagem_cesta(cesta_id)
                        st.rerun()
                    except Exception as erro:
                        st.error(f"Erro ao remover: {erro}")
            else:
                st.info("Nenhuma imagem.")

        # Bloco de Nova Imagem
        nova_imagem = st.file_uploader("Trocar imagem", type=["png", "jpg", "jpeg", "webp"])

        if nova_imagem:
            with col_img2:
                st.caption("Nova Imagem")
                st.image(nova_imagem, width=130)

    st.write("")

    # Botões de Ação
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        salvar = st.button("💾 Salvar Alterações", use_container_width=True, type="primary")

    with col_b2:
        cancelar = st.button("❌ Cancelar", use_container_width=True)


# =====================================================
# CANCELAR
# =====================================================

if cancelar:
    st.session_state.pop("cesta_editar", None)
    st.switch_page("pages/04_Cestas.py")


# =====================================================
# SALVAR (COM DRIBLE DE CACHE INFALÍVEL)
# =====================================================

if salvar:
    if not nome.strip():
        st.error("Informe o nome da cesta.")
        st.stop()

    imagem = imagem_atual

    if nova_imagem:
        try:
            imagem = upload_imagem_cesta(nova_imagem)
        except Exception as erro:
            st.error(f"Erro no upload: {erro}")
            st.stop()

    try:
        # TENTA A FUNÇÃO NOVA
        atualizar_cesta(
            cesta_id=cesta_id,
            nome=nome.strip(),
            descricao=descricao.strip(),
            preco=preco,
            imagem=imagem,
            ativa=ativa,
            ordem=int(nova_ordem)
        )
        st.success("Cesta atualizada e reordenada com sucesso!")
        st.session_state.pop("cesta_editar", None)
        st.switch_page("pages/04_Cestas.py")

    except TypeError as erro_tipo:
        # SE O CACHE ESTIVER TRAVADO COM A FUNÇÃO VELHA, NÓS DRIBLAMOS ELE AQUI!
        if "ordem" in str(erro_tipo):
            try:
                # 1. Salva os dados básicos com a função antiga que está na memória
                atualizar_cesta(
                    cesta_id=cesta_id,
                    nome=nome.strip(),
                    descricao=descricao.strip(),
                    preco=preco,
                    imagem=imagem,
                    ativa=ativa
                )
                
                # 2. Faz a reordenação em cascata das outras cestas direto no banco de dados
                cestas_existentes = listar_cestas()
                for c in cestas_existentes:
                    if c["id"] != cesta_id and c.get("ordem", 0) >= int(nova_ordem):
                        nova_ordem_cascata = c.get("ordem", 0) + 1
                        supabase.table("cestas").update({"ordem": nova_ordem_cascata}).eq("id", c["id"]).execute()
                
                # 3. Salva a nova ordem da cesta que estamos editando direto no banco de dados
                supabase.table("cestas").update({"ordem": int(nova_ordem)}).eq("id", cesta_id).execute()

                st.success("Cesta atualizada e reordenada com sucesso! (Drible de cache ativado)")
                st.session_state.pop("cesta_editar", None)
                st.switch_page("pages/04_Cestas.py")

            except Exception as erro_drible:
                st.error(f"Erro durante o drible de cache: {erro_drible}")
        else:
            st.error(f"Erro ao atualizar cesta: {erro_tipo}")
            
    except Exception as erro:
        st.error(f"Erro ao atualizar cesta: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("🎁 Edição de Cestas - Doce Cesta Brasília")
