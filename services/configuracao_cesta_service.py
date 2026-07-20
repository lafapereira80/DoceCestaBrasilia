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



        # Busca produto
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



        # Busca categoria
        categoria_resp = (
            supabase
            .table("categorias")
            .select("nome")
            .eq(
                "id",
                produto["categoria_id"]
            )
            .single()
            .execute()
        )



        if not categoria_resp.data:

            continue



        categoria_nome = categoria_resp.data["nome"]



        # Cria agrupamento por categoria
        if categoria_nome not in categorias:


            categorias[categoria_nome] = {


                "categoria": categoria_nome,


                # quantidade mínima obrigatória
                "min_escolhas": item.get(
                    "min_escolhas",
                    0
                ),


                # quantidade máxima permitida
                "max_escolhas": item.get(
                    "max_escolhas",
                    1
                ),


                "produtos": []

            }



        categorias[categoria_nome]["produtos"].append(
            produto
        )



    return list(
        categorias.values()
    )



# =====================================================
# SALVAR CONFIGURAÇÃO DA CESTA
# =====================================================

def salvar_configuracao_cesta(
    cesta_id,
    configuracoes
):


    # Remove configuração anterior

    (
        supabase
        .table("cesta_produtos")
        .delete()
        .eq(
            "cesta_id",
            cesta_id
        )
        .execute()
    )



    registros = []



    for grupo in configuracoes:


        categoria_id = grupo["categoria_id"]


        min_escolhas = grupo.get(
            "min_escolhas",
            0
        )


        max_escolhas = grupo.get(
            "max_escolhas",
            1
        )



        for produto_id in grupo["produtos"]:


            registros.append({


                "cesta_id": cesta_id,


                "produto_id": produto_id,


                "min_escolhas": min_escolhas,


                "max_escolhas": max_escolhas


            })



    if registros:


        (
            supabase
            .table("cesta_produtos")
            .insert(registros)
            .execute()
        )
