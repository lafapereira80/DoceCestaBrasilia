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
# CSS PREMIUM E LIMPO
# =====================================================
st.markdown(
"""
<style>
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 950px; }
h1 { font-size: 28px !important; font-weight: 800 !important; color: #4a2e1b; margin-bottom: 2px !important; letter-spacing: -0.5px; }

div[data-testid="stExpander"] { background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 16px !important; box-shadow: 0 4px 15px rgba(90, 59, 40, 0.05) !important; margin-bottom: 30px; }
div[data-testid="stExpander"] summary { background: #faf7f3; padding: 15px 20px !important; font-size: 16px !important; font-weight: 800 !important; color: #5a3b28 !important; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff; border: 1px solid #e8ddd3 !important; border-radius: 12px !important;
    padding: 12px 20px !important; margin-bottom: 8px !important; box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #d2bfae !important; box-shadow: 0 4px 12px rgba(90, 59, 40, 0.06); }

div[data-testid="stButton"] button { font-weight: 800 !important; border-radius: 8px !important; transition: all 0.2s ease; }
div[data-testid="stButton"] button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)


col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("🗂️ Organização da Vitrine")
    st.caption("Crie, renomeie, exclua e defina a ordem exata de exibição no site.")


# =====================================================
# SINCRONIZAÇÃO E CORREÇÃO AUTOMÁTICA (Cestas de Café)
# =====================================================
try:
    # 1. Renomeia 'Cestas Tradicionais' para 'Cestas de Café' (se existir)
    supabase.table("vitrine_secoes").update({"nome": "Cestas de Café"}).eq("nome", "Cestas Tradicionais").execute()
    supabase.table("cestas").update({"secao_vitrine": "Cestas de Café"}).eq("secao_vitrine", "Cestas Tradicionais").execute()
    
    # 2. Busca todas as seções ordenadas
    res_sec = supabase.table("vitrine_secoes").select("*").order("ordem").execute()
    secoes_bd = res_sec.data or []
        
    # 3. Garante que 'Cestas de Café' sempre exista
    if not any(s["nome"] == "Cestas de Café" for s in secoes_bd):
        nova = supabase.table("vitrine_secoes").insert({"nome": "Cestas de Café", "ordem": 1}).execute()
        if nova.data:
            secoes_bd.insert(0, nova.data[0])

    # 4. Normaliza as ordens para não ter "buracos" (ex: 1, 2, 3...)
    for i, s in enumerate(secoes_bd):
        ordem_correta = i + 1
        if s["ordem"] != ordem_correta:
            supabase.table("vitrine_secoes").update({"ordem": ordem_correta}).eq("id", s["id"]).execute()
            s["ordem"] = ordem_correta

except Exception as e:
    st.error(f"Erro ao sincronizar banco de dados: {e}")
    secoes_bd = []

total_secoes = len(secoes_bd)


# =====================================================
# 1. CRIAR NOVA SEÇÃO
# =====================================================
with st.expander("✨ Criar Nova Seção na Vitrine", expanded=False):
    c1, c2 = st.columns([2, 1])
    with c1:
        nova_sec_nome = st.text_input("Nome da nova seção (Ex: Tábuas de Frios)")
    with c2:
        # A trava da ordem: Não deixa ser maior que o total + 1
        posicao_maxima = total_secoes + 1
        nova_sec_ordem = st.number_input("Posição na Vitrine", min_value=1, max_value=posicao_maxima, value=posicao_maxima)
        
    if st.button("💾 Adicionar Seção", type="primary"):
        if not nova_sec_nome.strip():
            st.error("Digite um nome para a seção!")
        elif any(s["nome"].lower() == nova_sec_nome.strip().lower() for s in secoes_bd):
            st.warning("Esta seção já existe.")
        else:
            try:
                # Insere a nova
                novo_registro = {"nome": nova_sec_nome.strip(), "ordem": nova_sec_ordem}
                supabase.table("vitrine_secoes").insert(novo_registro).execute()
                
                # Se inseriu no meio, empurra as outras pra baixo
                if nova_sec_ordem <= total_secoes:
                    for s in secoes_bd:
                        if s["ordem"] >= nova_sec_ordem:
                            supabase.table("vitrine_secoes").update({"ordem": s["ordem"] + 1}).eq("id", s["id"]).execute()
                            
                st.success("✅ Seção criada com sucesso!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao criar: {e}")


# =====================================================
# 2. LISTA LIMPA PARA GERENCIAR
# =====================================================
st.subheader(f"📋 Seções Existentes ({total_secoes})")

# Cabeçalho da tabela mais limpo
h1, h2, h3, h4 = st.columns([0.8, 3, 1, 1])
h1.markdown("**Posição**")
h2.markdown("**Nome da Seção**")
h3.markdown("")
h4.markdown("")

for sec in secoes_bd:
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([0.8, 3, 1, 1], vertical_alignment="bottom")
        
        with c1:
            # Trava na edição: não deixa colocar número maior que o total de seções
            ordem_input = st.number_input("Ordem", min_value=1, max_value=total_secoes, value=int(sec["ordem"]), key=f"ord_{sec['id']}", label_visibility="collapsed")
        
        with c2:
            nome_input = st.text_input("Nome", value=sec["nome"], key=f"nome_{sec['id']}", label_visibility="collapsed")
            
        with c3:
            if st.button("💾 Salvar", key=f"salvar_{sec['id']}", use_container_width=True):
                nome_formatado = nome_input.strip()
                if not nome_formatado:
                    st.error("O nome não pode ficar vazio.")
                else:
                    try:
                        # 1. Atualiza Nome (e arruma na tabela de produtos se mudou)
                        if nome_formatado != sec["nome"]:
                            supabase.table("vitrine_secoes").update({"nome": nome_formatado}).eq("id", sec["id"]).execute()
                            supabase.table("cestas").update({"secao_vitrine": nome_formatado}).eq("secao_vitrine", sec["nome"]).execute()
                        
                        # 2. Reordenação Inteligente (Empurra as outras pra não ter posição duplicada)
                        if ordem_input != sec["ordem"]:
                            lista_sem_ela = [s for s in secoes_bd if s["id"] != sec["id"]]
                            lista_sem_ela.insert(ordem_input - 1, sec) # Insere na nova posição
                            
                            for i, s in enumerate(lista_sem_ela):
                                supabase.table("vitrine_secoes").update({"ordem": i + 1}).eq("id", s["id"]).execute()
                            
                        st.toast(f"✅ Seção atualizada!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

        with c4:
            if sec["nome"] == "Cestas de Café":
                st.button("🔒 Padrão", disabled=True, key=f"excluir_{sec['id']}", use_container_width=True, help="A seção principal não pode ser excluída.")
            else:
                if st.button("🗑️ Excluir", key=f"excluir_{sec['id']}", use_container_width=True):
                    try:
                        # Move os produtos para o padrão e apaga a seção
                        supabase.table("cestas").update({"secao_vitrine": "Cestas de Café"}).eq("secao_vitrine", sec["nome"]).execute()
                        supabase.table("vitrine_secoes").delete().eq("id", sec["id"]).execute()
                        
                        # Reorganiza as posições que sobraram
                        lista_sem_ela = [s for s in secoes_bd if s["id"] != sec["id"]]
                        for i, s in enumerate(lista_sem_ela):
                            supabase.table("vitrine_secoes").update({"ordem": i + 1}).eq("id", s["id"]).execute()

                        st.success("✅ Seção apagada! Produtos foram movidos para 'Cestas de Café'.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
