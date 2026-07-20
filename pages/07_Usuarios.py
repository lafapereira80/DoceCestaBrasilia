import streamlit as st

from services.usuario_service import (
    listar_usuarios,
    salvar_usuario,
    excluir_usuario,
    atualizar_usuario
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
# NOVO USUÁRIO
# =====================================================

st.subheader(
    "➕ Novo Usuário"
)


col1, col2 = st.columns(2)


with col1:

    novo_login = st.text_input(
        "Login",
        key="novo_login"
    )


with col2:

    nova_senha = st.text_input(
        "Senha",
        type="password",
        key="nova_senha"
    )


novo_perfil = st.selectbox(

    "Perfil",

    [
        "Administrador",
        "Operador"
    ],

    key="novo_perfil"

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

            novo_perfil

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
# LISTAGEM
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
# USUÁRIOS
# =====================================================


for usuario in usuarios:


    with st.container(border=True):


        st.markdown(
            f"### 👤 {usuario['login']}"
        )


        col1, col2, col3 = st.columns(3)



        with col1:

            st.write(
                "**Perfil:**"
            )

            st.write(
                usuario["perfil"]
            )



        with col2:

            st.write(
                "**Criado em:**"
            )

            st.write(
                str(
                    usuario.get(
                        "created_at",
                        "-"
                    )
                )[:10]
            )



        with col3:

            if usuario["login"] == usuario_logado["login"]:

                st.info(
                    "Usuário atual"
                )

            else:

                st.warning(
                    "Gerenciar"
                )



        # =================================================
        # EDITAR
        # =================================================


        with st.expander(
            "✏️ Editar usuário"
        ):


            editar_login = st.text_input(

                "Login",

                value=usuario["login"],

                key=f"login_{usuario['id']}"

            )



            editar_senha = st.text_input(

                "Nova senha (opcional)",

                type="password",

                key=f"senha_{usuario['id']}"

            )



            editar_perfil = st.selectbox(

                "Perfil",

                [
                    "Administrador",
                    "Operador"
                ],

                index=
                0
                if usuario["perfil"] == "Administrador"
                else 1,

                key=f"perfil_{usuario['id']}"

            )



            if st.button(

                "💾 Atualizar",

                key=f"update_{usuario['id']}",

                use_container_width=True

            ):


                try:


                    atualizar_usuario(

                        usuario["id"],

                        editar_login,

                        editar_senha,

                        editar_perfil

                    )


                    st.success(
                        "Usuário atualizado!"
                    )


                    st.rerun()



                except Exception as erro:


                    st.error(
                        f"Erro ao atualizar: {erro}"
                    )



        # =================================================
        # EXCLUIR
        # =================================================


        if usuario["login"] != usuario_logado["login"]:


            if st.button(

                "🗑️ Excluir usuário",

                key=f"delete_{usuario['id']}",

                use_container_width=True

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
                        f"Erro ao excluir: {erro}"
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
