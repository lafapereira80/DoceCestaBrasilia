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

# =====================================================
# LISTAR PRODUTOS DA CATEGORIA
# =====================================================

def listar_produtos_categoria(categoria_nome):

    resposta_categoria = (
        supabase
        .table("categorias")
        .select("id")
        .eq("nome", categoria_nome)
        .single()
        .execute()
    )

    categoria_id = resposta_categoria.data["id"]

    resposta = (
        supabase
        .table("produtos")
        .select("*")
        .eq("categoria_id", categoria_id)
        .eq("ativo", True)
        .order("nome")
        .execute()
    )

    return resposta.data


# =====================================================
# LISTAR PRODUTOS DA CESTA
# =====================================================

def listar_produtos_cesta(cesta_id):

    resposta = (
        supabase
        .table("cesta_produtos")
        .select("*")
        .eq("cesta_id", cesta_id)
        .execute()
    )

    return resposta.data


# =====================================================
# SALVAR CONFIGURAÇÃO
# =====================================================

def salvar_configuracao(

    cesta_id,
    categoria,
    produtos,
    min_escolhas,
    max_escolhas

):

    (
        supabase
        .table("cesta_produtos")
        .delete()
        .eq("cesta_id", cesta_id)
        .eq("categoria", categoria)
        .execute()
    )

    for produto in produtos:

        (
            supabase
            .table("cesta_produtos")
            .insert({

                "cesta_id": cesta_id,

                "produto_id": produto,

                "categoria": categoria,

                "quantidade": 1,

                "min_escolhas": min_escolhas,

                "max_escolhas": max_escolhas,

                "ordem": 0

            })
            .execute()
        )
