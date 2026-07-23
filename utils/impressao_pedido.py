import io
import json


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)


from reportlab.lib.enums import (
    TA_LEFT,
    TA_CENTER
)


from services.pedido_adicional_service import (
    listar_adicionais_pedido
)





# =====================================================
# CONFIGURAÇÃO DOS FORMATOS
# =====================================================

LARGURA_ETIQUETA = 7 * cm

ALTURA_ETIQUETA = 10 * cm





# =====================================================
# NORMALIZA JSON
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
# FORMATAÇÕES
# =====================================================

def formatar_data(data):


    if not data:

        return "-"



    try:


        if isinstance(data, str):


            data = data[:10]



            from datetime import datetime


            data = datetime.strptime(

                data,

                "%Y-%m-%d"

            )



        return data.strftime(

            "%d/%m/%Y"

        )



    except:


        return str(data)







def formatar_horario(horario):


    if not horario:


        return ""



    return str(horario)[:5]







def limitar_texto(
    texto,
    tamanho=80
):


    if not texto:

        return "-"



    texto = str(texto).replace(

        "\n",

        " "

    )



    if len(texto) > tamanho:


        return texto[:tamanho] + "..."



    return texto







def formatar_valor(valor):


    try:


        return (

            f"R$ {float(valor):,.2f}"

            .replace(",", "X")

            .replace(".", ",")

            .replace("X",".")

        )



    except:


        return "R$ 0,00"







# =====================================================
# ESTILOS PDF
# =====================================================

styles = getSampleStyleSheet()





estilo_titulo = ParagraphStyle(

    "titulo",

    parent=styles["Normal"],

    fontName="Helvetica-Bold",

    fontSize=11,

    alignment=TA_CENTER,

    leading=12

)






estilo_cliente = ParagraphStyle(

    "cliente",

    parent=styles["Normal"],

    fontName="Helvetica-Bold",

    fontSize=10,

    leading=11,

    alignment=TA_LEFT

)







estilo_normal = ParagraphStyle(

    "normal",

    parent=styles["Normal"],

    fontSize=8,

    leading=9,

    alignment=TA_LEFT

)








estilo_item = ParagraphStyle(

    "item",

    parent=styles["Normal"],

    fontSize=7,

    leading=8,

    alignment=TA_LEFT

)








estilo_observacao = ParagraphStyle(

    "observacao",

    parent=styles["Normal"],

    fontSize=7,

    leading=8,

    alignment=TA_LEFT

)
# =====================================================
# BUSCA ITENS PARA MONTAGEM
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


        for item in str(produtos).split("\n"):


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
# MONTA LISTA DE ITENS
# =====================================================

def montar_itens_pdf(itens):


    if not itens:


        return Paragraph(

            "Sem itens",

            estilo_item

        )



    linhas = []



    for item in itens:


        linhas.append(

            f"☐ {item}"

        )



    return Paragraph(

        "<br/>".join(linhas),

        estilo_item

    )







# =====================================================
# MONTA CONTEÚDO DA ETIQUETA
# =====================================================

def montar_conteudo_etiqueta(
    pedido
):


    elementos = []





    cliente = limitar_texto(

        pedido.get(

            "cliente_nome",

            "-"

        ),

        40

    )



    telefone = pedido.get(

        "cliente_telefone",

        "-"

    )



    cesta = limitar_texto(

        pedido.get(

            "cesta_nome",

            "-"

        ),

        35

    )





    data = formatar_data(

        pedido.get(

            "data_entrega"

        )

    )



    horario = formatar_horario(

        pedido.get(

            "horario_combinado"

        )

    )





    periodo = pedido.get(

        "periodo_entrega",

        ""

    )





    # ---------------------------------------------
    # Cliente
    # ---------------------------------------------

    elementos.append(

        Paragraph(

            cliente,

            estilo_cliente

        )

    )



    elementos.append(

        Paragraph(

            f"☎ {telefone}",

            estilo_normal

        )

    )





    # ---------------------------------------------
    # Cesta
    # ---------------------------------------------

    elementos.append(

        Paragraph(

            f"🎁 {cesta}",

            estilo_normal

        )

    )





    # ---------------------------------------------
    # Entrega
    # ---------------------------------------------

    elementos.append(

        Paragraph(

            f"📅 {data}",

            estilo_normal

        )

    )



    if periodo:


        elementos.append(

            Paragraph(

                f"🕒 {periodo}",

                estilo_normal

            )

        )



    if horario:


        elementos.append(

            Paragraph(

                f"⏰ Horário: {horario}",

                estilo_normal

            )

        )





    elementos.append(

        Spacer(

            1,

            4

        )

    )





    # ---------------------------------------------
    # Montagem
    # ---------------------------------------------

    elementos.append(

        Paragraph(

            "<b>MONTAGEM</b>",

            estilo_normal

        )

    )



    elementos.append(

        montar_itens_pdf(

            buscar_itens_montagem(

                pedido

            )

        )

    )





    elementos.append(

        Spacer(

            1,

            4

        )

    )





    # ---------------------------------------------
    # Endereço
    # ---------------------------------------------

    endereco = limitar_texto(

        pedido.get(

            "endereco",

            "-"

        ),

        90

    )



    elementos.append(

        Paragraph(

            f"<b>END:</b> {endereco}",

            estilo_observacao

        )

    )





    # ---------------------------------------------
    # Mensagem cliente
    # ---------------------------------------------

    mensagem = limitar_texto(

        pedido.get(

            "mensagem",

            "-"

        ),

        90

    )



    elementos.append(

        Paragraph(

            f"<b>MSG:</b> {mensagem}",

            estilo_observacao

        )

    )





    # ---------------------------------------------
    # Observação interna
    # ---------------------------------------------

    observacao = limitar_texto(

        pedido.get(

            "observacao_admin",

            ""

        ),

        100

    )



    if observacao and observacao != "-":


        elementos.append(

            Spacer(

                1,

                3

            )

        )



        elementos.append(

            Paragraph(

                f"<b>OBS ADM:</b> {observacao}",

                estilo_observacao

            )

        )



    return elementos
    # =====================================================
# CRIA CAIXA 7X10 PARA FOLHA A4
# =====================================================

def criar_caixa_7x10(
    pedido
):


    conteudo = montar_conteudo_etiqueta(

        pedido

    )



    tabela = Table(

        [

            [

                conteudo

            ]

        ],

        colWidths=[

            LARGURA_ETIQUETA - 0.3*cm

        ],

        rowHeights=[

            ALTURA_ETIQUETA - 0.3*cm

        ]

    )



    tabela.setStyle(

        TableStyle(

            [

                (

                    "BOX",

                    (0,0),

                    (-1,-1),

                    0.8,

                    None

                ),


                (

                    "VALIGN",

                    (0,0),

                    (-1,-1),

                    "TOP"

                ),


                (

                    "LEFTPADDING",

                    (0,0),

                    (-1,-1),

                    5

                ),


                (

                    "RIGHTPADDING",

                    (0,0),

                    (-1,-1),

                    5

                ),


                (

                    "TOPPADDING",

                    (0,0),

                    (-1,-1),

                    5

                ),


                (

                    "BOTTOMPADDING",

                    (0,0),

                    (-1,-1),

                    5

                )

            ]

        )

    )



    return tabela







# =====================================================
# PDF A4 - 12 PEDIDOS
# =====================================================

def gerar_pdf_a4(
    pedidos
):


    arquivo = io.BytesIO()



    doc = SimpleDocTemplate(

        arquivo,

        pagesize=A4,

        rightMargin=0.4*cm,

        leftMargin=0.4*cm,

        topMargin=0.4*cm,

        bottomMargin=0.4*cm

    )



    elementos = []



    caixas = []



    for pedido in pedidos:


        caixas.append(

            criar_caixa_7x10(

                pedido

            )

        )





    # fecha sempre grupos de 12

    while len(caixas) % 12 != 0:


        caixas.append("")





    for pagina_inicio in range(

        0,

        len(caixas),

        12

    ):



        pagina = caixas[

            pagina_inicio:

            pagina_inicio + 12

        ]



        linhas = []



        for i in range(

            0,

            12,

            3

        ):


            linhas.append(

                pagina[i:i+3]

            )





        tabela = Table(

            linhas,

            colWidths=[

                LARGURA_ETIQUETA,

                LARGURA_ETIQUETA,

                LARGURA_ETIQUETA

            ],

            rowHeights=[

                ALTURA_ETIQUETA

            ] * 4

        )





        tabela.setStyle(

            TableStyle(

                [

                    (

                        "VALIGN",

                        (0,0),

                        (-1,-1),

                        "TOP"

                    ),


                    (

                        "LEFTPADDING",

                        (0,0),

                        (-1,-1),

                        0

                    ),


                    (

                        "RIGHTPADDING",

                        (0,0),

                        (-1,-1),

                        0

                    ),


                    (

                        "TOPPADDING",

                        (0,0),

                        (-1,-1),

                        0

                    ),


                    (

                        "BOTTOMPADDING",

                        (0,0),

                        (-1,-1),

                        0

                    )

                ]

            )

        )




        elementos.append(

            tabela

        )





        if pagina_inicio + 12 < len(caixas):


            elementos.append(

                PageBreak()

            )





    doc.build(

        elementos

    )



    arquivo.seek(0)



    return arquivo.getvalue()
    # =====================================================
# PDF INDIVIDUAL 7X10 CM
# =====================================================

def gerar_pdf_individual(
    pedidos
):


    arquivo = io.BytesIO()



    doc = SimpleDocTemplate(

        arquivo,

        pagesize=(

            LARGURA_ETIQUETA,

            ALTURA_ETIQUETA

        ),

        rightMargin=0.3*cm,

        leftMargin=0.3*cm,

        topMargin=0.3*cm,

        bottomMargin=0.3*cm

    )



    elementos = []



    for indice, pedido in enumerate(pedidos):



        conteudo = montar_conteudo_etiqueta(

            pedido

        )



        bloco = KeepTogether(

            conteudo

        )



        elementos.append(

            bloco

        )



        if indice < len(pedidos)-1:


            elementos.append(

                PageBreak()

            )





    doc.build(

        elementos

    )



    arquivo.seek(0)



    return arquivo.getvalue()







# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================

def gerar_pdf_pedidos(

    pedidos,

    formato

):


    if formato.startswith(

        "📄"

    ):


        return gerar_pdf_a4(

            pedidos

        )



    return gerar_pdf_individual(

        pedidos

    )
