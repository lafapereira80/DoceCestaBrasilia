import io
import json
from datetime import datetime

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
# FORMATAÇÕES E TRATAMENTO DE TEXTO
# =====================================================
def formatar_data(data):
    if not data:
        return "-"
    try:
        if isinstance(data, str):
            data = data[:10]
            data = datetime.strptime(data, "%Y-%m-%d")
        return data.strftime("%d/%m/%Y")
    except:
        return str(data)

def formatar_horario(horario):
    if not horario:
        return ""
    return str(horario)[:5]

def limitar_texto(texto, tamanho=80):
    if not texto:
        return "-"
    # Troca quebras de linha por espaço
    texto = str(texto).replace("\n", " ")
    if len(texto) > tamanho:
        return texto[:tamanho] + "..."
    return texto


# =====================================================
# ESTILOS PDF
# =====================================================
styles = getSampleStyleSheet()

estilo_destaque = ParagraphStyle(
    "destaque",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=11,
    alignment=TA_LEFT
)

estilo_normal = ParagraphStyle(
    "normal",
    parent=styles["Normal"],
    fontSize=8,
    leading=10,
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

    # 1. Produtos da cesta principal
    produtos = pedido.get("produtos", "")
    if produtos:
        for item in str(produtos).split("\n"):
            item = item.strip()
            if item:
                # Remove bullets soltos
                item = item.replace('•', '').strip()
                itens.append(item)

    # 2. Adicionais
    try:
        adicionais = listar_adicionais_pedido(pedido["id"])
        for adicional in adicionais:
            nome = adicional.get("nome_produto", "")
            if nome:
                itens.append(f"[Adicional] {nome}")
    except Exception:
        pass

    # 3. Itens preço sob consulta
    consulta = normalizar_itens_consulta(pedido.get("itens_consulta"))
    for nome in consulta.keys():
        nome_marcado = f"[Extra] {nome}"
        if nome_marcado not in itens:
            itens.append(nome_marcado)

    return itens


# =====================================================
# MONTA LISTA DE ITENS COM CHECKBOX EM TEXTO
# =====================================================
def montar_itens_pdf(itens):
    if not itens:
        return Paragraph("Sem itens na montagem", estilo_item)

    linhas = []
    for item in itens:
        # Usamos colchetes normais para garantir compatibilidade 100% com a fonte
        linhas.append(f"[  ] {item}")

    return Paragraph("<br/>".join(linhas), estilo_item)


# =====================================================
# MONTA CONTEÚDO DA ETIQUETA (O CORAÇÃO DO PDF)
# =====================================================
def montar_conteudo_etiqueta(pedido):
    elementos = []

    # --- Extração e Tratamento de Dados ---
    cliente_nome = limitar_texto(pedido.get("cliente_nome", "-"), 30)
    cliente_tel = pedido.get("cliente_telefone", "-")
    
    destinatario_nome = limitar_texto(pedido.get("destinatario_nome", "-"), 30)
    destinatario_tel = pedido.get("destinatario_telefone", "-")

    cesta = limitar_texto(pedido.get("cesta_nome", "-"), 40)
    data = formatar_data(pedido.get("data_entrega"))
    periodo = pedido.get("periodo_entrega", "")
    horario = formatar_horario(pedido.get("horario_combinado"))
    horario_str = f" ({horario})" if horario else ""

    # --- 1. Título / Cesta ---
    elementos.append(Paragraph(f"<b>CESTA: {cesta.upper()}</b>", estilo_destaque))
    elementos.append(Spacer(1, 4))

    # --- 2. Envolvidos (Comprador e Homenageado) ---
    elementos.append(Paragraph(f"<b>COMPRADOR:</b> {cliente_nome} | Tel: {cliente_tel}", estilo_normal))
    elementos.append(Paragraph(f"<b>HOMENAGEADO:</b> {destinatario_nome} | Tel: {destinatario_tel}", estilo_normal))
    
    # --- 3. Logística de Entrega ---
    elementos.append(Paragraph(f"<b>ENTREGA:</b> {data} - {periodo}{horario_str}", estilo_normal))
    elementos.append(Spacer(1, 4))

    # --- 4. Checklist de Montagem ---
    elementos.append(Paragraph("<b>ITENS PARA MONTAGEM:</b>", estilo_normal))
    elementos.append(Spacer(1, 2))
    elementos.append(montar_itens_pdf(buscar_itens_montagem(pedido)))
    elementos.append(Spacer(1, 5))

    # --- 5. Endereço e Mensagem do Cartão ---
    endereco = limitar_texto(pedido.get("endereco", "-"), 90)
    elementos.append(Paragraph(f"<b>ENDERECO:</b> {endereco}", estilo_observacao))
    
    mensagem = limitar_texto(pedido.get("mensagem", "-"), 90)
    elementos.append(Paragraph(f"<b>CARTAO:</b> {mensagem}", estilo_observacao))

    # --- 6. Pedido Especial (Opcional) ---
    pedido_especial = limitar_texto(pedido.get("pedido_especial", ""), 90)
    if pedido_especial and pedido_especial != "-":
        elementos.append(Paragraph(f"<b>ATENCAO - PEDIDO ESPECIAL:</b> {pedido_especial}", estilo_observacao))

    # --- 7. Observações da Administração (Opcional) ---
    observacao = limitar_texto(pedido.get("anotacoes_internas", ""), 100)
    if observacao and observacao != "-":
        elementos.append(Spacer(1, 2))
        elementos.append(Paragraph(f"<b>OBS INTERNA:</b> {observacao}", estilo_observacao))

    return elementos


# =====================================================
# CRIA CAIXA 7X10 PARA FOLHA A4
# =====================================================
def criar_caixa_7x10(pedido):
    conteudo = montar_conteudo_etiqueta(pedido)

    tabela = Table(
        [[conteudo]],
        colWidths=[LARGURA_ETIQUETA - 0.3*cm],
        rowHeights=[ALTURA_ETIQUETA - 0.3*cm]
    )

    tabela.setStyle(
        TableStyle([
            ("BOX", (0,0), (-1,-1), 0.8, None),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5)
        ])
    )

    return tabela


# =====================================================
# PDF A4 - 12 PEDIDOS
# =====================================================
def gerar_pdf_a4(pedidos):
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
        caixas.append(criar_caixa_7x10(pedido))

    # Fecha blocos de 12 para a folha A4
    while len(caixas) % 12 != 0:
        caixas.append("")

    for pagina_inicio in range(0, len(caixas), 12):
        pagina = caixas[pagina_inicio : pagina_inicio + 12]
        linhas = []

        for i in range(0, 12, 3):
            linhas.append(pagina[i:i+3])

        tabela = Table(
            linhas,
            colWidths=[LARGURA_ETIQUETA, LARGURA_ETIQUETA, LARGURA_ETIQUETA],
            rowHeights=[ALTURA_ETIQUETA] * 4
        )

        tabela.setStyle(
            TableStyle([
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("LEFTPADDING", (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("TOPPADDING", (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0)
            ])
        )

        elementos.append(tabela)

        if pagina_inicio + 12 < len(caixas):
            elementos.append(PageBreak())

    doc.build(elementos)
    arquivo.seek(0)
    return arquivo.getvalue()


# =====================================================
# PDF INDIVIDUAL 7X10 CM
# =====================================================
def gerar_pdf_individual(pedidos):
    arquivo = io.BytesIO()

    doc = SimpleDocTemplate(
        arquivo,
        pagesize=(LARGURA_ETIQUETA, ALTURA_ETIQUETA),
        rightMargin=0.3*cm,
        leftMargin=0.3*cm,
        topMargin=0.3*cm,
        bottomMargin=0.3*cm
    )

    elementos = []

    for indice, pedido in enumerate(pedidos):
        conteudo = montar_conteudo_etiqueta(pedido)
        bloco = KeepTogether(conteudo)
        elementos.append(bloco)

        if indice < len(pedidos) - 1:
            elementos.append(PageBreak())

    doc.build(elementos)
    arquivo.seek(0)
    return arquivo.getvalue()


# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================
def gerar_pdf_pedidos(pedidos, formato):
    # A verificação pelo "📄" é baseada na label do rádio do streamlit
    if formato.startswith("📄"):
        return gerar_pdf_a4(pedidos)

    return gerar_pdf_individual(pedidos)
