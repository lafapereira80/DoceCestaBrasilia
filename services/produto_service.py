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
# LISTAR CATEGORIAS DO PEDIDO
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
# LISTAR PRODUTOS POR CATEGORIA
# =====================================================

def listar_produtos_por_categoria(
    categoria_nome
):

    categoria = (
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


    if not categoria.data:

        return []


    return listar_produtos_por_categoria_id(
        categoria.data["id"]
    )





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

def buscar_produto(
    produto_id
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
            "id",
            produto_id
        )
        .single()
        .execute()
    )

    return resposta.data





# =====================================================
# BUSCAR CATEGORIA
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



    if not categoria.get(
        "possui_preco",
        False
    ):

        preco = None
        tipo_preco = "Incluso na cesta"



    resposta = (
        supabase
        .table("produtos")
        .update({

            "categoria_id": categoria_id,
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "ativo": ativo,
            "tipo_preco": tipo_preco

        })
        .eq(
            "id",
            produto_id
        )
        .execute()
    )


    return resposta.data





# =====================================================
# STATUS PRODUTO
# =====================================================

def alterar_status_produto(
    produto_id,
    ativo
):

    resposta = (
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


    return resposta.data





def desativar_produto(
    produto_id
):

    return alterar_status_produto(
        produto_id,
        False
    )





# =====================================================
# VERIFICA USO EM CESTAS
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
# EXCLUIR PRODUTO COM SEGURANÇA
# =====================================================

def excluir_produto(
    produto_id
):

    try:


        # ---------------------------------------------
        # REMOVE VÍNCULOS COM CESTAS
        # ---------------------------------------------

        vinculos = (
            supabase
            .table("cesta_produtos")
            .delete()
            .eq(
                "produto_id",
                produto_id
            )
            .execute()
        )



        # ---------------------------------------------
        # REMOVE PRODUTO
        # ---------------------------------------------

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



    except Exception as erro:


        raise Exception(

            "Não foi possível excluir o produto. "
            "Verifique se existem vínculos ou permissões no Supabase.\n\n"
            f"Detalhes: {erro}"

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
# LISTAR PRODUTOS PARA ADMIN
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
# VALIDAR PREÇO DA CATEGORIA
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
           
