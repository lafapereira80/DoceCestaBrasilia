import streamlit as st
import pandas as pd
import json
from services.vitrine_service import obter_configuracao_vitrine, atualizar_configuracao_vitrine
from utils.menu import configurar_pagina, menu_lateral

st.set_page_config(page_title="Configurar Vitrine", page_icon="🖥️", layout="wide")
configurar_pagina()
menu_lateral()

usuario_logado = st.session_state.get("usuario", {})
perfil = usuario_logado.get("perfil", "") if isinstance(usuario_logado, dict) else getattr(usuario_logado, "perfil", "")

if perfil != "Administrador":
    st.error("🚫 Acesso restrito. Apenas administradores podem acessar esta página.")
    if st.button("⬅ Voltar ao Painel"): st.switch_page("pages/99_Admin.py")
    st.stop()

st.title("🖥️ Editor da Vitrine (CMS Dinâmico)")
st.caption("Crie, altere, ordene ou remova áreas do site público com total liberdade.")
st.divider()

config = obter_configuracao_vitrine()

# Carrega seções salvas
secoes = config.get("secoes", [])
if isinstance(secoes, str):
    try: secoes = json.loads(secoes)
    except: secoes = []

aba1, aba2, aba3 = st.tabs(["1. Cabeçalho e Rodapé", "2. Gerenciar e Criar Seções", "3. Ordem das Seções"])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📌 Cabeçalho")
        cabecalho_titulo = st.text_input("Título Principal", value=config.get("cabecalho_titulo", ""))
        cabecalho_subtitulo = st.text_input("Subtítulo", value=config.get("cabecalho_subtitulo", ""))
    
    with col2:
        st.subheader("📍 Rodapé (Fale Conosco)")
        rodapé_ativo = st.toggle("Exibir Rodapé no Site", value=config.get("rodapé_ativo", True))
        rodape_titulo = st.text_input("Título do Rodapé", value=config.get("rodape_titulo", ""))
        rodape_texto = st.text_area("Texto/Endereço (HTML)", value=config.get("rodape_texto", ""), height=70)
        
        col_wpp, col_insta = st.columns(2)
        with col_wpp:
            rodape_whatsapp_numero = st.text_input("Nº WhatsApp (Ex: 556199999999)", value=config.get("rodape_whatsapp_numero", ""))
            rodape_whatsapp_texto = st.text_input("Texto Botão Wpp", value=config.get("rodape_whatsapp_texto", ""))
        with col_insta:
            rodape_instagram_usuario = st.text_input("Instagram (sem @)", value=config.get("rodape_instagram_usuario", ""))
            rodape_instagram_texto = st.text_input("Texto Botão Insta", value=config.get("rodape_instagram_texto", ""))

with aba2:
    st.subheader("🧩 Suas Seções Atuais")
    st.caption("Edite os textos das seções abaixo ou clique em 'Excluir Seção' para removê-las.")

    novas_secoes = []
    for idx, sec in enumerate(secoes):
        with st.container(border=True):
            col_s1, col_s2, col_s3 = st.columns([2, 1.5, 0.8])
            with col_s1:
                s_titulo = st.text_input(f"Título da Seção #{idx+1}", value=sec.get("titulo", ""), key=f"sec_tit_{idx}")
            with col_s2:
                s_tipo = st.selectbox("Tipo de Conteúdo", ["textos", "catalogo", "adicionais"], index=["textos", "catalogo", "adicionais"].index(sec.get("tipo", "textos")), key=f"sec_tipo_{idx}")
            with col_s3:
                s_ativa = st.toggle("Ativa", value=sec.get("ativa", True), key=f"sec_ativ_{idx}")

            s_subtitulo = sec.get("subtitulo", "")
            s_conteudo = sec.get("conteudo_html", "")
            s_itens = sec.get("itens_lista", [])

            if s_tipo == "textos":
                s_conteudo = st.text_area(f"Texto Principal (HTML)", value=s_conteudo, key=f"sec_cont_{idx}", height=100)
                
                st.write("Tópicos de Lista (Ex: Como Fazer o Pedido)")
                df_temp = pd.DataFrame(s_itens, columns=["Tópico"])
                df_res = st.data_editor(df_temp, num_rows="dynamic", key=f"sec_lista_{idx}", hide_index=True, use_container_width=True)
                s_itens = df_res["Tópico"].tolist()

            elif s_tipo == "catalogo":
                s_subtitulo = st.text_input("Subtítulo do Catálogo", value=s_subtitulo, key=f"sec_sub_{idx}")

            # Botão de exclusão individual da seção
            excluir = st.button("🗑️ Excluir Seção", key=f"del_sec_{idx}", type="secondary")
            
            if not excluir:
                novas_secoes.append({
                    "id": sec.get("id", f"sec_{idx}"),
                    "titulo": s_titulo,
                    "tipo": s_tipo,
                    "ativa": s_ativa,
                    "subtitulo": s_subtitulo,
                    "conteudo_html": s_conteudo,
                    "itens_lista": s_itens
                })

    st.divider()
    st.subheader("➕ Criar Nova Seção")
    with st.form("nova_secao_form"):
        novo_titulo = st.text_input("Título da Nova Seção")
        novo_tipo = st.selectbox("Tipo da Nova Seção", ["textos", "catalogo", "adicionais"])
        adicionar = st.form_submit_button("Criar e Adicionar Seção")
        
        if adicionar and novo_titulo:
            nova = {
                "id": f"sec_nova_{len(secoes)+1}",
                "titulo": novo_titulo,
                "tipo": novo_tipo,
                "ativa": True,
                "conteudo_html": "Escreva seu texto aqui...",
                "subtitulo": "Subtítulo opcional",
                "itens_lista": ["Item 1"]
            }
            secoes.append(nova)
            atualizar_configuracao_vitrine({"secoes": secoes})
            st.success("Nova seção criada com sucesso! Atualize a página.")
            st.rerun()

with aba3:
    st.subheader("🔄 Ordem de Exibição das Seções")
    st.caption("Aqui você define a ordem em que as seções aparecem no site de cima para baixo.")
    
    ids_atuais = [s["id"] for s in secoes]
    nomes_map = {s["id"]: s["titulo"] for s in secoes}
    
    ordem_selecionada = st.multiselect(
        "Selecione as seções na ordem desejada:",
        options=ids_atuais,
        default=ids_atuais,
        format_func=lambda x: nomes_map.get(x, x)
    )

st.divider()

if st.button("💾 Salvar Todas as Alterações", type="primary", use_container_width=True):
    # Reorganiza a lista de seções com base na ordem selecionada na aba 3
    secoes_ordenadas = []
    for sid in ordem_selecionada:
        match = next((s for s in novas_secoes if s["id"] == sid), None)
        if match: secoes_ordenadas.append(match)
    # Adiciona eventuais seções que ficaram fora da multiselect por segurança
    for s in novas_secoes:
        if s not in secoes_ordenadas: secoes_ordenadas.append(s)

    dados = {
        "cabecalho_titulo": cabecalho_titulo,
        "cabecalho_subtitulo": cabecalho_subtitulo,
        "rodapé_ativo": rodapé_ativo,
        "rodape_titulo": rodape_titulo,
        "rodape_texto": rodape_texto,
        "rodape_whatsapp_numero": rodape_whatsapp_numero,
        "rodape_whatsapp_texto": rodape_whatsapp_texto,
        "rodape_instagram_usuario": rodape_instagram_usuario,
        "rodape_instagram_texto": rodape_instagram_texto,
        "secoes": secoes_ordenadas
    }
    
    if atualizar_configuracao_vitrine(dados):
        st.success("✅ CMS atualizado com sucesso!")
        st.rerun()
    else:
        st.error("Erro ao salvar.")
