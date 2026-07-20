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
# LISTAR PRODUTOS POR CATEGORIA
# USADO NO FORMULÁRIO DO CLIENTE
# =====================================================

def listar_produtos_por_categoria(
    nome_categoria
):


    # Busca categoria

    categoria = (

        supabase
        .table("categorias")
        .select("id")
        .eq(
            "nome",
            nome_categoria
        )
        .single()
        .execute()

    )



    if not categoria.data:

        return []



    categoria_id = categoria.data["id"]



    # Busca produtos ativos da categoria


    resposta = (

        supabase
        .table("produtos")
        .select("*")
        .eq(
            "categoria_id",
            categoria_id
        )
        .eq(
            "ativo",
            True
        )
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

def excluir_produto(
    produto_id
):

    (
        supabase
        .table("produtos")
        .delete()
        .eq(
            "id",
            produto_id
        )
        .execute()
    )



# =====================================================
# ALTERAR STATUS
# =====================================================

def alterar_status(
    produto_id,
    ativo
):

    (
        supabase
        .table("produtos")
        .update({

            "ativo": ativo

        })
        .eq(
            "id",
            produto_id
        )
        .execute()
    )



# =====================================================
# BUSCAR PRODUTO
# =====================================================

def buscar_produto(
    produto_id
):

    resposta = (

        supabase
        .table("produtos")
        .select("*")
        .eq(
            "id",
            produto_id
        )
        .single()
        .execute()

    )

    return resposta.data



# =====================================================
# ATUALIZAR PRODUTO
# =====================================================

def atualizar_produto(
    produto_id,
    categoria_id,
    nome,
    preco,
    ativo
):

    (
        supabase
        .table("produtos")
        .update({

            "categoria_id": categoria_id,
            "nome": nome,
            "preco": preco,
            "ativo": ativo

        })
        .eq(
            "id",
            produto_id
        )
        .execute()
    )
