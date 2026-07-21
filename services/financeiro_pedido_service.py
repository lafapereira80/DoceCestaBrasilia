from config.supabase import supabase



# =====================================================
# BUSCAR VALOR DA CESTA
# =====================================================

def buscar_valor_cesta(cesta_id):


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



    if resposta.data:


        return float(

            resposta.data.get(

                "preco",

                0

            )

            or 0

        )



    return 0





# =====================================================
# BUSCAR PRODUTOS POR NOME
# =====================================================

def buscar_produtos_por_nome(lista_nomes):


    if not lista_nomes:


        return []



    resposta = (

        supabase

        .table("produtos")

        .select(

            """

            id,

            nome,

            preco

            """

        )

        .in_(

            "nome",

            lista_nomes

        )

        .execute()

    )


    return resposta.data or []





# =====================================================
# ANALISAR ADICIONAIS DO PEDIDO
#
# Retorna:
#
# - valor dos adicionais
# - itens sem preço
#
# =====================================================

def calcular_adicionais(adicionais_texto):


    if not adicionais_texto:


        return 0, []



    nomes = [


        item.strip()


        for item in adicionais_texto.split(",")


        if item.strip()

    ]



    produtos = buscar_produtos_por_nome(

        nomes

    )



    total = 0


    consulta = []



    for produto in produtos:



        preco = produto.get(

            "preco"

        )



        if preco is None:



            consulta.append({

                "produto":

                    produto["nome"],


                "valor":

                    0

            })



        else:



            total += float(

                preco

            )



    return total, consulta





# =====================================================
# CALCULAR VALOR FINAL
# =====================================================

def calcular_valor_total(

    valor_cesta,

    valor_adicionais,

    itens_consulta,

    frete,

    desconto

):


    valor_consulta = 0



    if itens_consulta:


        for item in itens_consulta:


            valor_consulta += float(

                item.get(

                    "valor",

                    0

                )

                or 0

            )



    total = (

        valor_cesta

        +

        valor_adicionais

        +

        valor_consulta

        +

        frete

        -

        desconto

    )



    if total < 0:


        total = 0



    return total





# =====================================================
# GERAR RESUMO FINANCEIRO
# =====================================================

def resumo_financeiro(

    valor_cesta,

    valor_adicionais,

    itens_consulta,

    frete,

    desconto

):


    valor_consulta = 0



    if itens_consulta:


        for item in itens_consulta:


            valor_consulta += float(

                item.get(

                    "valor",

                    0

                )

                or 0

            )



    total = calcular_valor_total(

        valor_cesta,

        valor_adicionais,

        itens_consulta,

        frete,

        desconto

    )



    return {


        "valor_cesta":

            valor_cesta,


        "valor_adicionais":

            valor_adicionais,


        "valor_consulta":

            valor_consulta,


        "frete":

            frete,


        "desconto":

            desconto,


        "total":

            total

    }
