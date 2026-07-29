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
from config.supabase import supabase


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

@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
    
    div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        margin-top: 15px !important;
        justify-content: space-between;
    }

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
    st.title("🎁 Gestão de Cestas e Vitrine")
    st.caption("Cadastre e gerencie as opções de presentes e suas ordens de exibição no site.")


# =====================================================
# CARREGA E ORGANIZA CESTAS (DIRETO DA COLUNA 'ordem')
# =====================================================

try:
    resposta = supabase.table("cestas").select("*").order("ordem", desc=False).execute()
    cestas = resposta.data or []
    
    for i, c in enumerate(cestas):
        nova_pos = i + 1
        if c.get("ordem") != nova_pos:
            supabase.table("cestas").update({"ordem": nova_pos}).eq("id", c["id"]).execute()
            c["ordem"] = nova_pos
            
except Exception as erro:
    st.error(f"Erro ao carregar cestas do banco: {erro}")
    cestas = []

total_cestas = len(cestas)
proxima_ordem = total_cestas + 1


# =====================================================
# BUSCA DE SEÇÕES OFICIAIS EXCLUSIVAS (TABELA vitrine_secoes)
# =====================================================
try:
    res_secoes = supabase.table("vitrine_secoes").select("nome").order("ordem").execute()
    lista_secoes = [s["nome"] for s in (res_secoes.data or [])]
    if not lista_secoes:
        lista_secoes = ["Cestas de Café"]
except:
    lista_secoes = ["Cestas de Café"]


# =====================================================
# NOVA CESTA (EXPANDER)
# =====================================================

salvar = False

if usuario.get("perfil") == "Administrador":
    with st.expander("✨ Cadastrar Nova Opção (Cesta/Tábua)", expanded=False):
        col_f1, col_f2 = st.columns([1.5, 1])

        with col_f1:
            nome = st.text_input("Nome da Opção", placeholder="Ex: Tábua de Frios Premium")
            
            # DROPDOWN PUXANDO APENAS AS SEÇÕES OFICIAIS CADASTRADAS NO MÓDULO EXCLUSIVO
            secao_selecionada = st.selectbox(
                "Seção na Vitrine", 
                lista_secoes,
                help="Selecione a seção correspondente. Para criar ou gerenciar seções, utilize o menu 'Seções da Vitrine'."
            )
            
            descricao = st.text_area("Descrição", height=105, placeholder="Descreva os itens principais que acompanham...")

        with col_f2:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                preco = st.number_input("Preço (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
            with col_p2:
                ordem_escolhida = st.number_input(
                    "Ordem Geral", 
                    min_value=1, 
                    max_value=proxima_ordem, 
                    value=proxima_ordem, 
                    step=1,
                    help=f"A posição sequencial deve ser de 1 a {proxima_ordem}."
                )
            
            imagem_arquivo = st.file_uploader("📷 Foto Principal", type=["jpg", "jpeg", "png", "webp"])

            if imagem_arquivo:
                st.image(imagem_arquivo, width=90, caption="Pré-visualização")

        st.write("")
        salvar = st.button("💾 Cadastrar no Catálogo", use_container_width=True, type="primary")

else:
    st.info("Modo consulta ativo. Apenas Administradores podem cadastrar novos itens.")


# =====================================================
# SALVAR CESTA E REALINHAR SEQUÊNCIA NO SUPABASE
# =====================================================

if salvar:
    if not nome.strip():
        st.error("Informe o nome do produto.")
    elif not secao_selecionada:
        st.error("Selecione a seção para a vitrine.")
    else:
        try:
            with st.spinner("Registrando produto e ajustando posições no banco..."):
                imagem_url = None
                if imagem_arquivo:
                    imagem_url = upload_imagem_cesta(imagem_arquivo)

                pos_desejada = int(ordem_escolhida)

                for c in cestas:
                    if c["ordem"] >= pos_desejada:
                        supabase.table("cestas").update({"ordem": c["ordem"] + 1}).eq("id", c["id"]).execute()

                cadastrar_cesta(
                    nome=nome.strip(), 
                    descricao=descricao.strip(), 
                    preco=preco, 
                    imagem=imagem_url, 
                    ordem=pos_desejada
                )
                
                # Associa diretamente com a seção selecionada
                supabase.table("cestas").update({"secao_vitrine": secao_selecionada}).eq("nome", nome.strip()).execute()

            st.success(f"✅ Opção cadastrada na seção '{secao_selecionada}' com sucesso!")
            st.rerun()

        except Exception as erro:
            st.error(f"Erro ao cadastrar: {erro}")


# =====================================================
# LISTAGEM DE CESTAS (CARDS PREMIUM)
# =====================================================

st.write("")
st.subheader(f"📋 Catálogo Oficial ({total_cestas})")

if not cestas:
    st.info("Nenhum item cadastrado. Utilize o botão acima para começar.")
else:
    for cesta in cestas:
        ativa = cesta.get("ativa", True)
        posicao_display = cesta.get("ordem", 1)
        secao_badge = cesta.get("secao_vitrine", "Cestas Tradicionais")

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([4.2, 2.0, 1.3, 2.5])

            with col1:
                imagem_url = cesta.get("imagem")
                if imagem_url:
                    img_col, txt_col = st.columns([1.2, 4])
                    with img_col:
                        st.image(imagem_url, width=65)
                    with txt_col:
                        st.markdown(f'<span class="posicao-badge">Posição #{posicao_display} • {secao_badge}</span>', unsafe_allow_html=True)
                        st.markdown(f'<div class="cesta-nome">{cesta["nome"]}</div>', unsafe_allow_html=True)
                        if cesta.get("descricao"):
                            desc = cesta["descricao"]
                            if len(desc) > 80: desc = desc[:80] + "..."
                            st.caption(desc)
                else:
                    st.markdown(f'<span class="posicao-badge">Posição #{posicao_display} • {secao_badge}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="cesta-nome">{cesta["nome"]}</div>', unsafe_allow_html=True)
                    if cesta.get("descricao"):
                        desc = cesta["descricao"]
                        if len(desc) > 90: desc = desc[:90] + "..."
                        st.caption(desc)

            with col2:
                try:
                    valor = float(cesta.get("preco", 0))
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")
                    st.markdown(f'<div class="cesta-preco">{valor_fmt}</div>', unsafe_allow_html=True)
                except:
                    st.caption("Sob consulta")

            with col3:
                if ativa:
                    st.markdown('<span class="badge-ativa">Ativa</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-inativa">Inativa</span>', unsafe_allow_html=True)

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
                            ordem_removida = cesta["ordem"]
                            excluir_cesta(cesta["id"])
                            
                            cestas_restantes = supabase.table("cestas").select("*").order("ordem", desc=False).execute().data or []
                            for idx_r, rest in enumerate(cestas_restantes):
                                nova_ordem_correta = idx_r + 1
                                if rest.get("ordem") != nova_ordem_correta:
                                    supabase.table("cestas").update({"ordem": nova_ordem_correta}).eq("id", rest["id"]).execute()

                            st.toast("✅ Cesta excluída e posições reorganizadas!")
                            st.rerun()
                        except Exception as erro:
                            st.error(f"Erro: {erro}")


# =====================================================
# RODAPÉ
# =====================================================

st.write("")
st.divider()
st.caption("📦 Gerenciamento Oficial de Cestas - Doce Cesta Brasília")
