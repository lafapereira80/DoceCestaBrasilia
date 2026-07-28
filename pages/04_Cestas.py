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
    page_title="Gestão de Cestas",
    page_icon="🎁",
    layout="wide"
)

configurar_pagina()
menu_lateral()
administrador_operador()

usuario = st.session_state.usuario


# =====================================================
# CSS PREMIUM E ANIMAÇÕES
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
    max-width: 1150px;
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
   ACORDEÃO (EXPANDER) "NOVA CESTA"
========================================== */
div[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05) !important;
    overflow: hidden;
    margin-bottom: 25px;
}
div[data-testid="stExpander"] summary {
    background: #faf7f3;
    padding: 15px 20px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    color: #5a3b28 !important;
    transition: all 0.3s ease;
}
div[data-testid="stExpander"] summary:hover {
    background: #f3ece6;
}
div[data-testid="stExpanderDetails"] {
    padding: 20px !important;
}

/* =========================================
   CARDS DE CESTAS
========================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8ddd3 !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #d2bfae !important;
    box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08);
    transform: translateY(-2px);
}

/* Alinhamento vertical Desktop */
@media (min-width: 641px) {
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
}

/* =========================================
   ELEMENTOS DE TEXTO & BADGES
========================================== */
.cesta-nome {
    font-weight: 800;
    color: #2c1e14;
    font-size: 16px !important;
    margin-bottom: 2px;
}

.cesta-preco {
    font-weight: 800;
    color: #2e7d32;
    font-size: 16px !important;
}

.posicao-badge {
    background: #f3ece6;
    color: #5a3b28;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 800;
    font-size: 11px;
    display: inline-block;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
}

.badge-ativa, .badge-inativa {
    display: inline-block;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-ativa { background-color: #e6f4ea; color: #137333; border: 1px solid #ceead6; }
.badge-inativa { background-color: #fce8e6; color: #c5221f; border: 1px solid #fad2cf; }

/* =========================================
   BOTÕES DE AÇÃO NA TABELA
========================================== */
div[data-testid="stColumn"] div[data-testid="stButton"] button {
    font-size: 15px !important;
    padding: 4px 6px !important;
    border-radius: 10px !important;
    min-height: 38px !important;
    border: 1px solid #e8ddd3 !important;
    background: #faf7f3 !important;
    transition: all 0.2s ease;
}
div[data-testid="stColumn"] div[data-testid="stButton"] button:hover {
    background: #e8ddd3 !important;
    transform: scale(1.05);
}

.stImage img { border-radius: 8px; object-fit: cover; border: 1px solid #e8ddd3; }

/* =========================================
   RESPONSIVIDADE MOBILE E BOTÕES (4 LADO A LADO)
========================================== */
@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
    
    /* Força os botões a ficarem na horizontal no mobile */
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        margin-top: 15px !important;
        justify-content: space-between;
    }

    /* Como são 4 botões nas cestas, cada um assume 25% do espaço */
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {
        width: 25% !important;
        flex: 1 1 0% !important;
        min-width: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) button {
        width: 100% !important;
        padding: 6px 0px !important;
    }
}
</style>
""",
unsafe_allow_html=True
)


# =====================================================
# TÍTULO E CABEÇALHO
# =====================================================

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("🎁 Gestão de Cestas")
    st.caption("Cadastre e gerencie os pacotes de cestas e suas ordens de exibição na vitrine.")


# =====================================================
# CARREGA CESTAS ANTES DO CADASTRO
# =====================================================

try:
    cestas = listar_cestas()
    
    # Tratamento para garantir a ordenação via Python
    for cesta in cestas:
        if "ordem" not in cesta or cesta["ordem"] is None:
            cesta["ordem"] = 999 
            
    # Ordena explicitamente a lista baseada na chave "ordem"
    cestas = sorted(cestas, key=lambda c: c["ordem"])
    
except Exception as erro:
    st.error(f"Erro ao carregar cestas: {erro}")
    cestas = []

total_cestas = len(cestas)
proxima_ordem = total_cestas + 1


# =====================================================
# NOVA CESTA (NOVO MODELO COM EXPANDER)
# =====================================================

salvar = False

if usuario.get("perfil") == "Administrador":
    # Expander de Cadastro, começa fechado para manter a interface premium
    with st.expander("✨ Cadastrar Nova Cesta", expanded=False):
        col_f1, col_f2 = st.columns([1.5, 1])

        with col_f1:
            nome = st.text_input("Nome da Cesta", placeholder="Ex: Cesta Café da Manhã Premium")
            descricao = st.text_area("Descrição", height=105, placeholder="Descreva os itens principais que acompanham a cesta...")

        with col_f2:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                preco = st.number_input("Preço de Venda (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
            with col_p2:
                ordem_escolhida = st.number_input("Ordem na Vitrine", min_value=1, value=proxima_ordem, step=1)
            
            imagem_arquivo = st.file_uploader("📷 Foto da Cesta", type=["jpg", "jpeg", "png", "webp"])

            if imagem_arquivo:
                st.image(imagem_arquivo, width=90, caption="Pré-visualização")

        st.write("")
        salvar = st.button("💾 Cadastrar Cesta no Catálogo", use_container_width=True, type="primary")

else:
    st.info("Modo consulta ativo. Apenas Administradores podem cadastrar novas cestas.")


# =====================================================
# SALVAR CESTA
# =====================================================

if salvar:
    if not nome.strip():
        st.error("Informe o nome da cesta.")
    else:
        try:
            with st.spinner("Registrando cesta e ajustando posições..."):
                imagem_url = None
                if imagem_arquivo:
                    imagem_url = upload_imagem_cesta(imagem_arquivo)

                cadastrar_cesta(
                    nome=nome.strip(), 
                    descricao=descricao.strip(), 
                    preco=preco, 
                    imagem=imagem_url, 
                    ordem=int(ordem_escolhida)
                )
            st.success("✅ Cesta cadastrada e reordenada com sucesso!")
            st.rerun()

        except TypeError as erro_tipo:
            if "ordem" in str(erro_tipo):
                st.error("⚠️ Erro de Cache. Apague o __pycache__ e reinicie o app.")
            else:
                st.error(f"Erro ao cadastrar: {erro_tipo}")
        except Exception as erro:
            st.error(f"Erro ao cadastrar cesta: {erro}")


# =====================================================
# LISTAGEM DE CESTAS (CARDS PREMIUM)
# =====================================================

st.write("")
st.subheader(f"📋 Catálogo de Cestas ({total_cestas})")

if not cestas:
    st.info("Nenhuma cesta cadastrada. Utilize o botão acima para começar.")
else:
    for cesta in cestas:
        ativa = cesta.get("ativa", True)
        posicao_atual_num = cesta.get("ordem", 999)
        posicao_display = str(posicao_atual_num) if posicao_atual_num != 999 else "-"

        with st.container(border=True):
            # Layout de colunas sutilmente reajustado para caberem 4 botões na direita
            col1, col2, col3, col4 = st.columns([4.2, 2.0, 1.3, 2.5])

            # Coluna 1: Imagem, Posição, Nome e Descrição
            with col1:
                imagem_url = cesta.get("imagem")
                if imagem_url:
                    img_col, txt_col = st.columns([1.2, 4])
                    with img_col:
                        st.image(imagem_url, width=65)
                    with txt_col:
                        st.markdown(f'<span class="posicao-badge">Posição #{posicao_display}</span>', unsafe_allow_html=True)
                        st.markdown(f'<div class="cesta-nome">{cesta["nome"]}</div>', unsafe_allow_html=True)
                        if cesta.get("descricao"):
                            desc = cesta["descricao"]
                            if len(desc) > 80: desc = desc[:80] + "..."
                            st.caption(desc)
                else:
                    st.markdown(f'<span class="posicao-badge">Posição #{posicao_display}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="cesta-nome">{cesta["nome"]}</div>', unsafe_allow_html=True)
                    if cesta.get("descricao"):
                        desc = cesta["descricao"]
                        if len(desc) > 90: desc = desc[:90] + "..."
                        st.caption(desc)

            # Coluna 2: Preço
            with col2:
                try:
                    valor = float(cesta.get("preco", 0))
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f'<div class="cesta-preco">{valor_fmt}</div>', unsafe_allow_html=True)
                except:
                    st.caption("Sob consulta")

            # Coluna 3: Status
            with col3:
                if ativa:
                    st.markdown('<span class="badge-ativa">Ativa</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-inativa">Inativa</span>', unsafe_allow_html=True)

            # Coluna 4: Ações (4 botões em linha)
            with col4:
                b1, b2, b3, b4 = st.columns(4)

                with b1:
                    if st.button("✏️", key=f"editar_{cesta['id']}", help="Editar Informações", use_container_width=True):
                        st.session_state["cesta_editar"] = cesta["id"]
                        st.switch_page("pages/11_Editar_Cesta.py")

                with b2:
                    if st.button("📦", key=f"produtos_{cesta['id']}", help="Gerenciar Itens da Cesta", use_container_width=True):
                        st.session_state["cesta_produtos"] = cesta["id"]
                        st.switch_page("pages/12_Produtos_da_Cesta.py")

                with b3:
                    if st.button("⚙️", key=f"config_{cesta['id']}", help="Configurações Avançadas", use_container_width=True):
                        st.session_state["cesta_configurar"] = cesta["id"]
                        st.switch_page("pages/14_Configurar_Cesta.py")

                with b4:
                    if st.button("🗑️", key=f"excluir_{cesta['id']}", help="Excluir Cesta", use_container_width=True):
                        try:
                            excluir_cesta(cesta["id"])
                            st.toast("✅ Cesta excluída com sucesso!")
                            st.rerun()
                        except Exception as erro:
                            st.error(f"Erro: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.write("")
st.divider()
st.caption("📦 Gerenciamento Oficial de Cestas - Doce Cesta Brasília")
