import streamlit as st
from pathlib import Path


from services.pedido_service import salvar_pedido
from services.foto_service import salvar_fotos
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.categoria_service import listar_categorias_pedido
from services.produto_service import listar_produtos_por_categoria_id
from services.pedido_adicional_service import salvar_adicionais_pedido



# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(

    page_title="Doce Cesta Brasília",

    page_icon="🎁",

    layout="centered",

    initial_sidebar_state="collapsed"

)



# ==========================================================
# CSS
# ==========================================================

st.markdown(
"""
<style>

section[data-testid="stSidebar"]{
    display:none;
}

[data-testid="collapsedControl"]{
    display:none;
}

header{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

#MainMenu{
    visibility:hidden;
}


.block-container{

    max-width:720px;

    padding-top:15px;

    padding-bottom:30px;

}


h1{

    font-size:26px !important;

}


h2{

    font-size:20px !important;

}


h3{

    font-size:17px !important;

    color:#8B5A2B;

}


p, label, div{

    font-size:14px;

}


input{

    height:42px !important;

    font-size:15px !important;

}


textarea{

    font-size:15px !important;

    border-radius:10px !important;

}


div[data-baseweb="select"] > div{

    border-radius:10px;

    border:1px solid #c9b8a8;

}


div[data-testid="stCheckbox"]{

    background:#fffaf5;

    padding:8px;

    border-radius:8px;

}


.stButton button{

    background:#8B5A2B;

    color:white;

    border-radius:12px;

    height:52px;

    font-size:16px;

    font-weight:bold;

    width:100%;

}


.imagem-cesta img{

    border-radius:15px;

    border:1px solid #ead8c7;

}


</style>
""",
unsafe_allow_html=True
)




# ==========================================================
# LOGO
# ==========================================================

logo = Path(
    "assets/logo.webp"
)



if logo.exists():

    col1,col2,col3 = st.columns(
        [1,1,1]
    )


    with col2:

        st.image(

            str(logo),

            width=130

        )



st.markdown(
"""
<h1 style="
text-align:center;
color:#8B5A2B;
margin-bottom:0;
">

Doce Cesta Brasília

</h1>
""",
unsafe_allow_html=True
)



st.markdown(
"""
<p style="
text-align:center;
margin-top:5px;
">

Cestas personalizadas para momentos especiais 💝

</p>
""",
unsafe_allow_html=True
)




# ==========================================================
# FORMULÁRIO
# ==========================================================


st.markdown(
"### 📝 Faça seu pedido"
)




# ==========================================================
# CLIENTE
# ==========================================================


st.markdown(
"### 👤 Seus dados"
)



col1,col2 = st.columns(2)



with col1:

    nome = st.text_input(

        "Nome completo *",

        placeholder="Digite seu nome"

    )



with col2:

    telefone = st.text_input(

        "Telefone *",

        placeholder="(61) 99999-9999"

    )



cpf = st.text_input(

    "CPF *",

    placeholder="000.000.000-00"

)




# ==========================================================
# CESTAS
# ==========================================================


st.markdown(
"### 🎁 Escolha sua cesta"
)



try:

    cestas = listar_cestas()


except Exception as erro:

    cestas = []

    st.error(

        f"Erro ao carregar cestas: {erro}"

    )





cesta = None



if cestas:


    opcoes_cestas = [

        {

            "id":None,

            "nome":"Selecione..."

        }

    ] + cestas



    cesta_selecionada = st.selectbox(

        "Selecione a cesta",

        opcoes_cestas,

        format_func=lambda c:

            c["nome"],

        key="selecao_cesta"

    )



    if cesta_selecionada.get("id"):


        cesta = cesta_selecionada



else:


    st.warning(

        "Nenhuma cesta cadastrada."

    )




# ==========================================================
# DETALHES DA CESTA
# ==========================================================


if cesta:


    col1,col2 = st.columns(

        [1,2]

    )


    with col1:


        if cesta.get("imagem"):


            st.markdown(

                '<div class="imagem-cesta">',

                unsafe_allow_html=True

            )


            st.image(

                cesta["imagem"],

                width=220

            )


            st.markdown(

                "</div>",

                unsafe_allow_html=True

            )



        else:


            st.info(

                "Imagem da cesta não cadastrada."

            )



    with col2:


        if cesta.get("descricao"):


            st.info(

                cesta["descricao"]

            )



        if cesta.get("preco") is not None:


            valor = float(

                cesta["preco"]

            )


            valor_formatado = (

                f"R$ {valor:,.2f}"

                .replace(",", "X")

                .replace(".", ",")

                .replace("X",".")

            )


            st.markdown(

                f"""

### 🎁 Valor da cesta

**{valor_formatado}**

""",

                unsafe_allow_html=True
                # ==========================================================
# PERSONALIZAÇÃO DA CESTA
# ==========================================================


st.markdown(

    "### 🍓 Personalize sua cesta"

)



selecoes_cliente = {}




# ==========================================================
# PRODUTOS DA CESTA ESCOLHIDA
#
# REGRA:
#
# Sem cesta:
#   não mostra produtos configurados
#
# Com cesta:
#   mostra somente produtos vinculados
#   àquela cesta
#
# ==========================================================


if cesta:



    try:


        configuracao = carregar_configuracao_cesta(

            cesta["id"]

        )


    except Exception as erro:


        configuracao = []


        st.error(

            f"Erro ao carregar produtos da cesta: {erro}"

        )





    if configuracao:



        for grupo in configuracao:



            categoria = grupo.get(

                "categoria",

                "Sem categoria"

            )



            produtos = grupo.get(

                "produtos",

                []

            )



            minimo = grupo.get(

                "min_escolhas",

                0

            )



            maximo = grupo.get(

                "max_escolhas",

                1

            )





            # ignora grupo sem produtos

            if not produtos:


                continue





            with st.container(border=True):


                st.markdown(

                    f"**{categoria}**"

                )





                if maximo == 1:



                    escolhido = st.radio(


                        "Escolha uma opção",


                        produtos,


                        format_func=lambda p:

                            p["nome"],


                        key=f"radio_{cesta['id']}_{categoria}"


                    )



                    if escolhido:



                        selecoes_cliente[categoria] = [


                            escolhido


                        ]





                else:



                    escolhidos = st.multiselect(


                        f"Escolha entre {minimo} e {maximo} opções",


                        produtos,


                        format_func=lambda p:

                            p["nome"],


                        max_selections=maximo,


                        key=f"multi_{cesta['id']}_{categoria}"


                    )



                    selecoes_cliente[categoria] = escolhidos





    else:



        st.info(

            "Esta cesta ainda não possui produtos configurados."

        )





else:



    st.info(

        "Escolha uma cesta acima para visualizar os produtos disponíveis."

    )

    # ==========================================================
# COMPLEMENTOS DO PEDIDO
#
# REGRAS:
#
# 1 - Adicionais aparecem sempre
#
# 2 - Outras categorias aparecem somente
#     se estiverem configuradas na cesta
#
# ==========================================================


st.markdown(

    "### 🎀 Complementos"

)


st.caption(

    "Escolha itens adicionais para complementar sua cesta."

)



adicionais_selecionados = []


polaroid = False





try:


    categorias_pedido = listar_categorias_pedido()



except Exception as erro:


    categorias_pedido = []


    st.error(

        f"Erro ao carregar complementos: {erro}"

    )





# ==========================================================
# DEFINIR CATEGORIAS DISPONÍVEIS
# ==========================================================


categorias_exibir = []





# ----------------------------------------------------------
# SEM CESTA
# somente Adicionais
# ----------------------------------------------------------


if not cesta:



    for categoria in categorias_pedido:



        nome_categoria = categoria.get(

            "nome",

            ""

        ).strip().lower()



        if nome_categoria == "adicionais":


            categorias_exibir.append(

                categoria

            )





# ----------------------------------------------------------
# COM CESTA
# Adicionais + categorias da cesta
# ----------------------------------------------------------


else:



    # Adicionais sempre entram


    for categoria in categorias_pedido:



        nome_categoria = categoria.get(

            "nome",

            ""

        ).strip()



        if nome_categoria.lower() == "adicionais":


            categorias_exibir.append(

                categoria

            )





    # Buscar categorias configuradas


    try:


        configuracao = carregar_configuracao_cesta(

            cesta["id"]

        )


    except:


        configuracao = []





    categorias_cesta = []



    for grupo in configuracao:



        nome = grupo.get(

            "categoria"

        )



        if nome:


            categorias_cesta.append(

                nome.strip()

            )





    # adiciona categorias da cesta


    for categoria in categorias_pedido:



        nome_categoria = categoria.get(

            "nome",

            ""

        ).strip()



        if nome_categoria in categorias_cesta:



            if categoria not in categorias_exibir:


                categorias_exibir.append(

                    categoria

                )





# ==========================================================
# EXIBIR PRODUTOS DOS COMPLEMENTOS
# ==========================================================


for categoria in categorias_exibir:



    nome_categoria = categoria.get(

        "nome",

        ""

    )



    produtos_categoria = listar_produtos_por_categoria_id(

        categoria["id"]

    )



    if not produtos_categoria:


        continue





    with st.container(border=True):


        st.markdown(

            f"**{nome_categoria}**"

        )



        colunas = st.columns(2)



        for indice, produto in enumerate(produtos_categoria):


            coluna = colunas[indice % 2]



            with coluna:



                mostrar_valor = (

                    nome_categoria.strip().lower()

                    ==

                    "adicionais"

                )





                if mostrar_valor:



                    preco = produto.get(

                        "preco"

                    )



                    if preco is None:


                        texto_valor = "Consultar valor"



                    else:


                        valor = float(preco)


                        texto_valor = (

                            f"R$ {valor:,.2f}"

                            .replace(",", "X")

                            .replace(".", ",")

                            .replace("X",".")

                        )



                    label_produto = (

                        f"{produto['nome']} | {texto_valor}"

                    )



                else:



                    label_produto = produto["nome"]





                marcado = st.checkbox(


                    label_produto,


                    key=f"produto_extra_{produto['id']}"


                )





                if marcado:



                    adicionais_selecionados.append(


                        {


                            "produto_id":

                                produto["id"],



                            "nome":

                                produto["nome"],



                            "preco":

                                produto.get("preco")

                                if mostrar_valor

                                else None,



                            "categoria":

                                nome_categoria



                        }


                    )





                    if produto["nome"].lower().strip() == "polaroid":


                        polaroid = True
                        # ==========================================================
# FOTOS POLAROID
# ==========================================================


if polaroid:


    st.markdown(

        "### 📷 Fotos da Polaroid"

    )



    fotos = st.file_uploader(


        "Selecione as imagens",


        type=[

            "jpg",

            "jpeg",

            "png",

            "webp"

        ],


        accept_multiple_files=True,


        key="upload_polaroid"


    )


else:


    fotos = []





# ==========================================================
# PAGAMENTO
# ==========================================================


st.markdown(

    "### 💳 Pagamento"

)



with st.container(border=True):


    pagamento = st.radio(


        "Forma de pagamento",


        [

            "Pix",

            "Cartão de Crédito"

        ],


        horizontal=True,


        key="forma_pagamento"


    )





# ==========================================================
# MENSAGEM
# ==========================================================


st.markdown(

    "### 💌 Mensagem"

)



mensagem = st.text_area(


    "Mensagem que acompanhará a cesta",


    height=100,


    placeholder="Digite uma mensagem especial...",


    key="mensagem_cliente"


)





# ==========================================================
# PEDIDO ESPECIAL
# ==========================================================


st.markdown(

    "### ✨ Pedido especial"

)



pedido_especial = st.text_area(


    "Alguma solicitação especial?",


    height=100,


    placeholder="Exemplo: entregar pela manhã...",


    key="pedido_especial"


)





# ==========================================================
# ENTREGA
# ==========================================================


st.markdown(

    "### 📍 Entrega"

)



endereco = st.text_area(


    "Endereço de entrega",


    height=100,


    placeholder="Informe o endereço completo...",


    key="endereco"


)




col1,col2 = st.columns(2)



with col1:


    data_entrega = st.date_input(


        "📅 Data de entrega",


        format="DD/MM/YYYY"


    )



with col2:


    periodo_entrega = st.selectbox(


        "🕘 Período",


        [

            "Manhã",

            "Tarde",

            "Noite"

        ]


    )

    # ==========================================================
# CÁLCULO DOS VALORES
# ==========================================================


valor_cesta = 0


valor_adicionais = 0


tem_adicional_consulta = False





if cesta:


    try:


        valor_cesta = float(

            cesta.get(

                "preco",

                0

            )

        )


    except:


        valor_cesta = 0





for item in adicionais_selecionados:



    if item["preco"] is None:


        tem_adicional_consulta = True


        continue



    try:


        valor_adicionais += float(

            item["preco"]

        )


    except:


        pass





valor_estimado = (

    valor_cesta +

    valor_adicionais

)





# ==========================================================
# RESUMO DO PEDIDO
# ==========================================================


if cesta:


    st.divider()



    st.markdown(

        "### 💰 Resumo do pedido"

    )



    col1,col2 = st.columns(2)



    with col1:


        st.write(

            "🎁 Valor da cesta"

        )


        st.write(

            f"R$ {valor_cesta:,.2f}"

            .replace(",", "X")

            .replace(".", ",")

            .replace("X",".")

        )





    with col2:


        st.write(

            "🎀 Complementos"

        )


        st.write(

            f"R$ {valor_adicionais:,.2f}"

            .replace(",", "X")

            .replace(".", ",")

            .replace("X",".")

        )





    st.success(

        f"💝 Valor estimado: R$ {valor_estimado:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )





    if tem_adicional_consulta:


        st.warning(

            "⚠️ Existem itens com valor sob consulta. "
            "Nossa equipe informará o valor final."

        )





# ==========================================================
# BOTÃO ENVIO
# ==========================================================


st.divider()



enviar = st.button(


    "🎁 ENVIAR PEDIDO",


    use_container_width=True,


    type="primary",


    key="enviar_pedido"


)





# ==========================================================
# PROCESSAMENTO DO PEDIDO
# ==========================================================


if enviar:



    if not nome.strip():


        st.error(

            "Informe o nome do cliente."

        )

        st.stop()





    if not cpf.strip():


        st.error(

            "Informe o CPF."

        )

        st.stop()





    if not telefone.strip():


        st.error(

            "Informe o telefone."

        )

        st.stop()





    if not cesta:


        st.error(

            "Selecione uma cesta."

        )

        st.stop()





    # ======================================================
    # PRODUTOS ESCOLHIDOS
    # ======================================================


    produtos_escolhidos = []



    for categoria, itens in selecoes_cliente.items():


        for item in itens:


            produtos_escolhidos.append(

                f"{categoria}: {item['nome']}"

            )





    # ======================================================
    # COMPLEMENTOS
    # ======================================================


    complementos_texto = []



    for item in adicionais_selecionados:



        if item["preco"] is None:


            complementos_texto.append(

                f"{item['nome']} (Preço sob consulta)"

            )


        else:


            complementos_texto.append(

                item["nome"]

            )





    # ======================================================
    # DADOS DO PEDIDO
    # ======================================================


    dados = {


        "cliente_nome":

            nome,



        "cliente_cpf":

            cpf,



        "cliente_telefone":

            telefone,



        "cesta_id":

            cesta["id"],



        "cesta_nome":

            cesta["nome"],



        "produtos":

            "\n".join(

                produtos_escolhidos

            ),



        "adicionais":

            ", ".join(

                complementos_texto

            ),



        "pagamento":

            pagamento,



        "mensagem":

            mensagem,



        "pedido_especial":

            pedido_especial,



        "endereco":

            endereco,



        "data_entrega":

            data_entrega.strftime(

                "%Y-%m-%d"

            ),



        "periodo_entrega":

            periodo_entrega,



        "status":

            "Recebido",



        "valor_frete":

            0,



        "valor_total":

            valor_estimado


    }





    try:


        sucesso, pedido_id = salvar_pedido(

            dados

        )



    except Exception as erro:


        st.error(

            f"Erro ao salvar pedido: {erro}"

        )

        st.stop()





    if sucesso:



        # salvar adicionais


        if adicionais_selecionados:



            try:


                salvar_adicionais_pedido(

                    pedido_id,

                    adicionais_selecionados

                )


            except Exception as erro:


                st.warning(

                    f"Pedido salvo, mas erro nos adicionais: {erro}"

                )





        # salvar fotos


        if polaroid and fotos:



            try:


                salvar_fotos(

                    pedido_id,

                    fotos

                )


            except Exception as erro:


                st.warning(

                    f"Pedido salvo, mas erro nas fotos: {erro}"

                )





        st.success(

            "🎉 Pedido enviado com sucesso!"

        )



        st.info(
"""
❤️ Obrigado por escolher a **Doce Cesta Brasília**!

Recebemos seu pedido.

Nossa equipe entrará em contato para confirmar:

✅ Valores dos itens sob consulta  
✅ Valor do frete  
✅ Valor final do pedido  
✅ Detalhes da entrega
"""
        )





    else:


        st.error(

            f"Erro ao salvar pedido: {pedido_id}"

        )





# ==========================================================
# RODAPÉ
# ==========================================================


st.divider()



st.markdown(
"""
<div style="
text-align:center;
font-size:12px;
padding:15px;
">

© 2026 Doce Cesta Brasília

</div>
""",

unsafe_allow_html=True

)



st.page_link(

    "pages/99_Admin.py",

    label="Área Administrativa",

    icon="🔒"

)

            )
