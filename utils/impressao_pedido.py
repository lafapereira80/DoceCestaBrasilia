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
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import TA_CENTER


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
# FORMATAÇÕES
# =====================================================


def formatar_data(data):

    if not data:

        return "-"


    try:

        return data.strftime(
            "%d/%m/%Y"
        )

    except:

        return str(data)





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
# BUSCA ITENS PARA MONTAGEM
# =====================================================


def buscar_itens_montagem(pedido):


    itens = []



    produtos = pedido.get(

        "produtos",

        ""

    )



    if produtos:


        for item in produtos.split("\n"):


            item = item.strip()


            if item:

                itens.append(item)





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



    except:


        pass





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
# ESTILOS PDF
# =====================================================


styles = getSampleStyleSheet()



estilo_titulo = ParagraphStyle(

    "titulo",

    parent=styles["Normal"],

    fontName="Helvetica-Bold",

    fontSize=9,

    alignment=TA_CENTER,

    spaceAfter=4

)




estilo_normal = ParagraphStyle(

    "normal",

    parent=styles["Normal"],

    fontSize=6.5,

    leading=8

)



estilo_cliente = ParagraphStyle(

    "cliente",

    parent=styles["Normal"],

    fontName="Helvetica-Bold",

    fontSize=8,

    leading=9

)





# =====================================================
# MONTA CONTEÚDO DE UMA CAIXA
# =====================================================


def montar_caixa_pedido(
    pedido
):


    conteudo = []



    cliente = str(

        pedido.get(

            "cliente_nome",

            "-"

        )

    ).strip()



    telefone = pedido.get(

        "cliente_telefone",

        "-"

    )



    cesta = pedido.get(

        "cesta_nome",

        "-"

    )



    data = formatar_data(

        pedido.get(

            "data_entrega"

        )

    )



    horario = pedido.get(

        "horario_entrega",

        ""

    )



    entrega = data



    if horario:

        entrega += f" {str(horario)[:5]}"





    conteudo.append(

        Paragraph(

            cliente,

            estilo_cliente

        )

    )



    conteudo.append(

        Paragraph(

            f"☎ {telefone}",

            estilo_normal

        )

    )



    conteudo.append(

        Paragraph(

            f"🎁 {cesta}",

            estilo_normal

        )

    )



    conteudo.append(

        Paragraph(

            f"📅 {entrega}",

            estilo_normal

        )

    )



    conteudo.append(

        Spacer(

            1,

            3

        )

    )



    conteudo.append(

        Paragraph(

            "<b>MONTAGEM</b>",

            estilo_normal

        )

    )




    itens = buscar_itens_montagem(

        pedido

    )



    if itens:


        for item in itens:


            conteudo.append(

                Paragraph(

                    f"☐ {item}",

                    estilo_normal

                )

            )


    else:


        conteudo.append(

            Paragraph(

                "Sem itens",

                estilo_normal

            )

        )





    conteudo.append(

        Spacer(

            1,

            3

        )

    )



    endereco = str(

        pedido.get(

            "endereco",

            "-"

        )

    )



    mensagem = str(

        pedido.get(

            "mensagem",

            "-"

        )

    )





    conteudo.append(

        Paragraph(

            f"<b>END:</b> {endereco}",

            estilo_normal

        )

    )



    conteudo.append(

        Paragraph(

            f"<b>MSG:</b> {mensagem}",

            estilo_normal

        )

    )



    return conteudo





# =====================================================
# CRIA CAIXAS 7X10
# =====================================================


def criar_caixa_7x10(
    pedido
):


    elementos = montar_caixa_pedido(

        pedido

    )


    tabela = Table(

        [

            [

                elementos

            ]

        ],

        colWidths=[

            7 * cm

        ],

        rowHeights=[

            10 * cm

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
# GERA PDF A4 - 12 PEDIDOS
# =====================================================


def gerar_pdf_a4(
    pedidos
):


    arquivo = io.BytesIO()



    doc = SimpleDocTemplate(

        arquivo,

        pagesize=A4,

        rightMargin=0.5*cm,

        leftMargin=0.5*cm,

        topMargin=0.5*cm,

        bottomMargin=0.5*cm

    )



    elementos = []



    titulo = Paragraph(

        "PEDIDOS PARA PRODUÇÃO",

        estilo_titulo

    )


    elementos.append(

        titulo

    )


    elementos.append(

        Spacer(

            1,

            5

        )

    )





    caixas = []



    for pedido in pedidos:


        caixas.append(

            criar_caixa_7x10(

                pedido

            )

        )





    # completa espaços vazios

    while len(caixas) % 3 != 0:


        caixas.append("")





    linhas = []



    for i in range(

        0,

        len(caixas),

        3

    ):


        linhas.append(

            caixas[i:i+3]

        )





    tabela = Table(

        linhas,

        colWidths=[

            7*cm,

            7*cm,

            7*cm

        ],

        hAlign="CENTER"

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

                    2

                ),

                (

                    "RIGHTPADDING",

                    (0,0),

                    (-1,-1),

                    2

                ),

            ]

        )

    )



    elementos.append(

        tabela

    )



    doc.build(

        elementos

    )



    arquivo.seek(0)



    return arquivo.getvalue()







# =====================================================
# GERA PDF INDIVIDUAL 7X10
# =====================================================


def gerar_pdf_individual(
    pedidos
):


    arquivo = io.BytesIO()



    doc = SimpleDocTemplate(

        arquivo,

        pagesize=(

            7*cm,

            10*cm

        ),

        rightMargin=0.2*cm,

        leftMargin=0.2*cm,

        topMargin=0.2*cm,

        bottomMargin=0.2*cm

    )



    elementos = []



    for pedido in pedidos:



        elementos.append(

            criar_caixa_7x10(

                pedido

            )

        )


        if pedido != pedidos[-1]:


            elementos.append(

                PageBreak()

            )



    doc.build(

        elementos

    )



    arquivo.seek(0)



    return arquivo.getvalue()






# =====================================================
# FUNÇÃO PRINCIPAL CHAMADA PELO SISTEMA
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



    else:


        return gerar_pdf_individual(

            pedidos

        )
