from config.supabase import supabase


# =====================================================
# LISTAR PRODUTOS DA CESTA
# =====================================================

def listar_produtos_da_cesta(cesta_id):

    resposta = (
        supabase
        .table("cesta_produtos")
        .select("*")
        .eq("cesta_id", cesta_id)
        .execute()
    )

    return resposta.data or []


# =====================================================
# SALVAR PRODUTOS DA CESTA
# =====================================================

def salvar_produtos_da_cesta(
    cesta_id,
    produtos_selecionados
):

    # Remove todos os produtos atuais da cesta

    (
        supabase
        .table("cesta_produtos")
        .delete()
        .eq("cesta_id", cesta_id)
        .execute()
    )

    # Insere novamente os produtos selecionados

    for produto_id in produtos_selecionados:

        (
            supabase
            .table("cesta_produtos")
            .insert({

                "cesta_id": cesta_id,
                "produto_id": produto_id,
                "quantidade": 1

            })
            .execute()
        )
