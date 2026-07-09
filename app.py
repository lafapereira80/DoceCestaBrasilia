import streamlit as st

# ======================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================

st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================
# CORES
# ======================================

verde = "#9BC58A"
marrom = "#B86A34"
fundo = "#FAF8F5"

# ======================================
# CSS
# ======================================

st.markdown(f"""
<style>

.stApp{{
    background:{fundo};
}}

h1,h2,h3{{
    color:{marrom};
    text-align:center;
}}

p{{
    text-align:center;
    font-size:18px;
}}

.botao{{
    background:{marrom};
    color:white;
    padding:15px;
    border-radius:12px;
    text-align:center;
    font-size:22px;
    font-weight:bold;
}}

.card{{
    background:white;
    border-radius:15px;
    padding:25px;
    box-shadow:0px 4px 12px rgba(0,0,0,.10);
}}

</style>
""", unsafe_allow_html=True)

# ======================================
# LOGO
# ======================================

st.image("assets/logo.webp", width=260)

# ======================================
# TÍTULO
# ======================================

st.title("Doce Cesta Brasília")

st.subheader("Cestas personalizadas para momentos especiais ❤️")

st.write("")

# ======================================
# APRESENTAÇÃO
# ======================================

st.markdown("""
### Bem-vindo!

Escolha sua cesta personalizada e monte um presente inesquecível.

Nossa equipe entrará em contato após o envio do pedido para informar:

- 🚚 Valor do frete

- 💰 Valor final da cesta

- 📅 Confirmação da entrega
""")

st.write("")

# ======================================
# COMO FUNCIONA
# ======================================

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.success("🎁\n\nEscolha sua cesta")

with col2:
    st.success("🍞\n\nPersonalize")

with col3:
    st.success("📷\n\nEnvie suas fotos")

with col4:
    st.success("🚚\n\nReceba em casa")

st.write("")

st.info("O formulário completo estará disponível na próxima atualização do sistema.")

st.button("🛒 FAZER PEDIDO")

st.write("")

st.caption("© Doce Cesta Brasília")
