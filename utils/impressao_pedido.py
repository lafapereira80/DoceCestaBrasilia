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





def formatar_horario(horario):

    if not horario:

        return ""


    return str(horario)[:5]





def limitar_texto(
    texto,
    tamanho=120
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

    leading=10

)




estilo_cliente = ParagraphStyle(

    "cliente",

    parent=styles["Normal"],

    fontName="Helvetica-Bold",

    fontSize=8,

    leading=9,

    alignment=TA_LEFT

)




estilo_normal = ParagraphStyle(

    "normal",

    parent=styles["Normal"],

    fontSize=6.5,

    leading=7.5,

    alignment=TA_LEFT

)




estilo_pequeno = ParagraphStyle(

    "pequeno",

    parent=styles["Normal"],

    fontSize=5.5,

    leading=6

)





# =====================================================
# CONFIGURAÇÃO TAMANHO ETIQUETA
# =====================================================


LARGURA_ETIQUETA = 7 * cm

ALTURA_ETIQUETA = 10 * cm
# =====================================================
# BUSCA ITENS PARA MONTAGEM
# =====================================================

def buscar_itens_montagem(
    pedido
):


    itens = []



    # Produtos da cesta

    produtos = pedido.get(
        "produtos",
        ""
    )



    if produtos:


        for item in str(produtos).split("\n"):


            item = item.strip()


            if item:

                itens.append(item)





    # Adicionais

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





    # Itens sob consulta

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
# MONTA LISTA DE ITENS COMPACTA
# =====================================================

def montar_itens_pdf(
    itens
):


    if not itens:

        return Paragraph(

            "Sem itens",

            estilo_pequeno

        )



    linhas = []



    for item in itens:


        linhas.append(

            f"☐ {item}"

        )



    texto = "<br/>".join(

        linhas

    )



    return Paragraph(

        texto,

        estilo_pequeno

    )








# =====================================================
# CONTEÚDO DA ETIQUETA
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

        35

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

        30

    )



    data = formatar_data(

        pedido.get(

            "data_entrega"

        )

    )



    horario = formatar_horario(

        pedido.get(

            "horario_entrega"

        )

    )



    entrega = data



    if horario:

        entrega += " " + horario





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



    elementos.append(

        Paragraph(

            f"🎁 {cesta}",

            estilo_normal

        )

    )



    elementos.append(

        Paragraph(

            f"📅 {entrega}",

            estilo_normal

        )

    )



    elementos.append(

        Spacer(

            1,

            3

        )

    )



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

            3

        )

    )



    endereco = limitar_texto(

        pedido.get(

            "endereco",

            "-"

        ),

        70

    )



    mensagem = limitar_texto(

        pedido.get(

            "mensagem",

            "-"

        ),

        70

    )



    elementos.append(

        Paragraph(

            f"<b>END:</b> {endereco}",

            estilo_pequeno

        )

    )



    elementos.append(

        Paragraph(

            f"<b>MSG:</b> {mensagem}",

            estilo_pequeno

        )

    )



    return elementos
    # =====================================================
# CRIA CAIXA 7X10
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

            LARGURA_ETIQUETA - 0.4*cm

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

                    4

                ),


                (

                    "RIGHTPADDING",

                    (0,0),

                    (-1,-1),

                    4

                ),


                (

                    "TOPPADDING",

                    (0,0),

                    (-1,-1),

                    4

                ),


                (

                    "BOTTOMPADDING",

                    (0,0),

                    (-1,-1),

                    4

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




    while len(caixas) < 12:


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

            LARGURA_ETIQUETA,

            LARGURA_ETIQUETA,

            LARGURA_ETIQUETA

        ]

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

                )

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
