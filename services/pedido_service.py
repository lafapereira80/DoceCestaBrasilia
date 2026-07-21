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
# LISTAR PEDIDOS ATIVOS
#
# Não retorna Entregues
# =====================================================

def listar_pedidos_ativos():


    resposta = (

        supabase

        .table("pedidos")

        .select("*")

        .neq(

            "status",

            "Entregue"

        )

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
# BUSCAR PREÇO DA CESTA
#
# Usa tabela cestas
# Campo: preco
# =====================================================

def buscar_preco_cesta(cesta_id):


    if not cesta_id:


        return 0



    resposta = (

        supabase

        .table("cestas")

        .select(

            "preco"

        )

        .eq(

            "id",

            cesta_id

        )

        .single()

        .execute()

    )



    if not resposta.data:


        return 0



    return float(

        resposta.data.get(

            "preco",

            0

        )

        or 0

    )





# =====================================================
# ATUALIZAR PEDIDO
#
# Atualiza:
# - Status
# - Frete
# - Valor total
# - Desconto
# =====================================================

def atualizar_pedido(

    pedido_id,

    status,

    valor_frete,

    valor_total,

    desconto=0

):


    resposta = (

        supabase

        .table("pedidos")

        .update({

            "status":

                status,


            "valor_frete":

                valor_frete,


            "valor_total":

                valor_total,


            "desconto":

                desconto

        })

        .eq(

            "id",

            pedido_id

        )

        .execute()

    )


    return resposta.data





# =====================================================
# ATUALIZAR ANOTAÇÃO INTERNA
#
# Uso administrativo
# =====================================================

def atualizar_anotacao_pedido(

    pedido_id,

    anotacao

):


    resposta = (

        supabase

        .table("pedidos")

        .update({

            "anotacoes_internas":

                anotacao

        })

        .eq(

            "id",

            pedido_id

        )

        .execute()

    )


    return resposta.data





# =====================================================
# ATUALIZAR ITENS SOB CONSULTA
#
# Salva valores informados pelo administrador
# =====================================================

def atualizar_itens_consulta(

    pedido_id,

    itens

):


    resposta = (

        supabase

        .table("pedidos")

        .update({

            "itens_consulta":

                itens

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
#
# Remove:
# 1 - Fotos Storage
# 2 - Registros pedido_fotos
# 3 - Pedido
# =====================================================

def excluir_pedido_completo(pedido_id):

    try:


        fotos = (

            supabase

            .table("pedido_fotos")

            .select("arquivo")

            .eq(

                "pedido_id",

                pedido_id

            )

            .execute()

        )



        arquivos = []



        if fotos.data:


            for foto in fotos.data:


                arquivo = foto.get(

                    "arquivo"

                )


                if arquivo:


                    arquivos.append(

                        arquivo

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
