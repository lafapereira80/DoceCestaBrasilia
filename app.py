import streamlit as st
from pathlib import Path
from datetime import datetime


from services.pedido_service import salvar_pedido
from services.foto_service import salvar_fotos
from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta
from services.produto_service import listar_produtos_por_categoria



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



div[data-baseweb="input"]{

    background:white;

    border-radius:10px;

    border:1px solid #c9b8a8;

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
        [2,1,2]
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


try:

    cestas = listar_cestas()


except Exception as erro:

    st.error(
        f"Erro ao carregar cestas: {erro}"
    )

    cestas = []



st.markdown(
"### 🎁 Escolha sua cesta"
)



cesta = None



if cestas:


    opcoes_cestas = [

        {"nome":"Selecione...", "id":None}

    ] + cestas



    cesta = st.selectbox(

        "Selecione a cesta",

        opcoes_cestas,

        format_func=lambda c:
            c["nome"],

        index=0

    )



    if cesta["id"] is None:

        cesta = None



else:


    st.warning(
        "Nenhuma cesta cadastrada."
    )



# ==========================================================
# DADOS VISUAIS DA CESTA
# ==========================================================


if cesta:


    col1, col2 = st.columns(

        [1,2]

    )



    with col1:


        if cesta.get("imagem"):


            st.markdown(

            """
            <style>

            .imagem-cesta img{

                border-radius:15px;

                border:1px solid #ead8c7;

            }

            </style>
            """,

            unsafe_allow_html=True

            )



            st.markdown(

                '<div class="imagem-cesta">',

                unsafe_allow_html=True

            )


            st.image(

                cesta["imagem"],

                width=220

            )


            st.markdown(

                '</div>',

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


            preco = float(

                cesta["preco"]

            )


            st.markdown(

                f"""
                <div style="
                background:#fffaf5;
                border:1px solid #ead8c7;
                border-radius:12px;
                padding:12px;
                margin-top:10px;
                ">

                <b>🎁 Valor da cesta</b><br>

                <span style="
                font-size:22px;
                color:#8B5A2B;
                font-weight:bold;
                ">

                R$ {preco:,.2f}

                </span>

                </div>
                """,

                unsafe_allow_html=True

            )
            
# ==========================================================
# PERSONALIZAÇÃO DA CESTA
# ==========================================================


st.markdown(
    "### 🍓 Personalize sua cesta"
)



selecoes_cliente = {}



if cesta:


    configuracao = carregar_configuracao_cesta(

        cesta["id"]

    )


    if configuracao:


        for grupo in configuracao:


            categoria = grupo.get(

                "categoria",

                "Sem Categoria"

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



            with st.container(border=True):


                st.markdown(

                    f"**{categoria}**"

                )



                # ======================================
                # UMA ESCOLHA
                # ======================================


                if maximo == 1:



                    escolhido = st.radio(


                        "Escolha uma opção",


                        produtos,


                        format_func=lambda p:

                            p["nome"],


                        key=f"radio_{cesta['id']}_{categoria}"

                    )



                    selecoes_cliente[categoria] = [

                        escolhido

                    ]



                # ======================================
                # VÁRIAS ESCOLHAS
                # ======================================


                else:



                    escolhidos = st.multiselect(


                        f"Escolha entre {minimo} e {maximo} opções",


                        produtos,


                        format_func=lambda p:

                            p["nome"],


                        max_selections=maximo,


                        key=f"multi_{cesta['id']}_{categoria}"

                    )



                    if len(escolhidos) < minimo:


                        st.warning(

                            f"Escolha pelo menos {minimo} opção(ões)."

                        )



                    selecoes_cliente[categoria] = escolhidos



    else:


        st.info(

            "Esta cesta ainda não possui produtos configurados."

        )



else:


    st.info(

        "Escolha uma cesta para personalizar."

    )





# ==========================================================
# ADICIONAIS
# ==========================================================


st.markdown(

    "### 🎀 Adicionais"

)



try:


    adicionais_cadastrados = listar_produtos_por_categoria(

        "Adicionais"

    )


except Exception as erro:


    adicionais_cadastrados = []


    st.error(

        f"Erro ao carregar adicionais: {erro}"

    )



adicionais_selecionados = []


polaroid = False



with st.container(border=True):


    if adicionais_cadastrados:


        colunas = st.columns(2)



        for indice, adicional in enumerate(adicionais_cadastrados):


            with colunas[indice % 2]:


                preco = adicional.get(

                    "preco",

                    0

                )



                try:

                    preco_formatado = (

                        f"{float(preco):,.2f}"

                        .replace(",", "X")

                        .replace(".", ",")

                        .replace("X",".")

                    )


                except:


                    preco_formatado = "0,00"



                texto_adicional = (

                    f"{adicional['nome']} - R$ {preco_formatado}"

                )



                marcado = st.checkbox(


                    texto_adicional,


                    key=f"adicional_{adicional['id']}"

                )



                if marcado:


                    adicionais_selecionados.append(


                        {


                            "nome":

                                adicional["nome"],


                            "preco":

                                preco


                        }


                    )



                    if adicional["nome"].lower().strip() == "polaroid":


                        polaroid = True



    else:


        st.info(

            "Nenhum adicional cadastrado."

        )





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


        key="fotos_polaroid"

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


    key="pedido_especial_cliente"

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


    key="endereco_entrega"

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
# CALCULO VALOR ESTIMADO
# ==========================================================


valor_cesta = 0


valor_adicionais = 0



if cesta:


    valor_cesta = cesta.get(

        "preco",

        0

    )



    try:

        valor_cesta = float(valor_cesta)

    except:

        valor_cesta = 0





for item in adicionais_selecionados:


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





if cesta:


    st.divider()



    st.markdown(

        "### 💰 Resumo do pedido"

    )



    col1,col2 = st.columns(2)



    with col1:


        st.write(

            "Valor da cesta"

        )


        st.write(

            f"R$ {valor_cesta:,.2f}"

            .replace(",", "X")
            .replace(".", ",")
            .replace("X",".")

        )



    with col2:


        st.write(

            "Adicionais"

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



    # ======================================================
    # VALIDAÇÕES
    # ======================================================


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
    # VALIDAÇÃO DAS ESCOLHAS
    # ======================================================


    configuracao = carregar_configuracao_cesta(

        cesta["id"]

    )



    for grupo in configuracao or []:



        categoria = grupo.get(

            "categoria",

            ""

        )



        minimo = grupo.get(

            "min_escolhas",

            0

        )



        selecionados = selecoes_cliente.get(

            categoria,

            []

        )



        if len(selecionados) < minimo:



            st.error(

                f"A categoria {categoria} exige pelo menos {minimo} escolha(s)."

            )

            st.stop()





    # ======================================================
    # PRODUTOS ESCOLHIDOS
    # ======================================================


    produtos_escolhidos = []



    for categoria,itens in selecoes_cliente.items():


        for item in itens:


            produtos_escolhidos.append(

                f"{categoria}: {item['nome']}"

            )





    # ======================================================
    # ADICIONAIS TEXTO
    # ======================================================


    adicionais_texto = []



    for item in adicionais_selecionados:


        adicionais_texto.append(

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

                adicionais_texto

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

                "%d/%m/%Y"

            ),



        "periodo_entrega":

            periodo_entrega,



        "status":

            "Recebido",



        # permanece zerado para cálculo administrativo

        "valor_frete":

            0,



        "valor_total":

            0



    }





    # ======================================================
    # SALVAR PEDIDO
    # ======================================================


    try:


        sucesso, pedido_id = salvar_pedido(

            dados

        )



    except Exception as erro:


        st.error(

            f"Erro ao gravar pedido: {erro}"

        )

        st.stop()





    if sucesso:




        # ==================================================
        # SALVAR FOTOS POLAROID
        # ==================================================


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

✅ Valor do frete  
✅ Valor final da cesta  
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
