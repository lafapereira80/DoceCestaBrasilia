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


    categoria_resposta = (

        supabase

        .table("categorias")

        .select("id")

        .eq(
            "nome",
            categoria_nome
        )

        .single()

        .execute()

    )


    if not categoria_resposta.data:

        return []


    categoria_id = categoria_resposta.data["id"]



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
# BUSCAR PRODUTO
# =====================================================

def buscar_produto(produto_id):


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
            "id",
            produto_id
        )

        .single()

        .execute()

    )


    return resposta.data





# =====================================================
# PRODUTOS SOB CONSULTA
# =====================================================

def listar_produtos_sob_consulta():


    resposta = (

        supabase

        .table("produtos")

        .select("*")

        .eq(
            "tipo_preco",
            "Preço sob consulta"
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

    descricao,

    preco,

    ativo=True,

    tipo_preco="Incluso na cesta"

):


    # verifica categoria

    categoria = (

        supabase

        .table("categorias")

        .select("nome")

        .eq(
            "id",
            categoria_id
        )

        .single()

        .execute()

    )


    nome_categoria = (

        categoria.data["nome"]

        .strip()

        .lower()

    )



    # Regra:
    # somente adicionais possuem preço

    if nome_categoria != "adicionais":

        preco = None

        tipo_preco = "Incluso na cesta"



    dados = {


        "categoria_id":

            categoria_id,


        "nome":

            nome,


        "descricao":

            descricao,


        "preco":

            preco,


        "ativo":

            ativo,


        "tipo_preco":

            tipo_preco

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

def excluir_produto(produto_id):


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

    descricao,

    preco,

    ativo,

    tipo_preco="Incluso na cesta"

):


    categoria = (

        supabase

        .table("categorias")

        .select("nome")

        .eq(
            "id",
            categoria_id
        )

        .single()

        .execute()

    )


    nome_categoria = (

        categoria.data["nome"]

        .strip()

        .lower()

    )



    # Regra:
    # somente adicionais possuem valor

    if nome_categoria != "adicionais":

        preco = None

        tipo_preco = "Incluso na cesta"



    dados = {


        "categoria_id":

            categoria_id,


        "nome":

            nome,


        "descricao":

            descricao,


        "preco":

            preco,


        "ativo":

            ativo,


        "tipo_preco":

            tipo_preco

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
