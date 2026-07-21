from config.supabase import supabase



# =====================================================
# LISTAR PRODUTOS
# =====================================================

def listar_produtos():


    resposta = (

        supabase

        .table("produtos")

        .select(
            """
            *,
            categorias(
                id,
                nome
            )
            """
        )

        .order("nome")

        .execute()

    )


    return resposta.data or []




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
# LISTAR PRODUTOS POR CATEGORIA
# =====================================================

def listar_produtos_por_categoria(
    categoria_nome
):


    resposta = (

        supabase

        .table("produtos")

        .select(
            """
            *,
            categorias(
                id,
                nome
            )
            """
        )

        .eq(
            "categorias.nome",
            categoria_nome
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

    preco,

    ativo=True

):


    dados = {


        "categoria_id":

            categoria_id,


        "nome":

            nome,


        "preco":

            preco,


        "ativo":

            ativo


    }



    resposta = (

        supabase

        .table("produtos")

        .insert(dados)

        .execute()

    )


    return resposta.data





# =====================================================
# EXCLUIR PRODUTO
# =====================================================

def excluir_produto(

    produto_id

):


    resposta = (

        supabase

        .table("produtos")

        .delete()

        .eq(

            "id",

            produto_id

        )

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


    dados = {


        "categoria_id":

            categoria_id,


        "nome":

            nome,


        "preco":

            preco,


        "ativo":

            ativo


    }



    resposta = (

        supabase

        .table("produtos")

        .update(dados)

        .eq(

            "id",

            produto_id

        )

        .execute()

    )


    return resposta.data
    
