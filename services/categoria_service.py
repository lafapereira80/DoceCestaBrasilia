from config.supabase import supabase



# =====================================================
# LISTAR TODAS AS CATEGORIAS
# USO ADMINISTRATIVO
# =====================================================

def listar_categorias():


    resposta = (

        supabase

        .table("categorias")

        .select("*")

        .order("ordem")

        .execute()

    )


    return resposta.data or []





# =====================================================
# LISTAR CATEGORIAS ATIVAS
# USO GERAL
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
# LISTAR CATEGORIAS PARA O PEDIDO
# USADO NO APP.PY
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
# BUSCAR CATEGORIA
# =====================================================

def buscar_categoria(categoria_id):


    resposta = (

        supabase

        .table("categorias")

        .select("*")

        .eq(
            "id",
            categoria_id
        )

        .single()

        .execute()

    )


    return resposta.data





# =====================================================
# CADASTRAR CATEGORIA
# =====================================================

def cadastrar_categoria(

    nome,

    possui_preco,

    exibir_no_pedido,

    ativo=True,

    ordem=0

):


    dados = {


        "nome": nome,


        "possui_preco": bool(possui_preco),


        "exibir_no_pedido": bool(exibir_no_pedido),


        "ativo": bool(ativo),


        "ordem": ordem


    }



    resposta = (

        supabase

        .table("categorias")

        .insert(dados)

        .execute()

    )


    return resposta.data





# =====================================================
# ATUALIZAR CATEGORIA
# =====================================================

def atualizar_categoria(

    categoria_id,

    nome,

    possui_preco,

    exibir_no_pedido,

    ativo,

    ordem

):


    dados = {


        "nome": nome,


        "possui_preco": bool(possui_preco),


        "exibir_no_pedido": bool(exibir_no_pedido),


        "ativo": bool(ativo),


        "ordem": ordem


    }



    resposta = (

        supabase

        .table("categorias")

        .update(dados)

        .eq(

            "id",

            categoria_id

        )

        .execute()

    )


    return resposta.data





# =====================================================
# ALTERAR STATUS DA CATEGORIA
# ATIVO / INATIVO
# =====================================================

def alterar_status_categoria(

    categoria_id,

    ativo

):


    dados = {


        "ativo": bool(ativo)

    }



    resposta = (

        supabase

        .table("categorias")

        .update(dados)

        .eq(

            "id",

            categoria_id

        )

        .execute()

    )



    if not resposta.data:


        raise Exception(

            "Nenhuma categoria foi atualizada. Verifique o ID da categoria."

        )



    return resposta.data





# =====================================================
# EXCLUIR CATEGORIA
# =====================================================

def excluir_categoria(categoria_id):


    resposta = (

        supabase

        .table("categorias")

        .delete()

        .eq(

            "id",

            categoria_id

        )

        .execute()

    )


    return resposta.data
