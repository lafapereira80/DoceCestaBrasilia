import streamlit as st

from services.cesta_service import (
    listar_cestas,
    cadastrar_cesta,
    excluir_cesta,
    upload_imagem_cesta
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
    page_title="Cestas",
    page_icon="🎁",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CSS COMPACTO E ESTILIZADO
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

p, div, span, label {
    font-family: Arial, sans-serif !important;
    font-size: 13px !important;
}

/* =========================================
   CONTAINERS DAS CESTAS (CARDS LINHA)
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #dfcdbb !important;
    box-shadow: 0 2px 6px rgba(90, 59, 40, 0.08);
}

/* =========================================
   ELEMENTOS DE TEXTO & BADGES
========================================== */
.cesta-nome {
    font-weight: 700;
    color: #333;
    font-size: 15px !important;
}

.cesta-preco {
    font-weight: 700;
    color: #2e7d32;
    font-size: 14px !important;
}

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

.cabecalho-tabela {
    font-weight: 700;
    color: #775a46;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

/* Ajustes de botões */
.stButton button {
    font-size: 13px !important;
    padding: 2px 6px !important;
    border-radius: 8px !important;
    min-height: 32px !important;
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
# TÍTULO E CABEÇALHO
# =====================================================

st.title("🎁 Gestão de Cestas")
st.caption("Cadastre e gerencie os modelos de cestas disponíveis.")
st.divider()


# =====================================================
# NOVA CESTA (EXPANSIBLE FORM)
# =====================================================

if usuario.get("perfil") == "Administrador":
    with st.expander("➕ **Cadastrar Nova Cesta**", expanded=False):
        with st.form("nova_cesta"):
            col_f1, col_f2 = st.columns([2, 1])

            with col_f1:
                nome = st.text_input("Nome da Cesta")
                descricao = st.text_area("Descrição", height=70)

            with col_f2:
                preco = st.number_input("Preço (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
                imagem_arquivo = st.file_uploader("📷 Foto da Cesta", type=["jpg", "jpeg", "png", "webp"])

                if imagem_arquivo:
                    st.image(imagem_arquivo, width=120)

            salvar = st.form_submit_button("💾 Cadastrar Cesta", use_container_width=True, type="primary")

        if salvar:
            if not nome.strip():
                st.error("Informe o nome da cesta.")
            else:
                try:
                    imagem_url = None
                    if imagem_arquivo:
                        imagem_url = upload_imagem_cesta(imagem_arquivo)

                    cadastrar_cesta(nome.strip(), descricao.strip(), preco, imagem_url)
                    st.success("Cesta cadastrada com sucesso!")
                    st.rerun()

                except Exception as erro:
                    st.error(f"Erro ao cadastrar cesta: {erro}")
else:
    st.info("Modo consulta. Apenas Administradores podem cadastrar novas cestas.")


# =====================================================
# CARREGA CESTAS
# =====================================================

try:
    cestas = listar_cestas()
except Exception as erro:
    st.error(f"Erro ao carregar cestas: {erro}")
    st.stop()


# =====================================================
# LISTAGEM
# =====================================================

st.subheader("📋 Cestas Cadastradas")

if not cestas:
    st.info("Nenhuma cesta cadastrada.")
else:
    # Cabeçalho
    col_h1, col_h2, col_h3, col_h4 = st.columns([5.0, 1.8, 1.4, 1.8])
    with col_h1:
        st.markdown('<div class="cabecalho-tabela">Cesta</div>', unsafe_allow_html=True)
    with col_h2:
        st.markdown('<div class="cabecalho-tabela">Preço</div>', unsafe_allow_html=True)
    with col_h3:
        st.markdown('<div class="cabecalho-tabela">Status</div>', unsafe_allow_html=True)
    with col_h4:
        st.markdown('<div class="cabecalho-tabela">Ações</div>', unsafe_allow_html=True)

    # Cards da Lista
    for cesta in cestas:
        ativa = cesta.get("ativa", True)

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([5.0, 1.8, 1.4, 1.8])

            # Coluna 1: Imagem + Nome + Descrição
            with col1:
                img_col, txt_col = st.columns([1, 5]) if cesta.get("imagem") else (None, col1)

                if cesta.get("imagem"):
                    with img_col:
                        st.image(cesta["imagem"], width=60)
                    with txt_col:
                        st.markdown(f'<div class="cesta-nome">{cesta["nome"]}</div>', unsafe_allow_html=True)
                        if cesta.get("descricao"):
                            desc = cesta["descricao"]
                            if len(desc) > 85:
                                desc = desc[:85] + "..."
                            st.caption(desc)
                else:
                    st.markdown(f'<div class="cesta-nome">{cesta["nome"]}</div>', unsafe_allow_html=True)
                    if cesta.get("descricao"):
                        desc = cesta["descricao"]
                        if len(desc) > 85:
                            desc = desc[:85] + "..."
                        st.caption(desc)

            # Coluna 2: Preço
            with col2:
                try:
                    valor = float(cesta.get("preco", 0))
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f'<div class="cesta-preco">{valor_fmt}</div>', unsafe_allow_html=True)
                except:
                    st.caption("Sem preço")

            # Coluna 3: Status
            with col3:
                if ativa:
                    st.markdown('<span class="badge-ativa">✓ Ativa</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-inativa">✕ Inativa</span>', unsafe_allow_html=True)

            # Coluna 4: Botões de Ação
            with col4:
                b1, b2, b3, b4 = st.columns(4)

                with b1:
                    if st.button("✏️", key=f"editar_{cesta['id']}", help="Editar Cesta", use_container_width=True):
                        st.session_state["cesta_editar"] = cesta["id"]
                        st.switch_page("pages/11_Editar_Cesta.py")

                with b2:
                    if st.button("📦", key=f"produtos_{cesta['id']}", help="Produtos da Cesta", use_container_width=True):
                        st.session_state["cesta_produtos"] = cesta["id"]
                        st.switch_page("pages/12_Produtos_da_Cesta.py")

                with b3:
                    if st.button("⚙️", key=f"config_{cesta['id']}", help="Configurar Cesta", use_container_width=True):
                        st.session_state["cesta_configurar"] = cesta["id"]
                        st.switch_page("pages/14_Configurar_Cesta.py")

                with b4:
                    if st.button("🗑️", key=f"excluir_{cesta['id']}", help="Excluir Cesta", use_container_width=True):
                        try:
                            excluir_cesta(cesta["id"])
                            st.success("Cesta excluída.")
                            st.rerun()
                        except Exception as erro:
                            st.error(f"Erro: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.divider()
st.caption("Doce Cesta Brasília - Cadastro de Cestas")
