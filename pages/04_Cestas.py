import streamlit as st
import pandas as pd
import uuid
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

/* Upload Widget Styling */
div[data-testid="stFileUploader"] { background-color: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 10px; }

/* RESPONSIVIDADE */
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

# =====================================================
# FUNÇÕES DE BANCO DE DADOS E UPLOAD
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

def fazer_upload_imagem(arquivo):
    """Faz o upload do arquivo para o bucket 'cestas' e retorna a URL pública."""
    if arquivo is None:
        return None
    try:
        # Gera um nome único para o arquivo usando UUID para não sobrescrever imagens antigas
        extensao = arquivo.name.split('.')[-1]
        nome_arquivo = f"{uuid.uuid4()}.{extensao}"
        bytes_arquivo = arquivo.getvalue()
        
        # Upload para o bucket 'cestas' no Supabase
        supabase.storage.from_("cestas").upload(
            file=bytes_arquivo,
            path=nome_arquivo,
            file_options={"content-type": arquivo.type}
        )
        
        # Retorna a URL pública gerada
        url_publica = supabase.storage.from_("cestas").get_public_url(nome_arquivo)
        return url_publica
    except Exception as e:
        st.error(f"Erro no upload da imagem: {e}")
        return None

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
                secao = st.selectbox("Seção da Vitrine (Aba) *", secoes_disponiveis, help="Em qual aba do site essa cesta vai aparecer?")
                preco = st.number_input("Preço Base (R$)", min_value=0.0, step=10.0, format="%.2f")
                sem_preco = st.checkbox("💬 Preço sob consulta (não definido)", help="Marque se essa cesta ainda não tem preço fechado. A vitrine mostrará 'Sob consulta' em vez de R$ 0,00.")
            
            with col2:
                ordem = st.number_input("Ordem de Exibição", min_value=1, step=1, value=1, help="1 aparece primeiro, 2 depois...")
                ativa = st.checkbox("Cesta Ativa (Aparece no site)?", value=True)
                
                # Novo sistema híbrido de imagens (Upload ou Link)
                imagem_arquivo = st.file_uploader("📸 Upload da Imagem (Recomendado)", type=["jpg", "jpeg", "png", "webp"], help="Faça o upload direto do seu dispositivo para a nuvem.")
                imagem_url = st.text_input("Ou URL externa da imagem", placeholder="Ex: https://... (Deixe em branco se fizer o upload acima)")

            descricao = st.text_area("Descrição (Opcional)", placeholder="Itens pré-definidos ou texto de encantamento...")
            
            st.write("")
            submit = st.form_submit_button("✅ Salvar Cesta no Catálogo", type="primary", use_container_width=True)
            
            if submit:
                if not nome.strip():
                    st.error("O nome da cesta é obrigatório!")
                else:
                    # Lógica para definir a imagem
                    link_final_imagem = imagem_url.strip()
                    if imagem_arquivo is not None:
                        url_upload = fazer_upload_imagem(imagem_arquivo)
                        if url_upload:
                            link_final_imagem = url_upload

                    dados = {
                        "nome": nome.strip(),
                        "descricao": descricao.strip(),
                        "preco": None if sem_preco else preco,
                        "imagem": link_final_imagem,
                        "secao_vitrine": secao,
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
        df_display = df[["ordem", "nome", "secao_vitrine", "preco", "ativa"]].copy()
        df_display["preco"] = df_display["preco"].apply(lambda x: "💬 Sob consulta" if x is None else f"R$ {formatar_moeda(x)}")
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
                        
                        secao_atual = cesta_selecionada.get("secao_vitrine", "Cestas de Café")
                        opcoes_secao = secoes_disponiveis if secao_atual in secoes_disponiveis else [secao_atual] + secoes_disponiveis
                        idx_secao = opcoes_secao.index(secao_atual)
                        
                        e_secao = st.selectbox("Seção da Vitrine", opcoes_secao, index=idx_secao)
                        preco_atual = cesta_selecionada.get("preco")
                        e_preco = st.number_input("Preço", value=float(preco_atual) if preco_atual is not None else 0.0, step=10.0, format="%.2f")
                        e_sem_preco = st.checkbox("💬 Preço sob consulta (não definido)", value=preco_atual is None)
                        
                    with e_col2:
                        e_ordem = st.number_input("Ordem", value=int(cesta_selecionada.get("ordem", 1)), step=1)
                        e_ativa = st.checkbox("Ativa?", value=bool(cesta_selecionada.get("ativa", True)))
                        
                        # Upload na edição
                        e_imagem_arquivo = st.file_uploader("📸 Nova Foto (Substituir a atual)", type=["jpg", "jpeg", "png", "webp"])
                        e_imagem_url = st.text_input("URL da Imagem Atual", value=cesta_selecionada.get("imagem", ""), help="Você pode colar uma nova URL ou fazer o upload acima.")
                        
                    e_desc = st.text_area("Descrição", value=cesta_selecionada.get("descricao", ""))
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                            
                            # Lógica para definir a nova imagem na edição
                            link_final_imagem_edit = e_imagem_url.strip()
                            if e_imagem_arquivo is not None:
                                url_upload_edit = fazer_upload_imagem(e_imagem_arquivo)
                                if url_upload_edit:
                                    link_final_imagem_edit = url_upload_edit
                            
                            update_data = {
                                "nome": e_nome.strip(), "descricao": e_desc.strip(), "preco": None if e_sem_preco else e_preco,
                                "imagem": link_final_imagem_edit, "secao_vitrine": e_secao, "ordem": e_ordem, "ativa": e_ativa
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
