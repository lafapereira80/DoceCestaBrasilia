from config.supabase import supabase


# =====================================================
# LISTAR CESTAS
# =====================================================

def listar_cestas():

    resposta = (
        supabase
        .table("cestas")
        .select("*")
        .order("nome")
        .execute()
    )

    return resposta.data


# =====================================================
# CADASTRAR CESTA
# =====================================================

def cadastrar_cesta(
    nome,
    descricao,
    preco
):

    resposta = (
        supabase
        .table("cestas")
        .insert({

            "nome": nome,

            "descricao": descricao,

            "preco": preco,

            "ativa": True

        })
        .execute()
    )

    return resposta.data


# =====================================================
# BUSCAR CESTA
# =====================================================

def buscar_cesta(cesta_id):

    resposta = (
        supabase
        .table("cestas")
        .select("*")
        .eq("id", cesta_id)
        .single()
        .execute()
    )

    return resposta.data


# =====================================================
# EXCLUIR CESTA
# =====================================================

def excluir_cesta(cesta_id):

    resposta = (
        supabase
        .table("cestas")
        .delete()
        .eq("id", cesta_id)
        .execute()
    )

    return resposta.data
