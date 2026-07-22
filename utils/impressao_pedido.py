import streamlit as st
import json

from services.pedido_adicional_service import (
    listar_adicionais_pedido
)


# =====================================================
# NORMALIZA ITENS CONSULTA
# =====================================================

def normalizar_itens_consulta(valor):

    if not valor:
        return {}

    if isinstance(valor, dict):
        return valor

    if isinstance(valor, str):

        try:
            return json.loads(valor)

        except:

            return {}

    return {}



# =====================================================
# FORMATA DATA
# =====================================================

def formatar_data(data):

    if not data:
        return "-"

    try:

        return data.strftime("%d/%m/%Y")

    except:

        return str(data)



# =====================================================
# FORMATA HORÁRIO
# =====================================================

def formatar_horario(horario):

    if not horario:
        return ""

    return str(horario)[:5]



# =====================================================
# BUSCA ITENS DO PEDIDO
# =====================================================

def buscar_itens_montagem(pedido):

    itens = []


    # ---------------------------------------------
    # Produtos da cesta
    # ---------------------------------------------

    produtos = pedido.get(
        "produtos",
        ""
    )


    if produtos:


        for item in produtos.split("\n"):


            item = item.strip()


            if item:

                itens.append(item)



    # ---------------------------------------------
    # Adicionais
    # ---------------------------------------------

    try:

        adicionais = listar_adicionais_pedido(
            pedido["id"]
        )


        for adicional in adicionais:


            nome = adicional.get(
                "nome_produto",
                ""
            )


            if nome:

                itens.append(nome)



    except Exception:


        pass



    # ---------------------------------------------
    # Itens preço sob consulta
    # ---------------------------------------------

    consulta = normalizar_itens_consulta(

        pedido.get(
            "itens_consulta"
        )

    )


    for nome in consulta.keys():


        if nome not in itens:

            itens.append(nome)



    return itens




# =====================================================
# MONTA ITENS EM COLUNAS
# =====================================================

def montar_lista_compacta(itens):

    if not itens:

        return "Nenhum item"



    html = ""


    for i, item in enumerate(itens):


        html += f"""

        <span class="item">

        ☐ {item}

        </span>

        """



        if (i + 1) % 3 == 0:

            html += "<br>"



    return html




# =====================================================
# GERA HTML DE IMPRESSÃO
# =====================================================

def gerar_impressao_pedidos(
    pedidos
):


    blocos = ""



    for pedido in pedidos:


        itens = buscar_itens_montagem(
            pedido
        )


        lista_itens = montar_lista_compacta(
            itens
        )



        data_entrega = formatar_data(

            pedido.get(
                "data_entrega"
            )

        )


        horario = formatar_horario(

            pedido.get(
                "horario_entrega"
            )

        )



        entrega = data_entrega


        if horario:

            entrega += f" {horario}"



        blocos += f"""

        <div class="pedido">


            <div class="linha">

                <b>CLIENTE:</b>
                {pedido.get('cliente_nome','-')}

                |

                ☎ {pedido.get('cliente_telefone','-')}

            </div>


            <div class="linha">

                <b>CESTA:</b>
                {pedido.get('cesta_nome','-')}

                |

                <b>ENTREGA:</b>
                {entrega}

            </div>



            <div class="titulo">

                MONTAGEM:

            </div>


            <div class="itens">

                {lista_itens}

            </div>



            <div class="linha">

                <b>END:</b>

                {pedido.get('endereco','-')}

            </div>



            <div class="linha">

                <b>MSG:</b>

                {pedido.get('mensagem','-')}

            </div>


        </div>


        """




    html = f"""

    <html>

    <head>


    <style>


    @page {{

        size: A4;

        margin: 5mm;

    }}



    body {{


        font-family: Arial, sans-serif;

        font-size: 9px;


    }}



    .titulo-principal {{


        text-align:center;

        font-size:12px;

        font-weight:bold;

        margin-bottom:5px;


    }}



    .pedido {{


        border-bottom:1px solid #000;

        padding:4px 0;

        margin-bottom:4px;


    }}



    .linha {{


        line-height:12px;


    }}



    .titulo {{


        font-weight:bold;

        margin-top:3px;


    }}



    .item {{


        display:inline-block;

        width:32%;

        line-height:14px;


    }}


    </style>


    </head>


    <body>


    <div class="titulo-principal">

        PEDIDOS PARA PRODUÇÃO

    </div>


    {blocos}


    </body>


    </html>


    """


    return html




# =====================================================
# ABRIR IMPRESSÃO
# =====================================================

def abrir_impressao(
    pedidos
):

    html = gerar_impressao_pedidos(
        pedidos
    )


    st.components.v1.html(

        html,

        height=800,

        scrolling=True

    )
  
