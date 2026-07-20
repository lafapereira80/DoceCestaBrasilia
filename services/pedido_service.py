from config.supabase import supabase



# =====================================================
# SALVAR PEDIDO
# =====================================================

def salvar_pedido(dados):

    try:

        resposta = (
            supabase
            .table("pedidos")
            .insert(dados)
            .execute()
        )


        pedido_id = resposta.data[0]["id"]

        return True, pedido_id


    except Exception as erro:

        return False, str(erro)



# =====================================================
# LISTAR TODOS OS PEDIDOS
# =====================================================

def listar_pedidos():

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )


    return resposta.data or []



# =====================================================
# BUSCAR PEDIDO PELO ID
# =====================================================

def buscar_pedido(pedido_id):

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq(
            "id",
            pedido_id
        )
        .single()
        .execute()
    )


    return resposta.data



# =====================================================
# ATUALIZAR PEDIDO
# =====================================================

def atualizar_pedido(
    pedido_id,
    status,
    valor_frete,
    valor_total
):

    resposta = (
        supabase
        .table("pedidos")
        .update({

            "status": status,

            "valor_frete": valor_frete,

            "valor_total": valor_total

        })
        .eq(
            "id",
            pedido_id
        )
        .execute()
    )


    return resposta.data



# =====================================================
# EXCLUIR PEDIDO COMPLETO
# Remove:
# 1 - Fotos do Storage
# 2 - Registros pedido_fotos
# 3 - Pedido
# =====================================================

def excluir_pedido_completo(pedido_id):

    try:


        # ---------------------------------------------
        # Busca fotos vinculadas
        # ---------------------------------------------

        fotos = (
            supabase
            .table("pedido_fotos")
            .select("*")
            .eq(
                "pedido_id",
                pedido_id
            )
            .execute()
        )


        # ---------------------------------------------
        # Remove arquivos do Storage
        # ---------------------------------------------

        if fotos.data:

            arquivos = []


            for foto in fotos.data:

                caminho = foto.get(
                    "arquivo"
                )


                if caminho:

                    arquivos.append(
                        caminho
                    )


            if arquivos:

                (
                    supabase
                    .storage
                    .from_(
                        "pedido_fotos"
                    )
                    .remove(
                        arquivos
                    )
                )



        # ---------------------------------------------
        # Remove registros da tabela pedido_fotos
        # ---------------------------------------------

        (
            supabase
            .table("pedido_fotos")
            .delete()
            .eq(
                "pedido_id",
                pedido_id
            )
            .execute()
        )



        # ---------------------------------------------
        # Remove pedido principal
        # ---------------------------------------------

        (
            supabase
            .table("pedidos")
            .delete()
            .eq(
                "id",
                pedido_id
            )
            .execute()
        )


        return True, "Pedido excluído com sucesso"



    except Exception as erro:


        return False, str(erro)
