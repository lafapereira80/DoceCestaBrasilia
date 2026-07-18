from config.supabase import supabase


# =====================================================
# LISTAR CATEGORIAS
# =====================================================

def listar_categorias():

    resposta = (
        supabase
        .table("categorias")
        .select("*")
        .order("nome")
        .execute()
    )

    return resposta.data or []


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

    return resposta.data or []


# =====================================================
# CADASTRAR PRODUTO
# =====================================================

def cadastrar_produto(
    categoria_id,
    nome,
    preco
):

    supabase.table("produtos").insert({

        "categoria_id": categoria_id,
        "nome": nome,
        "preco": preco,
        "ativo": True

    }).execute()


# =====================================================
# EXCLUIR PRODUTO
# =====================================================

def excluir_produto(produto_id):

    supabase.table("produtos")\
        .delete()\
        .eq("id", produto_id)\
        .execute()


# =====================================================
# ALTERAR STATUS
# =====================================================

def alterar_status(
    produto_id,
    ativo
):

    supabase.table("produtos").update({

        "ativo": ativo

    }).eq(
        "id",
        produto_id
    ).execute()
