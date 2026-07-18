from config.supabase import supabase


# =====================================================
# LISTAR PRODUTOS
# =====================================================

def listar_produtos():

    resposta = (
        supabase
        .table("produtos")
        .select("*")
        .order("nome")
        .execute()
    )

    return resposta.data


# =====================================================
# LISTAR POR CATEGORIA
# =====================================================

def listar_produtos_categoria(categoria_id):

    resposta = (
        supabase
        .table("produtos")
        .select("*")
        .eq("categoria_id", categoria_id)
        .order("nome")
        .execute()
    )

    return resposta.data


# =====================================================
# CADASTRAR
# =====================================================

def cadastrar_produto(

    categoria_id,
    nome,
    preco

):

    resposta = (
        supabase
        .table("produtos")
        .insert({

            "categoria_id": categoria_id,

            "nome": nome,

            "preco": preco,

            "ativo": True

        })
        .execute()
    )

    return resposta.data


# =====================================================
# ATUALIZAR
# =====================================================

def atualizar_produto(

    produto_id,
    categoria_id,
    nome,
    preco,
    ativo

):

    resposta = (
        supabase
        .table("produtos")
        .update({

            "categoria_id": categoria_id,

            "nome": nome,

            "preco": preco,

            "ativo": ativo

        })
        .eq("id", produto_id)
        .execute()
    )

    return resposta.data


# =====================================================
# EXCLUIR
# =====================================================

def excluir_produto(produto_id):

    resposta = (
        supabase
        .table("produtos")
        .delete()
        .eq("id", produto_id)
        .execute()
    )

    return resposta.data
