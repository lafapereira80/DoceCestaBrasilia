from config.supabase import supabase


# =====================================================
# CARREGA CONFIGURAÇÃO DA CESTA
# =====================================================

def carregar_configuracao_cesta(cesta_id):

    resposta = (
        supabase
        .table("configuracao_cestas")
        .select("""
            categoria,
            quantidade,
            produtos:produto_id(
                id,
                nome,
                preco,
                ativo
            )
        """)
        .eq("cesta_id", cesta_id)
        .order("categoria")
        .execute()
    )

    configuracao = []

    categorias = {}

    for item in resposta.data or []:

        categoria = item["categoria"]

        if categoria not in categorias:

            categorias[categoria] = {
                "categoria": categoria,
                "quantidade": item["quantidade"],
                "produtos": []
            }

        produto = item["produtos"]

        if produto and produto["ativo"]:

            categorias[categoria]["produtos"].append(produto)

    configuracao = list(categorias.values())

    return configuracao
