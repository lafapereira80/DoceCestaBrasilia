from config.supabase import supabase



# =====================================================
# AUTENTICA USUÁRIO
# =====================================================

def autenticar_usuario(
    login,
    senha
):

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




# =====================================================
# LISTAR USUÁRIOS
# =====================================================

def listar_usuarios():

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




# =====================================================
# SALVAR USUÁRIO
# =====================================================

def salvar_usuario(
    login,
    senha,
    perfil
):

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


    return resposta.data




# =====================================================
# EXCLUIR USUÁRIO
# =====================================================

def excluir_usuario(
    usuario_id
):

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
