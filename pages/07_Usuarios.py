import streamlit as st

from services.usuario_service import (
    listar_usuarios,
    salvar_usuario,
    excluir_usuario
)


st.set_page_config(
    page_title="Usuários",
    page_icon="👤",
    layout="wide"
)


# =====================================================
# VERIFICA LOGIN
# =====================================================

if "usuario" not in st.session_state or st.session_state.usuario is None:

    st.error(
        "Acesso não autorizado."
    )

    st.stop()



usuario_logado = st.session_state.usuario



# =====================================================
# PERMISSÃO
# =====================================================

if usuario_logado["perfil"] != "Administrador":

    st.error(
        "Somente Administradores podem acessar este módulo."
    )

    st.stop()



# =====================================================
# CSS
# =====================================================


st.markdown(
"""
<style>

#MainMenu{
display:none;
}

footer{
display:none;
}

header{
display:none;
}


.card{

background:#ffffff;

padding:15px;

border-radius:12px;

border:1px solid #ddd;

margin-bottom:10px;

}


</style>
""",
unsafe_allow_html=True
)



# =====================================================
# TÍTULO
# =====================================================


st.title(
    "👤 Usuários do Sistema"
)


st.write(
    "Gerencie os acessos administrativos da Doce Cesta Brasília."
)


st.divider()



# =====================================================
# CADASTRO
# =====================================================


st.subheader(
    "➕ Novo Usuário"
)



col1, col2 = st.columns(2)



with col1:

    novo_login = st.text_input(
        "Login"
    )



with col2:

    nova_senha = st.text_input(
        "Senha",
        type="password"
    )



perfil = st.selectbox(

    "Perfil",

    [
        "Administrador",
        "Operador"
    ]

)



if st.button(

    "💾 Salvar Usuário",

    use_container_width=True

):


    if not novo_login:

        st.error(
            "Informe o login."
        )

        st.stop()



    if not nova_senha:

        st.error(
            "Informe a senha."
        )

        st.stop()



    try:


        salvar_usuario(

            novo_login,

            nova_senha,

            perfil

        )


        st.success(
            "Usuário cadastrado com sucesso!"
        )


        st.rerun()



    except Exception as erro:


        st.error(
            f"Erro ao cadastrar usuário: {erro}"
        )



st.divider()



# =====================================================
# LISTA USUÁRIOS
# =====================================================


st.subheader(
    "📋 Usuários cadastrados"
)



try:

    usuarios = listar_usuarios()


except Exception as erro:


    st.error(
        f"Erro ao carregar usuários: {erro}"
    )

    st.stop()



if not usuarios:


    st.info(
        "Nenhum usuário cadastrado."
    )

    st.stop()



# =====================================================
# CARDS
# =====================================================


for usuario in usuarios:


    with st.container(border=True):


        col1, col2, col3, col4 = st.columns(
            [3,2,2,1]
        )



        with col1:

            st.write(
                f"**👤 {usuario['login']}**"
            )



        with col2:

            st.write(
                "Perfil"
            )

            st.write(
                usuario["perfil"]
            )



        with col3:

            st.write(
                "Criado em"
            )

            st.write(
                str(
                    usuario.get(
                        "created_at",
                        "-"
                    )
                )[:10]
            )



        with col4:


            if usuario["login"] != usuario_logado["login"]:


                if st.button(

                    "🗑️",

                    key=f"del_{usuario['id']}"

                ):


                    try:


                        excluir_usuario(
                            usuario["id"]
                        )


                        st.success(
                            "Usuário excluído."
                        )


                        st.rerun()



                    except Exception as erro:


                        st.error(
                            f"Erro: {erro}"
                        )


            else:


                st.info(
                    "Atual"
                )



st.divider()



# =====================================================
# VOLTAR
# =====================================================


if st.button(
    "⬅ Voltar ao início",
    use_container_width=True
):

    st.switch_page(
        "pages/99_Admin.py"
    )
