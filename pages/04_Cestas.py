import streamlit as st
import pandas as pd
from config.supabase import supabase
from services.cesta_service import (
    listar_cestas,
    cadastrar_cesta,
    atualizar_cesta,
    excluir_cesta,
    upload_imagem_cesta,
)
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador
from utils.formatacao import formatar_moeda

st.set_page_config(page_title="Gestão de Cestas", page_icon="🧺", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

if "cesta_confirmar_exclusao" not in st.session_state:
    st.session_state["cesta_confirmar_exclusao"] = None

# =====================================================
# CSS APP NATIVO (CRYSTAL CLEAN)
# =====================================================
st.markdown("""
<style>
.app-header { font-size: clamp(24px, 4vw, 32px); font-weight: 800; color: #0F172A; margin-top: 10px; margin-bottom: 5px; letter-spacing: -1px; }
.app-sub { font-size: 15px; color: #64748B; margin-bottom: 25px; font-weight: 500; }
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 24px !important; padding: 24px !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02) !important; margin-bottom: 24px !important; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stNumberInput>div>div>input { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; background-color: #F8FAFC !important; color: #1E293B !important; }
div[data-testid="stFormSubmitButton"] button, div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 700 !important; }
div[data-testid="stFormSubmitButton"] button[kind="primary"] { background: #10B981 !important; color: white !important; border: none !important; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2) !important; }
div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(16, 185, 129, 0.3) !important; }
.stTabs [data-baseweb="tab"] { font-weight: 700 !important; }

@media (max-width: 1024px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 18px !important; }
}

@media (max-width: 640px) {
    .block-container { padding-left: .8rem !important; padding-right: .8rem !important; }
    .app-sub { font-size: 13px; margin-bottom: 16px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 14px !important; border-radius: 18px !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-header">🧺 Gestão de Cestas e Kits</div><div class="app-sub">Cadastre novos pacotes e organize as abas da sua vitrine pública.</div>', unsafe_allow_html=True)

def carregar_secoes():
    try:
        res = supabase.table("vitrine_secoes").select("nome").eq("ativa", True).order("ordem").execute()
        return [s["nome"] for s in res.data] if res.data else ["Cestas de Café"]
    except:
        return ["Cestas de Café"]

secoes_disponiveis = carregar_secoes()
todas_cestas = listar_cestas()

aba_lista, aba_nova = st.tabs(["📋 Cestas Cadastradas", "➕ Adicionar Nova Cesta"])

with aba_nova:
    with st.container(border=True):
        st.markdown('<div style="font-weight: 700; color: #1E293B; margin-bottom: 15px; font-size: 16px;">✨ Criar Novo Pacote</div>', unsafe_allow_html=True)
        with st.form("form_nova_cesta", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da Cesta/Kit *", placeholder="Ex: Cesta Romântica Luxo")
                secao = st.selectbox("Seção da Vitrine (Aba) *", secoes_disponiveis, help="Em qual aba do site essa cesta vai aparecer?")
                preco = st.number_input("Preço Base (R$)", min_value=0.0, step=10.0, format="%.2f")
                sem_preco = st.checkbox("💬 Preço sob consulta (não definido)", help="Marque se essa cesta ainda não tem preço fechado. A vitrine mostrará 'Sob consulta' em vez de R$ 0,00.")

            with col2:
                total_para_nova = len(todas_cestas) + 1
                ordem = st.number_input(
                    "Ordem de Exibição", min_value=1, max_value=total_para_nova, step=1, value=total_para_nova,
                    help=f"Posição na vitrine (1 a {total_para_nova}). As demais cestas se reajustam automaticamente."
                )
                ativa = st.checkbox("Cesta Ativa (Aparece no site)?", value=True)
                imagem_arquivo = st.file_uploader(
                    "📷 Foto de Referência (aparece na vitrine e no checkout)",
                    type=["jpg", "jpeg", "png", "webp"],
                    help="Essa é a mesma foto exibida no site público (app.py) e na tela de montagem de pedido."
                )
                if imagem_arquivo:
                    st.image(imagem_arquivo, width=120, caption="Pré-visualização")

            descricao = st.text_area("Descrição (Opcional)", placeholder="Itens pré-definidos ou texto de encantamento...")

            st.write("")
            submit = st.form_submit_button("✅ Salvar Cesta no Catálogo", type="primary", use_container_width=True)

            if submit:
                if not nome.strip():
                    st.error("O nome da cesta é obrigatório!")
                else:
                    try:
                        imagem_url = upload_imagem_cesta(imagem_arquivo) if imagem_arquivo else None
                        dados = {
                            "nome": nome.strip(),
                            "descricao": descricao.strip(),
                            "preco": None if sem_preco else preco,
                            "imagem": imagem_url,
                            "secao_vitrine": secao,
                            "ordem": int(ordem),
                            "ativa": ativa,
                        }
                        cadastrar_cesta(dados)
                        st.success(f"Cesta '{nome}' adicionada com sucesso na seção '{secao}'!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

with aba_lista:
    if not todas_cestas:
        st.info("Nenhuma cesta cadastrada ainda. Vá para a aba 'Adicionar Nova Cesta'.")
        st.stop()

    nomes_abas_secao = ["🗂️ Todas"] + secoes_disponiveis
    abas_secao = st.tabs(nomes_abas_secao)

    for idx_aba, aba_secao in enumerate(abas_secao):
        with aba_secao:
            if idx_aba == 0:
                cestas_da_aba = todas_cestas
            else:
                secao_alvo = secoes_disponiveis[idx_aba - 1]
                cestas_da_aba = [c for c in todas_cestas if (c.get("secao_vitrine") or "Cestas de Café") == secao_alvo]

            if not cestas_da_aba:
                st.info("Nenhuma cesta cadastrada nesta seção ainda.")
                continue

            df = pd.DataFrame(cestas_da_aba)
            df_display = df[["ordem", "nome", "secao_vitrine", "preco", "ativa"]].copy()
            df_display["preco"] = df_display["preco"].apply(lambda x: "💬 Sob consulta" if x is None else f"R$ {formatar_moeda(x)}")
            df_display = df_display.rename(columns={"ordem": "Posição", "nome": "Cesta", "secao_vitrine": "Aba da Vitrine", "preco": "Preço", "ativa": "Ativa?"})

            with st.container(border=True):
                st.dataframe(df_display, use_container_width=True, hide_index=True)

            st.markdown('<div style="font-weight: 700; color: #1E293B; margin-top: 20px; margin-bottom: 10px;">✏️ Editar ou Excluir Cesta</div>', unsafe_allow_html=True)
            with st.container(border=True):
                cesta_selecionada = st.selectbox(
                    "Selecione a cesta que deseja gerenciar", cestas_da_aba,
                    format_func=lambda x: f"{x['nome']} (Aba: {x.get('secao_vitrine', 'N/A')})",
                    key=f"sel_cesta_{idx_aba}",
                )

                if cesta_selecionada:
                    c_id = cesta_selecionada["id"]

                    with st.form(f"form_editar_cesta_{idx_aba}"):
                        e_col1, e_col2 = st.columns(2)
                        with e_col1:
                            e_nome = st.text_input("Nome", value=cesta_selecionada.get("nome", ""))

                            secao_atual = cesta_selecionada.get("secao_vitrine") or "Cestas de Café"
                            opcoes_secao = secoes_disponiveis if secao_atual in secoes_disponiveis else [secao_atual] + secoes_disponiveis
                            idx_secao = opcoes_secao.index(secao_atual)

                            e_secao = st.selectbox("Seção da Vitrine", opcoes_secao, index=idx_secao)
                            preco_atual = cesta_selecionada.get("preco")
                            e_preco = st.number_input("Preço", value=float(preco_atual) if preco_atual is not None else 0.0, step=10.0, format="%.2f")
                            e_sem_preco = st.checkbox("💬 Preço sob consulta (não definido)", value=preco_atual is None, help="Marque se essa cesta ainda não tem preço fechado.")

                        with e_col2:
                            total_cestas = len(todas_cestas)
                            e_ordem = st.number_input(
                                "Ordem", value=min(int(cesta_selecionada.get("ordem", 1)), total_cestas),
                                min_value=1, max_value=total_cestas, step=1,
                                help=f"Posição na vitrine (1 a {total_cestas}). As demais cestas se reajustam automaticamente."
                            )
                            e_ativa = st.checkbox("Ativa?", value=bool(cesta_selecionada.get("ativa", True)))

                            if cesta_selecionada.get("imagem"):
                                st.image(cesta_selecionada["imagem"], width=110, caption="Foto atual")
                            e_imagem_arquivo = st.file_uploader(
                                "📷 Substituir Foto de Referência (opcional)",
                                type=["jpg", "jpeg", "png", "webp"],
                                key=f"upl_cesta_{idx_aba}",
                            )

                        e_desc = st.text_area("Descrição", value=cesta_selecionada.get("descricao", ""))

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            salvar_click = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                        with col_btn2:
                            excluir_click = st.form_submit_button("🗑️ Excluir Cesta", use_container_width=True)

                        if salvar_click:
                            try:
                                imagem_final = cesta_selecionada.get("imagem")
                                if e_imagem_arquivo:
                                    imagem_final = upload_imagem_cesta(e_imagem_arquivo)

                                update_data = {
                                    "nome": e_nome.strip(), "descricao": e_desc.strip(), "preco": None if e_sem_preco else e_preco,
                                    "imagem": imagem_final, "secao_vitrine": e_secao, "ordem": int(e_ordem), "ativa": e_ativa
                                }
                                atualizar_cesta(c_id, update_data)
                                st.success("Atualizado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")

                        if excluir_click:
                            st.session_state["cesta_confirmar_exclusao"] = c_id
                            st.rerun()

                    if st.session_state.get("cesta_confirmar_exclusao") == c_id:
                        st.warning(f"⚠️ Confirma excluir a cesta **{cesta_selecionada.get('nome')}**? Essa ação não pode ser desfeita.")
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            if st.button("✅ Sim, excluir", key=f"conf_del_cesta_{idx_aba}", use_container_width=True, type="primary"):
                                try:
                                    excluir_cesta(c_id)
                                    st.session_state["cesta_confirmar_exclusao"] = None
                                    st.warning("Cesta excluída!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {e}")
                        with cc2:
                            if st.button("❌ Cancelar", key=f"canc_del_cesta_{idx_aba}", use_container_width=True):
                                st.session_state["cesta_confirmar_exclusao"] = None
                                st.rerun()
