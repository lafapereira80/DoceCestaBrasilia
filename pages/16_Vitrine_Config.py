import streamlit as st
import pandas as pd
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

st.title("🖥️ Editor da Vitrine (CMS)")
st.caption("Altere títulos, textos, links e a ordem de exibição do site público.")
st.divider()

config = obter_configuracao_vitrine()

aba1, aba2, aba3, aba4 = st.tabs(["1. Cabeçalho e Textos", "2. Catálogo e Adicionais", "3. Rodapé (Fale Conosco)", "4. Layout e Visibilidade"])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        cabecalho_titulo = st.text_input("Título do Cabeçalho", value=config.get("cabecalho_titulo", ""))
        cabecalho_subtitulo = st.text_input("Subtítulo do Cabeçalho", value=config.get("cabecalho_subtitulo", ""))
        st.divider()
        boas_vindas_titulo = st.text_input("Título de Boas-Vindas", value=config.get("boas_vindas_titulo", ""))
        boas_vindas_texto = st.text_area("Texto de Boas-Vindas (HTML ativado)", value=config.get("boas_vindas_texto", ""), height=150)
    
    with col2:
        como_pedir_titulo = st.text_input("Título das Regras", value=config.get("como_pedir_titulo", ""))
        st.write("**Tópicos: Como Fazer o Pedido**")
        itens_atuais = config.get("como_pedir_itens", [])
        if isinstance(itens_atuais, str):
            import json
            try: itens_atuais = json.loads(itens_atuais)
            except: itens_atuais = []
        df_itens = pd.DataFrame(itens_atuais, columns=["Regras do Pedido"])
        df_editado = st.data_editor(df_itens, num_rows="dynamic", use_container_width=True, hide_index=True, height=220)

with aba2:
    catalogo_titulo = st.text_input("Título da área de Cestas", value=config.get("catalogo_titulo", ""))
    catalogo_subtitulo = st.text_input("Subtítulo da área de Cestas", value=config.get("catalogo_subtitulo", ""))
    st.divider()
    adicionais_titulo = st.text_input("Título da área de Adicionais", value=config.get("adicionais_titulo", ""))

with aba3:
    rodape_titulo = st.text_input("Título do Rodapé", value=config.get("rodape_titulo", ""))
    rodape_texto = st.text_area("Texto do Rodapé (aceita HTML)", value=config.get("rodape_texto", ""), height=80)
    col_wpp, col_insta = st.columns(2)
    with col_wpp:
        rodape_whatsapp_numero = st.text_input("Número do WhatsApp (Ex: 556199999999)", value=config.get("rodape_whatsapp_numero", ""))
        rodape_whatsapp_texto = st.text_input("Texto do Botão WhatsApp", value=config.get("rodape_whatsapp_texto", ""))
    with col_insta:
        rodape_instagram_usuario = st.text_input("Usuário do Instagram (sem o @)", value=config.get("rodape_instagram_usuario", ""))
        rodape_instagram_texto = st.text_input("Texto do Botão Instagram", value=config.get("rodape_instagram_texto", ""))

with aba4:
    col_vis, col_ord = st.columns(2)
    with col_vis:
        st.subheader("👁️ Visibilidade")
        mostrar_textos = st.toggle("Exibir Textos (Boas-Vindas e Como Pedir)", value=config.get("mostrar_textos", True))
        mostrar_catalogo = st.toggle("Exibir Catálogo de Cestas", value=config.get("mostrar_catalogo", True))
        mostrar_adicionais = st.toggle("Exibir Área de Adicionais", value=config.get("mostrar_adicionais", True))
        mostrar_rodape = st.toggle("Exibir Rodapé (Fale Conosco)", value=config.get("mostrar_rodape", True))

    with col_ord:
        st.subheader("🧩 Ordem de Exibição")
        layout_atual = config.get("ordem_layout", ["textos", "catalogo", "adicionais"])
        if isinstance(layout_atual, str):
            import json
            layout_atual = json.loads(layout_atual)
        opcoes_layout = ["textos", "catalogo", "adicionais"]
        nova_ordem = st.multiselect("Organize os blocos (de cima para baixo):", opcoes_layout, default=layout_atual)

st.divider()

if st.button("💾 Salvar Configurações da Vitrine", type="primary", use_container_width=True):
    nova_lista_itens = [str(item).strip() for item in df_editado["Regras do Pedido"].tolist() if str(item).strip()]

    dados = {
        "cabecalho_titulo": cabecalho_titulo,
        "cabecalho_subtitulo": cabecalho_subtitulo,
        "boas_vindas_titulo": boas_vindas_titulo,
        "boas_vindas_texto": boas_vindas_texto,
        "como_pedir_titulo": como_pedir_titulo,
        "como_pedir_itens": nova_lista_itens,
        "catalogo_titulo": catalogo_titulo,
        "catalogo_subtitulo": catalogo_subtitulo,
        "adicionais_titulo": adicionais_titulo,
        "rodape_titulo": rodape_titulo,
        "rodape_texto": rodape_texto,
        "rodape_whatsapp_numero": rodape_whatsapp_numero,
        "rodape_whatsapp_texto": rodape_whatsapp_texto,
        "rodape_instagram_usuario": rodape_instagram_usuario,
        "rodape_instagram_texto": rodape_instagram_texto,
        "ordem_layout": nova_ordem,
        "mostrar_textos": mostrar_textos,
        "mostrar_catalogo": mostrar_catalogo,
        "mostrar_adicionais": mostrar_adicionais,
        "mostrar_rodape": mostrar_rodape
    }
    
    if atualizar_configuracao_vitrine(dados):
        st.success("✅ Vitrine atualizada com sucesso! Acesse o site para ver as mudanças.")
    else:
        st.error("Erro ao salvar configurações.")
