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
                nome,
                possui_preco
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
# LISTAR CATEGORIAS ATIVAS
# =====================================================

def listar_categorias_ativas():


    resposta = (

        supabase

        .table("categorias")

        .select("*")

        .eq(
            "ativo",
            True
        )

        .order("ordem")

        .execute()

    )


    return resposta.data or []





# =====================================================
# LISTAR CATEGORIAS EXIBIDAS NO PEDIDO
# =====================================================

def listar_categorias_pedido():


    resposta = (

        supabase

        .table("categorias")

        .select("*")

        .eq(
            "ativo",
            True
        )

        .eq(
            "exibir_no_pedido",
            True
        )

        .order("ordem")

        .execute()

    )


    return resposta.data or []





# =====================================================
# LISTAR PRODUTOS POR NOME DA CATEGORIA
# (mantido para compatibilidade)
# =====================================================

def listar_produtos_por_categoria(
    categoria_nome
):


    categoria = (

        supabase

        .table("categorias")

        .select(
            """
            id
            """
        )

        .eq(
            "nome",
            categoria_nome
        )

        .single()

        .execute()

    )


    if not categoria.data:

        return []



    return listar_produtos_por_categoria_id(

        categoria.data["id"]

    )





# =====================================================
# LISTAR PRODUTOS POR ID DA CATEGORIA
# =====================================================

def listar_produtos_por_categoria_id(
    categoria_id
):


    resposta = (

        supabase

        .table("produtos")

        .select(
            """
            *,
            categorias(
                id,
                nome,
                possui_preco
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
                nome,
                possui_preco
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

        .select(
            """
            *,
            categorias(
                id,
                nome,
                possui_preco
            )
            """
        )

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
# BUSCAR CATEGORIA DO PRODUTO
# =====================================================

def buscar_categoria_produto(
    categoria_id
):


    resposta = (

        supabase

        .table("categorias")

        .select(
            """
            id,
            nome,
            possui_preco
            """
        )

        .eq(
            "id",
            categoria_id
        )

        .single()

        .execute()

    )


    return resposta.data





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


    categoria = buscar_categoria_produto(

        categoria_id

    )



    if not categoria:


        raise Exception(

            "Categoria não encontrada."

        )





    # =================================================
    # REGRA DE PREÇO BASEADA NA CATEGORIA
    # =================================================

    if not categoria.get(

        "possui_preco",

        False

    ):


        preco = None


        tipo_preco = "Incluso na cesta"





    dados = {


        "categoria_id": categoria_id,


        "nome": nome,


        "descricao": descricao,


        "preco": preco,


        "ativo": ativo,


        "tipo_preco": tipo_preco


    }





    resposta = (

        supabase

        .table("produtos")

        .insert(dados)

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


    categoria = buscar_categoria_produto(

        categoria_id

    )



    if not categoria:


        raise Exception(

            "Categoria não encontrada."

        )





    # =================================================
    # REGRA DE PREÇO BASEADA NA CATEGORIA
    # =================================================

    if not categoria.get(

        "possui_preco",

        False

    ):


        preco = None


        tipo_preco = "Incluso na cesta"





    dados = {


        "categoria_id": categoria_id,


        "nome": nome,


        "descricao": descricao,


        "preco": preco,


        "ativo": ativo,


        "tipo_preco": tipo_preco


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





# =====================================================
# ALTERAR STATUS DO PRODUTO
# =====================================================

def alterar_status_produto(

    produto_id,

    ativo

):


    resposta = (

        supabase

        .table("produtos")

        .update(

            {

                "ativo": ativo

            }

        )

        .eq(

            "id",

            produto_id

        )

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
# VALIDAR SE CATEGORIA POSSUI PREÇO
# =====================================================

def categoria_possui_preco(

    categoria_id

):


    categoria = buscar_categoria_produto(

        categoria_id

    )


    if not categoria:


        return False



    return categoria.get(

        "possui_preco",

        False

    )





# =====================================================
# LISTAR PRODUTOS ATIVOS
# =====================================================

def listar_produtos_ativos():


    resposta = (

        supabase

        .table("produtos")

        .select(
            """
            *,
            categorias(
                id,
                nome,
                possui_preco
            )
            """
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
# LISTAR PRODUTOS POR CATEGORIA PARA ADMIN
# =====================================================

def listar_produtos_categoria_admin(

    categoria_id

):


    resposta = (

        supabase

        .table("produtos")

        .select(
            """
            *,
            categorias(
                id,
                nome,
                possui_preco
            )
            """
        )

        .eq(

            "categoria_id",

            categoria_id

        )

        .order("nome")

        .execute()

    )


    return resposta.data or []

# =====================================================
# VERIFICAR SE PRODUTO ESTÁ SENDO USADO EM CESTAS
# =====================================================

def verificar_uso_produto(
    produto_id
):


    resposta = (

        supabase

        .table("cesta_produtos")

        .select(

            "id"

        )

        .eq(

            "produto_id",

            produto_id

        )

        .limit(1)

        .execute()

    )


    return bool(

        resposta.data

    )





# =====================================================
# DESATIVAR PRODUTO
# =====================================================

def desativar_produto(

    produto_id

):


    resposta = (

        supabase

        .table("produtos")

        .update(

            {

                "ativo": False

            }

        )

        .eq(

            "id",

            produto_id

        )

        .execute()

    )


    return resposta.data





# =====================================================
# EXCLUIR PRODUTO COM SEGURANÇA
# =====================================================

def excluir_produto(

    produto_id

):


    usado = verificar_uso_produto(

        produto_id

    )


    if usado:


        raise Exception(

            "Este produto está vinculado a uma ou mais cestas. "

            "Utilize a opção de desativar o produto."

        )




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
