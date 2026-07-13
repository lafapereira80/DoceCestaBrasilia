import streamlit as st

st.set_page_config(
    page_title="Área Administrativa",
    page_icon="🔒",
    layout="wide"
)

# Proteção provisória
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    st.title("🔒 Área Administrativa")

    st.write("Faça login para acessar o sistema.")

    usuario = st.text_input("Usuário")

    senha = st.text_input("Senha", type="password")

    entrar = st.button("Entrar", use_container_width=True)

    if entrar:

        # Login temporário
        if usuario == "admin" and senha == "123456":

            st.session_state.logado = True

            st.rerun()

        else:

            st.error("Usuário ou senha inválidos.")

else:

    st.success("Bem-vindo ao painel administrativo!")

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Pedidos", "0")

    col2.metric("Clientes", "0")

    col3.metric("Faturamento", "R$ 0,00")

    col4.metric("Cestas", "0")

    st.divider()

    st.info("Nas próximas etapas construiremos os módulos administrativos.")
