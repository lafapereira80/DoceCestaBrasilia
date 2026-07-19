from config.supabase import supabase


# =====================================================
# CARREGA CONFIGURAÇÃO DA CESTA
# =====================================================

def carregar_configuracao_cesta(cesta_id):

    # Busca produtos vinculados à cesta
    resposta = (
        supabase
        .table("cesta_produtos")
        .select("*")
        .eq("cesta_id", cesta_id)
        .execute()
    )

    if not resposta.data:

        return []

    categorias = {}

    for item in resposta.data:

        produto_id = item["produto_id"]

        # Busca o produto
        produto_resp = (
            supabase
            .table("produtos")
            .select("*")
            .eq("id", produto_id)
            .single()
            .execute()
        )

        produto = produto_resp.data

        if not produto:

            continue

        # Busca categoria do produto
        categoria_resp = (
            supabase
            .table("categorias")
            .select("nome")
            .eq("id", produto["categoria_id"])
            .single()
            .execute()
        )

        categoria_nome = categoria_resp.data["nome"]


        if categoria_nome not in categorias:

            categorias[categoria_nome] = {

                "categoria": categoria_nome,

                "quantidade": item.get(
                    "quantidade",
                    1
                ),

                "produtos": []

            }


        categorias[categoria_nome]["produtos"].append(produto)


    return list(categorias.values())
