import streamlit as st

from services.usuario_service import (
    listar_usuarios,
    salvar_usuario,
    excluir_usuario,
    atualizar_usuario
)

from utils.menu import (
    configurar_pagina,
    menu_lateral
)

from utils.permissao import (
    administrador
)


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Usuários",
    page_icon="👤",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador()

usuario_logado = st.session_state.usuario


# =====================================================
# CSS ISOLADO E ULTRA COMPACTO
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

h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-bottom: 2px !important;
}

h2, h3 {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #5a3b28;
    margin-top: 10px !important;
    margin-bottom: 8px !important;
}

.block-container p, 
.block-container label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CARDS DE USUÁRIOS (LINHAS COMPACTAS)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
}

/* =========================================
   ELEMENTOS VISUAIS & BADGES
========================================== */
.user-title {
    font-weight: 700;
    color: #333;
    font-size: 14px !important;
}

.badge-admin {
    display: inline-block;
    background-color: #fef7e0;
    color: #b06000;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

.badge-operador {
    display: inline-block;
    background-color: #e8f0fe;
    color: #1a73e8;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

.badge-self {
    display: inline-block;
    background-color: #e6f4ea;
    color: #137333;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px !important;
}

/* Ajustes direcionados para botões */
div[data-testid="stColumn"] > div > div > div > div[data-testid="stButton"] > button {
    font-size: 13px !important;
    padding: 2px 8px !important;
    border-radius: 8px !important;
    min-height: 32px !important;
}

div[data-testid="stExpander"] {
    border: none !important;
    box-shadow: none !important;
    margin-top: 4px !important;
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

st.title("👤 Usuários do Sistema")
st.caption("Gerencie os acessos administrativos da Doce Cesta Brasília.")
st.divider()


# =====================================================
# NOVO USUÁRIO
# =====================================================

st.subheader("➕ Novo Usuário")

with st.container(border=True):
    col1, col2, col3 = st.columns([1.5, 1.5, 1])

    with col1:
        novo_login = st.text_input("Login", key="novo_login", placeholder="Ex: joao.silva")

    with col2:
        nova_senha = st.text_input("Senha", type="password", key="nova_senha", placeholder="••••••••")

    with col3:
        novo_perfil = st.selectbox("Perfil", ["Administrador", "Operador"], key="novo_perfil")

    if st.button("💾 Salvar Usuário", use_container_width=True, type="primary"):
        if not novo_login:
            st.error("Informe o login.")
            st.stop()

        if not nova_senha:
            st.error("Informe a senha.")
            st.stop()

        sucesso, mensagem = salvar_usuario(
            novo_login,
            nova_senha,
            novo_perfil
        )

        if sucesso:
            st.success("Usuário cadastrado com sucesso!")
            st.rerun()
        else:
            st.error(mensagem)


st.divider()


# =====================================================
# LISTAGEM
# =====================================================

st.subheader("📋 Usuários Cadastrados")

try:
    usuarios = listar_usuarios()
except Exception as erro:
    st.error(f"Erro ao carregar usuários: {erro}")
    st.stop()

if not usuarios:
    st.info("Nenhum usuário cadastrado.")
    st.stop()


# =====================================================
# LISTAGEM DE USUÁRIOS
# =====================================================

for usuario in usuarios:
    with st.container(border=True):
        col_u1, col_u2, col_u3, col_u4 = st.columns([3, 2, 2, 2])

        # Login e identificação do usuário atual
        with col_u1:
            st.markdown(f'<div class="user-title">👤 {usuario["login"]}</div>', unsafe_allow_html=True)

        # Perfil (Badge Visual)
        with col_u2:
            if usuario["perfil"] == "Administrador":
                st.markdown('<span class="badge-admin">👑 Administrador</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-operador">👤 Operador</span>', unsafe_allow_html=True)

        # Data de Criação
        with col_u3:
            data_criacao = str(usuario.get("created_at", "-"))[:10]
            st.caption(f"🗓️ Criado: {data_criacao}")

        # Indicador de Conta Conectada
        with col_u4:
            if usuario["login"] == usuario_logado["login"]:
                st.markdown('<span class="badge-self">🔒 Conta Atual</span>', unsafe_allow_html=True)
            else:
                st.caption("⚙️ Gerenciável")

        # =================================================
        # EDITAR / EXCLUIR EXPANSIBLE
        # =================================================
        with st.expander("✏️ Editar ou Excluir", expanded=False):
            col_ed1, col_ed2 = st.columns(2)

            with col_ed1:
                editar_login = st.text_input("Login", value=usuario["login"], key=f"login_{usuario['id']}")
                editar_senha = st.text_input("Nova senha (deixe vazio para manter)", type="password", key=f"senha_{usuario['id']}")

            with col_ed2:
                editar_perfil = st.selectbox(
                    "Perfil",
                    ["Administrador", "Operador"],
                    index=0 if usuario["perfil"] == "Administrador" else 1,
                    key=f"perfil_{usuario['id']}"
                )

                if st.button("💾 Atualizar Dados", key=f"update_{usuario['id']}", use_container_width=True, type="primary"):
                    sucesso, mensagem = atualizar_usuario(
                        usuario["id"],
                        editar_login,
                        editar_senha,
                        editar_perfil
                    )

                    if sucesso:
                        st.success("Usuário atualizado!")
                        st.rerun()
                    else:
                        st.error(mensagem)

            st.divider()

            # Área de Exclusão
            if usuario["login"] != usuario_logado["login"]:
                col_del1, col_del2 = st.columns([2, 1])
                with col_del1:
                    confirmar = st.checkbox("Confirmar exclusão deste usuário", key=f"confirm_{usuario['id']}")

                with col_del2:
                    if confirmar:
                        if st.button("🗑️ Excluir definitivamente", key=f"delete_{usuario['id']}", use_container_width=True):
                            sucesso, mensagem = excluir_usuario(usuario["id"])
                            if sucesso:
                                st.success("Usuário excluído com sucesso!")
                                st.rerun()
                            else:
                                st.error(mensagem)
            else:
                st.info("🔒 O usuário atualmente conectado não pode ser excluído.")


st.divider()


# =====================================================
# VOLTAR
# =====================================================

if st.button("⬅ Voltar ao Início", use_container_width=True):
    st.switch_page("pages/99_Admin.py")
