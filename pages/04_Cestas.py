import streamlit as st
import pandas as pd
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador
from utils.formatacao import formatar_moeda

st.set_page_config(page_title="Gestão de Cestas", page_icon="🧺", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-header">🧺 Gestão de Cestas e Kits</div><div class="app-sub">Cadastre novos pacotes e organize as abas da sua vitrine pública.</div>', unsafe_allow_html=True)

# =====================================================
# FUNÇÕES DE BANCO DE DADOS
# =====================================================
def carregar_secoes():
    """Busca as seções cadastradas para organizar as abas da vitrine"""
    try:
        res = supabase.table("vitrine_secoes").select("nome").eq("ativa", True).order("ordem").execute()
        return [s["nome"] for s in res.data] if res.data else ["Cestas de Café"]
    except:
        return ["Cestas de Café"]

def carregar_cestas():
    try: return supabase.table("cestas").select("*").order("ordem").execute().data or []
    except Exception as e: st.error(f"Erro ao carregar cestas: {e}"); return []

secoes_disponiveis = carregar_secoes()

# =====================================================
# ABAS DE GESTÃO
# =====================================================
aba_lista, aba_nova = st.tabs(["📋 Cestas Cadastradas", "➕ Adicionar Nova Cesta"])

with aba_nova:
    with st.container(border=True):
        st.markdown('<div style="font-weight: 700; color: #1E293B; margin-bottom: 15px; font-size: 16px;">✨ Criar Novo Pacote</div>', unsafe_allow_html=True)
        with st.form("form_nova_cesta", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da Cesta/Kit *", placeholder="Ex: Cesta Romântica Luxo")
                # A MÁGICA ACONTECE AQUI: Ligação direta com a Vitrine
                secao = st.selectbox("Seção da Vitrine (Aba) *", secoes_disponiveis, help="Em qual aba do site essa cesta vai aparecer?")
                preco = st.number_input("Preço Base (R$)", min_value=0.0, step=10.0, format="%.2f")
            
            with col2:
                ordem = st.number_input("Ordem de Exibição", min_value=1, step=1, value=1, help="1 aparece primeiro, 2 depois...")
                ativa = st.checkbox("Cesta Ativa (Aparece no site)?", value=True)
                imagem = st.text_input("URL da Imagem Principal", placeholder="Link da foto no Google Drive/Imgur")

            descricao = st.text_area("Descrição (Opcional)", placeholder="Itens pré-definidos ou texto de encantamento...")
            
            st.write("")
            submit = st.form_submit_button("✅ Salvar Cesta no Catálogo", type="primary", use_container_width=True)
            
            if submit:
                if not nome.strip():
                    st.error("O nome da cesta é obrigatório!")
                else:
                    dados = {
                        "nome": nome.strip(),
                        "descricao": descricao.strip(),
                        "preco": preco,
                        "imagem": imagem.strip(),
                        "secao_vitrine": secao, # <-- Salvando a Seção!
                        "ordem": ordem,
                        "ativa": ativa
                    }
                    try:
                        supabase.table("cestas").insert(dados).execute()
                        st.success(f"Cesta '{nome}' adicionada com sucesso na seção '{secao}'!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

with aba_lista:
    cestas = carregar_cestas()
    
    if not cestas:
        st.info("Nenhuma cesta cadastrada ainda. Vá para a aba 'Adicionar Nova Cesta'.")
    else:
        df = pd.DataFrame(cestas)
        # Exibimos a Seção na tabela para o administrador ter controle visual
        df_display = df[["ordem", "nome", "secao_vitrine", "preco", "ativa"]].copy()
        df_display["preco"] = df_display["preco"].apply(lambda x: f"R$ {formatar_moeda(x)}")
        df_display = df_display.rename(columns={"ordem": "Posição", "nome": "Cesta", "secao_vitrine": "Aba da Vitrine", "preco": "Preço", "ativa": "Ativa?"})
        
        with st.container(border=True):
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
        st.markdown('<div style="font-weight: 700; color: #1E293B; margin-top: 20px; margin-bottom: 10px;">✏️ Editar ou Excluir Cesta</div>', unsafe_allow_html=True)
        with st.container(border=True):
            cesta_selecionada = st.selectbox("Selecione a cesta que deseja gerenciar", cestas, format_func=lambda x: f"{x['nome']} (Aba: {x.get('secao_vitrine', 'N/A')})")
            
            if cesta_selecionada:
                with st.form("form_editar_cesta"):
                    c_id = cesta_selecionada["id"]
                    
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        e_nome = st.text_input("Nome", value=cesta_selecionada.get("nome", ""))
                        
                        # Garantir que o selectbox de edição reconheça a seção salva, mesmo se ela foi apagada do banco
                        secao_atual = cesta_selecionada.get("secao_vitrine", "Cestas de Café")
                        opcoes_secao = secoes_disponiveis if secao_atual in secoes_disponiveis else [secao_atual] + secoes_disponiveis
                        idx_secao = opcoes_secao.index(secao_atual)
                        
                        e_secao = st.selectbox("Seção da Vitrine", opcoes_secao, index=idx_secao)
                        e_preco = st.number_input("Preço", value=float(cesta_selecionada.get("preco", 0.0)), step=10.0, format="%.2f")
                        
                    with e_col2:
                        e_ordem = st.number_input("Ordem", value=int(cesta_selecionada.get("ordem", 1)), step=1)
                        e_ativa = st.checkbox("Ativa?", value=bool(cesta_selecionada.get("ativa", True)))
                        e_imagem = st.text_input("URL da Imagem", value=cesta_selecionada.get("imagem", ""))
                        
                    e_desc = st.text_area("Descrição", value=cesta_selecionada.get("descricao", ""))
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                            update_data = {
                                "nome": e_nome.strip(), "descricao": e_desc.strip(), "preco": e_preco,
                                "imagem": e_imagem.strip(), "secao_vitrine": e_secao, "ordem": e_ordem, "ativa": e_ativa
                            }
                            try:
                                supabase.table("cestas").update(update_data).eq("id", c_id).execute()
                                st.success("Atualizado com sucesso!")
                                st.rerun()
                            except Exception as e: st.error(f"Erro: {e}")
                    
                    with col_btn2:
                        if st.form_submit_button("🗑️ Excluir Cesta", use_container_width=True):
                            try:
                                supabase.table("cestas").delete().eq("id", c_id).execute()
                                st.warning("Cesta excluída!")
                                st.rerun()
                            except Exception as e: st.error(f"Erro ao excluir: {e}")
