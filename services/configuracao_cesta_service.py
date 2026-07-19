from config.supabase import supabase


# =====================================================
# CARREGA CONFIGURAÇÃO DA CESTA
# =====================================================

def carregar_configuracao_cesta(cesta_id):

    resposta = (
        supabase
        .table("cesta_produtos")
        .select("""
            quantidade,
            produtos:produto_id(
                id,
                nome,
                categoria_id,
                preco,
                ativo
            )
        """)
        .eq("cesta_id", cesta_id)
        .execute()
    )

    if not resposta.data:
        return []

    categorias = {}

    for item in resposta.data:

        produto = item["produtos"]

        if not produto:
            continue

        categoria_id = produto["categoria_id"]

        categoria = (
            supabase
            .table("categorias")
            .select("nome")
            .eq("id", categoria_id)
            .single()
            .execute()
        )

        nome_categoria = categoria.data["nome"]

        if nome_categoria not in categorias:

            categorias[nome_categoria] = {
                "categoria": nome_categoria,
                "quantidade": item["quantidade"],
                "produtos": []
            }

        categorias[nome_categoria]["produtos"].append(produto)

    return list(categorias.values())
