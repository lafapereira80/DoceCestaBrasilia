import io
import json

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib.pagesizes import A4

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
# FORMATA VALORES
# =====================================================

def formatar_valor(valor):

    try:

        valor = float(valor)

        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    except:

        return "R$ 0,00"





# =====================================================
# FORMATA DATA
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





# =====================================================
# FORMATA HORÁRIO
# =====================================================

def formatar_horario(horario):

    if not horario:

        return ""


    return str(horario)[:5]





# =====================================================
# LIMPA TEXTO
# =====================================================

def limpar_texto(texto):

    if not texto:

        return "-"


    return (
        str(texto)
        .replace("\n", " ")
        .strip()
    )





# =====================================================
# BUSCA ITENS PARA MONTAGEM
# =====================================================

def buscar_itens_montagem(pedido):

    itens = []



    # -----------------------------
    # Produtos da cesta
    # -----------------------------

    produtos = pedido.get(
        "produtos",
        ""
    )


    if produtos:


        for item in produtos.split("\n"):


            item = item.strip()


            if item:

                itens.append(item)





    # -----------------------------
    # Adicionais cadastrados
    # -----------------------------

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





    # -----------------------------
    # Itens sob consulta
    # -----------------------------

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
# DESENHA TEXTO LIMITADO
# =====================================================

def desenhar_linha(
    pdf,
    texto,
    x,
    y,
    tamanho=7
):

    pdf.setFont(
        "Helvetica",
        tamanho
    )


    pdf.drawString(
        x,
        y,
        limpar_texto(texto)[:45]
    )

# =====================================================
# DESENHA CAIXA DE PEDIDO
# =====================================================

def desenhar_caixa_pedido(
    pdf,
    pedido,
    x,
    y,
    largura,
    altura
):


    # borda da caixa

    pdf.rect(
        x,
        y,
        largura,
        altura
    )


    margem = 4 * mm


    pos_y = y + altura - margem



    # -----------------------------
    # CABEÇALHO
    # -----------------------------

    pdf.setFont(
        "Helvetica-Bold",
        9
    )


    pdf.drawString(
        x + margem,
        pos_y,
        "DOCE CESTA"
    )


    pos_y -= 12



    pdf.setFont(
        "Helvetica-Bold",
        8
    )


    pdf.drawString(
        x + margem,
        pos_y,
        limpar_texto(
            pedido.get(
                "cliente_nome",
                "-"
            )
        )[:32]
    )


    pos_y -= 11



    pdf.setFont(
        "Helvetica",
        7
    )


    pdf.drawString(
        x + margem,
        pos_y,
        f"Tel: {pedido.get('cliente_telefone','-')}"
    )


    pos_y -= 11



    # -----------------------------
    # DADOS PEDIDO
    # -----------------------------

    pdf.drawString(
        x + margem,
        pos_y,
        f"Cesta: {limpar_texto(pedido.get('cesta_nome'))[:25]}"
    )


    pos_y -= 11



    entrega = formatar_data(
        pedido.get(
            "data_entrega"
        )
    )


    horario = formatar_horario(
        pedido.get(
            "horario_entrega"
        )
    )


    if horario:

        entrega += f" {horario}"



    pdf.drawString(
        x + margem,
        pos_y,
        f"Entrega: {entrega}"
    )


    pos_y -= 14




    # -----------------------------
    # MONTAGEM
    # -----------------------------

    pdf.setFont(
        "Helvetica-Bold",
        7
    )


    pdf.drawString(
        x + margem,
        pos_y,
        "MONTAGEM:"
    )


    pos_y -= 10



    pdf.setFont(
        "Helvetica",
        6.5
    )


    itens = buscar_itens_montagem(
        pedido
    )


    for item in itens:


        if pos_y < y + 25:

            break


        texto = (
            "☐ "
            +
            limpar_texto(item)
        )


        pdf.drawString(
            x + margem,
            pos_y,
            texto[:38]
        )


        pos_y -= 9




    # -----------------------------
    # MENSAGEM
    # -----------------------------

    if pos_y > y + 15:


        pdf.setFont(
            "Helvetica-Bold",
            6
        )


        pdf.drawString(
            x + margem,
            pos_y,
            "MSG:"
        )


        pos_y -= 8


        pdf.setFont(
            "Helvetica",
            6
        )


        pdf.drawString(
            x + margem,
            pos_y,
            limpar_texto(
                pedido.get(
                    "mensagem",
                    "-"
                )
            )[:38]
        )





# =====================================================
# GERA PDF A4 PRODUÇÃO
# =====================================================

def gerar_pdf_producao_a4(
    pedidos
):


    arquivo = io.BytesIO()



    pdf = canvas.Canvas(
        arquivo,
        pagesize=A4
    )



    largura_pagina, altura_pagina = A4



    largura_caixa = 7 * cm

    altura_caixa = 10 * cm



    margem_x = (
        largura_pagina
        -
        (3 * largura_caixa)
    ) / 2



    margem_y = (
        altura_pagina
        -
        (4 * altura_caixa)
    ) / 2





    coluna = 0

    linha = 0



    for pedido in pedidos:



        x = (
            margem_x
            +
            coluna * largura_caixa
        )


        y = (
            altura_pagina
            -
            margem_y
            -
            (linha + 1)
            *
            altura_caixa
        )



        desenhar_caixa_pedido(

            pdf,

            pedido,

            x,

            y,

            largura_caixa,

            altura_caixa

        )



        coluna += 1



        if coluna == 3:


            coluna = 0

            linha += 1




        if linha == 4:


            pdf.showPage()

            coluna = 0

            linha = 0




    pdf.save()



    arquivo.seek(0)



    return arquivo.getvalue()





# =====================================================
# GERA PDF INDIVIDUAL 7x10
# =====================================================

def gerar_pdf_individual_7x10(
    pedido
):


    arquivo = io.BytesIO()



    tamanho = (
        70 * mm,
        100 * mm
    )



    pdf = canvas.Canvas(

        arquivo,

        pagesize=tamanho

    )



    desenhar_caixa_pedido(

        pdf,

        pedido,

        0,

        0,

        70 * mm,

        100 * mm

    )



    pdf.save()



    arquivo.seek(0)



    return arquivo.getvalue()





# =====================================================
# COMPATIBILIDADE ATUAL
# =====================================================

def abrir_impressao(
    pedidos
):

    pdf = gerar_pdf_producao_a4(
        pedidos
    )


    return pdf
