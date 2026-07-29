import streamlit as st
from config.supabase import supabase
from utils.menu import configurar_pagina, menu_lateral

# Configuração Padrão
st.set_page_config(page_title="Seções da Vitrine", page_icon="🗂️", layout="wide")
configurar_pagina()
menu_lateral()

# Controle de acesso (Apenas Administrador)
if "usuario" not in st.session_state or st.session_state.usuario.get("perfil") != "Administrador":
    st.error("Acesso negado. Apenas administradores podem acessar esta página.")
    st.stop()

st.title("🗂️ Organização das Seções da Vitrine")
st.markdown("Gerencie como as suas Cestas e Tábuas são agrupadas lá na vitrine principal do site.")
st.divider()

# ==========================================
# 1. BUSCAR TODAS AS SEÇÕES EXISTENTES
# ==========================================
try:
    # Busca todos os produtos para vermos as seções únicas
    resposta = supabase.table("cestas").select("secao_vitrine").execute()
    todas_secoes = []
    
    if resposta.data:
        for item in resposta.data:
            sec = item.get("secao_vitrine")
            if not sec or str(sec).strip() == "":
                sec = "Cestas Tradicionais"
            
            if sec not in todas_secoes:
                todas_secoes.append(sec)
                
    todas_secoes = sorted(todas_secoes)
except Exception as e:
    st.error(f"Erro ao buscar seções: {e}")
    todas_secoes = []

if not todas_secoes:
    st.info("Nenhuma seção customizada encontrada. O sistema está usando 'Cestas Tradicionais'.")
    st.stop()

# ==========================================
# 2. PAINEL DE AÇÃO (RENOMEAR OU EXCLUIR)
# ==========================================
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("Modificar uma Seção")
    secao_selecionada = st.selectbox("1. Escolha a seção que deseja alterar:", todas_secoes)
    
    acao = st.radio("2. O que deseja fazer com esta seção?", 
                    ["Renomear (Mudar o nome)", "Excluir (Desfazer seção)"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ------------------------------------
    # AÇÃO: RENOMEAR
    # ------------------------------------
    if acao == "Renomear (Mudar o nome)":
        st.info("💡 Isso mudará o nome da seção para todos os produtos que estão nela.")
        novo_nome = st.text_input("Digite o novo nome para a seção:", placeholder="Ex: Kits Corporativos")
        
        if st.button("Salvar Novo Nome", type="primary", use_container_width=True):
            if not novo_nome.strip():
                st.warning("Digite um nome válido!")
            elif novo_nome.strip() == secao_selecionada:
                st.warning("O nome digitado é igual ao atual.")
            else:
                try:
                    # Atualiza em massa no banco de dados
                    supabase.table("cestas").update({"secao_vitrine": novo_nome.strip()}).eq("secao_vitrine", secao_selecionada).execute()
                    
                    st.success(f"✅ Seção renomeada com sucesso para '{novo_nome}'!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao renomear: {e}")
                    
    # ------------------------------------
    # AÇÃO: EXCLUIR
    # ------------------------------------
    elif acao == "Excluir (Desfazer seção)":
        st.warning("⚠️ Se você excluir esta seção, todos os produtos dela voltarão a aparecer em **'Cestas Tradicionais'**. Nenhum produto será apagado.")
        
        if secao_selecionada == "Cestas Tradicionais":
            st.error("A seção 'Cestas Tradicionais' é o padrão do sistema e não pode ser excluída.")
        else:
            if st.button("🗑️ Excluir Seção e Mover Produtos", type="primary", use_container_width=True):
                try:
                    # Move os produtos para o padrão
                    supabase.table("cestas").update({"secao_vitrine": "Cestas Tradicionais"}).eq("secao_vitrine", secao_selecionada).execute()
                    st.success("✅ Seção excluída! Produtos movidos para 'Cestas Tradicionais'.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir: {e}")

with col2:
    st.subheader("Como criar uma seção nova?")
    with st.container(border=True):
        st.markdown("""
        Para criar uma categoria inteiramente nova na sua vitrine, **você não precisa fazer isso por aqui.**
        
        Siga este passo a passo simples:
        1. Vá em **Cestas e Vitrine**.
        2. Clique em **Editar** em algum produto (ou crie um novo).
        3. No campo **"Seção da Vitrine"**, simplesmente **digite o novo nome** (Ex: *Kits Dia dos Pais*).
        4. Salve o produto.
        
        🎉 **Pronto!** A nova seção será criada instantaneamente e aparecerá no seu site.
        """)
