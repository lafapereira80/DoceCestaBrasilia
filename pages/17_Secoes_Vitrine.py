import streamlit as st
import time
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

# =====================================================
# CONFIGURAÇÃO DA PÁGINA E CSS
# =====================================================
st.set_page_config(page_title="Seções da Vitrine", page_icon="🗂️", layout="wide")
configurar_pagina()
menu_lateral()

if "usuario" not in st.session_state or st.session_state.usuario.get("perfil") != "Administrador":
    st.error("Acesso negado. Apenas administradores podem acessar.")
    st.stop()

st.markdown(
"""
<style>
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1000px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 2px !important; letter-spacing: -0.5px; }
div[data-testid="stExpander"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 16px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05) !important; margin-bottom: 30px; }
div[data-testid="stExpander"] summary { background: #faf7f3; padding: 15px 20px !important; font-size: 16px !important; font-weight: 800 !important; color: #5a3b28 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 12px !important; padding: 12px 20px !important; margin-bottom: 8px !important; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #d2bfae !important; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.06); }
div[data-testid="stButton"] button { font-weight: 800 !important; border-radius: 8px !important; transition: all 0.2s ease; }
div[data-testid="stButton"] button:hover { transform: scale(1.02); }
div[data-baseweb="select"] { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("🗂️ Organização da Vitrine")
    st.caption("Crie, renomeie, exclua, ative/desative e defina a ordem de exibição no site.")

# =====================================================
# SINCRONIZAÇÃO INTELIGENTE 
# =====================================================
try:
    res_sec = supabase.table("vitrine_secoes").select("*").order("ordem").execute()
    secoes_bd = res_sec.data or []
        
    if len(secoes_bd) == 0:
        nova = supabase.table("vitrine_secoes").insert({"nome": "Cestas de Café", "ordem": 1, "ativa": True}).execute()
        if nova.data: secoes_bd.append(nova.data[0])

    for i, s in enumerate(secoes_bd):
        ordem_correta = i + 1
        if s["ordem"] != ordem_correta:
            supabase.table("vitrine_secoes").update({"ordem": ordem_correta}).eq("id", s["id"]).execute()
            s["ordem"] = ordem_correta
except Exception as e:
    st.error(f"Erro ao sincronizar: {e}")
    secoes_bd = []

total_secoes = len(secoes_bd)
secao_padrao = secoes_bd[0] if total_secoes > 0 else None

# =====================================================
# 1. CRIAR NOVA SEÇÃO
# =====================================================
with st.expander("✨ Criar Nova Seção na Vitrine", expanded=False):
    c1, c2 = st.columns([2, 1])
    with c1: nova_sec_nome = st.text_input("Nome da nova seção (Ex: Tábuas de Frios)")
    with c2:
        posicao_maxima = total_secoes + 1
        nova_sec_ordem = st.selectbox("Posição", list(range(1, posicao_maxima + 1)), index=total_secoes)
        
    if st.button("💾 Adicionar Seção", type="primary"):
        if not nova_sec_nome.strip(): st.error("Digite um nome para a seção!")
        elif any(s["nome"].lower() == nova_sec_nome.strip().lower() for s in secoes_bd): st.warning("Esta seção já existe.")
        else:
            try:
                novo_registro = {"nome": nova_sec_nome.strip(), "ordem": nova_sec_ordem, "ativa": True}
                supabase.table("vitrine_secoes").insert(novo_registro).execute()
                if nova_sec_ordem <= total_secoes:
                    for s in secoes_bd:
                        if s["ordem"] >= nova_sec_ordem:
                            supabase.table("vitrine_secoes").update({"ordem": s["ordem"] + 1}).eq("id", s["id"]).execute()
                st.success("✅ Seção criada com sucesso!")
                time.sleep(1)
                st.rerun()
            except Exception as e: st.error(f"Erro: {e}")


# =====================================================
# 2. LISTA PARA GERENCIAR
# =====================================================
st.subheader(f"📋 Seções Existentes ({total_secoes})")

h1, h2, h3, h4, h5 = st.columns([0.8, 1, 2.3, 1.8, 1])
h1.markdown("**Posição**")
h2.markdown("**Status**")
h3.markdown("**Nome da Seção**")

opcoes_ordem = list(range(1, total_secoes + 1))

for sec in secoes_bd:
    sec_id = sec["id"]
    if f"editando_{sec_id}" not in st.session_state: st.session_state[f"editando_{sec_id}"] = False

    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([0.8, 1, 2.3, 1.8, 1], vertical_alignment="center")
        
        # 1. ORDEM
        with c1:
            nova_ordem = st.selectbox("Ordem", opcoes_ordem, index=sec["ordem"] - 1, key=f"ord_{sec_id}", label_visibility="collapsed")
            if nova_ordem != sec["ordem"]:
                with st.spinner("Reordenando..."):
                    lista_sem_ela = [s for s in secoes_bd if s["id"] != sec_id]
                    lista_sem_ela.insert(nova_ordem - 1, sec)
                    for i, s in enumerate(lista_sem_ela):
                        supabase.table("vitrine_secoes").update({"ordem": i + 1}).eq("id", s["id"]).execute()
                st.toast("✅ Ordem atualizada!")
                time.sleep(0.5)
                st.rerun()
                
        # 2. STATUS (ATIVA/INATIVA)
        with c2:
            is_ativa = sec.get("ativa", True)
            if st.toggle("Visível", value=is_ativa, key=f"tgl_{sec_id}"):
                if not is_ativa:
                    supabase.table("vitrine_secoes").update({"ativa": True}).eq("id", sec_id).execute()
                    st.toast(f"✅ '{sec['nome']}' ativada!")
                    time.sleep(0.5)
                    st.rerun()
            else:
                if is_ativa:
                    supabase.table("vitrine_secoes").update({"ativa": False}).eq("id", sec_id).execute()
                    st.toast(f"❌ '{sec['nome']}' desativada!")
                    time.sleep(0.5)
                    st.rerun()
        
        # 3. NOME
        with c3:
            if st.session_state[f"editando_{sec_id}"]:
                nome_input = st.text_input("Nome", value=sec["nome"], key=f"nome_{sec_id}", label_visibility="collapsed")
            else:
                st.text_input("Nome", value=sec["nome"], key=f"nome_block_{sec_id}", disabled=True, label_visibility="collapsed")
            
        # 4. AÇÕES DE EDIÇÃO
        with c4:
            if st.session_state[f"editando_{sec_id}"]:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾", key=f"salvar_{sec_id}", type="primary", use_container_width=True):
                        nome_formatado = nome_input.strip()
                        if nome_formatado and nome_formatado != sec["nome"]:
                            supabase.table("vitrine_secoes").update({"nome": nome_formatado}).eq("id", sec_id).execute()
                            supabase.table("cestas").update({"secao_vitrine": nome_formatado}).eq("secao_vitrine", sec["nome"]).execute()
                            st.session_state[f"editando_{sec_id}"] = False
                            st.toast("✅ Nome alterado!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.session_state[f"editando_{sec_id}"] = False
                            st.rerun()
                with b2:
                    if st.button("❌", key=f"cancel_{sec_id}", use_container_width=True):
                        st.session_state[f"editando_{sec_id}"] = False
                        st.rerun()
            else:
                if st.button("✏️ Alterar Nome", key=f"editar_{sec_id}", use_container_width=True):
                    st.session_state[f"editando_{sec_id}"] = True
                    st.rerun()

        # 5. EXCLUSÃO
        with c5:
            if secao_padrao and sec["id"] == secao_padrao["id"]:
                st.button("🔒 Padrão", disabled=True, key=f"excluir_{sec_id}", use_container_width=True)
            else:
                if st.button("🗑️ Excluir", key=f"excluir_{sec_id}", use_container_width=True):
                    try:
                        supabase.table("cestas").update({"secao_vitrine": secao_padrao["nome"]}).eq("secao_vitrine", sec["nome"]).execute()
                        supabase.table("vitrine_secoes").delete().eq("id", sec_id).execute()
                        lista_sem_ela = [s for s in secoes_bd if s["id"] != sec_id]
                        for i, s in enumerate(lista_sem_ela):
                            supabase.table("vitrine_secoes").update({"ordem": i + 1}).eq("id", s["id"]).execute()
                        st.success(f"✅ Seção apagada! Produtos movidos para '{secao_padrao['nome']}'.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e: st.error(f"Erro ao excluir: {e}")
