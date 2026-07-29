import streamlit as st
import time
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Seções da Vitrine", page_icon="🗂️", layout="wide")
configurar_pagina()
menu_lateral()

# Controle de acesso
if "usuario" not in st.session_state or st.session_state.usuario.get("perfil") != "Administrador":
    st.error("Acesso negado. Apenas administradores podem acessar esta página.")
    st.stop()

# =====================================================
# CSS PREMIUM
# =====================================================
st.markdown(
"""
<style>
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1050px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 2px !important; letter-spacing: -0.5px; }

/* Acordeão Criar Novo */
div[data-testid="stExpander"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 16px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05) !important; margin-bottom: 25px; }
div[data-testid="stExpander"] summary { background: #faf7f3; padding: 15px 20px !important; font-size: 16px !important; font-weight: 800 !important; color: #5a3b28 !important; }

/* Cards da Lista */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 14px !important;
    padding: 16px 20px !important; margin-bottom: 10px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    transition: all 0.2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #d2bfae !important; box-shadow: 0 8px 20px rgba(90, 59, 40, 0.08); transform: translateY(-2px); }

/* Botões */
div[data-testid="stButton"] button { font-weight: 800 !important; border-radius: 10px !important; transition: all 0.2s ease; }
div[data-testid="stButton"] button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)


col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("🗂️ Organização da Vitrine")
    st.caption("Crie, renomeie, exclua e defina a ordem exata de exibição dos blocos no site.")


# =====================================================
# SINCRONIZAÇÃO INTELIGENTE COM O BANCO
# =====================================================
secoes_bd = {}
try:
    # 1. Pega as seções configuradas na nova tabela
    res_sec = supabase.table("vitrine_secoes").select("*").execute()
    if res_sec.data:
        secoes_bd = {s["nome"]: s for s in res_sec.data}
        
    # 2. Varre as cestas pra ver se tem alguma seção "órfã" e já insere na tabela nova
    res_cestas = supabase.table("cestas").select("secao_vitrine").execute()
    if res_cestas.data:
        for c in res_cestas.data:
            val = c.get("secao_vitrine")
            if val and str(val).strip() != "":
                nome_sec = str(val).strip()
                if nome_sec not in secoes_bd:
                    nova = supabase.table("vitrine_secoes").insert({"nome": nome_sec, "ordem": 99}).execute()
                    if nova.data:
                        secoes_bd[nome_sec] = nova.data[0]
                        
    # 3. Garante que "Cestas Tradicionais" sempre exista
    if "Cestas Tradicionais" not in secoes_bd:
        nova = supabase.table("vitrine_secoes").insert({"nome": "Cestas Tradicionais", "ordem": 1}).execute()
        if nova.data:
            secoes_bd["Cestas Tradicionais"] = nova.data[0]

except Exception as e:
    st.error(f"Erro ao sincronizar seções: {e}")


# =====================================================
# 1. CRIAR NOVA SEÇÃO INDEPENDENTE
# =====================================================
with st.expander("✨ Criar Nova Seção na Vitrine", expanded=False):
    c1, c2 = st.columns([2, 1])
    with c1:
        nova_sec_nome = st.text_input("Nome da nova seção (Ex: Kits Corporativos)")
    with c2:
        nova_sec_ordem = st.number_input("Ordem de exibição", min_value=1, value=99)
        
    if st.button("💾 Adicionar Seção", type="primary"):
        if not nova_sec_nome.strip():
            st.error("Digite um nome!")
        elif nova_sec_nome.strip() in secoes_bd:
            st.warning("Esta seção já existe.")
        else:
            try:
                supabase.table("vitrine_secoes").insert({"nome": nova_sec_nome.strip(), "ordem": nova_sec_ordem}).execute()
                st.success("✅ Seção criada com sucesso!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao criar: {e}")


# =====================================================
# 2. LISTA PARA GERENCIAR, ORDENAR E EXCLUIR
# =====================================================
st.write("")
st.subheader("📋 Seções Existentes")

secoes_lista = sorted(secoes_bd.values(), key=lambda x: x["ordem"])

# Cabeçalhos da tabela
h1, h2, h3, h4 = st.columns([1, 3, 1, 1])
h1.markdown("**Posição (Ordem)**")
h2.markdown("**Nome da Seção**")
h3.markdown("**Ação**")
h4.markdown("**Ação**")

for sec in secoes_lista:
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1, 3, 1, 1], vertical_alignment="bottom")
        
        with c1:
            ordem_input = st.number_input("Ordem", value=int(sec["ordem"]), key=f"ord_{sec['id']}", label_visibility="collapsed")
        
        with c2:
            nome_input = st.text_input("Nome", value=sec["nome"], key=f"nome_{sec['id']}", label_visibility="collapsed")
            
        with c3:
            if st.button("💾 Salvar", key=f"salvar_{sec['id']}", use_container_width=True):
                nome_formatado = nome_input.strip()
                if not nome_formatado:
                    st.error("O nome não pode ficar vazio.")
                else:
                    try:
                        # 1. Atualiza na tabela de seções
                        supabase.table("vitrine_secoes").update({"nome": nome_formatado, "ordem": ordem_input}).eq("id", sec["id"]).execute()
                        
                        # 2. Se mudou o nome, atualiza todos os produtos que estavam nela automaticamente!
                        if nome_formatado != sec["nome"]:
                            supabase.table("cestas").update({"secao_vitrine": nome_formatado}).eq("secao_vitrine", sec["nome"]).execute()
                            
                        st.toast(f"✅ '{nome_formatado}' atualizada!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

        with c4:
            if sec["nome"] == "Cestas Tradicionais":
                st.button("🔒 Padrão", disabled=True, key=f"excluir_{sec['id']}", use_container_width=True)
            else:
                if st.button("🗑️ Excluir", key=f"excluir_{sec['id']}", use_container_width=True):
                    try:
                        # 1. Move os produtos dessa seção para a padrão
                        supabase.table("cestas").update({"secao_vitrine": "Cestas Tradicionais"}).eq("secao_vitrine", sec["nome"]).execute()
                        # 2. Apaga a seção
                        supabase.table("vitrine_secoes").delete().eq("id", sec["id"]).execute()
                        
                        st.success("✅ Seção apagada! Produtos movidos para 'Cestas Tradicionais'.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
