import streamlit as st
import time

from config.supabase import supabase  # Importação direta para driblar o cache e apagar o arquivo

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
# CSS PREMIUM E RESPONSIVIDADE
# =====================================================

st.markdown(
"""
<style>
/* =========================================
   CONFIGURAÇÃO GERAL E ESPAÇAMENTOS
========================================== */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1050px;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}

h1 {
    font-size: 28px !important;
    font-weight: 800 !important;
    color: #4a2e1b;
    margin-bottom: 2px !important;
    letter-spacing: -0.5px;
}

.block-container p, 
.block-container label {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINER CARD DO FORMULÁRIO (FOCUS CARD)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 16px !important;
    padding: 24px 28px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.04);
    transition: all 0.3s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #d2bfae !important;
    box-shadow: 0 8px 25px rgba(90, 59, 40, 0.08);
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
    padding: 12px !important;
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
    font-weight: 800 !important;
    border-radius: 10px !important;
    padding: 6px 16px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stFileUploader"] section button span {
    display: none !important;
}

div[data-testid="stFileUploader"] section button::after {
    content: "📁 Selecionar Nova Foto" !important;
    font-size: 13px !important;
    font-weight: 800 !important;
}

/* =========================================
   ESTILIZAÇÃO DE BOTÕES E IMAGENS
========================================== */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 14px !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    min-height: 40px !important;
    transition: all 0.2s ease;
}
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button:hover {
    transform: scale(1.02);
}

.stImage img {
    border-radius: 10px;
    object-fit: cover;
    border: 1px solid #e8ddd3;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* =========================================
   RESPONSIVIDADE MOBILE E BOTÕES (LADO A LADO)
========================================== */
@media (max-width: 768px) {
    h1 { font-size: 26px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 16px 14px !important; }
    
    /* Força os botões de ação a ficarem na horizontal no mobile */
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
        margin-top: 15px !important;
        justify-content: space-between;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {
        flex: 1 1 0% !important; 
        min-width: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) button {
        width: 100% !important;
        padding: 8px 0px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# VERIFICA CESTA
# =====================================================

if "cesta_editar" not in st.session_state or not st.session_state["cesta_editar"]:
    st.warning("⚠️ Nenhuma cesta selecionada para edição.")
    if st.button("⬅ Voltar para Cestas"):
        st.switch_page("pages/04_Cestas.py")
    st.stop()

cesta_id = st.session_state["cesta_editar"]


# =====================================================
# BUSCA CESTA
# =====================================================

try:
    cesta = buscar_cesta(cesta_id)
    if not cesta:
        st.error("Cesta não encontrada no banco de dados.")
        st.stop()
except Exception as erro:
    st.error(f"Erro ao carregar cesta: {erro}")
    st.stop()


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("✏️ Edição de Cesta")
    st.caption("Atualize as informações, ajuste a ordem de exibição na vitrine e altere a foto principal.")


# =====================================================
# FORMULÁRIO DE EDIÇÃO (FOCUS CARD COMPACTO)
# =====================================================

with st.container(border=True):
    col_dados, col_imagem = st.columns([1.4, 1])

    # Coluna 1: Informações da Cesta
    with col_dados:
        st.markdown("<div style='font-size: 16px; font-weight: 800; color: #5a3b28; margin-bottom: 10px;'>📝 Dados Principais</div>", unsafe_allow_html=True)
        nome = st.text_input("🏷️ Nome da Cesta", value=cesta.get("nome", ""), placeholder="Ex: Cesta Café Especial")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            preco = st.number_input("💰 Preço de Venda (R$)", min_value=0.0, value=float(cesta.get("preco", 0)), step=1.0, format="%.2f")
        with col_p2:
            ordem_banco = cesta.get("ordem")
            ordem_atual = int(ordem_banco) if ordem_banco is not None and int(ordem_banco) >= 1 else 1
            nova_ordem = st.number_input("🔢 Posição na Vitrine", min_value=1, value=ordem_atual, step=1)

        descricao = st.text_area("📋 Descrição Detalhada", value=cesta.get("descricao", "") or "", height=95, placeholder="Descreva os itens principais da cesta...")
        ativa = st.checkbox("🟢 Cesta Ativa e Visível", value=cesta.get("ativa", True))

    # Coluna 2: Gestão de Imagem
    with col_imagem:
        st.markdown("<div style='font-size: 16px; font-weight: 800; color: #5a3b28; margin-bottom: 10px;'>📷 Imagem de Vitrine</div>", unsafe_allow_html=True)
        imagem_atual = cesta.get("imagem", "")

        col_img1, col_img2 = st.columns(2)

        # Bloco da Imagem Atual + Botão de Excluir
        with col_img1:
            if imagem_atual:
                st.image(imagem_atual, width=120)
                if st.button("❌ Remover Foto", key="rm_foto_editar", use_container_width=True):
                    with st.spinner("Removendo foto..."):
                        try:
                            # 1. TENTA APAGAR O ARQUIVO FÍSICO DO SUPABASE BUCKET
                            if "/public/" in str(imagem_atual):
                                try:
                                    caminho_pos_public = str(imagem_atual).split("/public/")[1]
                                    partes = caminho_pos_public.split("/")
                                    
                                    nome_bucket = partes[0]
                                    caminho_arquivo = "/".join(partes[1:])
                                    
                                    supabase.storage.from_(nome_bucket).remove([caminho_arquivo])
                                except Exception as erro_storage:
                                    print(f"Aviso: O arquivo físico já não existia ou houve erro: {erro_storage}")

                            # 2. REMOVE A REFERÊNCIA NO BANCO DE DADOS
                            remover_imagem_cesta(cesta_id)
                            st.toast("✅ Imagem removida com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as erro:
                            st.error(f"Erro ao remover: {erro}")
            else:
                st.caption("Nenhuma imagem cadastrada no momento.")

        # Bloco de Nova Imagem
        nova_imagem = st.file_uploader("Upload de Nova Foto", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

        if nova_imagem:
            with col_img2:
                st.image(nova_imagem, width=120, caption="Nova Imagem")

    st.write("")
    st.divider()

    # Botões de Ação
    col_b1, col_b2, col_b3 = st.columns([1.5, 1.5, 1])

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

    with st.spinner("Atualizando configurações do pacote..."):
        if nova_imagem:
            try:
                # Apaga a imagem velha do bucket caso o usuário esteja apenas enviando uma foto nova por cima
                if imagem_atual and "/public/" in str(imagem_atual):
                    try:
                        caminho_pos_public = str(imagem_atual).split("/public/")[1]
                        partes = caminho_pos_public.split("/")
                        supabase.storage.from_(partes[0]).remove(["/".join(partes[1:])])
                    except:
                        pass
                        
                imagem = upload_imagem_cesta(nova_imagem)
            except Exception as erro:
                st.error(f"Erro no upload da foto: {erro}")
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
            st.success("✅ Cesta atualizada e reordenada com sucesso!")
            st.session_state.pop("cesta_editar", None)
            time.sleep(1)
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

                    st.success("✅ Cesta atualizada e reordenada com sucesso! (Drible de cache ativado)")
                    st.session_state.pop("cesta_editar", None)
                    time.sleep(1)
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

st.write("")
st.caption("🎁 Configurações de Catálogo - Doce Cesta Brasília")
