from config.supabase import supabase


# =====================================================
# BUSCAR CONFIGURAÇÕES DA CESTA
# =====================================================

def buscar_configuracoes_da_cesta(cesta_id):

    resposta = (
        supabase
        .table("configuracao_cestas")
        .select("*")
        .eq("cesta_id", cesta_id)
        .execute()
    )

    return resposta.data or []


# =====================================================
# SALVAR CONFIGURAÇÕES
# =====================================================

def salvar_configuracoes(
    cesta_id,
    configuracoes
):

    # Remove todas as configurações atuais

    (
        supabase
        .table("configuracao_cestas")
        .delete()
        .eq("cesta_id", cesta_id)
        .execute()
    )

    # Insere novamente

    for categoria, quantidade in configuracoes.items():

        (
            supabase
            .table("configuracao_cestas")
            .insert({

                "cesta_id": cesta_id,

                "categoria": categoria,

                "quantidade": quantidade

            })
            .execute()
        )
