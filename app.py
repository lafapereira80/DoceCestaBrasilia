import streamlit as st
from pathlib import Path


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
# CSS - DESIGN CLIENTE
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




/* CAMPOS */

div[data-baseweb="input"]{

    background:white;

    border-radius:10px;

    border:1px solid #c9b8a8;

}



div[data-baseweb="input"]:focus-within{

    border:2px solid #8B5A2B;

}



input{

    height:42px !important;

    font-size:15px !important;

}



textarea{

    font-size:15px !important;

    border-radius:10px !important;

}



/* SELECT */

div[data-baseweb="select"] > div{

    border-radius:10px;

    border:1px solid #c9b8a8;

    min-height:42px;

}




/* CHECKBOX */

div[data-testid="stCheckbox"]{

    background:#fffaf5;

    padding:8px;

    border-radius:8px;

}



/* BOTÃO */

.stButton button{

    background:#8B5A2B;

    color:white;

    border-radius:12px;

    height:52px;

    font-size:16px;

    font-weight:bold;

    width:100%;

}



.stButton button:hover{

    background:#6f451f;

}




/* CAIXAS */

.caixa-secao{

    background:#fffaf5;

    border-radius:12px;

    padding:15px;

    border:1px solid #ead8c7;

    margin-bottom:15px;

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
# DADOS CLIENTE
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


    cesta = st.selectbox(


        "Selecione a cesta",


        cestas,


        format_func=lambda c:

            c["nome"]

    )



else:


    st.warning(

        "Nenhuma cesta cadastrada no momento."

    )



# ==========================================================
# DADOS VISUAIS DA CESTA
# ==========================================================


if cesta:


    col1,col2 = st.columns(

        [1,2]

    )



    with col1:


        if cesta.get("imagem"):


            st.image(

                cesta["imagem"],

                use_container_width=True

            )



    with col2:


        if cesta.get("descricao"):


            st.info(

                cesta["descricao"]

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



            categoria = grupo["categoria"]


            produtos = grupo["produtos"]


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



                # --------------------------------
                # SOMENTE 1 ESCOLHA
                # --------------------------------


                if maximo == 1:



                    escolhido = st.radio(


                        "Escolha uma opção",


                        produtos,


                        format_func=lambda p:

                            p["nome"],


                        key=f"radio_{categoria}"

                    )



                    selecoes_cliente[categoria] = [


                        escolhido


                    ]



                # --------------------------------
                # MAIS DE UMA ESCOLHA
                # --------------------------------


                else:



                    escolhidos = st.multiselect(



                        f"Escolha entre {minimo} e {maximo} opções",



                        produtos,



                        format_func=lambda p:

                            p["nome"],



                        max_selections=maximo,



                        key=f"multi_{categoria}"



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

        "Escolha uma cesta para personalizar os produtos."

    )





# ==========================================================
# ADICIONAIS DINÂMICOS
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



            coluna = colunas[

                indice % 2

            ]



            with coluna:



                marcado = st.checkbox(


                    adicional["nome"],


                    key=f"adicional_{adicional['id']}"



                )



                if marcado:



                    adicionais_selecionados.append(

                        adicional["nome"]

                    )



                    # identifica polaroid

                    if adicional["nome"].lower().strip() == "polaroid":


                        polaroid = True




    else:



        st.info(

            "Nenhum adicional cadastrado."

        )




# ==========================================================
# ENVIO DE FOTOS POLAROID
# ==========================================================


if polaroid:



    st.markdown(

        "### 📷 Envie as fotos para a Polaroid"

    )



    fotos = st.file_uploader(



        "Selecione as imagens",



        type=[



            "jpg",



            "jpeg",



            "png",



            "webp"



        ],



        accept_multiple_files=True



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



        "",



        [



            "Pix",



            "Cartão de Crédito"



        ],



        horizontal=True



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


    placeholder="Digite uma mensagem especial..."


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


    placeholder="Exemplo: entregar pela manhã..."


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



    placeholder="Informe o endereço completo..."



)



col1,col2 = st.columns(2)



with col1:



    data_entrega = st.date_input(



        "📅 Data"



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
# BOTÃO
# ==========================================================


st.divider()



enviar = st.button(



    "🎁 ENVIAR PEDIDO",



    use_container_width=True,



    type="primary"



)





# ==========================================================
# PROCESSAMENTO
# ==========================================================


if enviar:



    # -------------------------------
    # VALIDAÇÕES
    # -------------------------------


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




    # -------------------------------
    # VALIDAÇÃO DAS ESCOLHAS
    # -------------------------------


    configuracao = carregar_configuracao_cesta(

        cesta["id"]

    )



    for grupo in configuracao:



        categoria = grupo["categoria"]


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





    # -------------------------------
    # PRODUTOS ESCOLHIDOS
    # -------------------------------


    produtos_escolhidos = []



    for categoria,itens in selecoes_cliente.items():



        for item in itens:



            produtos_escolhidos.append(



                f"{categoria}: {item['nome']}"



            )





    # -------------------------------
    # DADOS DO PEDIDO
    # -------------------------------


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

                adicionais_selecionados

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

            str(data_entrega),



        "periodo_entrega":

            periodo_entrega,



        "status":

            "Recebido",



        "valor_frete":

            0,



        "valor_total":

            0



    }





    # -------------------------------
    # SALVAR PEDIDO
    # -------------------------------


    sucesso, pedido_id = salvar_pedido(

        dados

    )





    if sucesso:




        # -------------------------------
        # SALVAR FOTOS POLAROID
        # -------------------------------


        if polaroid and fotos:



            try:



                salvar_fotos(



                    pedido_id,



                    fotos



                )



            except Exception as erro:



                st.warning(



                    f"Pedido salvo, mas houve erro nas fotos: {erro}"



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
