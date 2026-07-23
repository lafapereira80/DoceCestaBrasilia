import streamlit as st

from services.categoria_service import (
    listar_categorias,
    cadastrar_categoria,
    atualizar_categoria,
    alterar_status_categoria,
    excluir_categoria
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
    page_title="Categorias",
    page_icon="📂",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()


# =====================================================
# CONTROLE DE EDIÇÃO
# =====================================================

if "categoria_editando" not in st.session_state:
    st.session_state["categoria_editando"] = None


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
    max-width: 1100px;
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
    margin-top: 4px !important;
    margin-bottom: 6px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINERS DAS CATEGORIAS (CARDS LINHA)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    transition: all 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
}

.categoria-nome {
    font-weight: 700;
    color: #333;
    font-size: 15px !important;
}

/* Badges e Tags */
.badge-ativa {
    display: inline-block;
    background-color: #e6f4ea;
    color: #137333;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

.badge-inativa {
    display: inline-block;
    background-color: #fce8e6;
    color: #c5221f;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

.badge-info {
    display: inline-block;
    background-color: #f3ece6;
    color: #5a3b28;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 11px !important;
    border: 1px solid #dfcdbb;
}

/* Botões da Tabela */
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
# TÍTULO E CABEÇALHO
# =====================================================

st.title("📂 Categorias")
st.caption("Gerencie as categorias de produtos da Doce Cesta Brasília")
st.divider()


# =====================================================
# NOVA CATEGORIA
# =====================================================

with st.expander("➕ Nova Categoria", expanded=False):
    col_n1, col_n2 = st.columns([1.5, 1])

    with col_n1:
        nome_categoria = st.text_input("Nome da categoria", placeholder="Ex: Bebidas Quentes")

    with col_n2:
        ordem = st.number_input("Ordem de exibição", min_value=0, value=0, step=1)

    c1, c2, c3 = st.columns(3)
    with c1:
        possui_preco = st.checkbox("Possui preço individual")
    with c2:
        exibir_no_pedido = st.checkbox("Exibir no formulário de pedido")
    with c3:
        ativo = st.checkbox("Categoria ativa", value=True)

    if st.button("💾 Salvar Categoria", use_container_width=True, type="primary"):
        if not nome_categoria.strip():
            st.error("Informe o nome da categoria.")
        else:
            try:
                cadastrar_categoria(
                    nome_categoria.strip(),
                    possui_preco,
                    exibir_no_pedido,
                    ativo,
                    ordem
                )
                st.success("Categoria cadastrada com sucesso!")
                st.rerun()
            except Exception as erro:
                st.error(f"Erro ao cadastrar: {erro}")


st.divider()


# =====================================================
# LISTAGEM DE CATEGORIAS
# =====================================================

st.subheader("📋 Categorias Cadastradas")

try:
    categorias = listar_categorias()
except Exception as erro:
    st.error(f"Erro ao carregar categorias: {erro}")
    st.stop()

if not categorias:
    st.info("Nenhuma categoria cadastrada.")
    st.stop()


# Loop das Categorias
for categoria in categorias:
    categoria_id = categoria["id"]
    nome = categoria.get("nome", "")
    ativo = categoria.get("ativo", False)
    possui_preco = categoria.get("possui_preco", False)
    exibir_pedido = categoria.get("exibir_no_pedido", False)
    ordem_atual = categoria.get("ordem", 0)

    with st.container(border=True):
        col1, col2, col3 = st.columns([4, 3, 2])

        # Coluna 1: Nome e Status
        with col1:
            st.markdown(f'<div class="categoria-nome">{nome}</div>', unsafe_allow_html=True)
            if ativo:
                st.markdown('<span class="badge-ativa">🟢 Ativa</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-inativa">🔴 Inativa</span>', unsafe_allow_html=True)

        # Coluna 2: Detalhes em Badges
        with col2:
            st.markdown(
                f"""
                <span class="badge-info">🏷️ Preço: {'Sim' if possui_preco else 'Não'}</span>
                <span class="badge-info">📋 Pedido: {'Sim' if exibir_pedido else 'Não'}</span>
                <span class="badge-info">🔢 Ordem: {ordem_atual}</span>
                """,
                unsafe_allow_html=True
            )

        # Coluna 3: Botões de Ação
        with col3:
            col_b1, col_b2, col_b3 = st.columns(3)

            with col_b1:
                texto_botao = "🔴" if ativo else "🟢"
                if st.button(texto_botao, key=f"status_{categoria_id}", help="Ativar/Desativar", use_container_width=True):
                    try:
                        alterar_status_categoria(categoria_id, not ativo)
                        st.success("Status alterado!")
                        st.rerun()
                    except Exception as erro:
                        st.error(f"Erro ao alterar status: {erro}")

            with col_b2:
                if st.button("✏️", key=f"editar_{categoria_id}", help="Editar Categoria", use_container_width=True):
                    st.session_state["categoria_editando"] = categoria_id
                    st.rerun()

            with col_b3:
                excluir = st.button("🗑️", key=f"excluir_{categoria_id}", help="Excluir Categoria", use_container_width=True)

        # =====================================================
        # FORMULÁRIO DE EDIÇÃO INLINE
        # =====================================================
        if st.session_state["categoria_editando"] == categoria_id:
            st.divider()
            st.markdown("#### ✏️ Editando Categoria")

            with st.form(key=f"form_edicao_{categoria_id}"):
                col_e1, col_e2 = st.columns([1.5, 1])

                with col_e1:
                    novo_nome = st.text_input("Nome da categoria", value=nome)

                with col_e2:
                    nova_ordem = st.number_input("Ordem de exibição", min_value=0, value=int(ordem_atual), step=1, key=f"ordem_edit_{categoria_id}")

                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    novo_preco = st.checkbox("Possui preço", value=possui_preco, key=f"preco_edit_{categoria_id}")
                with col_c2:
                    novo_exibir = st.checkbox("Exibir no pedido", value=exibir_pedido, key=f"pedido_edit_{categoria_id}")
                with col_c3:
                    novo_ativo = st.checkbox("Categoria ativa", value=ativo, key=f"ativo_edit_{categoria_id}")

                col_salvar, col_cancelar = st.columns(2)

                with col_salvar:
                    salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)

                with col_cancelar:
                    cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

                if salvar:
                    if not novo_nome.strip():
                        st.error("Informe o nome da categoria.")
                    else:
                        try:
                            atualizar_categoria(
                                categoria_id,
                                novo_nome.strip(),
                                novo_preco,
                                novo_exibir,
                                novo_ativo,
                                nova_ordem
                            )
                            st.session_state["categoria_editando"] = None
                            st.success("Categoria atualizada!")
                            st.rerun()
                        except Exception as erro:
                            st.error(f"Erro ao atualizar: {erro}")

                if cancelar:
                    st.session_state["categoria_editando"] = None
                    st.rerun()

        # =====================================================
        # CONFIRMAÇÃO DE EXCLUSÃO
        # =====================================================
        if excluir:
            st.warning(f"Deseja realmente excluir a categoria **{nome}**?")
            col_confirmar, col_cancelar = st.columns(2)

            with col_confirmar:
                if st.button("✅ Confirmar exclusão", key=f"confirmar_excluir_{categoria_id}", use_container_width=True):
                    try:
                        resultado = excluir_categoria(categoria_id)
                        if resultado is False:
                            st.error("Não foi possível excluir a categoria.")
                        else:
                            st.success("Categoria excluída com sucesso!")
                            st.session_state["categoria_editando"] = None
                            st.rerun()
                    except Exception as erro:
                        st.error(f"Erro ao excluir: {erro}")

            with col_cancelar:
                if st.button("❌ Cancelar", key=f"cancelar_excluir_{categoria_id}", use_container_width=True):
                    st.rerun()


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("Doce Cesta Brasília - Gestão de Categorias")
