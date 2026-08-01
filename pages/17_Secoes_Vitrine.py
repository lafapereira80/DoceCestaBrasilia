import streamlit as st
import pandas as pd
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

st.set_page_config(page_title="Seções da Vitrine", page_icon="🖥️", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# =====================================================
# CSS APP NATIVO
# =====================================================
st.markdown("""
<style>
.app-header { font-size: clamp(24px, 4vw, 32px); font-weight: 800; color: #0F172A; margin-top: 10px; margin-bottom: 5px; letter-spacing: -1px; }
.app-sub { font-size: 15px; color: #64748B; margin-bottom: 25px; font-weight: 500; }
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 24px !important; padding: 24px !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02) !important; margin-bottom: 24px !important; }
.stTextInput>div>div>input, .stNumberInput>div>div>input { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; background-color: #F8FAFC !important; color: #1E293B !important; }
div[data-testid="stFormSubmitButton"] button, div[data-testid="stButton"] button { border-radius: 12px !important; font-weight: 700 !important; }
div[data-testid="stFormSubmitButton"] button[kind="primary"] { background: #10B981 !important; color: white !important; border: none !important; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2) !important; }
div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(16, 185, 129, 0.3) !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-header">🖥️ Seções da Vitrine</div><div class="app-sub">Crie e organize as abas do seu catálogo público.</div>', unsafe_allow_html=True)

# =====================================================
# GESTÃO DE SEÇÕES
# =====================================================
aba_lista, aba_nova = st.tabs(["📋 Abas Cadastradas", "➕ Criar Nova Aba"])

with aba_nova:
    with st.container(border=True):
        st.markdown('<div style="font-weight: 700; color: #1E293B; margin-bottom: 15px;">✨ Configurar Nova Seção</div>', unsafe_allow_html=True)
        with st.form("form_nova_secao", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome da Aba *", placeholder="Ex: Cestas de Café")
                ativa = st.checkbox("Aba Ativa (Aparece no site)?", value=True)
            with col2:
                ordem = st.number_input("Ordem de Exibição", min_value=1, step=1, value=1, help="1 aparece primeiro (mais à esquerda).")
            
            st.write("")
            if st.form_submit_button("✅ Adicionar à Vitrine", type="primary", use_container_width=True):
                if not nome.strip():
                    st.error("O nome da seção é obrigatório!")
                else:
                    try:
                        supabase.table("vitrine_secoes").insert({"nome": nome.strip(), "ordem": ordem, "ativa": ativa}).execute()
                        st.success(f"Aba '{nome}' criada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao salvar. Verifique se o nome já existe.")

with aba_lista:
    try:
        secoes = supabase.table("vitrine_secoes").select("*").order("ordem").execute().data or []
    except:
        secoes = []
        
    if not secoes:
        st.info("Nenhuma seção cadastrada.")
    else:
        df = pd.DataFrame(secoes)
        df_display = df[["ordem", "nome", "ativa"]].rename(columns={"ordem": "Posição", "nome": "Nome da Aba", "ativa": "Ativa no Site?"})
        
        with st.container(border=True):
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
        st.markdown('<div style="font-weight: 700; color: #1E293B; margin-top: 20px; margin-bottom: 10px;">✏️ Editar ou Excluir</div>', unsafe_allow_html=True)
        with st.container(border=True):
            secao_selecionada = st.selectbox("Selecione a aba", secoes, format_func=lambda x: f"{x['nome']}")
            
            if secao_selecionada:
                with st.form("form_editar_secao"):
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        e_nome = st.text_input("Nome", value=secao_selecionada["nome"])
                        e_ativa = st.checkbox("Ativa?", value=bool(secao_selecionada["ativa"]))
                    with e_col2:
                        e_ordem = st.number_input("Ordem", value=int(secao_selecionada["ordem"]), step=1)
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                            try:
                                supabase.table("vitrine_secoes").update({"nome": e_nome.strip(), "ordem": e_ordem, "ativa": e_ativa}).eq("id", secao_selecionada["id"]).execute()
                                st.success("Atualizado com sucesso!")
                                st.rerun()
                            except: st.error("Erro ao atualizar.")
                    with c_btn2:
                        if st.form_submit_button("🗑️ Excluir Aba", use_container_width=True):
                            try:
                                supabase.table("vitrine_secoes").delete().eq("id", secao_selecionada["id"]).execute()
                                st.warning("Aba excluída!")
                                st.rerun()
                            except: st.error("Erro: existem cestas vinculadas a esta aba. Altere as cestas antes de excluir.")
