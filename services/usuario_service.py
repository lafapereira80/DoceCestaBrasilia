from config.supabase import supabase



# =====================================================
# AUTENTICA USUÁRIO
# =====================================================

def autenticar_usuario(
    login,
    senha
):

    try:

        resposta = (

            supabase
            .table("usuarios")
            .select("*")
            .eq(
                "login",
                login
            )
            .eq(
                "senha",
                senha
            )
            .execute()

        )


        if resposta.data:

            return resposta.data[0]


        return None


    except Exception as erro:

        raise Exception(
            f"Erro na autenticação: {erro}"
        )



# =====================================================
# BUSCAR USUÁRIO PELO LOGIN
# =====================================================

def buscar_usuario_por_login(
    login
):

    try:

        resposta = (

            supabase
            .table("usuarios")
            .select("*")
            .eq(
                "login",
                login
            )
            .execute()

        )


        if resposta.data:

            return resposta.data[0]


        return None


    except Exception as erro:

        raise Exception(
            f"Erro ao buscar usuário: {erro}"
        )



# =====================================================
# LISTAR USUÁRIOS
# =====================================================

def listar_usuarios():

    try:

        resposta = (

            supabase
            .table("usuarios")
            .select("*")
            .order(
                "created_at",
                desc=True
            )
            .execute()

        )


        return resposta.data or []


    except Exception as erro:

        raise Exception(
            f"Erro ao listar usuários: {erro}"
        )



# =====================================================
# SALVAR USUÁRIO
# =====================================================

def salvar_usuario(
    login,
    senha,
    perfil
):

    try:

        # verifica se já existe

        usuario_existente = buscar_usuario_por_login(
            login
        )


        if usuario_existente:

            return (
                False,
                "Este login já existe."
            )


        resposta = (

            supabase
            .table("usuarios")
            .insert({

                "login": login,

                "senha": senha,

                "perfil": perfil

            })
            .execute()

        )


        return (

            True,
            resposta.data

        )


    except Exception as erro:


        return (

            False,
            str(erro)

        )



# =====================================================
# ATUALIZAR USUÁRIO
# =====================================================

def atualizar_usuario(
    usuario_id,
    login,
    senha,
    perfil
):

    try:

        resposta = (

            supabase
            .table("usuarios")
            .update({

                "login": login,

                "senha": senha,

                "perfil": perfil

            })
            .eq(
                "id",
                usuario_id
            )
            .execute()

        )


        return (

            True,
            resposta.data

        )


    except Exception as erro:


        return (

            False,
            str(erro)

        )



# =====================================================
# EXCLUIR USUÁRIO
# =====================================================

def excluir_usuario(
    usuario_id
):

    try:

        (

            supabase
            .table("usuarios")
            .delete()
            .eq(
                "id",
                usuario_id
            )
            .execute()

        )


        return (

            True,
            "Usuário excluído com sucesso."

        )


    except Exception as erro:


        return (

            False,
            str(erro)

        )
