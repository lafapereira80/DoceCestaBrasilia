from config.supabase import supabase

from services.pedido_adicional_service import (
    salvar_adicionais_pedido
)



# =====================================================
# SALVAR PEDIDO
# =====================================================

def salvar_pedido(dados):

    try:

        adicionais = dados.pop(
            "adicionais_detalhados",
            []
        )


        resposta = (

            supabase

            .table("pedidos")

            .insert(dados)

            .execute()

        )


        pedido_id = resposta.data[0]["id"]



        if adicionais:


            salvar_adicionais_pedido(

                pedido_id,

                adicionais

            )



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
# Não retorna Entregue
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
#
# Retorna:
# - dados do pedido
# - adicionais vinculados
# - fotos vinculadas
# =====================================================

def buscar_pedido(pedido_id):


    resposta = (

        supabase

        .table("pedidos")

        .select(

            """
            *,
            pedido_adicionais(
                id,
                produto_id,
                nome_produto,
                quantidade,
                valor_unitario
            ),
            pedido_fotos(
                id,
                arquivo
            )
            """

        )

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
# Novo padrão:
#
# atualizar_pedido(
#     id,
#     {
#       "status":"Pago",
#       "valor_frete":10,
#       "valor_total":100
#     }
# )
#
# Mantém compatibilidade antiga
# =====================================================

def atualizar_pedido(

    pedido_id,

    dados,

    valor_frete=None,

    valor_total=None,

    desconto=0

):


    try:



        # ---------------------------------------------
        # NOVO PADRÃO
        # Recebe dicionário
        # ---------------------------------------------

        if isinstance(

            dados,

            dict

        ):


            campos = dados





        # ---------------------------------------------
        # PADRÃO ANTIGO
        # Recebia status separado
        # ---------------------------------------------

        else:


            campos = {


                "status":

                    dados,


                "valor_frete":

                    valor_frete,


                "valor_total":

                    valor_total,


                "desconto":

                    desconto


            }






        resposta = (

            supabase

            .table("pedidos")

            .update(

                campos

            )

            .eq(

                "id",

                pedido_id

            )

            .execute()

        )



        return True, "Pedido atualizado com sucesso"



    except Exception as erro:


        return False, str(erro)






# =====================================================
# ATUALIZAR ANOTAÇÃO INTERNA
# =====================================================

def atualizar_anotacao_pedido(

    pedido_id,

    anotacao

):


    resposta = (

        supabase

        .table("pedidos")

        .update(

            {

                "anotacoes_internas":

                    anotacao

            }

        )

        .eq(

            "id",

            pedido_id

        )

        .execute()

    )


    return resposta.data






# =====================================================
# ATUALIZAR ITENS SOB CONSULTA
# =====================================================

def atualizar_itens_consulta(

    pedido_id,

    itens

):


    resposta = (

        supabase

        .table("pedidos")

        .update(

            {

                "itens_consulta":

                    itens

            }

        )

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
# 3 - Adicionais
# 4 - Pedido
# =====================================================

def excluir_pedido_completo(pedido_id):

    try:


        # -----------------------------------------
        # BUSCA FOTOS
        # -----------------------------------------

        fotos = (

            supabase

            .table("pedido_fotos")

            .select(

                "arquivo"

            )

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






        # -----------------------------------------
        # REMOVE ARQUIVOS DO STORAGE
        # -----------------------------------------

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







        # -----------------------------------------
        # REMOVE REGISTROS DE FOTOS
        # -----------------------------------------

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







        # -----------------------------------------
        # REMOVE ADICIONAIS
        # -----------------------------------------

        (

            supabase

            .table("pedido_adicionais")

            .delete()

            .eq(

                "pedido_id",

                pedido_id

            )

            .execute()

        )







        # -----------------------------------------
        # REMOVE PEDIDO
        # -----------------------------------------

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
