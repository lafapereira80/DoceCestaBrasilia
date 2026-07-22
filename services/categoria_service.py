from config.supabase import supabase



# =====================================================
# LISTAR TODAS AS CATEGORIAS
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
# LISTAR SOMENTE CATEGORIAS ATIVAS
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
# BUSCAR CATEGORIA POR ID
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

    descricao,

    icone,

    possui_preco,

    exibir_pedido,

    ativo=True

):


    dados = {


        "nome": nome,


        "descricao": descricao,


        "icone": icone,


        "possui_preco": possui_preco,


        "exibir_pedido": exibir_pedido,


        "ativo": ativo


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

    descricao,

    icone,

    possui_preco,

    exibir_pedido,

    ativo

):


    dados = {


        "nome": nome,


        "descricao": descricao,


        "icone": icone,


        "possui_preco": possui_preco,


        "exibir_pedido": exibir_pedido,


        "ativo": ativo


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
# ALTERAR STATUS
# =====================================================

def alterar_status_categoria(

    categoria_id,

    ativo

):


    resposta = (

        supabase

        .table("categorias")

        .update(

            {

                "ativo": ativo

            }

        )

        .eq(

            "id",

            categoria_id

        )

        .execute()

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
