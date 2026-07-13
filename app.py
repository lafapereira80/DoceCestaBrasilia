import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Esconde completamente a navegação e o menu do Streamlit
st.markdown("""
<style>

/* Esconde a barra lateral */
section[data-testid="stSidebar"]{
    display:none;
}

/* Esconde o botão que abre a barra lateral */
button[kind="header"]{
    display:none;
}

/* Esconde menu superior */
#MainMenu{
    visibility:hidden;
}

/* Esconde rodapé do Streamlit */
footer{
    visibility:hidden;
}

/* Esconde cabeçalho */
header{
    visibility:hidden;
}

/* Centraliza conteúdo */
.block-container{
    max-width:850px;
    padding-top:1rem;
    padding-bottom:3rem;
}

.logo{
    display:block;
    margin-left:auto;
    margin-right:auto;
    margin-bottom:20px;
}

.titulo{
    text-align:center;
    color:#8B5A2B;
    font-size:42px;
    font-weight:bold;
}

.subtitulo{
    text-align:center;
    color:#666;
    font-size:18px;
    margin-bottom:25px;
}

.rodape{
    text-align:center;
    margin-top:60px;
    color:#888;
    font-size:14px;
}

a{
    text-decoration:none;
}

</style>
""", unsafe_allow_html=True)

# Logo
logo = Path("assets/logo.webp")

if logo.exists():
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image(str(logo), use_container_width=True)

st.markdown("<div class='titulo'>Doce Cesta Brasília</div>", unsafe_allow_html=True)

st.markdown("<div class='subtitulo'>Cestas personalizadas para momentos especiais 💝</div>", unsafe_allow_html=True)

st.info(
"""
Esta página será o formulário oficial de pedidos.

Na próxima etapa iremos mover todo o formulário para esta página.
"""
)

st.divider()

st.markdown("""
<div class="rodape">

© Doce Cesta Brasília

<br><br>

<a href="/Admin" target="_self">

🔒 Área Administrativa

</a>

</div>
""", unsafe_allow_html=True)
