import streamlit as st

from config.supabase import supabase  # <-- IMPORTAÇÃO PARA APAGAR O ARQUIVO FÍSICO

from services.produto_service import (
    listar_categorias,
    buscar_produto,
    atualizar_produto,
    upload_imagem_produto,
    remover_imagem_produto
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
    page_title="Editar Produto",
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
    max-width: 1000px;
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
    padding: 14px 16px !important;
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
# VALIDA PRODUTO
# =====================================================

if "produto_editar" not in st.session_state:
    st.error("Nenhum produto selecionado.")
    if st.button("⬅ Voltar"):
        st.switch_page("pages/05_Produtos.py")
    st.stop()

produto_id = st.session_state["produto_editar"]


# =====================================================
# BUSCAR DADOS
# =====================================================

try:
    produto = buscar_produto(produto_id)
    categorias = listar_categorias()
except Exception as erro:
    st.error(f"Erro ao carregar produto: {erro}")
    st.stop()

if not produto:
    st.error("Produto não encontrado.")
    st.stop()


# =====================================================
# TÍTULO
# =====================================================

st.title("✏️ Editar Produto")
st.caption("Atualize as informações do produto.")
st.divider()


# =====================================================
# IDENTIFICA CATEGORIA ATUAL
# =====================================================

indice_categoria = 0

for i, categoria_item in enumerate(categorias):
    if categoria_item["id"] == produto["categoria_id"]:
        indice_categoria = i
        break


# =====================================================
# FORMULÁRIO DE EDIÇÃO (CARD COMPACTO SIDE-BY-SIDE)
# =====================================================

with st.container(border=True):
    col1, col2 = st.columns([1.3, 1])

    with col1:
        categoria = st.selectbox(
            "Categoria",
            categorias,
            index=indice_categoria,
            format_func=lambda c: c["nome"]
        )

        nome = st.text_input(
            "Nome do Produto",
            value=produto.get("nome", "")
        )

        descricao = st.text_area(
            "Descrição",
            value=produto.get("descricao", "") or "",
            height=90
        )
        
        ativo = st.checkbox(
            "Produto ativo",
            value=produto.get("ativo", True)
        )

    with col2:
        # Regra de preço
        categoria_nome = categoria["nome"].strip().lower()

        if categoria_nome == "adicionais":
            tipo_atual = produto.get("tipo_preco", "Preço definido")

            tipo_preco = st.radio(
                "Tipo de preço",
                ["Preço definido", "Preço sob consulta"],
                index=(1 if tipo_atual == "Preço sob consulta" else 0),
                horizontal=True
            )

            if tipo_preco == "Preço sob consulta":
                preco = None
                st.info("Produto sem valor definido. O preço será informado no pedido.")
            else:
                preco = st.number_input(
                    "Preço (R$)",
                    min_value=0.0,
                    value=float(produto.get("preco", 0) or 0),
                    step=0.50,
                    format="%.2f"
                )
        else:
            tipo_preco = "Incluso na cesta"
            preco = None
            st.info("Produto incluso na composição da cesta. Não possui preço individual.")

        # =========================================
        # GESTÃO DE IMAGEM (APENAS PARA ADICIONAIS)
        # =========================================
        nova_imagem = None
        imagem_atual = produto.get("imagem", "")

        if "adicional" in categoria_nome or "adicionais" in categoria_nome:
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            st.write("**📷 Foto do Produto**")
            
            col_img1, col_img2 = st.columns(2)
            
            with col_img1:
                if imagem_atual:
                    st.image(imagem_atual, width=80)
                    if st.button("❌ Remover", key="rm_foto_prod", use_container_width=True):
                        try:
                            # 1. TENTA APAGAR O ARQUIVO FÍSICO DO SUPABASE BUCKET
                            if "/public/" in str(imagem_atual):
                                try:
                                    # Extrai o caminho depois de '/public/' (Ex: produtos/arquivo.jpg)
                                    caminho_pos_public = str(imagem_atual).split("/public/")[1]
                                    partes = caminho_pos_public.split("/")
                                    
                                    nome_bucket = partes[0] # Ex: 'produtos' ou 'adicionais'
                                    caminho_arquivo = "/".join(partes[1:]) # Ex: 'uuid_da_foto.jpg'
                                    
                                    # Comando que realmente deleta o arquivo físico do storage
                                    supabase.storage.from_(nome_bucket).remove([caminho_arquivo])
                                except Exception as erro_storage:
                                    print(f"Aviso: O arquivo físico já não existia ou houve erro: {erro_storage}")

                            # 2. REMOVE A REFERÊNCIA NO BANCO DE DADOS
                            remover_imagem_produto(produto_id)
                            st.rerun()
                        except Exception as erro:
                            st.error(f"Erro ao remover: {erro}")
                else:
                    st.caption("Sem foto atual")
            
            nova_imagem = st.file_uploader("Nova foto", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
            if nova_imagem:
                with col_img2:
                    st.image(nova_imagem, width=80)

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
    st.session_state.pop("produto_editar", None)
    st.switch_page("pages/05_Produtos.py")


# =====================================================
# SALVAR ALTERAÇÕES
# =====================================================

if salvar:
    if not nome.strip():
        st.error("Informe o nome do produto.")
        st.stop()

    # Validação de Preço
    if (
        "adicional" in categoria_nome or "adicionais" in categoria_nome
    ):
        if tipo_preco == "Preço definido" and (preco is None or preco <= 0):
            st.error("Informe o valor do adicional.")
            st.stop()
            
    # Tratamento da Imagem
    imagem_final = imagem_atual
    
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
            
            # Faz o upload da nova imagem
            imagem_final = upload_imagem_produto(nova_imagem)
        except Exception as erro:
            st.error(f"Erro no upload da imagem: {erro}")
            st.stop()

    try:
        atualizar_produto(
            produto_id,
            categoria["id"],
            nome.strip(),
            descricao.strip(),
            preco,
            ativo,
            tipo_preco,
            imagem_final  
        )

        st.success("Produto atualizado com sucesso!")
        st.session_state.pop("produto_editar", None)
        st.switch_page("pages/05_Produtos.py")

    except Exception as erro:
        st.error(f"Erro ao atualizar produto: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("✏️ Edição de produtos - Doce Cesta Brasília")
